import secrets
from bson.objectid import ObjectId


import sys
import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import pickle

from flask import Flask, request, jsonify, session, make_response
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List, Dict, Any
import logging

from interfaces.cli import ExoCortexCLI
from interfaces.voice_interface import VoiceInterface
from ai_model.integrations_manager import AIAssistant
from ai_model.fine_tune import FineTuner
from ai_model.context_manager import ContextManager
from cortex.cortex import Cortex, KnowledgeIngestion
from utils.database import db
from models import (
    User, AIProfile, AIConfig, Preferences, FineTuneRequest,
    DeployRequest, PPOAgent, GNNModelWrapper, CustomEnv
)
import joblib
from stable_baselines3 import PPO
from ai_model.agent_manager import get_agent_manager



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





app = Flask(__name__)
app.secret_key = 'admin'  # Set a secret key for sessions
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
# Initialize database

# Configure logging


# Example in-memory storage for AI profiles and deployments
ai_profiles = {}
deployments = {}
models = {}
preferences_db = {}
ai_profiles_db = {}

# Global variables for RL agent and GNN model
rl_agent = None
gnn_model = None

MODEL_SAVE_PATH = 'saved_models/'
RL_AGENT_FILE = 'rl_agent.zip'
GNN_MODEL_FILE = 'gnn_model.joblib'

def save_model(model, filename):
    os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
    if isinstance(model, PPOAgent):
        model.model.save(os.path.join(MODEL_SAVE_PATH, filename))
    else:
        joblib.dump(model, os.path.join(MODEL_SAVE_PATH, filename))

def load_model(filename, model_type):
    try:
        if model_type == 'rl_agent':
            model = PPO.load(os.path.join(MODEL_SAVE_PATH, filename))
            return PPOAgent(model=model)
        else:
            return joblib.load(os.path.join(MODEL_SAVE_PATH, filename))
    except FileNotFoundError:
        return None

def initialize_models():
    global rl_agent, gnn_model
    
    # Try to load the RL agent
    rl_agent = load_model(RL_AGENT_FILE, 'rl_agent')
    if rl_agent is None:
        logger.info("Training new RL agent...")
        rl_agent = PPOAgent(total_timesteps=10000)
        rl_agent.train()
        save_model(rl_agent, RL_AGENT_FILE)
        logger.info("RL agent training completed and saved.")
    else:
        logger.info("Loaded pre-trained RL agent.")
    
    # Try to load the GNN model
    gnn_model = load_model(GNN_MODEL_FILE, 'gnn_model')
    if gnn_model is None:
        logger.info("Initializing new GNN model...")
        gnn_model = GNNModelWrapper(input_dim=10, hidden_dim=16, output_dim=4)
        gnn_model.initialize_model()
        save_model(gnn_model, GNN_MODEL_FILE)
        logger.info("GNN model initialized and saved.")
    else:
        logger.info("Loaded pre-trained GNN model.")



def cors_error_handler(error):
    response = make_response(jsonify({"error": str(error)}), error.code if hasattr(error, 'code') else 500)
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Register the error handler for all exceptions
app.register_error_handler(Exception, cors_error_handler)

@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = app.make_default_options_response()
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response



@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if db.users.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 400

    hashed_password = generate_password_hash(password)
    user_id = db.users.insert_one({
        "username": username,
        "email": email,
        "password": hashed_password
    }).inserted_id

    session['user_id'] = str(user_id)
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = db.users.find_one({"email": email})
    if user and check_password_hash(user['password'], password):
        session['user_id'] = str(user['_id'])
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401
    
    
    
@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/api/request_password_reset', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email')

    user = db.users.find_one({"email": email})
    if not user:
        return jsonify({"error": "Email not found"}), 404

    reset_token = secrets.token_urlsafe(16)
    db.password_resets.insert_one({
        "user_id": user['_id'],
        "token": reset_token
    })

    # Send reset_token to user's email (implementation depends on your email service)
    # send_email(email, reset_token)

    return jsonify({"message": "Password reset token sent"}), 200

