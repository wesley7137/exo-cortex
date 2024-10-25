# ai_model/integration.py
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from ai_model.model_loader import ModelLoader
from ai_model.context_manager import ContextManager
from cortex.cortex import Cortex
from personalization.behavior_model import BehaviorModel
import os
from litellm import completion

from transformers import pipeline
import torch


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs/integration.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)





class ModelLoader:
    _model_cache = {}

    @staticmethod
    def load_base_model(model_name='EleutherAI/gpt-neo-1.3B'):
        if model_name in ModelLoader._model_cache:
            logger.info(f"Model '{model_name}' loaded from cache.")
            return ModelLoader._model_cache[model_name]

        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            ModelLoader._model_cache[model_name] = (tokenizer, model)
            logger.info(f"Model '{model_name}' loaded successfully.")
            return tokenizer, model
        except Exception as e:
            logger.error(f"Failed to load model '{model_name}': {e}")
            raise



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




def generate_llama_response(prompt, max_tokens=512):
    model_id = "meta-llama/Llama-3.2-1B-Instruct"
    pipe = pipeline(
        "text-generation",
        model=model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto" )
    messages = [
        {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
        {"role": "user", "content": prompt}]
    try:
        outputs = pipe(
            messages,
            max_new_tokens=max_tokens )
        return outputs[0]["generated_text"][-1]
    except Exception as e:
        print(f"Error generating Llama response: {e}")
        return None


def generate_openai_response(prompt, max_tokens=512):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=user_api_key.profile)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating OpenAI response: {e}")
        return None


def generate_anthropic_response(prompt, max_tokens=512):
    try:
        response = completion(
            model="anthropic/claude-2",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating Anthropic response: {e}")
        return None



def generate_ollama_response(prompt, max_tokens=512, history=None, images=None):
    try:
        messages = history if history else []
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": "llama3.2",
            "messages": messages
        }
        if images:
            payload["messages"][-1]["images"] = images
        response = completion(
            model="ollama/llama3",
            messages=payload["messages"],
            max_tokens=max_tokens )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating Ollama response: {e}")
        return None