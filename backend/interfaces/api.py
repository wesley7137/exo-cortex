# interfaces/api.py
from flask import Flask, request, jsonify
from cortex.cortex import KnowledgeIngestion
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs/api.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# Additional endpoints can be added for document, audio, and image ingestion
