"""
Lazy imports for optional ML dependencies.
Gracefully degrades when heavy libraries are not available.
"""

# Try to import heavy ML libraries
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

try:
    import sklearn
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    sklearn = None

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

# Check if RAG features are fully available
RAG_AVAILABLE = FAISS_AVAILABLE and SENTENCE_TRANSFORMERS_AVAILABLE

def check_rag_dependencies():
    """Check if RAG dependencies are available."""
    if not RAG_AVAILABLE:
        missing = []
        if not FAISS_AVAILABLE:
            missing.append("faiss-cpu")
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            missing.append("sentence-transformers")
        return False, f"Missing dependencies: {', '.join(missing)}"
    return True, "All RAG dependencies available"

def get_embedding_model():
    """Get embedding model if available, otherwise return None."""
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        return None
    try:
        return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        print(f"⚠️  Failed to load embedding model: {e}")
        return None
