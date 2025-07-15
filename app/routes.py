from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.config.config import CHROMA_PERSIST_DIRECTORY, OLLAMA_BASE_URL, OLLAMA_MODEL
from app.evaluation import eval_data
from app.evaluation.semantic_evaluator import evaluate_production_question
from app.llm.llm import embeddings, llm
from app.models.models import ChatRequest, ChatResponse, HealthResponse
from app.prompts.system_prompt import SYSTEM_PROMPT, SYSTEM_PROMPT_CONTEXT
from app.tracking import get_ollama_response
from app.vector_store.vector_store import get_context, vector_store

router = APIRouter()


@router.get("/", response_model=dict)
async def root():
    return {"message": "Simple Insurance Chatbot API", "docs": "/docs", "health": "/health"}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        test_response = llm.invoke("Hello")
        ollama_status = "healthy" if test_response else "unhealthy"
    except Exception as e:
        ollama_status = f"unhealthy: {str(e)}"
    if vector_store:
        try:
            vector_store._collection.count()
            vector_store_status = "healthy"
        except Exception as e:
            vector_store_status = f"unhealthy: {str(e)}"
    else:
        vector_store_status = "not initialized"
    overall_status = "healthy" if ollama_status == "healthy" else "degraded"
    return HealthResponse(status=overall_status, ollama_status=ollama_status, vector_store_status=vector_store_status)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        sources = []
        context = ""
        embeddings_supported = True
        try:
            _ = embeddings.embed_query("The insured person's name is Julien Look")
        except Exception as e:
            print(f"Embeddings not supported: {e}")
            embeddings_supported = False
        print(
            f"Using context: {request.use_context}, embeddings supported: {embeddings_supported}, vector_store:  {vector_store}"
        )
        if request.use_context and vector_store and embeddings_supported:
            context, sources = get_context(request.message)
            print(f"Context retrieved: {len(context)} characters, sources: {sources}")
        if context:
            messages = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT_CONTEXT,
                },
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {request.message}"},
            ]
        else:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.message},
            ]

        # Use auto-logged OpenAI client instead of direct LLM
        response = get_ollama_response(messages)

        # Perform semantic evaluation in background
        try:
            evaluation_result = await evaluate_production_question(request.message, response)
            print(f"🔍 Semantic evaluation: {evaluation_result}")
        except Exception as e:
            print(f"Error in semantic evaluation: {e}")
            evaluation_result = None

        return ChatResponse(response=response, sources=sources if sources else None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@router.get("/info")
async def get_info():
    doc_count = 0
    if vector_store:
        try:
            doc_count = vector_store._collection.count()
        except:
            doc_count = "unknown"
    return {
        "model": OLLAMA_MODEL,
        "base_url": OLLAMA_BASE_URL,
        "documents_indexed": doc_count,
        "vector_store_path": CHROMA_PERSIST_DIRECTORY,
    }


@router.get("/eval/sample")
async def get_evaluation_sample():
    """Get a sample of evaluation questions."""
    sample = eval_data.head(5)
    return {
        "total_questions": len(eval_data),
        "sample_size": len(sample),
        "questions": sample["inputs"].tolist(),
        "sample_data": sample.to_dict("records"),
    }


@router.get("/eval/categories")
async def get_evaluation_categories():
    """Get evaluation questions by category."""
    from app.evaluation.eval_data import get_question_categories

    categories = get_question_categories()

    result = {}
    for category, data in categories.items():
        result[category] = {"count": len(data), "questions": data["inputs"].tolist()}

    return result


@router.post("/eval/run")
async def run_evaluation_endpoint(
    sample_size: int = 5, use_context: bool = False, use_llm_judge: bool = True, log_to_mlflow: bool = True
):
    """Run evaluation on a sample of questions with optional MLflow tracking."""
    try:
        from app.evaluation.evaluator import run_evaluation, save_evaluation_results

        # Run the evaluation
        results = await run_evaluation(
            sample_size=sample_size, use_context=use_context, use_llm_judge=use_llm_judge, log_to_mlflow=log_to_mlflow
        )

        # Save results to file
        filepath = save_evaluation_results(results)

        return {
            "status": "completed",
            "summary": results["summary"],
            "results_file": str(filepath),
            "mlflow_tracking": log_to_mlflow,
            "mlflow_ui": "http://localhost:5000" if log_to_mlflow else None,
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/eval/production/stats")
async def get_production_evaluation_stats():
    """Get statistics about production evaluations."""
    from pathlib import Path

    from app.evaluation.semantic_evaluator import semantic_evaluator

    try:
        # Count evaluation files
        eval_dir = Path("app/evaluation/evaluation_results/production_evaluations")
        eval_files = list(eval_dir.glob("*.json")) if eval_dir.exists() else []

        # Get new questions count
        new_questions_count = len(semantic_evaluator.new_questions)

        return {
            "total_production_evaluations": len(eval_files),
            "new_questions_saved": new_questions_count,
            "confidence_threshold": semantic_evaluator.confidence_threshold,
            "evaluation_dataset_size": len(semantic_evaluator.eval_dataset),
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/eval/production/new-questions")
async def get_new_questions():
    """Get list of new questions that weren't matched in evaluation dataset."""
    from app.evaluation.semantic_evaluator import semantic_evaluator

    try:
        return {
            "total_new_questions": len(semantic_evaluator.new_questions),
            "questions": semantic_evaluator.new_questions[-10:],  # Return last 10
        }
    except Exception as e:
        return {"error": str(e)}


@router.post("/eval/production/test-similarity")
async def test_similarity(question: str):
    """Test semantic similarity detection for a question."""
    from app.evaluation.semantic_evaluator import semantic_evaluator

    try:
        result = await semantic_evaluator.find_similar_question(question)
        return {
            "test_question": question,
            "similarity_result": result,
            "confidence_threshold": semantic_evaluator.confidence_threshold,
        }
    except Exception as e:
        return {"error": str(e)}
