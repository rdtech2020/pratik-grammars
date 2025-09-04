#!/usr/bin/env python3
"""
Model Testing and Comparison Script

This script tests different grammar correction models to find the best one.
"""

import sys
from pathlib import Path
import json
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
from config.settings import settings


def test_model_performance(model_name: str, test_cases: list):
    """Test a specific model's performance on grammar correction."""
    print(f"\n🧪 Testing Model: {model_name}")
    print("=" * 50)
    
    try:
        # Load model
        print(f"Loading model {model_name}...")
        start_time = time.time()
        
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Create pipeline
        pipe = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            device=settings.DEVICE,
        )
        
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f} seconds")
        
        # Test cases
        results = []
        total_time = 0
        
        for i, test_case in enumerate(test_cases, 1):
            original = test_case["input"]
            expected = test_case.get("expected", "N/A")
            
            print(f"\nTest {i}: '{original}'")
            
            # Time the correction
            start_time = time.time()
            try:
                result = pipe(
                    original,
                    max_new_tokens=128,
                    temperature=0.1,
                    do_sample=False,
                    num_return_sequences=1,
                )
                correction_time = time.time() - start_time
                total_time += correction_time
                
                corrected = result[0]["generated_text"].strip()
                
                # Clean up response
                for prefix in ["grammar:", "Correct the grammar in this text:", "Corrected text:", "Corrected:"]:
                    if corrected.startswith(prefix):
                        corrected = corrected.replace(prefix, "").strip()
                
                print(f"   Output: '{corrected}'")
                print(f"   Expected: '{expected}'")
                print(f"   Time: {correction_time:.3f}s")
                
                if expected != "N/A":
                    accuracy = "✅" if corrected.lower() == expected.lower() else "❌"
                    print(f"   Accuracy: {accuracy}")
                
                results.append({
                    "input": original,
                    "output": corrected,
                    "expected": expected,
                    "time": correction_time
                })
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({
                    "input": original,
                    "output": f"ERROR: {e}",
                    "expected": expected,
                    "time": 0
                })
        
        # Summary
        avg_time = total_time / len(test_cases) if test_cases else 0
        print(f"\n📊 Summary for {model_name}:")
        print(f"   Average correction time: {avg_time:.3f}s")
        print(f"   Total test cases: {len(test_cases)}")
        
        return {
            "model": model_name,
            "load_time": load_time,
            "avg_correction_time": avg_time,
            "results": results
        }
        
    except Exception as e:
        print(f"❌ Failed to load model {model_name}: {e}")
        return {
            "model": model_name,
            "error": str(e),
            "results": []
        }


def main():
    """Main function to test different models."""
    print("🚀 Grammar Correction Model Comparison")
    print("=" * 60)
    
    # Test cases with expected outputs
    test_cases = [
        {"input": "hello world", "expected": "Hello world"},
        {"input": "i am going to store", "expected": "I am going to the store"},
        {"input": "he are going", "expected": "He is going"},
        {"input": "she dont like it", "expected": "She doesn't like it"},
        {"input": "i have a apple", "expected": "I have an apple"},
        {"input": "me and him goes to store", "expected": "He and I go to the store"},
        {"input": "i had done playing", "expected": "I had finished playing"},
        {"input": "how is you?", "expected": "How are you?"},
        {"input": "they is happy", "expected": "They are happy"},
        {"input": "i gonna go", "expected": "I am going to go"},
    ]
    
    # Models to test
    models_to_test = [
        "vennify/t5-base-grammar-correction",  # Current model
        "t5-base",  # Base T5 model
        "google/flan-t5-base",  # Better instruction following
        "facebook/bart-base",  # Good for text correction
        "microsoft/DialoGPT-medium",  # Conversational
    ]
    
    all_results = []
    
    for model_name in models_to_test:
        result = test_model_performance(model_name, test_cases)
        all_results.append(result)
    
    # Save results
    output_file = Path(__file__).parent.parent / "data" / "model_comparison_results.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Print summary
    print("\n🏆 MODEL COMPARISON SUMMARY")
    print("=" * 60)
    
    successful_models = [r for r in all_results if "error" not in r]
    
    if successful_models:
        # Sort by average correction time
        successful_models.sort(key=lambda x: x.get("avg_correction_time", float('inf')))
        
        print("\n📈 Performance Ranking (by speed):")
        for i, result in enumerate(successful_models, 1):
            model = result["model"]
            avg_time = result.get("avg_correction_time", 0)
            load_time = result.get("load_time", 0)
            print(f"{i}. {model}")
            print(f"   Load time: {load_time:.2f}s")
            print(f"   Avg correction: {avg_time:.3f}s")
    
    print(f"\n✅ Testing complete! Check {output_file} for detailed results.")


if __name__ == "__main__":
    main()
