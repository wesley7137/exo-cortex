import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
# app_new.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from interfaces.cli import ExoCortexCLI
from interfaces.voice_interface import VoiceInterface
from ai_model.integration import AIAssistant
from models import AIConfig, AIProfile, Preferences, FineTuneRequest, DeployRequest, PPOAgent, GNNModelWrapper, CustomEnv

from flask import Flask, request, jsonify
from typing import List, Dict, Any
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)



app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


# Example in-memory storage for AI profiles and deployments
ai_profiles = {}
deployments = {}
models = {}
# In-memory storage for preferences and AI profiles (for demonstration purposes)
preferences_db = {}
ai_profiles_db = {}

# Initialize RL Agent
rl_agent = PPOAgent(env=CustomEnv(), total_timesteps=10000)
rl_agent.train()
# Initialize GNN Model
gnn_model = GNNModelWrapper(input_dim=10, hidden_dim=16, output_dim=4)
gnn_model.initialize_model()


@app.route('/api/ai-profile', methods=['POST'])
def create_ai_profile():
    try:
        data = request.get_json()
        profile = generate_ai_profile(data)
        return jsonify(profile), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route("/api/get_preferences", methods=["GET"])
def get_preferences():
    """
    Endpoint to retrieve user preferences.
    """
    try:
        # For demonstration, return default preferences or fetch from a database
        # Replace with actual user identification and data retrieval logic
        preferences = Preferences(
            personality="friendly",
            tasks=["task1", "task2"],
            useCases=["useCase1", "useCase2"]
        )
        return jsonify(preferences.dict()), 200
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

@app.route("/api/set_preferences", methods=["POST"])
def set_preferences():
    """
    Endpoint to update user preferences.
    """
    try:
        data = request.get_json()
        preferences = Preferences(**data)
        # Save preferences to the database
        # Replace with actual persistence logic
        preferences_db["default_user"] = preferences
        return jsonify(preferences.dict()), 200
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

