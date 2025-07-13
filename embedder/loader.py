"""
Data loading utilities for processing various document formats.
Handles the ingestion and preprocessing of raw data files.
"""

import csv
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DataLoader:
    """Utility class for loading and preprocessing documents."""

    def __init__(self, raw_data_path: str, processed_data_path: str):
        self.raw_data_path = Path(raw_data_path)
        self.processed_data_path = Path(processed_data_path)

        # Ensure directories exist
        self.processed_data_path.mkdir(parents=True, exist_ok=True)

    def load_text_files(self, pattern: str = "*.txt") -> List[Dict[str, Any]]:
        """Load text files from the raw data directory."""
        documents = []

        for file_path in self.raw_data_path.glob(pattern):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                documents.append(
                    {"content": content, "source": str(file_path), "filename": file_path.name, "file_type": "text"}
                )

                logger.info(f"Loaded text file: {file_path}")

            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")

        return documents

    def load_json_files(self, pattern: str = "*.json") -> List[Dict[str, Any]]:
        """Load JSON files from the raw data directory."""
        documents = []

        for file_path in self.raw_data_path.glob(pattern):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Handle different JSON structures
                if isinstance(data, list):
                    for i, item in enumerate(data):
                        documents.append(
                            {
                                "content": json.dumps(item, indent=2),
                                "source": f"{file_path}#{i}",
                                "filename": file_path.name,
                                "file_type": "json",
                            }
                        )
                else:
                    documents.append(
                        {
                            "content": json.dumps(data, indent=2),
                            "source": str(file_path),
                            "filename": file_path.name,
                            "file_type": "json",
                        }
                    )

                logger.info(f"Loaded JSON file: {file_path}")

            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")

        return documents

    def load_csv_files(self, pattern: str = "*.csv") -> List[Dict[str, Any]]:
        """Load CSV files from the raw data directory."""
        documents = []

        for file_path in self.raw_data_path.glob(pattern):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)

                # Convert each row to a document
                for i, row in enumerate(rows):
                    content = "\n".join([f"{key}: {value}" for key, value in row.items()])

                    documents.append(
                        {
                            "content": content,
                            "source": f"{file_path}#row_{i}",
                            "filename": file_path.name,
                            "file_type": "csv",
                        }
                    )

                logger.info(f"Loaded CSV file: {file_path} with {len(rows)} rows")

            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")

        return documents

    def preprocess_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply preprocessing to documents."""
        processed_docs = []

        for doc in documents:
            try:
                # Basic text cleaning
                content = doc["content"]
                content = content.strip()

                # Remove excessive whitespace
                content = " ".join(content.split())

                # Skip empty documents
                if not content:
                    continue

                processed_doc = doc.copy()
                processed_doc["content"] = content
                processed_doc["word_count"] = len(content.split())
                processed_doc["char_count"] = len(content)

                processed_docs.append(processed_doc)

            except Exception as e:
                logger.error(f"Error preprocessing document {doc.get('source', 'unknown')}: {e}")

        return processed_docs

    def save_processed_documents(self, documents: List[Dict[str, Any]], filename: str = "processed_docs.json"):
        """Save processed documents to the processed data directory."""
        output_path = self.processed_data_path / filename

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(documents, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(documents)} processed documents to {output_path}")

        except Exception as e:
            logger.error(f"Error saving processed documents: {e}")

    def load_all_documents(self) -> List[Dict[str, Any]]:
        """Load all documents from the raw data directory."""
        all_docs = []

        # Load different file types
        all_docs.extend(self.load_text_files())
        all_docs.extend(self.load_json_files())
        all_docs.extend(self.load_csv_files())

        logger.info(f"Loaded {len(all_docs)} total documents")

        return all_docs

    def get_data_statistics(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics about the loaded data."""
        if not documents:
            return {}

        stats = {
            "total_documents": len(documents),
            "file_types": {},
            "total_words": 0,
            "total_chars": 0,
            "avg_words_per_doc": 0,
            "avg_chars_per_doc": 0,
        }

        for doc in documents:
            # Count file types
            file_type = doc.get("file_type", "unknown")
            stats["file_types"][file_type] = stats["file_types"].get(file_type, 0) + 1

            # Count words and characters
            word_count = doc.get("word_count", len(doc["content"].split()))
            char_count = doc.get("char_count", len(doc["content"]))

            stats["total_words"] += word_count
            stats["total_chars"] += char_count

        # Calculate averages
        if documents:
            stats["avg_words_per_doc"] = stats["total_words"] / len(documents)
            stats["avg_chars_per_doc"] = stats["total_chars"] / len(documents)

        return stats
