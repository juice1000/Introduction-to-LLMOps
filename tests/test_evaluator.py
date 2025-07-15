"""
Test runner for insurance chatbot evaluation (moved from app/evaluation/evaluator.py __main__ block).
"""

import asyncio
import os
import sys

# Ensure app/ is in the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

from evaluation.evaluator import run_evaluation, save_evaluation_results


async def main():
    print("🚀 Starting Insurance Chatbot Evaluation")

    # Run evaluation on first 3 questions with MLflow tracking
    results = await run_evaluation(sample_size=3, use_context=False, use_llm_judge=True, log_to_mlflow=True)

    # Print summary
    summary = results["summary"]
    print(f"\n📈 Evaluation Summary:")
    print(f"   Total Questions: {summary['total_questions']}")
    print(f"   Success Rate: {summary['success_rate']:.1%}")
    print(f"   Average Word Overlap: {summary['average_word_overlap']:.2f}")
    print(f"   Average LLM Judge Score: {summary['average_llm_judge_score']:.2f}/5")

    # Save results to file
    save_evaluation_results(results)

    print(f"\n📊 Check MLflow UI at http://localhost:5000 for detailed experiment tracking")
    print("✅ Evaluation completed!")


if __name__ == "__main__":
    asyncio.run(main())
