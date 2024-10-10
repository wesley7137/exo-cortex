# ai_model/fine_tune.py
import logging
import torch
from torch.utils.data import Dataset
from transformers import Trainer, TrainingArguments
from peft import get_peft_model, LoraConfig, TaskType
from ai_model.model_loader import ModelLoader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs/fine_tune.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class FineTuner:
    def __init__(self, user_id, base_model_name='EleutherAI/gpt-neo-1.3B'):
        self.user_id = user_id
        self.tokenizer, self.model = ModelLoader.load_base_model(base_model_name)

    def fine_tune(self, training_data):
        try:
            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                inference_mode=False,
                r=8,
                lora_alpha=32,
                lora_dropout=0.1
            )
            self.model = get_peft_model(self.model, lora_config)

            # Prepare dataset
            dataset = self.prepare_dataset(training_data)

            training_args = TrainingArguments(
                output_dir=f'./models/user_{self.user_id}',
                num_train_epochs=3,
                per_device_train_batch_size=2,
                save_steps=1000,
                save_total_limit=2,
                logging_steps=500,
                learning_rate=2e-5,
                fp16=torch.cuda.is_available(),
                evaluation_strategy="steps",
                eval_steps=1000,
                load_best_model_at_end=True
            )

            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=dataset,
            )

            trainer.train()
            trainer.save_model(f'./models/user_{self.user_id}')
            logger.info(f"Model fine-tuned and saved for user {self.user_id}.")
        except Exception as e:
            logger.error(f"Error during fine-tuning: {e}")
            raise

    def prepare_dataset(self, training_data):
        try:
            encodings = self.tokenizer(training_data["input_texts"], truncation=True, padding=True)
            labels = self.tokenizer(training_data["target_texts"], truncation=True, padding=True)["input_ids"]
            dataset = CustomDataset(encodings, labels)
            logger.info("Dataset prepared for fine-tuning.")
            return dataset
        except Exception as e:
            logger.error(f"Error preparing dataset: {e}")
            raise

class CustomDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        try:
            item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
            item["labels"] = torch.tensor(self.labels[idx])
            return item
        except Exception as e:
            logger.error(f"Error fetching item at index {idx}: {e}")
            raise

    def __len__(self):
        return len(self.labels)
