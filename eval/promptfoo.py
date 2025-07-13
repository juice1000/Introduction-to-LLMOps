"""
PromptFoo integration for LLM evaluation and testing.
Provides structured evaluation of chat responses and prompts.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class PromptFooEvaluator:
    """Interface for PromptFoo evaluation framework."""

    def __init__(self, config_path: str = "./eval/promptfoo.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load PromptFoo configuration."""
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f)
        else:
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """Create a default PromptFoo configuration."""
        default_config = {
            "description": "LLMOps Chatbot Evaluation Suite",
            "providers": [{"id": "openai:gpt-3.5-turbo", "config": {"temperature": 0.7, "max_tokens": 1000}}],
            "prompts": [{"id": "qa_prompt_v1", "path": "./app/prompts/qa_prompt_v1.txt"}],
            "tests": [
                {
                    "description": "Basic Q&A functionality",
                    "vars": {"question": "What is the main purpose of this system?"},
                    "assert": [
                        {"type": "contains", "value": "helpful"},
                        {"type": "not-contains", "value": "I don't know"},
                    ],
                }
            ],
            "outputPath": "./eval/results",
        }

        # Save default config
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False)

        return default_config

    def create_test_suite(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a test suite configuration for PromptFoo."""
        test_suite = {
            "description": "Generated Test Suite",
            "providers": self.config.get("providers", []),
            "prompts": self.config.get("prompts", []),
            "tests": test_cases,
        }

        return test_suite

    def add_test_case(
        self,
        description: str,
        question: str,
        expected_keywords: List[str] = None,
        forbidden_keywords: List[str] = None,
        context: str = None,
    ) -> Dict[str, Any]:
        """Create a single test case."""
        test_case = {"description": description, "vars": {"question": question}, "assert": []}

        if context:
            test_case["vars"]["context"] = context

        # Add keyword assertions
        if expected_keywords:
            for keyword in expected_keywords:
                test_case["assert"].append({"type": "contains", "value": keyword})

        if forbidden_keywords:
            for keyword in forbidden_keywords:
                test_case["assert"].append({"type": "not-contains", "value": keyword})

        # Add basic quality checks
        test_case["assert"].extend([{"type": "length", "min": 10, "max": 2000}, {"type": "not-empty"}])

        return test_case

    def save_test_suite(self, test_suite: Dict[str, Any], filename: str = "test_suite.yaml"):
        """Save test suite to file."""
        output_path = self.config_path.parent / filename

        with open(output_path, "w") as f:
            yaml.dump(test_suite, f, default_flow_style=False)

        logger.info(f"Test suite saved to {output_path}")
        return output_path
