#!/usr/bin/env python3
"""
Training script for fine-tuning the grammar correction model
Uses the local model and custom datasets to improve performance
"""

import os
import json
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSeq2SeqLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForSeq2Seq
)
from datasets import Dataset
import numpy as np

class GrammarModelTrainer:
    def __init__(self, model_path="./models/grammar_correction"):
        """Initialize the trainer with the local model"""
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
    def load_model_and_tokenizer(self):
        """Load the local model and tokenizer"""
        try:
            print(f"Loading model from {self.model_path}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path)
            
            # Move to device
            self.model = self.model.to(self.device)
            print("✅ Model and tokenizer loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to load model: {str(e)}")
            return False
    
    def create_sample_dataset(self):
        """Create a sample dataset for grammar correction training"""
        
        # Sample grammar correction pairs
        # Format: (incorrect_text, correct_text)
        sample_data = [
            # Basic grammar errors
            ("how is you?", "How are you?"),
            ("I goes to the store", "I go to the store."),
            ("She don't like it", "She doesn't like it."),
            ("They was happy", "They were happy."),
            ("The cat are sleeping", "The cat is sleeping."),
            ("He have a car", "He has a car."),
            ("We is going home", "We are going home."),
            
            # Complex sentences
            ("I want to go market but rain is coming", "I want to go to the market but the rain is coming."),
            ("The students was studying hard and they was tired", "The students were studying hard and they were tired."),
            ("She have three cats and they is very playful", "She has three cats and they are very playful."),
            
            # Articles and prepositions
            ("I went store yesterday", "I went to the store yesterday."),
            ("She lives in house near park", "She lives in a house near the park."),
            ("He works at company in city", "He works at a company in the city."),
            
            # Verb tenses
            ("I am go to school", "I am going to school."),
            ("She will goes to work", "She will go to work."),
            ("They have went to store", "They have gone to the store."),
            
            # Subject-verb agreement
            ("My friend like movies", "My friend likes movies."),
            ("The children is playing", "The children are playing."),
            ("Each student have book", "Each student has a book."),
            
            # Question formation
            ("Where you going?", "Where are you going?"),
            ("What time it is?", "What time is it?"),
            ("How long you been here?", "How long have you been here?")
        ]
        
        return sample_data
    
    def load_custom_dataset(self, file_path):
        """Load a custom dataset from JSON or CSV file"""
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif file_path.endswith('.csv'):
                import pandas as pd
                data = pd.read_csv(file_path).to_dict('records')
            else:
                print("❌ Unsupported file format. Use .json or .csv")
                return None
            
            # Expected format: list of dicts with 'input' and 'output' keys
            # Or list of tuples with (input, output)
            if isinstance(data[0], dict):
                if 'input' in data[0] and 'output' in data[0]:
                    return [(item['input'], item['output']) for item in data]
                elif 'incorrect' in data[0] and 'correct' in data[0]:
                    return [(item['incorrect'], item['correct']) for item in data]
                else:
                    print("❌ Dataset format not recognized. Expected 'input'/'output' or 'incorrect'/'correct' keys")
                    return None
            elif isinstance(data[0], (list, tuple)) and len(data[0]) == 2:
                return data
            else:
                print("❌ Dataset format not recognized")
                return None
                
        except Exception as e:
            print(f"❌ Failed to load dataset: {str(e)}")
            return None
    
    def prepare_dataset(self, data_pairs):
        """Prepare the dataset for training"""
        try:
            # Tokenize the data
            inputs = [pair[0] for pair in data_pairs]
            targets = [pair[1] for pair in data_pairs]
            
            # Tokenize inputs and targets
            model_inputs = self.tokenizer(
                inputs, 
                max_length=128, 
                truncation=True, 
                padding=True,
                return_tensors="pt"
            )
            
            with self.tokenizer.as_target_tokenizer():
                labels = self.tokenizer(
                    targets, 
                    max_length=128, 
                    truncation=True, 
                    padding=True,
                    return_tensors="pt"
                )
            
            # Create dataset
            dataset_dict = {
                'input_ids': model_inputs['input_ids'],
                'attention_mask': model_inputs['attention_mask'],
                'labels': labels['input_ids']
            }
            
            # Replace padding token id with -100 (ignore in loss calculation)
            dataset_dict['labels'][dataset_dict['labels'] == self.tokenizer.pad_token_id] = -100
            
            dataset = Dataset.from_dict(dataset_dict)
            print(f"✅ Dataset prepared with {len(data_pairs)} samples")
            return dataset
            
        except Exception as e:
            print(f"❌ Failed to prepare dataset: {str(e)}")
            return None
    
    def train_model(self, dataset, output_dir="./models/grammar_correction_finetuned", 
                   epochs=3, batch_size=4, learning_rate=5e-5):
        """Train the model on the prepared dataset"""
        try:
            print(f"🚀 Starting training...")
            print(f"📊 Dataset size: {len(dataset)} samples")
            print(f"⚙️  Training parameters:")
            print(f"   - Epochs: {epochs}")
            print(f"   - Batch size: {batch_size}")
            print(f"   - Learning rate: {learning_rate}")
            print(f"   - Output directory: {output_dir}")
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir=output_dir,
                num_train_epochs=epochs,
                per_device_train_batch_size=batch_size,
                per_device_eval_batch_size=batch_size,
                warmup_steps=100,
                weight_decay=0.01,
                logging_dir=f"{output_dir}/logs",
                logging_steps=10,
                save_steps=500,
                eval_steps=500,
                evaluation_strategy="steps",
                save_total_limit=2,
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                greater_is_better=False,
                learning_rate=learning_rate,
                fp16=torch.cuda.is_available(),  # Use mixed precision if available
                dataloader_num_workers=0,
                remove_unused_columns=False
            )
            
            # Data collator
            data_collator = DataCollatorForSeq2Seq(
                self.tokenizer,
                model=self.model,
                label_pad_token_id=-100,
                pad_to_multiple_of=8
            )
            
            # Initialize trainer
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=dataset,
                data_collator=data_collator,
                tokenizer=self.tokenizer
            )
            
            # Start training
            print("🔥 Training started...")
            trainer.train()
            
            # Save the model
            print(f"💾 Saving model to {output_dir}...")
            trainer.save_model(output_dir)
            self.tokenizer.save_pretrained(output_dir)
            
            print("✅ Training completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Training failed: {str(e)}")
            return False
    
    def test_finetuned_model(self, test_samples):
        """Test the fine-tuned model on some samples"""
        try:
            print("\n🧪 Testing fine-tuned model...")
            
            for i, (incorrect, correct) in enumerate(test_samples[:5]):  # Test first 5
                print(f"\nTest {i+1}:")
                print(f"Original: '{incorrect}'")
                print(f"Expected: '{correct}'")
                
                # Generate correction
                inputs = self.tokenizer(incorrect, return_tensors="pt", max_length=128, truncation=True)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_length=128,
                        num_beams=4,
                        early_stopping=True,
                        no_repeat_ngram_size=2
                    )
                
                generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                print(f"Generated: '{generated}'")
                
                # Check if correction was successful
                if generated.lower().strip() != incorrect.lower().strip():
                    print("✅ Correction successful!")
                else:
                    print("⚠️  No correction made")
                
                print("-" * 50)
                
        except Exception as e:
            print(f"❌ Testing failed: {str(e)}")

