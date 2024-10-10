# interfaces/cli.py
import argparse
from ai_model.integration import AIAssistant
from cortex import KnowledgeIngestion
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs/cli.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class ExoCortexCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Exo Cortex CLI')
        subparsers = self.parser.add_subparsers(dest='command')

        # Generate Response Command
        parser_generate = subparsers.add_parser('generate', help='Generate a response')
        parser_generate.add_argument('--user_id', type=int, required=True)
        parser_generate.add_argument('--input', type=str, required=True)

        # Ingest Text Command
        parser_ingest_text = subparsers.add_parser('ingest_text', help='Ingest text')
        parser_ingest_text.add_argument('--user_id', type=int, required=True)
        parser_ingest_text.add_argument('--text', type=str, required=True)

        # Other ingestion commands can be added similarly

    def run(self):
        args = self.parser.parse_args()
        if args.command == 'generate':
            self.generate_response(args.user_id, args.input)
        elif args.command == 'ingest_text':
            self.ingest_text(args.user_id, args.text)
        else:
            self.parser.print_help()

    def generate_response(self, user_id, user_input):
        assistant = AIAssistant(user_id)
        response = assistant.generate_response(user_input)
        print(f"Assistant: {response}")

    def ingest_text(self, user_id, text):
        ingestion = KnowledgeIngestion(user_id)
        ingestion.ingest_text(text)
        print("Text ingested successfully.")
