"""
Grounded generator that produces evidence-backed responses with citations.

Uses retrieved passages as context for the LLM to ensure factual responses.
"""

from typing import List, Optional, Dict, Any
from groq import Groq
import os
import re
from dotenv import load_dotenv

from .schemas import (
    RetrievalResult,
    GenerationContext,
    GeneratedResponse,
    DocumentChunk
)

load_dotenv()


class GroundedGenerator:
    """Generates evidence-backed medical explanations with citations."""
    
    MODELS = [
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-20b",
        "allam-2-7b",
    ]
    
    SYSTEM_PROMPT = """You are a medical education assistant. Your role is to explain laboratory test results in simple language based on provided medical references.

CRITICAL RULES:
1. Base your answers ONLY on the provided medical references - cite them as [1], [2], etc.
2. NEVER invent information not present in the references
3. If references don't contain enough information, say "The provided references don't cover this fully"
4. NEVER diagnose conditions or recommend specific treatments
5. Always suggest consulting a doctor for medical decisions
6. Distinguish clearly between what the report shows and general medical information
7. If a value is abnormal, explain what it might indicate, but emphasize the need for professional evaluation

RESPONSE FORMAT:
- Use simple, clear language
- Cite sources inline: [1], [2], etc.
- One citation per major fact
- If uncertain, acknowledge limitations"""

    SYSTEM_PROMPT_HI = """आप एक चिकित्सा शिक्षा सहायक हैं। आपकी भूमिका प्रदान किए गए चिकित्सा संदर्भों के आधार पर प्रयोगशाला परीक्षण परिणामों को सरल भाषा में समझाना है।

महत्वपूर्ण नियम:
1. अपने उत्तर केवल प्रदान किए गए चिकित्सा संदर्भों पर आधारित करें - उन्हें [1], [2], आदि के रूप में उद्धृत करें
2. संदर्भों में मौजूद नहीं जानकारी का आविष्कार न करें
3. यदि संदर्भ पर्याप्त जानकारी नहीं देते हैं, तो कहें "प्रदान किए गए संदर्भ इसे पूरी तरह से कवर नहीं करते"
4. कभी भी स्थितियों का निदान न करें या विशिष्ट उपचार की सिफारिश न करें
5. हमेशा चिकित्सा निर्णयों के लिए डॉक्टर से परामर्श करने का सुझाव दें
6. रिपोर्ट क्या दिखाती है और सामान्य चिकित्सा जानकारी के बीच स्पष्ट रूप से अंतर करें"""

    SYSTEM_PROMPT_GU = """તમે તબીબી શિક્ષણ સહાયક છો. તમારી ભૂમિકા પ્રદાન કરેલ તબીબી સંદર્ભોના આધારે પ્રયોગશાળા પરીક્ષણ પરિણામોને સરળ ભાષામાં સમજાવવાની છે.

મહત્વપૂર્ણ નિયમો:
1. તમારા જવાબો ફક્ત પ્રદાન કરેલા તબીબી સંદર્ભો પર આધારિત કરો - તેમને [1], [2], વગેરે તરીકે ટાંકો
2. સંદર્ભોમાં હાજર ન હોય તેવી માહિતીની શોધ કરશો નહીં
3. જો સંદર્ભો પૂરતી માહિતી આપતા નથી, તો કહો "પ્રદાન કરેલ સંદર્ભો આને સંપૂર્ણપણે આવરી લેતા નથી"
4. ક્યારેય પરિસ્થિતિઓનું નિદાન કરશો નહીં અથવા ચોક્કસ સારવારની ભલામણ કરશો નહીં
5. હંમેશા તબીબી નિર્ણયો માટે ડૉક્ટરની સલાહ લેવાનું સૂચન કરો"""

    LANG_PROMPTS = {
        "en": SYSTEM_PROMPT,
        "hi": SYSTEM_PROMPT_HI,
        "gu": SYSTEM_PROMPT_GU,
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize grounded generator.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
        """
        self.client = Groq(
            api_key=api_key or os.getenv("GROQ_API_KEY"),
            max_retries=0
        )
    
    def generate(self, context: GenerationContext) -> GeneratedResponse:
        """Generate a grounded response with citations.
        
        Args:
            context: GenerationContext with query and retrieved passages
        
        Returns:
            GeneratedResponse with answer and citations
        """
        if not context.retrieved_passages:
            # No evidence available - return limitation message
            return self._generate_no_evidence_response(context)
        
        # Build prompt
        prompt = self._build_prompt(context)
        
        # Call LLM
        try:
            answer = self._call_llm(prompt, context.language)
        except Exception as e:
            print(f"[GroundedGenerator] LLM call failed: {e}")
            return self._generate_error_response(context, str(e))
        
        # Extract citations
        citations = self._extract_citations(answer)
        
        # Validate citations
        valid_indices = set(range(1, len(context.retrieved_passages) + 1))
        citations = [c for c in citations if c in valid_indices]
        
        # Get cited sources
        sources = [
            context.retrieved_passages[i-1].chunk
            for i in citations
            if i <= len(context.retrieved_passages)
        ]
        
        # Calculate confidence based on citation coverage
        confidence = self._calculate_confidence(answer, citations, context)
        
        return GeneratedResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            sources=sources,
            requires_clarification=self._needs_clarification(answer)
        )
    
    def _build_prompt(self, context: GenerationContext) -> str:
        """Build the prompt for the LLM."""
        parts = []
        
        # Add retrieved references
        parts.append("Medical References:")
        for i, result in enumerate(context.retrieved_passages, 1):
            parts.append(f"\n[{i}] {result.chunk.text}")
            parts.append(f"    (Source: {result.chunk.source_title})")
        
        parts.append("\n---\n")
        
        # Add test-specific context if available
        if context.test_name:
            parts.append(f"Patient's Test Result:")
            parts.append(f"Test: {context.test_name}")
            if context.test_value:
                parts.append(f"Value: {context.test_value}")
            if context.reference_range:
                parts.append(f"Normal Range: {context.reference_range}")
            if context.abnormal_flag is not None:
                status = "Flagged as Abnormal" if context.abnormal_flag else "Within Normal Range"
                parts.append(f"Status: {status}")
            parts.append("")
        
        # Add conversation history if available
        if context.conversation_history:
            parts.append("Previous Conversation:")
            for turn in context.conversation_history[-2:]:
                parts.append(f"User: {turn.get('user', '')}")
                parts.append(f"Assistant: {turn.get('assistant', '')}")
            parts.append("")
        
        # Add the question
        parts.append(f"User Question: {context.question}")
        parts.append("\nProvide a clear explanation based on the references above. Cite sources as [1], [2], etc.")
        
        return "\n".join(parts)
    
    def _call_llm(self, prompt: str, language: str) -> str:
        """Call LLM with fallback chain."""
        system_prompt = self.LANG_PROMPTS.get(language, self.SYSTEM_PROMPT)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        last_error = None
        for model in self.MODELS:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.3,  # Low temperature for factual responses
                    max_tokens=1024,
                )
                return response.choices[0].message.content
                
            except Exception as e:
                err_str = str(e)
                last_error = e
                if "429" in err_str or "rate_limit" in err_str.lower():
                    print(f"[GroundedGenerator] Rate limit on {model}, trying next...")
                    continue
                elif "503" in err_str or "unavailable" in err_str.lower():
                    print(f"[GroundedGenerator] Model {model} unavailable, trying next...")
                    continue
                else:
                    raise
        
        raise Exception(f"All models failed. Last error: {last_error}")
    
    def _extract_citations(self, text: str) -> List[int]:
        """Extract citation numbers from text.
        
        Looks for patterns like [1], [2], [3] in the text.
        
        Args:
            text: Generated text
        
        Returns:
            List of unique citation indices found
        """
        citations = set()
        for match in re.finditer(r'\[(\d+)\]', text):
            citations.add(int(match.group(1)))
        return sorted(list(citations))
    
    def _calculate_confidence(
        self,
        answer: str,
        citations: List[int],
        context: GenerationContext
    ) -> float:
        """Calculate confidence score for the generated response.
        
        Based on:
        - Number of citations (more is better up to a point)
        - Retrieval scores of cited passages
        - Presence of uncertainty phrases
        
        Args:
            answer: Generated answer
            citations: Extracted citation indices
            context: Generation context
        
        Returns:
            Confidence score (0-1)
        """
        confidence = 0.5  # Base confidence
        
        # Citation coverage bonus
        if citations:
            citation_bonus = min(len(citations) * 0.1, 0.3)
            confidence += citation_bonus
        else:
            confidence -= 0.2  # Penalty for no citations
        
        # Average retrieval score of cited passages
        if citations and context.retrieved_passages:
            cited_scores = [
                context.retrieved_passages[i-1].score
                for i in citations
                if i <= len(context.retrieved_passages)
            ]
            if cited_scores:
                avg_score = sum(cited_scores) / len(cited_scores)
                confidence += avg_score * 0.2
        
        # Uncertainty phrases reduce confidence
        uncertainty_phrases = [
            "i don't have enough information",
            "the provided references don't",
            "i cannot",
            "not sure",
            "unclear",
            "may or may not"
        ]
        if any(phrase in answer.lower() for phrase in uncertainty_phrases):
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _needs_clarification(self, answer: str) -> bool:
        """Check if the response indicates need for clarification."""
        clarification_phrases = [
            "could you clarify",
            "which test",
            "which value",
            "more specific",
            "need more information"
        ]
        return any(phrase in answer.lower() for phrase in clarification_phrases)
    
    def _generate_no_evidence_response(self, context: GenerationContext) -> GeneratedResponse:
        """Generate response when no evidence is available."""
        messages = {
            "en": "I don't have enough medical reference information to answer this question reliably. Please consult your doctor for accurate information about your test results.",
            "hi": "मेरे पास इस प्रश्न का विश्वसनीय उत्तर देने के लिए पर्याप्त चिकित्सा संदर्भ जानकारी नहीं है। कृपया अपने परीक्षण परिणामों के बारे में सटीक जानकारी के लिए अपने डॉक्टर से परामर्श करें।",
            "gu": "મારી પાસે આ પ્રશ્નનો વિશ્વસનીય જવાબ આપવા માટે પર્યાપ્ત તબીબી સંદર્ભ માહિતી નથી. કૃપા કરીને તમારા પરીક્ષણ પરિણામો વિશે ચોક્કસ માહિતી માટે તમારા ડૉક્ટરની સલાહ લો."
        }
        
        answer = messages.get(context.language, messages["en"])
        
        return GeneratedResponse(
            answer=answer,
            citations=[],
            confidence=0.1,
            sources=[],
            limitations="No relevant medical references available in knowledge base."
        )
    
    def _generate_error_response(self, context: GenerationContext, error: str) -> GeneratedResponse:
        """Generate response for LLM errors."""
        messages = {
            "en": "I'm unable to process this question right now due to a technical issue. Please try again in a moment.",
            "hi": "तकनीकी समस्या के कारण मैं अभी इस प्रश्न को संसाधित करने में असमर्थ हूं। कृपया कुछ देर बाद पुनः प्रयास करें।",
            "gu": "તકનીકી સમસ્યાને કારણે હું અત્યારે આ પ્રશ્નને પ્રક્રિયા કરવામાં અસમર્થ છું. કૃપા કરીને થોડી વાર પછી ફરી પ્રયાસ કરો."
        }
        
        answer = messages.get(context.language, messages["en"])
        
        return GeneratedResponse(
            answer=answer,
            citations=[],
            confidence=0.0,
            sources=[],
            limitations=f"Technical error: {error}"
        )
    
    def generate_test_explanation(
        self,
        test_name: str,
        retrieved_passages: List[RetrievalResult],
        language: str = "en"
    ) -> GeneratedResponse:
        """Generate explanation for a specific test.
        
        Args:
            test_name: Name of the laboratory test
            retrieved_passages: Retrieved reference passages
            language: Response language
        
        Returns:
            GeneratedResponse with explanation
        """
        context = GenerationContext(
            question=f"What is the {test_name} test and what does it measure?",
            test_name=test_name,
            retrieved_passages=retrieved_passages,
            language=language
        )
        
        return self.generate(context)
    
    def generate_value_interpretation(
        self,
        test_name: str,
        test_value: str,
        reference_range: str,
        abnormal_flag: bool,
        retrieved_passages: List[RetrievalResult],
        language: str = "en"
    ) -> GeneratedResponse:
        """Generate interpretation for a test value.
        
        Args:
            test_name: Test name
            test_value: Patient's value
            reference_range: Normal range
            abnormal_flag: Whether value is abnormal
            retrieved_passages: Retrieved reference passages
            language: Response language
        
        Returns:
            GeneratedResponse with interpretation
        """
        status = "abnormal" if abnormal_flag else "normal"
        question = f"My {test_name} is {test_value} (normal range: {reference_range}). This is {status}. What does this mean?"
        
        context = GenerationContext(
            question=question,
            test_name=test_name,
            test_value=test_value,
            reference_range=reference_range,
            abnormal_flag=abnormal_flag,
            retrieved_passages=retrieved_passages,
            language=language
        )
        
        return self.generate(context)
