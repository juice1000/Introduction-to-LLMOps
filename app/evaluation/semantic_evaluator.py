"""
Semantic nearest neighbor evaluation for production questions.
Automatically evaluates production questions against known ground truth.
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path

import mlflow
import pandas as pd

from app.evaluation.eval_data import get_eval_dataset
from app.evaluation.evaluator import llm_judge_evaluation
from app.prompts.similarity_prompt import (
    SIMILARITY_SYSTEM_PROMPT,
    get_similarity_prompt,
)
from app.tracking import get_ollama_response


class SemanticEvaluator:
    """Handles semantic similarity detection and automatic evaluation."""

    def __init__(self, confidence_threshold: float = 0.98):
        self.confidence_threshold = confidence_threshold
        self.eval_dataset = get_eval_dataset()
        self.new_questions_file = Path("app/evaluation/evaluation_results/new_questions.json")
        self.new_questions_file.parent.mkdir(exist_ok=True)

        # Load existing new questions if file exists
        self.new_questions = self._load_new_questions()

    def _load_new_questions(self) -> list:
        """Load previously saved new questions."""
        if self.new_questions_file.exists():
            try:
                with open(self.new_questions_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_new_questions(self):
        """Save new questions to file."""
        with open(self.new_questions_file, "w") as f:
            json.dump(self.new_questions, f, indent=2, default=str)

    async def find_similar_question(self, user_question: str) -> dict:
        """
        Find semantically similar question in evaluation dataset.
        Returns match info with confidence score.
        """
        # Create list of evaluation questions with clear numbering
        eval_questions = []
        for i, question in enumerate(self.eval_dataset["inputs"].tolist()):
            eval_questions.append(f"Question {i+1}: {question}")

        # Use the prompt from system prompts
        similarity_prompt = get_similarity_prompt(user_question, eval_questions, self.confidence_threshold)
        messages = [
            {
                "role": "system",
                "content": SIMILARITY_SYSTEM_PROMPT,
            },
            {"role": "user", "content": similarity_prompt},
        ]

        try:
            response = get_ollama_response(messages)
            print(f"🔍 Similarity LLM response: {response}")  # Debug output
            return self._parse_similarity_response(response, user_question)
        except Exception as e:
            print(f"Error in similarity detection: {e}")
            return {"match": False, "confidence": 0.0, "reason": f"Error: {e}"}

    def _parse_similarity_response(self, response: str, user_question: str) -> dict:
        """Parse the LLM response for similarity matching."""
        result = {
            "match": False,
            "confidence": 0.0,
            "reason": "",
            "matched_question": None,
            "ground_truth": None,
            "user_question": user_question,
        }

        # Clean up the response
        response = response.strip()
        lines = [line.strip() for line in response.split("\n") if line.strip()]

        matched_question_number = 0
        matched_question_text = None

        # Parse each line
        for line in lines:
            # Look for MATCH pattern
            if line.upper().startswith("MATCH:"):
                try:
                    match_part = line.split(":", 1)[1].strip()
                    # Extract number from the match part
                    import re

                    numbers = re.findall(r"\d+", match_part)
                    if numbers:
                        matched_question_number = int(numbers[0])
                except Exception as e:
                    print(f"Error parsing MATCH: {e}")

            # Look for MATCHED EVALUATION QUESTION pattern
            elif line.upper().startswith("MATCHED EVALUATION QUESTION:"):
                try:
                    matched_question_text = line.split(":", 1)[1].strip()
                    # Don't use if it says "No match"
                    if matched_question_text.lower() in ["no match", "none", "n/a"]:
                        matched_question_text = None
                except Exception as e:
                    print(f"Error parsing MATCHED EVALUATION QUESTION: {e}")

            # Look for CONFIDENCE pattern
            elif line.upper().startswith("CONFIDENCE:"):
                try:
                    confidence_part = line.split(":", 1)[1].strip()
                    # Extract first number found
                    import re

                    numbers = re.findall(r"\d+\.?\d*", confidence_part)
                    if numbers:
                        confidence = float(numbers[0])
                        result["confidence"] = confidence
                except Exception as e:
                    print(f"Error parsing CONFIDENCE: {e}")

            # Look for REASON pattern
            elif line.upper().startswith("REASON:"):
                try:
                    result["reason"] = line.split(":", 1)[1].strip()
                except Exception as e:
                    print(f"Error parsing REASON: {e}")

        # Use the matched question information to get ground truth
        if matched_question_number > 0 and matched_question_number <= len(self.eval_dataset):
            question_index = matched_question_number - 1  # Convert to 0-based index
            result["matched_question"] = self.eval_dataset.iloc[question_index]["inputs"]
            result["ground_truth"] = self.eval_dataset.iloc[question_index]["ground_truth"]

            # Validate that the matched_question_text (if provided) matches what we found by number
            if matched_question_text and matched_question_text.lower() != "no match":
                expected_question = self.eval_dataset.iloc[question_index]["inputs"]
                if matched_question_text.strip() != expected_question.strip():
                    print(
                        f"⚠️  Warning: LLM provided question text doesn't match question number {matched_question_number}"
                    )
                    print(f"   LLM provided: '{matched_question_text}'")
                    print(f"   Expected: '{expected_question}'")

        elif matched_question_text and matched_question_text.lower() not in ["no match", "none", "n/a"]:
            # If we have question text but no valid number, try to find it in dataset
            # But also check if the LLM mistakenly put the user question here
            if matched_question_text.strip().lower() == user_question.strip().lower():
                print(f"⚠️  Warning: LLM incorrectly put user question in EVALUATION QUESTION field")
                print(f"   This indicates the LLM didn't understand the format correctly")
            else:
                try:
                    for idx, question in enumerate(self.eval_dataset["inputs"]):
                        if question.strip().lower() == matched_question_text.strip().lower():
                            result["matched_question"] = question
                            result["ground_truth"] = self.eval_dataset.iloc[idx]["ground_truth"]
                            print(f"✅ Found question by text match at index {idx + 1}")
                            break
                    else:
                        print(f"⚠️  Warning: Could not find evaluation question matching: '{matched_question_text}'")
                except Exception as e:
                    print(f"Error finding question by text: {e}")

        # Determine if it's a match based on confidence and presence of matched question
        if result["confidence"] >= self.confidence_threshold and result["matched_question"]:
            result["match"] = True

            # Additional validation: warn about potentially suspicious matches
            if result["confidence"] >= 0.95:
                # Check if the matched question and user question share key terms
                user_words = set(user_question.lower().split())
                matched_words = set(result["matched_question"].lower().split())
                common_words = user_words.intersection(matched_words)

                # Remove common stop words for better analysis
                stop_words = {
                    "what",
                    "does",
                    "is",
                    "the",
                    "a",
                    "an",
                    "and",
                    "or",
                    "but",
                    "in",
                    "on",
                    "at",
                    "to",
                    "for",
                    "of",
                    "with",
                    "by",
                    "how",
                    "do",
                    "i",
                    "you",
                    "can",
                    "will",
                    "would",
                    "should",
                }
                meaningful_common = common_words - stop_words

                if len(meaningful_common) < 2:
                    print(f"🚨 WARNING: High confidence ({result['confidence']:.2f}) but low word overlap!")
                    print(f"   User question: '{user_question}'")
                    print(f"   Matched question: '{result['matched_question']}'")
                    print(f"   Common meaningful words: {meaningful_common}")
                    print(f"   This might be a hallucination - consider reviewing.")

        print(
            f"🔍 Parsed result: match={result['match']}, confidence={result['confidence']}, question='{result['matched_question'][:50] if result['matched_question'] else None}...'"
        )

        return result

    async def evaluate_production_question(self, user_question: str, llm_response: str) -> dict:
        """
        Main method to handle production question evaluation.
        Returns evaluation results or saves as new question.
        """
        start_time = time.time()

        # Find similar question
        similarity_result = await self.find_similar_question(user_question)
        similarity_time = time.time() - start_time

        if similarity_result["match"]:
            # Found similar question - run evaluation
            print(f"🎯 Found similar question (confidence: {similarity_result['confidence']:.2f})")
            print(f"   Matched: {similarity_result['matched_question'][:100]}...")

            # Run LLM-as-a-judge evaluation
            judge_result = await llm_judge_evaluation(user_question, llm_response, similarity_result["ground_truth"])

            evaluation_result = {
                "timestamp": datetime.now().isoformat(),
                "evaluation_type": "production_similarity_match",
                "user_question": user_question,
                "llm_response": llm_response,
                "matched_question": similarity_result["matched_question"],
                "ground_truth": similarity_result["ground_truth"],
                "similarity_confidence": similarity_result["confidence"],
                "similarity_reason": similarity_result["reason"],
                "similarity_detection_time": similarity_time,
                "response_time": time.time() - start_time,
                "llm_judge_result": judge_result,
                "llm_judge_score": judge_result.get("overall_score", 0),
            }

            # Log to MLflow
            await self._log_to_mlflow(evaluation_result)

            # Save evaluation result
            self._save_evaluation_result(evaluation_result)

            return {
                "evaluated": True,
                "similarity_match": True,
                "confidence": similarity_result["confidence"],
                "llm_judge_score": judge_result.get("overall_score", 0),
                "evaluation_id": evaluation_result["timestamp"],
            }

        else:
            # No similar question found - save as new question
            print(f"📝 New question detected (max confidence: {similarity_result['confidence']:.2f})")

            new_question_entry = {
                "timestamp": datetime.now().isoformat(),
                "question": user_question,
                "llm_response": llm_response,
                "similarity_check": similarity_result,
                "response_time": time.time() - start_time,
            }

            self.new_questions.append(new_question_entry)
            self._save_new_questions()

            return {
                "evaluated": False,
                "similarity_match": False,
                "confidence": similarity_result["confidence"],
                "saved_as_new": True,
                "new_questions_count": len(self.new_questions),
            }

    async def _log_to_mlflow(self, evaluation_result: dict):
        """Log evaluation results to MLflow."""
        try:
            with mlflow.start_run(run_name="production_similarity_evaluation"):
                # Log parameters
                mlflow.log_params(
                    {
                        "evaluation_type": "production_similarity_match",
                        "similarity_confidence": evaluation_result["similarity_confidence"],
                        "confidence_threshold": self.confidence_threshold,
                    }
                )

                # Log metrics
                mlflow.log_metrics(
                    {
                        "similarity_confidence": evaluation_result["similarity_confidence"],
                        "llm_judge_score": evaluation_result["llm_judge_score"],
                        "similarity_detection_time": evaluation_result["similarity_detection_time"],
                        "total_response_time": evaluation_result["response_time"],
                    }
                )

                # Log text artifacts
                mlflow.log_text(evaluation_result["user_question"], "user_question.txt")
                mlflow.log_text(evaluation_result["llm_response"], "llm_response.txt")
                mlflow.log_text(evaluation_result["ground_truth"], "ground_truth.txt")

        except Exception as e:
            print(f"Error logging to MLflow: {e}")

    def _save_evaluation_result(self, evaluation_result: dict):
        """Save individual evaluation result to file."""
        results_dir = Path("app/evaluation/evaluation_results/production_evaluations")
        results_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:17]  # Include microseconds for uniqueness
        filename = f"production_eval_{timestamp}.json"

        filepath = results_dir / filename
        with open(filepath, "w") as f:
            json.dump(evaluation_result, f, indent=2, default=str)

        print(f"💾 Production evaluation saved to {filepath}")


# Global instance
semantic_evaluator = SemanticEvaluator()


async def evaluate_production_question(user_question: str, llm_response: str) -> dict:
    """
    Convenience function to evaluate a production question.
    """
    return await semantic_evaluator.evaluate_production_question(user_question, llm_response)
