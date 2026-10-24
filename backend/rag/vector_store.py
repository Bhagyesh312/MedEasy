"""
Vector store for medical knowledge chunks using sentence transformers + FAISS.

Uses local FAISS for simplicity - can be upgraded to Qdrant Cloud later.
"""

import numpy as np
from typing import List, Optional, Tuple
import pickle
import os
from sentence_transformers import SentenceTransformer

try:
    import faiss
except ImportError:
    faiss = None

from .schemas import DocumentChunk, RetrievalResult


class VectorStore:
    """Simple vector store using FAISS for local storage."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", index_path: Optional[str] = None):
        """Initialize vector store.
        
        Args:
            model_name: Sentence transformer model to use
            index_path: Path to save/load FAISS index
        """
        self.model_name = model_name
        self.index_path = index_path or "knowledge_index.faiss"
        self.chunks_path = f"{self.index_path}.chunks.pkl"
        
        # Load embedding model
        print(f"[VectorStore] Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        # Initialize FAISS index
        if faiss is None:
            raise ImportError("FAISS not installed. Install with: pip install faiss-cpu")
        
        self.index: Optional[faiss.Index] = None
        self.chunks: List[DocumentChunk] = []
        
        # Try to load existing index
        if os.path.exists(self.index_path):
            self.load()
    
    def add_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Add document chunks to the vector store.
        
        Args:
            chunks: List of DocumentChunk objects to add
        """
        if not chunks:
            return
        
        # Generate embeddings
        print(f"[VectorStore] Generating embeddings for {len(chunks)} chunks...")
        texts = [chunk.text for chunk in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        
        # Initialize index if needed
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings)
        
        # Store chunks
        self.chunks.extend(chunks)
        
        print(f"[VectorStore] Added {len(chunks)} chunks. Total: {len(self.chunks)}")
    
    def search(
        self, 
        query: str, 
        k: int = 5,
        filter_test_names: Optional[List[str]] = None
    ) -> List[RetrievalResult]:
        """Search for relevant chunks.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_test_names: Optional list of test names to filter by
        
        Returns:
            List of RetrievalResult objects ranked by relevance
        """
        if self.index is None or len(self.chunks) == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding, min(k * 2, len(self.chunks)))
        
        # Convert to results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= len(self.chunks):
                continue
            
            chunk = self.chunks[idx]
            
            # Apply filter if specified
            if filter_test_names:
                if not any(test.lower() in [t.lower() for t in chunk.test_names] for test in filter_test_names):
                    continue
            
            results.append(RetrievalResult(
                chunk=chunk,
                score=float(score),
                rank=len(results) + 1
            ))
            
            if len(results) >= k:
                break
        
        return results
    
    def save(self) -> None:
        """Save index and chunks to disk."""
        if self.index is None:
            return
        
        # Save FAISS index
        faiss.write_index(self.index, self.index_path)
        
        # Save chunks
        with open(self.chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
        
        print(f"[VectorStore] Saved index with {len(self.chunks)} chunks to {self.index_path}")
    
    def load(self) -> None:
        """Load index and chunks from disk."""
        if not os.path.exists(self.index_path):
            return
        
        # Load FAISS index
        self.index = faiss.read_index(self.index_path)
        
        # Load chunks
        if os.path.exists(self.chunks_path):
            with open(self.chunks_path, 'rb') as f:
                self.chunks = pickle.load(f)
        
        print(f"[VectorStore] Loaded index with {len(self.chunks)} chunks from {self.index_path}")
    
    def clear(self) -> None:
        """Clear all data from the vector store."""
        self.index = None
        self.chunks = []
        
        # Delete files
        for path in [self.index_path, self.chunks_path]:
            if os.path.exists(path):
                os.remove(path)
        
        print("[VectorStore] Cleared all data")