@app.route("/api/fine-tune", methods=["POST"])
def fine_tune():
    """
    Endpoint to fine-tune the AI model.
    """
    try:
        data = request.get_json()
        request_data = FineTuneRequest(**data)
        result = fine_tune_model(request_data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

@app.route("/deploy", methods=["POST"])
def deploy():
    """
    Endpoint to deploy the AI assistant.
    """
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
    """
    Generates an AI profile based on the provided configuration.

    Args:
        config (Dict[str, Any]): Configuration settings for the AI profile.

    Returns:
        Dict[str, Any]: Generated AI profile.
    """
    logging.info("Generating AI profile with config: %s", config)
    
    # Placeholder for actual AI profile generation logic
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
    logging.info("AI profile generated with ID: %d", profile_id)
    return ai_profile

# Flask route example for generating AI profile
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
    """
    Fine-tunes an existing AI model with the provided parameters.

    Args:
        model_id (str): Identifier of the model to fine-tune.
        fine_tune_params (Dict[str, Any]): Parameters for fine-tuning.

    Returns:
        Dict[str, Any]: Status and details of the fine-tuning process.
    """
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

# Flask route example for fine-tuning a model
@app.route('/api/fine_tune_model', methods=['POST'])
def api_fine_tune_model():
    data = request.json
    model_id = data.get('model_id')
    fine_tune_params = data.get('fine_tune_params')
    
    if not model_id or not fine_tune_params:
        return jsonify({"error": "Model ID and fine-tune parameters are required."}), 400
    try:
        result = fine_tune_model(model_id, fine_tune_params)
        if "error" in result:
            return jsonify(result), 404
        return jsonify(result), 200
    except Exception as e:
        logging.error("Error fine-tuning model: %s", e)
        return jsonify({"error": "Failed to fine-tune model."}), 500

# -------------------------------
# 3. Deploy AI Assistant
# -------------------------------
def deploy_ai_assistant(profile_id: int, deployment_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deploys an AI assistant based on the specified AI profile and deployment parameters.

    Args:
        profile_id (int): Identifier of the AI profile to deploy.
        deployment_params (Dict[str, Any]): Parameters for deployment (e.g., environment, scaling).

    Returns:
        Dict[str, Any]: Deployment status and details.
    """
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

# Flask route example for deploying an AI assistant
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
        logging.error("Error deploying AI assistant: %s", e)
        return jsonify({"error": "Failed to deploy AI assistant."}), 500

# -------------------------------
# 4. Customize AI Profile
# -------------------------------
def customize_ai_profile(profile_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Customizes an existing AI profile with the provided updates.

    Args:
        profile_id (int): Identifier of the AI profile to customize.
        updates (Dict[str, Any]): Fields to update in the AI profile.

    Returns:
        Dict[str, Any]: Updated AI profile or error message.
    """
    logging.info("Customizing AI profile ID: %d with updates: %s", profile_id, updates)
    
    if profile_id not in ai_profiles:
        logging.warning("AI Profile ID %d not found.", profile_id)
        return {"error": "AI Profile not found."}
    
    ai_profiles[profile_id].update(updates)
    logging.info("AI profile ID %d updated successfully.", profile_id)
    return ai_profiles[profile_id]

# Flask route example for customizing an AI profile
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
        logging.error("Error customizing AI profile: %s", e)
        return jsonify({"error": "Failed to customize AI profile."}), 500

# -------------------------------
# 5. Fine-Tune Model Button Action
# -------------------------------
def fine_tune_model_action(profile_id: int) -> Dict[str, Any]:
    """
    Initiates the fine-tuning process for the AI profile's base model.

    Args:
        profile_id (int): Identifier of the AI profile whose model is to be fine-tuned.

    Returns:
        Dict[str, Any]: Status of the fine-tuning initiation.
    """
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
# 6. Deploy AI Assistant Button Action
# -------------------------------
def deploy_ai_assistant_action(profile_id: int) -> Dict[str, Any]:
    """
    Initiates the deployment of an AI assistant based on the specified profile.

    Args:
        profile_id (int): Identifier of the AI profile to deploy.

    Returns:
        Dict[str, Any]: Deployment details or error message.
    """
    logging.info("Initiating deployment for profile ID: %d", profile_id)
    
    # Define default deployment parameters or retrieve from config
    deployment_params = {
        "environment": "production",
        "scaling": {
            "min_instances": 1,
            "max_instances": 5
        }
    }
    
    deployment = deploy_ai_assistant(profile_id, deployment_params)
    return deployment

# Flask route example for deploy AI assistant button action
@app.route('/api/deploy_action', methods=['POST'])
def api_deploy_action():
    data = request.json
    profile_id = data.get('profile_id')
    
    if not profile_id:
        return jsonify({"error": "Profile ID is required."}), 400
    try:
        deployment = deploy_ai_assistant_action(profile_id)
        if "error" in deployment:
            return jsonify(deployment), 404
        return jsonify(deployment), 201
    except Exception as e:
        logging.error("Error initiating deployment: %s", e)
        return jsonify({"error": "Failed to initiate deployment."}), 500

# -------------------------------
# Additional Helper Functions
# -------------------------------
def get_ai_profile(profile_id: int) -> Dict[str, Any]:
    """
    Retrieves an AI profile by its ID.

    Args:
        profile_id (int): Identifier of the AI profile.

    Returns:
        Dict[str, Any]: AI profile data or error message.
    """
    logging.info("Retrieving AI profile ID: %d", profile_id)
    profile = ai_profiles.get(profile_id)
    if not profile:
        logging.warning("AI Profile ID %d not found.", profile_id)
        return {"error": "AI Profile not found."}
    return profile

def list_ai_profiles() -> List[Dict[str, Any]]:
    """
    Lists all available AI profiles.

    Returns:
        List[Dict[str, Any]]: List of AI profiles.
    """
    logging.info("Listing all AI profiles.")
    return list(ai_profiles.values())

# Flask route examples for helper functions
@app.route('/api/ai_profiles/<int:profile_id>', methods=['GET'])
def api_get_ai_profile(profile_id):
    profile = get_ai_profile(profile_id)
    if "error" in profile:
        return jsonify(profile), 404
    return jsonify(profile), 200

@app.route('/api/ai_profiles', methods=['GET'])
def api_list_ai_profiles():
    profiles = list_ai_profiles()
    return jsonify(profiles), 200

# -------------------------------
# Run the Flask app
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)






def main():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        # Run the Flask API server
        app.run(host='0.0.0.0', port=5000)
    elif len(sys.argv) > 1 and sys.argv[1] == 'voice':
        # Run the voice interface
        voice_interface = VoiceInterface()
        assistant = AIAssistant(user_id=123)  # Replace with actual user ID
        while True:
            user_input = voice_interface.listen()
            if user_input:
                response = assistant.generate_response(user_input)
                voice_interface.speak(response)
    else:
        # Run the CLI
        cli = ExoCortexCLI()
        cli.run()

if __name__ == "__main__":
    main()