# ai_model/model_loader.py
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs/model_loader.log')
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
