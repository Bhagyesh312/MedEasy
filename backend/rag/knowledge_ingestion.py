"""
Medical knowledge ingestion from trusted public sources.

Fetches, parses, and chunks medical reference content for RAG system.
All sources respect licensing and attribution requirements.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Optional, Tuple
import re
import hashlib
from datetime import datetime

from .schemas import SourceDocument, SourceType, LicenseType, DocumentChunk


class MedicalKnowledgeIngester:
    """Ingests medical knowledge from public domain and open sources."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """Initialize ingester.
        
        Args:
            chunk_size: Target chunk size in tokens (approximate)
            chunk_overlap: Overlap between chunks for context preservation
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MedEasy Medical Education Bot/1.0 (Educational Use)'
        })
    
    def ingest_medlineplus_topic(self, topic_url: str) -> SourceDocument:
        """Ingest a MedlinePlus topic page.
        
        MedlinePlus is public domain content from the U.S. National Library of Medicine.
        
        Args:
            topic_url: URL of the MedlinePlus topic page
        
        Returns:
            SourceDocument object
        
        Example:
            url = "https://medlineplus.gov/lab-tests/hemoglobin-test/"
        """
        try:
            response = self.session.get(topic_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch MedlinePlus page: {e}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title_elem = soup.find('h1', class_='page-title') or soup.find('h1')
        title = title_elem.get_text(strip=True) if title_elem else "MedlinePlus Topic"
        
        # Extract main content
        content_div = soup.find('div', id='topic-content') or soup.find('main') or soup.find('article')
        if not content_div:
            raise Exception("Could not locate main content on MedlinePlus page")
        
        # Remove navigation, sidebars, ads
        for unwanted in content_div.find_all(['nav', 'aside', 'script', 'style', 'iframe']):
            unwanted.decompose()
        
        # Extract clean text
        paragraphs = []
        for p in content_div.find_all(['p', 'li', 'h2', 'h3']):
            text = p.get_text(strip=True)
            if text and len(text) > 20:  # Filter out very short fragments
                paragraphs.append(text)
        
        full_text = '\n\n'.join(paragraphs)
        
        # Generate source ID
        source_id = f"medlineplus_{hashlib.md5(topic_url.encode()).hexdigest()[:12]}"
        
        # Create source document
        doc = SourceDocument(
            source_id=source_id,
            title=title,
            url=topic_url,
            source_type=SourceType.MEDLINEPLUS,
            publisher="U.S. National Library of Medicine",
            license=LicenseType.PUBLIC_DOMAIN,
            full_text=full_text,
            language="en",
            is_peer_reviewed=False,
            credibility_score=0.95,  # High credibility for NIH sources
        )
        
        return doc
        
    def ingest_manual_content(
        self, 
        title: str, 
        content: str, 
        source_url: str,
        publisher: str = "MedEasy",
        license: LicenseType = LicenseType.EDUCATIONAL_USE,
        test_names: Optional[List[str]] = None
    ) -> SourceDocument:
        """Ingest manually curated educational content.
        
        Use this for content you've written or have explicit permission to use.
        
        Args:
            title: Document title
            content: Full text content
            source_url: Attribution URL (can be internal)
            publisher: Publishing organization
            license: Content license
            test_names: Laboratory tests covered
        
        Returns:
            SourceDocument object
        """
        source_id = f"manual_{hashlib.md5(f"{title}{content[:100]}".encode()).hexdigest()[:12]}"
        
        doc = SourceDocument(
            source_id=source_id,
            title=title,
            url=source_url,
            source_type=SourceType.MANUAL,
            publisher=publisher,
            license=license,
            full_text=content,
            test_names=test_names or [],
            language="en",
            is_peer_reviewed=False,
            credibility_score=0.8,
        )
        
        return doc
    
    def chunk_document(self, doc: SourceDocument) -> List[DocumentChunk]:
        """Chunk a source document into passages for embedding.
        
        Uses semantic chunking that respects paragraph boundaries.
        
        Args:
            doc: Source document to chunk
        
        Returns:
            List of DocumentChunk objects
        """
        # Split into paragraphs
        paragraphs = [p.strip() for p in doc.full_text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = []
        current_length = 0
        chunk_index = 0
        
        for para in paragraphs:
            # Approximate token count (rough: ~4 chars per token)
            para_tokens = len(para) // 4
            
            if current_length + para_tokens > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append(self._create_chunk(doc, chunk_text, chunk_index))
                chunk_index += 1
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0 and current_chunk:
                    # Keep last paragraph for overlap
                    current_chunk = [current_chunk[-1]]
                    current_length = len(current_chunk[-1]) // 4
                else:
                    current_chunk = []
                    current_length = 0
            
            current_chunk.append(para)
            current_length += para_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append(self._create_chunk(doc, chunk_text, chunk_index))
        
        return chunks
    
    def _create_chunk(self, doc: SourceDocument, text: str, index: int) -> DocumentChunk:
        """Create a DocumentChunk from source and text."""
        chunk_id = f"{doc.source_id}_chunk_{index}"
        
        return DocumentChunk(
            chunk_id=chunk_id,
            source_id=doc.source_id,
            text=text,
            chunk_index=index,
            source_title=doc.title,
            source_url=doc.url,
            source_type=doc.source_type,
            publisher=doc.publisher,
            topics=doc.topics,
            test_names=doc.test_names,
            conditions=doc.conditions,
            license=doc.license,
            credibility_score=doc.credibility_score,
        )
    
    def ingest_sample_knowledge_base(self) -> Tuple[List[SourceDocument], List[DocumentChunk]]:
        """Create a sample knowledge base with basic laboratory test information.
        
        This provides initial content for testing without external dependencies.
        All content is manually curated educational material.
        
        Returns:
            Tuple of (source_documents, chunks)
        """
        documents = []
        all_chunks = []
        
        # Sample document 1: Hemoglobin
        hemoglobin_content = """
        Hemoglobin is a protein in red blood cells that carries oxygen from your lungs to the rest of your body. 
        
        A hemoglobin test measures the amount of hemoglobin in your blood. It is part of a complete blood count (CBC).
        
        Normal hemoglobin levels vary by age and sex. For adult men, normal is typically 13.5 to 17.5 grams per deciliter (g/dL). For adult women, normal is 12.0 to 15.5 g/dL.
        
        Low hemoglobin levels may indicate anemia. Causes of low hemoglobin include iron deficiency, vitamin B12 deficiency, chronic kidney disease, and blood loss.
        
        High hemoglobin levels may occur with dehydration, lung disease, or living at high altitude. It can also indicate polycythemia vera, a bone marrow disorder.
        
        If your hemoglobin is outside the normal range, your doctor will order additional tests to determine the cause. Treatment depends on the underlying condition.
        """
        
        hb_doc = self.ingest_manual_content(
            title="Hemoglobin Test - Patient Education",
            content=hemoglobin_content,
            source_url="https://medeasy.internal/education/hemoglobin",
            test_names=["Hemoglobin", "Hb", "HGB"],
        )
        documents.append(hb_doc)
        all_chunks.extend(self.chunk_document(hb_doc))
        
        # Sample document 2: Blood Glucose
        glucose_content = """
        Blood glucose (blood sugar) is the main sugar found in your blood. It comes from the food you eat and is your body's main source of energy.
        
        A blood glucose test measures the amount of glucose in your blood. There are several types: fasting blood sugar (FBS), random blood sugar, and postprandial (after meal) glucose.
        
        Normal fasting blood glucose is 70-100 mg/dL. Levels between 100-125 mg/dL indicate prediabetes. Levels of 126 mg/dL or higher on two separate tests indicate diabetes.
        
        High blood sugar (hyperglycemia) over time can damage blood vessels and nerves. It can lead to complications affecting the eyes, kidneys, heart, and feet.
        
        Low blood sugar (hypoglycemia) below 70 mg/dL can cause symptoms like shakiness, sweating, confusion, and rapid heartbeat. Severe hypoglycemia can be dangerous.
        
        If your blood glucose is abnormal, your doctor may recommend lifestyle changes, additional testing (like HbA1c), or medication depending on the cause and severity.
        """
        
        glucose_doc = self.ingest_manual_content(
            title="Blood Glucose Test - Understanding Your Results",
            content=glucose_content,
            source_url="https://medeasy.internal/education/glucose",
            test_names=["Glucose", "Blood Sugar", "FBS", "Fasting Blood Sugar"],
        )
        documents.append(glucose_doc)
        all_chunks.extend(self.chunk_document(glucose_doc))
        
        # Sample document 3: Complete Blood Count
        cbc_content = """
        A Complete Blood Count (CBC) is one of the most common blood tests. It measures several components of your blood including red blood cells, white blood cells, and platelets.
        
        Red Blood Cell (RBC) count measures the number of oxygen-carrying red blood cells. Normal ranges are 4.5-5.5 million cells/μL for men and 4.0-5.0 million cells/μL for women.
        
        White Blood Cell (WBC) count measures infection-fighting white blood cells. Normal range is 4,000-11,000 cells/μL. High WBC may indicate infection or inflammation. Low WBC may indicate bone marrow problems or certain medications.
        
        Platelet count measures blood clotting cells. Normal range is 150,000-400,000/μL. Low platelets increase bleeding risk. High platelets may increase clotting risk.
        
        Hematocrit (HCT) measures the percentage of blood volume made up of red blood cells. Normal is 38-50% for men and 35-45% for women.
        
        Mean Corpuscular Volume (MCV) measures the average size of red blood cells. It helps diagnose the type of anemia if present.
        """
        
        cbc_doc = self.ingest_manual_content(
            title="Complete Blood Count (CBC) - What the Numbers Mean",
            content=cbc_content,
            source_url="https://medeasy.internal/education/cbc",
            test_names=["CBC", "Complete Blood Count", "RBC", "WBC", "Platelets", "Hematocrit", "MCV"],
        )
        documents.append(cbc_doc)
        all_chunks.extend(self.chunk_document(cbc_doc))
        
        return documents, all_chunks


# Sample usage patterns
COMMON_TEST_URLS = {
    # These are example URLs - real implementation would use actual MedlinePlus URLs
    "hemoglobin": "https://medlineplus.gov/lab-tests/hemoglobin-test/",
    "glucose": "https://medlineplus.gov/lab-tests/blood-glucose-test/",
    "cholesterol": "https://medlineplus.gov/lab-tests/cholesterol-levels/",
    "creatinine": "https://medlineplus.gov/lab-tests/creatinine-test/",
    "thyroid": "https://medlineplus.gov/lab-tests/thyroid-tests/",
}
