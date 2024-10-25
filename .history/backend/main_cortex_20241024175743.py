import logging
from utils.database import db, init_db, create_tables
from models import User
from ai_model.integrations_manager import IntegrationsManager
from ai_model.agent_manager import AgentManager
from ai_model.context_manager import ContextManager
from cortex.cortex import Cortex
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MainCortex:
    def __init__(self, user_id):
        self.app = Flask(__name__)
        self.setup_database()
        self.user = self.get_user(user_id)
        self.integrations_manager = IntegrationsManager(self.user)
        self.agent_manager = AgentManager(self.user)
        self.context_manager = ContextManager(self.user)
        self.cortex = Cortex(self.user)

    def setup_database(self):
        init_db(self.app)
        create_tables(self.app)

    def get_user(self, user_id):
        with self.app.app_context():
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"User with id {user_id} not found")
            return user

    def initialize_system(self):
        logger.info("Initializing MainCortex system...")
        
        # Set up integrations based on user preferences
        chat_model = self.integrations_manager.get_chat_model()
        self.agent_manager.set_chat_model(chat_model)
        
        # Set up tools and agents
        tools = self.integrations_manager.get_enabled_tools()
        self.agent_manager.setup_tools(tools)
        
        # Initialize context
        self.context_manager.initialize_context()
        
        # Set up Cortex with all components
        self.cortex.set_agent_manager(self.agent_manager)
        self.cortex.set_context_manager(self.context_manager)
        self.cortex.set_integrations_manager(self.integrations_manager)
        
        logger.info("MainCortex system initialized successfully.")

    def process_input(self, user_input):
        logger.info(f"Processing user input: {user_input}")
        
        # Update context with user input
        self.context_manager.update_context(user_input)
        
        # Get relevant context
        context = self.context_manager.get_relevant_context(user_input)
        
        # Process input through Cortex
        response = self.cortex.process_input(user_input, context)
        
        logger.info(f"Generated response: {response}")
        return response

    def run(self):
        logger.info("Starting MainCortex system...")
        self.initialize_system()
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            
            response = self.process_input(user_input)
            print(f"AI: {response}")
        
        logger.info("MainCortex system shutting down.")

if __name__ == "__main__":
    user_id = 1  # Replace with actual user ID or authentication method
    main_cortex = MainCortex(user_id)
    main_cortex.run()