@app.route('/api/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')

    reset_entry = db.password_resets.find_one({"token": token})
    if not reset_entry:
        return jsonify({"error": "Invalid or expired token"}), 400

    hashed_password = generate_password_hash(new_password)
    db.users.update_one(
        {"_id": reset_entry['user_id']},
        {"$set": {"password": hashed_password}}
    )

    db.password_resets.delete_one({"_id": reset_entry['_id']})

    return jsonify({"message": "Password reset successfully"}), 200



@app.route('/api/user', methods=['GET'])
def get_user():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user = db.users.find_one({"_id": ObjectId(session['user_id'])})
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(username=user.get('username'), email=user.get('email')), 200

@app.route('/api/users/me/preferences', methods=['GET', 'PUT'])
def user_preferences():
    print("Entering user_preferences function")  # Debug print
    if 'user_id' not in session:
        print(f"User not authenticated. Session: {session}")  # Debug print
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session['user_id']
    user = db.users.find_one({"_id": ObjectId(user_id)})
    print(f"User retrieved: {user}")  # Debug print
    if not user:
        print(f"User not found for id: {user_id}")  # Debug print
        return jsonify({"error": "User not found"}), 404
    
    if request.method == 'GET':
        print(f"GET request. Returning preferences: {user.get('preferences', {})}")  # Debug print
        return jsonify(user.get('preferences', {}))
    elif request.method == 'PUT':
        print(f"PUT request. Updating preferences with: {request.json}")  # Debug print
        preferences = request.json
        try:
            db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"preferences": preferences}})
            print("Preferences updated successfully")  # Debug print
            return jsonify({"message": "Preferences updated successfully"}), 200
        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Debug print
            return jsonify({"error": "Failed to update preferences"}), 400



@app.route('/api/users/me/api_keys', methods=['GET', 'PUT'])
def user_api_keys():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session['user_id']
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404

    if request.method == 'GET':
        secrets = user.get('secrets', {})
        api_keys = {
            "openai_api_key": secrets.get('openai_api_key'),
            "anthropic_api_key": secrets.get('anthropic_api_key'),
            "google_api_key": secrets.get('google_api_key'),
            "huggingface_token": secrets.get('huggingface_token'),
            "activeloop_token": secrets.get('activeloop_token'),
        }
        return jsonify(api_keys), 200
    elif request.method == 'PUT':
        data = request.get_json()
        secrets = user.get('secrets', {})
        for key in ['openai_api_key', 'anthropic_api_key', 'google_api_key', 'huggingface_token', 'activeloop_token']:
            if data.get(key):
                secrets[key] = data[key]
        try:
            db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"secrets": secrets}})
            return jsonify({"message": "API keys updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": "Failed to update API keys"}), 400
        
        
        
        
        
        
@app.route('/api/ai-profile', methods=['POST'])
def create_ai_profile():
    print("Entering create_ai_profile function")  # Debug print
    try:
        data = request.get_json()
        print(f"Received data for AI profile creation: {data}")  # Debug print
        profile = generate_ai_profile(data)
        print(f"Generated AI profile: {profile}")  # Debug print
        return jsonify(profile), 201
    except Exception as e:
        print(f"Error creating AI profile: {e}")  # Debug print
        logger.error(f"Error creating AI profile: {e}")
        return jsonify({"error": str(e)}), 500




@app.route("/api/set_preferences", methods=["POST"])
def set_preferences():
    print("Entering set_preferences function")  # Debug print
    try:
        data = request.get_json()
        print(f"Received data for setting preferences: {data}")  # Debug print
        preferences = Preferences(**data)
        # Save preferences to the database
        # Replace with actual persistence logic
        preferences_db["default_user"] = preferences
        print(f"Preferences saved: {preferences.dict()}")  # Debug print
        return jsonify(preferences.dict()), 200
    except Exception as e:
        print(f"Error in set_preferences: {str(e)}")  # Debug print
        return jsonify({"detail": str(e)}), 500


