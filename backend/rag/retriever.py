"""
Medical retriever with query rewriting and hybrid search.

Combines semantic similarity with metadata filtering for
relevant medical knowledge retrieval.
"""

from typing import List, Optional, Dict, Any
import re

from .schemas import RetrievalResult, DocumentChunk
from .vector_store import VectorStore


class MedicalRetriever:
    """Retrieves relevant medical knowledge for user queries."""
    
    def __init__(self, vector_store: VectorStore):
        """Initialize retriever.
        
        Args:
            vector_store: Initialized VectorStore instance
        """
        self.vector_store = vector_store
    
    def retrieve(
        self,
        query: str,
        k: int = 5,
        test_name: Optional[str] = None,
        rerank: bool = True
    ) -> List[RetrievalResult]:
        """Retrieve relevant passages for a query.
        
        Args:
            query: User's question
            k: Number of results to return
            test_name: Specific test being asked about (optional filter)
            rerank: Whether to rerank results
        
        Returns:
            List of RetrievalResult objects ranked by relevance
        """
        # Expand query for better retrieval
        expanded_query = self._expand_query(query, test_name)
        
        # Determine filter
        filter_tests = None
        if test_name:
            filter_tests = [test_name]
        
        # Retrieve from vector store
        results = self.vector_store.search(
            query=expanded_query,
            k=k * 2 if rerank else k,  # Get more for reranking
            filter_test_names=filter_tests
        )
        
        # Rerank if requested
        if rerank and len(results) > k:
            results = self._rerank_results(query, results, k)
        
        return results[:k]
    
    def _expand_query(self, query: str, test_name: Optional[str] = None) -> str:
        """Expand query with medical context for better retrieval.
        
        Args:
            query: Original query
            test_name: Test name if available
        
        Returns:
            Expanded query string
        """
        parts = [query]
        
        # Add test name context
        if test_name:
            parts.append(f"laboratory test: {test_name}")
        
        # Add general medical context terms
        if any(word in query.lower() for word in ["what", "meaning", "measure"]):
            parts.append("definition explanation")
        
        if any(word in query.lower() for word in ["high", "low", "abnormal", "elevated"]):
            parts.append("abnormal values causes")
        
        if any(word in query.lower() for word in ["normal", "range", "reference"]):
            parts.append("normal range reference values")
        
        if any(word in query.lower() for word in ["symptoms", "signs", "feel"]):
            parts.append("symptoms clinical signs")
        
        if any(word in query.lower() for word in ["treatment", "fix", "improve"]):
            parts.append("treatment management")
        
        return " ".join(parts)
    
    def _rerank_results(
        self,
        query: str,
        results: List[RetrievalResult],
        k: int
    ) -> List[RetrievalResult]:
        """Rerank results using heuristics.
        
        Simple reranking based on:
        - Query term overlap
        - Source credibility
        - Passage length quality
        
        Args:
            query: Original query
            results: Initial retrieval results
            k: Number of top results to keep
        
        Returns:
            Reranked results
        """
        query_terms = set(query.lower().split())
        
        # Calculate reranking scores
        for result in results:
            passage_terms = set(result.chunk.text.lower().split())
            
            # Term overlap bonus
            overlap = len(query_terms & passage_terms) / len(query_terms) if query_terms else 0
            
            # Credibility bonus
            credibility_bonus = result.chunk.credibility_score * 0.1
            
            # Length penalty for very short or very long passages
            text_len = len(result.chunk.text)
            if text_len < 100:
                length_penalty = 0.1
            elif text_len > 1500:
                length_penalty = 0.05
            else:
                length_penalty = 0.0
            
            # Combine scores
            result.score = (
                result.score * 0.7 +  # Original semantic score (70%)
                overlap * 0.2 +        # Term overlap (20%)
                credibility_bonus -    # Credibility bonus
                length_penalty         # Length penalty
            )
        
        # Sort by new scores
        results.sort(key=lambda r: r.score, reverse=True)
        
        # Update ranks
        for i, result in enumerate(results[:k], 1):
            result.rank = i
        
        return results
    
    def retrieve_for_test_explanation(
        self,
        test_name: str,
        k: int = 3
    ) -> List[RetrievalResult]:
        """Retrieve passages explaining a specific test.
        
        Optimized query for test definitions and explanations.
        
        Args:
            test_name: Name of the laboratory test
            k: Number of results
        
        Returns:
            Retrieved passages about the test
        """
        query = f"What is {test_name}? What does {test_name} measure? {test_name} test definition"
        return self.retrieve(query=query, k=k, test_name=test_name)
    
    def retrieve_for_abnormal_value(
        self,
        test_name: str,
        abnormality_type: str,
        k: int = 3
    ) -> List[RetrievalResult]:
        """Retrieve passages about abnormal test values.
        
        Args:
            test_name: Name of the test
            abnormality_type: "high", "low", or "critical"
            k: Number of results
        
        Returns:
            Retrieved passages about causes and implications
        """
        query = f"{abnormality_type} {test_name} causes symptoms what does {abnormality_type} {test_name} mean"
        return self.retrieve(query=query, k=k, test_name=test_name)
    
    def retrieve_for_general_question(
        self,
        question: str,
        k: int = 5
    ) -> List[RetrievalResult]:
        """Retrieve passages for a general medical question.
        
        Args:
            question: User's question
            k: Number of results
        
        Returns:
            Retrieved passages
        """
        return self.retrieve(query=question, k=k, test_name=None)
    
    def get_coverage_summary(self) -> Dict[str, Any]:
        """Get summary of knowledge base coverage.
        
        Returns:
            Dictionary with coverage statistics
        """
        if not self.vector_store.chunks:
            return {
                "total_chunks": 0,
                "total_sources": 0,
                "covered_tests": [],
                "source_types": []
            }
        
        # Aggregate statistics
        sources = set()
        test_names = set()
        source_types = set()
        
        for chunk in self.vector_store.chunks:
            sources.add(chunk.source_id)
            test_names.update(chunk.test_names)
            source_types.add(chunk.source_type.value)
        
        return {
            "total_chunks": len(self.vector_store.chunks),
            "total_sources": len(sources),
            "covered_tests": sorted(list(test_names)),
            "source_types": sorted(list(source_types))
        }
