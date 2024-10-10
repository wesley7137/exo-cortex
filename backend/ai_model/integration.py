# ai_model/integration.py
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from ai_model.model_loader import ModelLoader
from ai_model.context_manager import ContextManager
from cortex import Cortex
from personalization.behavior_model import BehaviorModel

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs/integration.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class AIAssistant:
    def __init__(self, user_id):
        self.user_id = user_id
        self.tokenizer, self.model = self.load_user_model()
        self.cortex = Cortex(user_id)
        self.context_manager = ContextManager()
        self.behavior_model = BehaviorModel(user_id)

    def load_user_model(self):
        try:
            model_path = f'./models/user_{self.user_id}'
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(model_path)
            logger.info(f"Fine-tuned model loaded for user {self.user_id}.")
            return tokenizer, model
        except Exception as e:
            logger.warning(f"Failed to load fine-tuned model for user {self.user_id}: {e}")
            # Fallback to base model
            return ModelLoader.load_base_model()


    def generate_response(self, user_input):
        # Check for calendar intents
        calendar_response = self.handle_calendar_intent(user_input)
        if calendar_response:
            response = calendar_response
        else:
            # Existing response generation
            response = self.generate_ai_response(user_input)
        # Apply user preferences
        response = self.behavior_model.apply_preferences(response)
        # Update context
        self.context_manager.update_history(user_input, response)
        return response

    def generate_ai_response(self, user_input):
        try:
            # Update context
            previous_context = self.context_manager.get_context()
            # Retrieve relevant memories
            relevant_memories = self.cortex.query_memory(user_input)
            if not relevant_memories:
                context = previous_context + f"User: {user_input}\nAssistant:"
            else:
                memory_text = "\n".join([item['document'] for item in relevant_memories])
                context = previous_context + memory_text + f"\nUser: {user_input}\nAssistant:"
            inputs = self.tokenizer.encode(context, return_tensors="pt")
            inputs = inputs.to(self.model.device)
            outputs = self.model.generate(
                inputs,
                max_length=512,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                temperature=0.7
            )
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            logger.info("Response generated.")
            return response
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, but I'm unable to process your request at the moment."