@app.route("/api/fine-tune", methods=["POST"])
def fine_tune():
    try:
        data = request.get_json()
        request_data = FineTuneRequest(**data)
        result = fine_tune_model(request_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


@app.route("/deploy", methods=["POST"])
def deploy():

    try:
        data = request.get_json()
        deploy_request = DeployRequest(**data)
        result = deploy_ai_assistant(deploy_request)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"detail": str(e)}), 500


# -------------------------------
# 1. Generate AI Profile
# -------------------------------
def generate_ai_profile(config: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Generating AI profile with config: {config}")
    profile_id = len(ai_profiles) + 1
    ai_profile = {
        "id": profile_id,
        "base_model": config.get("baseModel"),
        "personality": config.get("personality"),
        "primary_expertise": config.get("primaryExpertise"),
        "communication_style": config.get("communicationStyle"),
        "creativity_level": config.get("creativityLevel"),
        "response_length": config.get("responseLength"),
        "memory_modules": config.get("memoryModules"),
        "tool_integrations": config.get("toolIntegrations"),
        "execute_code": config.get("executeCode"),
        "always_on": config.get("alwaysOn"),
        "ethical_boundaries": config.get("ethicalBoundaries"),
        "language_proficiency": config.get("languageProficiency"),
        "voice_interface": config.get("voiceInterface"),
        "learning_rate": config.get("learningRate"),
        "speech_to_text": config.get("speechToText"),
    }
    ai_profiles[profile_id] = ai_profile
    logger.info(f"AI profile generated with ID: {profile_id}")
    return ai_profile



@app.route('/api/generate_ai_profile', methods=['POST'])
def api_generate_ai_profile():
    config = request.json.get('config')
    if not config:
        return jsonify({"error": "Configuration data is required."}), 400
    try:
        profile = generate_ai_profile(config)
        return jsonify(profile), 201
    except Exception as e:
        logging.error("Error generating AI profile: %s", e)
        return jsonify({"error": "Failed to generate AI profile."}), 500

# -------------------------------
# 2. Fine-Tune Model
# -------------------------------
def fine_tune_model(model_id: str, fine_tune_params: Dict[str, Any]) -> Dict[str, Any]:
    
    logging.info("Fine-tuning model ID: %s with params: %s", model_id, fine_tune_params)
    
    # Placeholder for actual fine-tuning logic
    if model_id not in models:
        logging.warning("Model ID %s not found.", model_id)
        return {"error": "Model not found."}
    
    # Simulate fine-tuning process
    fine_tuned_model = models[model_id].copy()
    fine_tuned_model.update(fine_tune_params)
    fine_tuned_model_id = f"{model_id}-fine-tuned"
    models[fine_tuned_model_id] = fine_tuned_model
    
    logging.info("Model fine-tuned successfully. New model ID: %s", fine_tuned_model_id)
    return {
        "status": "success",
        "fine_tuned_model_id": fine_tuned_model_id,
        "details": fine_tuned_model
    }

@app.route('/api/fine_tune_model', methods=['POST'])
def api_fine_tune_model():
    data = request.json
    model_id = data.get('model_id')
    fine_tune_params = data.get('fine_tune_params')
    if not model_id or not fine_tune_params:
        return jsonify({"error": "Model ID and fine-tune parameters are required."}), 400
    try:
        fine_tuner = FineTuner(user_id='default_user')  # Replace with dynamic user ID if needed
        fine_tuner.fine_tune(training_data=fine_tune_params)  # Adjust based on FineTuner's API
        return jsonify({"status": "Fine-tuning initiated."}), 200
    except Exception as e:
        logger.error(f"Error fine-tuning model: {e}")
        return jsonify({"error": "Failed to fine-tune model."}), 500

# -------------------------------
# 3. Deploy AI Assistant
# -------------------------------
def deploy_ai_assistant(profile_id: int, deployment_params: Dict[str, Any]) -> Dict[str, Any]:

    logging.info("Deploying AI assistant for profile ID: %d with params: %s", profile_id, deployment_params)
    
    # Placeholder for actual deployment logic
    if profile_id not in ai_profiles:
        logging.warning("AI Profile ID %d not found.", profile_id)
        return {"error": "AI Profile not found."}
    
    deployment_id = len(deployments) + 1
    deployment = {
        "id": deployment_id,
        "profile_id": profile_id,
        "deployment_params": deployment_params,
        "status": "deployed",  # In a real scenario, you might have statuses like 'pending', 'deployed', 'failed'
    }
    
    deployments[deployment_id] = deployment
    logging.info("AI assistant deployed successfully with Deployment ID: %d", deployment_id)
    return deployment

# -------------------------------
# 4. Customize AI Profile
# -------------------------------
def customize_ai_profile(profile_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:

    logging.info("Customizing AI profile ID: %d with updates: %s", profile_id, updates)
    
    if profile_id not in ai_profiles:
        logging.warning("AI Profile ID %d not found.", profile_id)
        return {"error": "AI Profile not found."}
    
    ai_profiles[profile_id].update(updates)
    logging.info("AI profile ID %d updated successfully.", profile_id)
    return ai_profiles[profile_id]


# -------------------------------
# 5. Fine-Tune Model Button Action
# -------------------------------
def fine_tune_model_action(profile_id: int) -> Dict[str, Any]:

    logging.info("Initiating fine-tune action for profile ID: %d", profile_id)
    
    profile = ai_profiles.get(profile_id)
    if not profile:
        logging.warning("AI Profile ID %d not found.", profile_id)
        return {"error": "AI Profile not found."}
    
    base_model = profile.get("base_model")
    if not base_model:
        logging.warning("Base model not specified for profile ID %d.", profile_id)
        return {"error": "Base model not specified."}
    
    # Placeholder: Start fine-tuning process asynchronously
    fine_tuned_model_id = f"{base_model}-fine-tuned"
    models[fine_tuned_model_id] = {"base_model": base_model, "fine_tuned": True}
    
    logging.info("Fine-tuning initiated for model ID: %s", fine_tuned_model_id)
    return {
        "status": "fine-tuning initiated",
        "fine_tuned_model_id": fine_tuned_model_id
    }

# Flask route example for fine-tune model button action
@app.route('/api/fine_tune_action', methods=['POST'])
def api_fine_tune_action():
    data = request.json
    profile_id = data.get('profile_id')
    
    if not profile_id:
        return jsonify({"error": "Profile ID is required."}), 400
    try:
        result = fine_tune_model_action(profile_id)
        if "error" in result:
            return jsonify(result), 404
        return jsonify(result), 200
    except Exception as e:
        logging.error("Error initiating fine-tune action: %s", e)
        return jsonify({"error": "Failed to initiate fine-tune action."}), 500

# -------------------------------
# 3. Deploy AI Assistant (API Endpoint)
# -------------------------------
@app.route('/api/deploy_ai_assistant', methods=['POST'])
def api_deploy_ai_assistant():
    data = request.json
    profile_id = data.get('profile_id')
    deployment_params = data.get('deployment_params', {})

    if not profile_id:
        return jsonify({"error": "Profile ID is required."}), 400
    try:
        deployment = deploy_ai_assistant(profile_id, deployment_params)
        if "error" in deployment:
            return jsonify(deployment), 404
        return jsonify(deployment), 201
    except Exception as e:
        logger.error(f"Error deploying AI assistant: {e}")
        return jsonify({"error": "Failed to deploy AI assistant."}), 500

# -------------------------------
# 4. Customize AI Profile (API Endpoint)
# -------------------------------
@app.route('/api/customize_ai_profile', methods=['PUT'])
def api_customize_ai_profile():
    data = request.json
    profile_id = data.get('profile_id')
    updates = data.get('updates')

    if not profile_id or not updates:
        return jsonify({"error": "Profile ID and updates are required."}), 400
    try:
        updated_profile = customize_ai_profile(profile_id, updates)
        if "error" in updated_profile:
            return jsonify(updated_profile), 404
        return jsonify(updated_profile), 200
    except Exception as e:
        logger.error(f"Error customizing AI profile: {e}")
        return jsonify({"error": "Failed to customize AI profile."}), 500

# -------------------------------
# Additional Helper Functions
# -------------------------------
def deploy_ai_assistant(profile_id: int, deployment_params: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Deploying AI assistant for profile ID: {profile_id} with params: {deployment_params}")
    if profile_id not in ai_profiles:
        logger.warning(f"AI Profile ID {profile_id} not found.")
        return {"error": "AI Profile not found."}
    
    deployment_id = len(deployments) + 1
    deployment = {
        "id": deployment_id,
        "profile_id": profile_id,
        "deployment_params": deployment_params,
        "status": "deployed",
    }
    deployments[deployment_id] = deployment
    logger.info(f"AI assistant deployed successfully with Deployment ID: {deployment_id}")
    return deployment




def fine_tune_model(model_id: str, fine_tune_params: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Fine-tuning model ID: {model_id} with params: {fine_tune_params}")
    if model_id not in models:
        logger.warning(f"Model ID {model_id} not found.")
        return {"error": "Model not found."}
    # Simulate fine-tuning or integrate with actual fine-tuning logic
    fine_tuned_model = models[model_id].copy()
    fine_tuned_model.update(fine_tune_params)
    fine_tuned_model_id = f"{model_id}-fine-tuned"
    models[fine_tuned_model_id] = fine_tuned_model
    logger.info(f"Model fine-tuned successfully. New model ID: {fine_tuned_model_id}")
    return {
        "status": "success",
        "fine_tuned_model_id": fine_tuned_model_id,
        "details": fine_tuned_model
    }




@app.route('/generate_response', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        user_input = data.get('user_input')
        assistant = AIAssistant(user_id)
        response = assistant.generate_response(user_input)
        logger.info(f"Response generated for user {user_id}.")
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Error in /generate_response: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/ingest_text', methods=['POST'])
def ingest_text():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        text = data.get('text')
        metadata = data.get('metadata')
        ingestion = KnowledgeIngestion(user_id)
        ingestion.ingest_text(text, metadata)
        logger.info(f"Text ingested for user {user_id}.")
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error in /ingest_text: {e}")
        return jsonify({'error': str(e)}), 500



@app.route('/api/chat', methods=['POST'])
def chat():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.json
    user_input = data.get('message')

    agent_manager = get_agent_manager(user_id)
    response = agent_manager.chat_with_model(user_input)

    return jsonify({"response": response})

def list_ai_profiles() -> List[Dict[str, Any]]:

    logging.info("Listing all AI profiles.")
    return list(ai_profiles.values())



@app.route('/api/ai_profiles', methods=['GET'])
def api_list_ai_profiles():
    profiles = list_ai_profiles()
    return jsonify(profiles), 200





@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response















# -------------------------------
# Run the Flask app
# -------------------------------
def run_server():
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True)  # Set debug=False for production

def run_voice_interface():
    voice_interface = VoiceInterface()
    assistant = AIAssistant(user_id=123)  # Replace with actual user ID
    while True:
        user_input = voice_interface.listen()
        if user_input:
            response = assistant.generate_response(user_input)
            voice_interface.speak(response)

def run_cli():
    cli = ExoCortexCLI()
    cli.run()


def main():
    initialize_models()  # Initialize or load RL agent and GNN model
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'runserver':
            run_server()
        elif command == 'voice':
            run_voice_interface()
        elif command == 'cli':
            run_cli()
        else:
            logger.error(f"Unknown command: {command}")
            print("Usage: python app_new.py [runserver|voice|cli]")
    else:
        run_server()  # Default action

if __name__ == '__main__':
    main()