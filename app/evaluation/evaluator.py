"""
Simple evaluation runner for testing chatbot responses against ground truth.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import mlflow
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.evaluation.eval_data import get_eval_dataset, get_question_categories
from app.prompts.system_prompt import EVALUATOR_SYSTEM_PROMPT, SYSTEM_PROMPT
from app.tracking import get_ollama_response


async def evaluate_single_question(
    question: str, ground_truth: str, use_context: bool = False, use_llm_judge: bool = True
):
    """Evaluate a single question against ground truth."""
    try:
        # Create messages for the model
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]

        # Get model response
        model_response = get_ollama_response(messages)

        # Simple evaluation metrics
        response_length = len(model_response)
        ground_truth_length = len(ground_truth)

        # Basic similarity check (contains key terms)
        ground_truth_words = set(ground_truth.lower().split())
        model_words = set(model_response.lower().split())
        common_words = ground_truth_words.intersection(model_words)
        word_overlap_ratio = len(common_words) / len(ground_truth_words) if ground_truth_words else 0

        metrics = {
            "response_length": response_length,
            "ground_truth_length": ground_truth_length,
            "word_overlap_ratio": word_overlap_ratio,
            "response_provided": len(model_response.strip()) > 0,
        }

        # Add LLM-as-a-judge evaluation
        llm_judge_result = None
        if use_llm_judge:
            llm_judge_result = await llm_judge_evaluation(question, model_response, ground_truth)
            metrics.update(
                {
                    "llm_judge_overall": llm_judge_result.get("overall_score", 0),
                    "llm_judge_scores": llm_judge_result.get("scores", {}),
                }
            )

        return {
            "question": question,
            "ground_truth": ground_truth,
            "model_response": model_response,
            "metrics": metrics,
            "llm_judge": llm_judge_result,
        }
    except Exception as e:
        return {
            "question": question,
            "ground_truth": ground_truth,
            "model_response": f"Error: {str(e)}",
            "metrics": {"error": True, "error_message": str(e)},
            "llm_judge": None,
        }


async def run_evaluation(
    sample_size: int = 5, use_context: bool = False, use_llm_judge: bool = True, log_to_mlflow: bool = True
):
    """Run evaluation on a sample of questions with optional MLflow tracking."""
    print(f"🧪 Running evaluation on {sample_size} questions...")
    print(f"   Using LLM-as-a-judge: {use_llm_judge}")
    print(f"   Logging to MLflow: {log_to_mlflow}")

    eval_data = get_eval_dataset()
    sample_data = eval_data.head(sample_size)

    results = []

    # Start MLflow run if logging is enabled
    mlflow_run = None
    if log_to_mlflow:
        mlflow_run = mlflow.start_run(run_name=f"evaluation_{sample_size}_questions")
        mlflow.log_params(
            {
                "sample_size": sample_size,
                "use_context": use_context,
                "use_llm_judge": use_llm_judge,
                "evaluation_timestamp": datetime.now().isoformat(),
            }
        )

    try:
        for idx, row in sample_data.iterrows():
            print(f"  Question {idx + 1}/{sample_size}: {row['inputs'][:50]}...")
            result = await evaluate_single_question(row["inputs"], row["ground_truth"], use_context, use_llm_judge)
            results.append(result)

            # Log individual metrics to MLflow
            if log_to_mlflow and mlflow_run and not result["metrics"].get("error", False):
                mlflow.log_metrics(
                    {
                        f"word_overlap_q{idx+1}": result["metrics"].get("word_overlap_ratio", 0),
                        f"response_time_q{idx+1}": result["metrics"].get("response_time", 0),
                    }
                )
                if use_llm_judge:
                    mlflow.log_metric(f"llm_judge_score_q{idx+1}", result["metrics"].get("llm_judge_overall", 0))

        # Calculate summary metrics
        total_questions = len(results)
        successful_responses = sum(1 for r in results if not r["metrics"].get("error", False))
        avg_word_overlap = sum(r["metrics"].get("word_overlap_ratio", 0) for r in results) / total_questions

        # Calculate LLM judge metrics if available
        avg_llm_judge_score = 0
        if use_llm_judge:
            llm_scores = [
                r["metrics"].get("llm_judge_overall", 0) for r in results if not r["metrics"].get("error", False)
            ]
            avg_llm_judge_score = sum(llm_scores) / len(llm_scores) if llm_scores else 0

        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_questions": total_questions,
            "successful_responses": successful_responses,
            "success_rate": successful_responses / total_questions,
            "average_word_overlap": avg_word_overlap,
            "average_llm_judge_score": avg_llm_judge_score,
            "use_context": use_context,
            "use_llm_judge": use_llm_judge,
        }

        # Log summary metrics to MLflow
        if log_to_mlflow and mlflow_run:
            mlflow.log_metrics(
                {
                    "success_rate": summary["success_rate"],
                    "avg_word_overlap": summary["average_word_overlap"],
                    "avg_response_time": sum(r["metrics"].get("response_time", 0) for r in results) / total_questions,
                }
            )
            if use_llm_judge:
                mlflow.log_metric("avg_llm_judge_score", summary["average_llm_judge_score"])

    finally:
        if log_to_mlflow and mlflow_run:
            mlflow.end_run()

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


async def llm_judge_evaluation(question: str, model_response: str, ground_truth: str):
    """Use LLM-as-a-judge to evaluate response quality."""
    try:
        judge_prompt = f"""
Question: {question}

Model Response: {model_response}

Ground Truth: {ground_truth}

Please evaluate the model response against the ground truth using the criteria provided in your system prompt. 
Provide scores (1-5) for accuracy, completeness, clarity, relevance, and helpfulness.
Also provide brief feedback.

Format your response as:
Accuracy: [score]/5
Completeness: [score]/5  
Clarity: [score]/5
Relevance: [score]/5
Helpfulness: [score]/5
Overall: [average score]/5
Feedback: [brief explanation]
"""

        judge_messages = [
            {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
            {"role": "user", "content": judge_prompt},
        ]

        judge_response = get_ollama_response(judge_messages)

        # Parse scores from response (simple parsing)
        scores = {}
        lines = judge_response.split("\n")
        for line in lines:
            if ":" in line:
                key = line.split(":")[0].strip().lower()
                if key in ["accuracy", "completeness", "clarity", "relevance", "helpfulness", "overall"]:
                    try:
                        score_part = line.split(":")[1].strip()
                        score = float(score_part.split("/")[0])
                        scores[key] = score
                    except:
                        continue

        return {
            "judge_response": judge_response,
            "scores": scores,
            "overall_score": scores.get("overall", sum(scores.values()) / len(scores) if scores else 0),
        }
    except Exception as e:
        return {"judge_response": f"Error: {str(e)}", "scores": {}, "overall_score": 0}


if __name__ == "__main__":
    # Run a quick evaluation with MLflow tracking
    import asyncio

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

    asyncio.run(main())