def main():
    """Main training function"""
    print("🎯 Grammar Model Training Script")
    print("=" * 50)
    
    # Initialize trainer
    trainer = GrammarModelTrainer()
    
    # Load model
    if not trainer.load_model_and_tokenizer():
        print("❌ Cannot proceed without loading the model")
        return
    
    # Choose dataset source
    print("\n📚 Choose dataset source:")
    print("1. Use sample dataset (built-in examples)")
    print("2. Load custom dataset from file")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        # Use sample dataset
        print("\n📖 Using sample dataset...")
        data_pairs = trainer.create_sample_dataset()
        
    elif choice == "2":
        # Load custom dataset
        file_path = input("Enter the path to your dataset file (.json or .csv): ").strip()
        data_pairs = trainer.load_custom_dataset(file_path)
        if data_pairs is None:
            print("❌ Failed to load custom dataset, using sample dataset instead")
            data_pairs = trainer.create_sample_dataset()
    
    else:
        print("❌ Invalid choice, using sample dataset")
        data_pairs = trainer.create_sample_dataset()
    
    # Prepare dataset
    dataset = trainer.prepare_dataset(data_pairs)
    if dataset is None:
        print("❌ Failed to prepare dataset")
        return
    
    # Training parameters
    print("\n⚙️  Training parameters:")
    epochs = int(input("Number of epochs (default 3): ") or "3")
    batch_size = int(input("Batch size (default 4): ") or "4")
    learning_rate = float(input("Learning rate (default 5e-5): ") or "5e-5")
    
    # Start training
    success = trainer.train_model(
        dataset=dataset,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate
    )
    
    if success:
        # Test the fine-tuned model
        test_samples = data_pairs[:5]  # Use first 5 samples for testing
        trainer.test_finetuned_model(test_samples)
        
        print(f"\n🎉 Training completed! Your fine-tuned model is saved.")
        print(f"📁 Model location: ./models/grammar_correction_finetuned")
        print(f"🔧 To use it, update your MODEL_DIR in services.py")
    else:
        print("❌ Training failed. Check the error messages above.")

if __name__ == "__main__":
    main()
