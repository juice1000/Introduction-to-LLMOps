"""
Simple evaluation runner for testing chatbot responses against ground truth.
"""

import asyncio
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.evaluation.eval_data import get_eval_dataset, get_question_categories
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.tracking import get_ollama_response


async def evaluate_single_question(question: str, ground_truth: str, use_context: bool = False):
    """Evaluate a single question against ground truth."""
    try:
        # Create messages for the model
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]

        # Get model response
        model_response = get_ollama_response(messages)

        # Simple evaluation metrics (you can enhance these)
        response_length = len(model_response)
        ground_truth_length = len(ground_truth)

        # Basic similarity check (contains key terms)
        ground_truth_words = set(ground_truth.lower().split())
        model_words = set(model_response.lower().split())
        common_words = ground_truth_words.intersection(model_words)
        word_overlap_ratio = len(common_words) / len(ground_truth_words) if ground_truth_words else 0

        return {
            "question": question,
            "ground_truth": ground_truth,
            "model_response": model_response,
            "metrics": {
                "response_length": response_length,
                "ground_truth_length": ground_truth_length,
                "word_overlap_ratio": word_overlap_ratio,
                "response_provided": len(model_response.strip()) > 0,
            },
        }
    except Exception as e:
        return {
            "question": question,
            "ground_truth": ground_truth,
            "model_response": f"Error: {str(e)}",
            "metrics": {"error": True, "error_message": str(e)},
        }


async def run_evaluation(sample_size: int = 5, use_context: bool = False):
    """Run evaluation on a sample of questions."""
    print(f"🧪 Running evaluation on {sample_size} questions...")

    eval_data = get_eval_dataset()
    sample_data = eval_data.head(sample_size)

    results = []

    for idx, row in sample_data.iterrows():
        print(f"  Question {idx + 1}/{sample_size}: {row['inputs'][:50]}...")
        result = await evaluate_single_question(row["inputs"], row["ground_truth"], use_context)
        results.append(result)

    # Calculate summary metrics
    total_questions = len(results)
    successful_responses = sum(1 for r in results if not r["metrics"].get("error", False))
    avg_word_overlap = sum(r["metrics"].get("word_overlap_ratio", 0) for r in results) / total_questions

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_questions": total_questions,
        "successful_responses": successful_responses,
        "success_rate": successful_responses / total_questions,
        "average_word_overlap": avg_word_overlap,
        "use_context": use_context,
    }

    return {"summary": summary, "results": results}


def save_evaluation_results(results, filename=None):
    """Save evaluation results to JSON file in evaluation_results/ directory."""
    results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "evaluation_results"))
    os.makedirs(results_dir, exist_ok=True)
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_results_{timestamp}.json"
    filepath = os.path.join(results_dir, filename)
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2)
    print(f"📊 Evaluation results saved to {filepath}")
    return filepath


if __name__ == "__main__":
    # Run a quick evaluation
    import asyncio

    async def main():
        print("🚀 Starting Insurance Chatbot Evaluation")

        # Run evaluation on first 3 questions
        results = await run_evaluation(sample_size=3, use_context=False)

        # Print summary
        summary = results["summary"]
        print(f"\n📈 Evaluation Summary:")
        print(f"   Total Questions: {summary['total_questions']}")
        print(f"   Success Rate: {summary['success_rate']:.1%}")
        print(f"   Average Word Overlap: {summary['average_word_overlap']:.2f}")

        # Save results
        save_evaluation_results(results)

        print("\n✅ Evaluation completed!")

    asyncio.run(main())
