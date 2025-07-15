#!/usr/bin/env python3
"""
Test script for semantic evaluator functionality.
"""

import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

from evaluation.semantic_evaluator import evaluate_production_question


async def test_semantic_evaluator():
    """Test the semantic evaluator with sample questions."""

    print("🧪 Testing Semantic Evaluator")
    print("=" * 50)

    # Test cases: questions that should match vs new questions
    test_cases = [
        {
            "name": "Should match liability question",
            "question": "What kind of protection does liability insurance provide?",
            "expected_match": True,
        },
        {
            "name": "Should match car claim question",
            "question": "How can I make a claim for my auto insurance?",
            "expected_match": True,
        },
        {
            "name": "New question - should not match",
            "question": "What are the business hours for customer service?",
            "expected_match": False,
        },
        {"name": "Nonsense question - should not match", "question": "Hello", "expected_match": False},
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Question: {test_case['question']}")

        # Simulate LLM response
        mock_response = f"This is a simulated response to: {test_case['question']}"

        try:
            result = await evaluate_production_question(test_case["question"], mock_response)

            print(f"   Result: {result}")
            print(f"   Match: {'✅' if result['similarity_match'] else '❌'}")
            print(f"   Confidence: {result['confidence']:.3f}")

            if result["evaluated"]:
                print(f"   LLM Judge Score: {result['llm_judge_score']:.2f}/5")

        except Exception as e:
            print(f"   Error: {e}")

    print("\n" + "=" * 50)
    print("✅ Semantic evaluator test completed!")


if __name__ == "__main__":
    asyncio.run(test_semantic_evaluator())
