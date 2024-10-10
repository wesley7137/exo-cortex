# interfaces/api.py
from flask import Flask, request, jsonify
from ai_model.integration import AIAssistant
from cortex import KnowledgeIngestion
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs/api.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

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

# Additional endpoints can be added for document, audio, and image ingestion
