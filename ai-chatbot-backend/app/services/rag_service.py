import time
import logging
from app.services.vector_store import search
from app.services.ollama_service import ask_llm_with_context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_DISTANCE = 2.0

def answer_question(question: str, history: list[dict] | None = None, n_results: int = 2):
    start_time = time.time()
    logger.info(f"Received query: {question}")
    
    if history is None:
        history = []
    
    previous_user_questions = [message.get("content", "").strip() for message in history if message.get("role") == "user" and message.get("content", "").strip()]
    previous_user_questions = previous_user_questions[-1:]
    
    if previous_user_questions:
        retrieval_query = previous_user_questions[0] + "\n" + question
    else:
        retrieval_query = question
        
    results = search(retrieval_query, top_k=n_results)
    
    if not results:
        end_time = time.time()
        logger.info(f"No results found for query. Total time: {(end_time - start_time):.2f}s")
        return {"answer": "I couldn't find relevant information in the knowledge base.", "sources": [], "response_time_ms": int((end_time - start_time) * 1000)}
        
    relevant_results = [result for result in results if result["score"] <= MAX_DISTANCE]
    logger.info(f"Found {len(relevant_results)} relevant results out of {len(results)} retrieved.")
    
    if not relevant_results:
        end_time = time.time()
        return {"answer": "I don't have enough information in the admission brochure to answer that reliably.", "sources": [], "response_time_ms": int((end_time - start_time) * 1000)}
        
    context_parts = []
    sources = []
    for result in relevant_results:
        context_parts.append(f"Source: {result['source']}\n{result['text']}")
        sources.append({"name": result["source"], "distance": result["score"]})
        
    context = "\n\n".join(context_parts)
    answer = ask_llm_with_context(question, context, history)
    
    end_time = time.time()
    response_time_ms = int((end_time - start_time) * 1000)
    logger.info(f"LLM response generated. Total time: {response_time_ms}ms")
    
    return {"answer": answer, "sources": sources, "response_time_ms": response_time_ms}