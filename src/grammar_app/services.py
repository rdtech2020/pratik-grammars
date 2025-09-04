"""
Grammar Correction Service

This module contains the core grammar correction functionality using AI models.
"""

import os
import re
from typing import List, Optional

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

from config.settings import settings


class GrammarCorrectionService:
    """Service class for grammar correction using AI models."""

    def __init__(self):
        """Initialize the grammar correction service."""
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.device = settings.DEVICE
        self.model_name = settings.MODEL_NAME
        self.model_dir = settings.MODEL_DIR

        # Load model on initialization
        self._load_model()

    def _load_model(self):
        """Load the grammar correction model."""
        try:
            # Check if model exists locally
            if os.path.exists(self.model_dir):
                print(f"Loading local model from {self.model_dir}")
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_dir)
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
            else:
                print(f"Downloading model {self.model_name}")
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

                # Save model locally for future use
                # os.makedirs(self.model_dir, exist_ok=True)
                # self.model.save_pretrained(self.model_dir)
                # self.tokenizer.save_pretrained(self.model_dir)
                # print(f"Model saved to {self.model_dir}")

            # Create pipeline
            self.pipeline = pipeline(
                "text2text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=self.device,
            )

        except Exception as e:
            print(f"Error loading model: {e}")
            self.pipeline = None

    def correct_grammar(self, text: str) -> str:
        """
        Correct grammar in the given text.

        Args:
            text: Input text to correct

        Returns:
            Corrected text
        """
        if not text or not text.strip():
            return text

        # Strategy 1: Apply basic rules first (fast and reliable)
        if settings.USE_BASIC_RULES_FIRST:
            basic_corrected = self._apply_basic_grammar_rules(text)
            if basic_corrected != text:
                print(f"Basic rules applied: '{text}' -> '{basic_corrected}'")
                return basic_corrected

        # Strategy 2: Try AI model for complex corrections
        if self.pipeline and settings.USE_AI_MODEL_FALLBACK:
            try:
                ai_corrected = self._correct_with_ai(text)
                if ai_corrected and ai_corrected != text and len(ai_corrected) > 0:
                    print(f"AI model applied: '{text}' -> '{ai_corrected}'")
                    return ai_corrected
            except Exception as e:
                print(f"AI correction failed: {e}")

        # Strategy 3: Apply basic rules as final fallback
        if not settings.USE_BASIC_RULES_FIRST:
            basic_corrected = self._apply_basic_grammar_rules(text)
            if basic_corrected != text:
                print(f"Basic rules fallback: '{text}' -> '{basic_corrected}'")
                return basic_corrected

        # Return original if no corrections made
        return text

    def _correct_with_ai(self, text: str) -> str:
        """Correct grammar using AI model."""
        try:
            # For T5 grammar correction models, use the text directly as input
            # The model is trained to take grammatically incorrect text and output corrected text

            # Generate correction with improved parameters
            result = self.pipeline(
                text,  # Use the text directly without a prompt
                max_new_tokens=settings.MODEL_MAX_LENGTH,
                temperature=settings.MODEL_TEMPERATURE,
                top_p=settings.MODEL_TOP_P,
                repetition_penalty=settings.MODEL_REPETITION_PENALTY,
                do_sample=settings.MODEL_DO_SAMPLE,
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

            if result and len(result) > 0:
                corrected = result[0]["generated_text"].strip()

                # Clean up the response - remove any prompt prefixes
                if corrected.startswith("grammar:"):
                    corrected = corrected.replace("grammar:", "").strip()
                elif corrected.startswith("Correct the grammar in this text:"):
                    corrected = corrected.replace(
                        "Correct the grammar in this text:", ""
                    ).strip()
                elif corrected.startswith("Corrected text:"):
                    corrected = corrected.replace("Corrected text:", "").strip()
                elif corrected.startswith("Corrected:"):
                    corrected = corrected.replace("Corrected:", "").strip()

                # If the corrected text is the same as input or empty, return original
                if corrected == text or not corrected:
                    return text

                return corrected

        except Exception as e:
            print(f"AI correction error: {e}")

        return text

    def _apply_basic_grammar_rules(self, text: str) -> str:
        """
        Apply basic grammar correction rules as fallback.

        Args:
            text: Input text

        Returns:
            Text with basic grammar corrections
        """
        if not text:
            return text

        # Common grammar fixes
        corrections = [
            # Subject-verb agreement for "is" vs "are"
            (r"\b(you)\s+(is)\b", r"\1 are"),
            (r"\b(we)\s+(is)\b", r"\1 are"),
            (r"\b(they)\s+(is)\b", r"\1 are"),
            (r"\b(I)\s+(are)\b", r"\1 am"),
            (r"\b(he)\s+(are)\b", r"\1 is"),
            (r"\b(she)\s+(are)\b", r"\1 is"),
            (r"\b(it)\s+(are)\b", r"\1 is"),
            # Subject-verb agreement - more specific rules
            (r"\b(he|she|it)\s+(am|are)\s+", r"\1 is "),
            (r"\b(I)\s+(are|is)\s+", r"\1 am "),
            (r"\b(we|you|they)\s+(am|is)\s+", r"\1 are "),
            (r"\b(I|he|she|it)\s+(go|goes)\s+", r"\1 goes "),
            (r"\b(we|you|they)\s+(goes)\s+", r"\1 go "),
            # Past perfect tense corrections
            (r"\bI\s+had\s+done\s+playing\b", r"I had finished playing"),
            (r"\bI\s+had\s+done\s+(\w+ing)\b", r"I had finished \1"),
            (r"\b(he|she|it)\s+had\s+done\s+(\w+ing)\b", r"\1 had finished \2"),
            (r"\b(we|you|they)\s+had\s+done\s+(\w+ing)\b", r"\1 had finished \2"),
            # Present perfect tense corrections
            (r"\bI\s+have\s+done\s+playing\b", r"I have finished playing"),
            (r"\bI\s+have\s+done\s+(\w+ing)\b", r"I have finished \1"),
            # Articles - Fixed implementation
            (r"\b(a)\s+([aeiou][a-z]*)\b", r"an \2"),  # a apple -> an apple
            (r"\b(an)\s+([bcdfghjklmnpqrstvwxyz][a-z]*)\b", r"a \2"),  # an book -> a book
            # Common contractions
            (r"\b(do not|don\'t)\b", r"don't"),
            (r"\b(does not|doesn\'t)\b", r"doesn't"),
            (r"\b(can not|cannot|can\'t)\b", r"can't"),
            (r"\b(will not|won\'t)\b", r"won't"),
            (r"\b(should not|shouldn\'t)\b", r"shouldn't"),
            (r"\b(would not|wouldn\'t)\b", r"wouldn't"),
            (r"\b(could not|couldn\'t)\b", r"couldn't"),
            (r"\b(has not|hasn\'t)\b", r"hasn't"),
            (r"\b(have not|haven\'t)\b", r"haven't"),
            (r"\b(had not|hadn\'t)\b", r"hadn't"),
            (r"\b(is not|isn\'t)\b", r"isn't"),
            (r"\b(are not|aren\'t)\b", r"aren't"),
            (r"\b(was not|wasn\'t)\b", r"wasn't"),
            (r"\b(were not|weren\'t)\b", r"weren't"),
            # Fix common informal contractions
            (r"\b(dont)\b", r"don't"),
            (r"\b(doesnt)\b", r"doesn't"),
            (r"\b(cant)\b", r"can't"),
            (r"\b(wont)\b", r"won't"),
            (r"\b(shouldnt)\b", r"shouldn't"),
            (r"\b(wouldnt)\b", r"wouldn't"),
            (r"\b(couldnt)\b", r"couldn't"),
            (r"\b(hasnt)\b", r"hasn't"),
            (r"\b(havent)\b", r"haven't"),
            (r"\b(hadnt)\b", r"hadn't"),
            (r"\b(isnt)\b", r"isn't"),
            (r"\b(arent)\b", r"aren't"),
            (r"\b(wasnt)\b", r"wasn't"),
            (r"\b(werent)\b", r"weren't"),
            # Capitalization fixes
            (r"\b(i)\b", r"I"),  # lowercase i -> I
            (r"\b(hello|hi)\b", r"Hello"),  # greetings
            (r"\b(bye|goodbye)\b", r"Goodbye"),
            # Advanced grammar rules
            (r"\b(me)\s+and\s+(him|her|them)\b", r"\2 and I"),  # me and him -> him and I
            (r"\b(him|her|them)\s+and\s+(me)\b", r"\1 and I"),  # him and me -> him and I
            (r"\b(me)\s+and\s+(I)\b", r"\2 and I"),  # me and I -> I and I
            (r"\b(I)\s+and\s+(me)\b", r"I and I"),  # I and me -> I and I
            # Fix common informal phrases
            (r"\b(gonna)\b", r"going to"),
            (r"\b(wanna)\b", r"want to"),
            (r"\b(gotta)\b", r"got to"),
            (r"\b(lemme)\b", r"let me"),
            (r"\b(gimme)\b", r"give me"),
            # Fix double negatives
            (r"\b(not)\s+\w+\s+(not)\b", r"\1 \2"),  # not do not -> not do not (simplified)
            # Fix common word confusions
            (r"\b(their)\s+(there)\b", r"they're there"),
            (r"\b(there)\s+(their)\b", r"there they're"),
            (r"\b(your)\s+(you're)\b", r"you're"),
            (r"\b(you're)\s+(your)\b", r"your"),
            (r"\b(its)\s+(it's)\b", r"it's"),
            (r"\b(it's)\s+(its)\b", r"its"),
            # Punctuation
            (r"\s+([.!?])", r"\1"),  # Remove spaces before punctuation
            (r"([.!?])\s*([a-z])", r"\1 \2"),  # Add space after punctuation
            (r"\s+", r" "),  # Multiple spaces to single space
        ]

        corrected = text
        for pattern, replacement in corrections:
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)

        # Capitalize first letter
        if corrected and corrected[0].islower():
            corrected = corrected[0].upper() + corrected[1:]

        return corrected.strip()

    def batch_correct(self, texts: List[str]) -> List[str]:
        """
        Correct grammar for multiple texts.

        Args:
            texts: List of texts to correct

        Returns:
            List of corrected texts
        """
        return [self.correct_grammar(text) for text in texts]

    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        return {
            "model_name": self.model_name,
            "model_dir": self.model_dir,
            "device": self.device,
            "model_loaded": self.pipeline is not None,
            "model_type": "text2text-generation",
        }


# Global service instance (singleton pattern)
_grammar_service = None


def get_grammar_service() -> GrammarCorrectionService:
    """Get the global grammar correction service instance."""
    global _grammar_service
    if _grammar_service is None:
        _grammar_service = GrammarCorrectionService()
    return _grammar_service


def correct_grammar(text: str) -> str:
    """
    Correct grammar in the given text.

    Args:
        text: Input text to correct

    Returns:
        Corrected text
    """
    service = get_grammar_service()
    return service.correct_grammar(text)


def batch_correct_grammar(texts: List[str]) -> List[str]:
    """
    Correct grammar for multiple texts.

    Args:
        texts: List of texts to correct

    Returns:
        List of corrected texts
    """
    service = get_grammar_service()
    return service.batch_correct(texts)


def get_model_info() -> dict:
    """Get information about the loaded model."""
    service = get_grammar_service()
    return service.get_model_info()
