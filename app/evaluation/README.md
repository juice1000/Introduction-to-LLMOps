# LLMOps Evaluation System

This directory contains the evaluation system for the insurance chatbot, combining custom LLM-as-a-judge scoring with MLflow experiment tracking.

## 🎯 Unified Evaluation Workflow

The evaluation system has been streamlined to avoid redundancy and provide a single, comprehensive evaluation pipeline that:

1. **Tests chatbot responses** against ground truth data
2. **Calculates objective metrics** (word overlap, response time)
3. **Uses LLM-as-a-judge** for qualitative scoring (accuracy, completeness, clarity, relevance, helpfulness)
4. **Tracks experiments** with MLflow for reproducibility
5. **Saves results** to JSON files for analysis

## 📁 Files

- `eval_data.py` - Evaluation dataset with 25 insurance Q&A pairs
- `evaluator.py` - Main evaluation runner with MLflow integration
- `evaluation_results/` - Directory for saved evaluation results

## 🚀 Usage

### Run Evaluation Directly

```bash
cd /path/to/Introduction-to-LLMOps
source venv/bin/activate
python app/evaluation/evaluator.py
```

### Run via API

```bash
curl -X POST "http://localhost:8000/eval/run" \
  -H "Content-Type: application/json" \
  -d '{
    "sample_size": 5,
    "use_context": false,
    "use_llm_judge": true,
    "log_to_mlflow": true
  }'
```

### View Results

- **JSON Results**: Check `evaluation_results/` directory
- **MLflow UI**: Visit http://localhost:5000 for experiment tracking

## 📊 Metrics

### Objective Metrics

- **Word Overlap**: Ratio of common words between response and ground truth
- **Response Time**: Time taken to generate response
- **Success Rate**: Percentage of responses with >30% word overlap

### LLM-as-a-Judge Scoring (1-5 scale)

- **Accuracy**: Correctness of information
- **Completeness**: Coverage of question requirements
- **Clarity**: Understandability of response
- **Relevance**: Appropriateness to question
- **Helpfulness**: Usefulness to user

## 🔧 Configuration

Parameters in `run_evaluation()`:

- `sample_size`: Number of questions to evaluate
- `use_context`: Whether to use vector store context (future feature)
- `use_llm_judge`: Enable LLM-as-a-judge scoring
- `log_to_mlflow`: Enable MLflow experiment tracking

## 🎯 Evaluation Philosophy

This system balances:

- **Quantitative metrics** for objective measurement
- **Qualitative scoring** for nuanced evaluation
- **Experiment tracking** for reproducible research
- **Domain-specific evaluation** tailored to insurance use cases

The LLM-as-a-judge approach is particularly valuable for open-ended responses where traditional metrics like BLEU or ROUGE may not capture semantic quality.
