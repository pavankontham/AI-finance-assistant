"""
Vector store for document storage and retrieval.
"""
import os
import logging
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """
    Simple vector store for document storage and retrieval.
    """
    
    def __init__(self):
        """Initialize the vector store."""
        self.documents = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize with some default documents
        self._initialize_default_documents()
    
    def _initialize_default_documents(self):
        """Initialize the vector store with some default documents."""
        default_docs = [
            {
                "id": "doc1",
                "text": "The S&P 500 is a stock market index tracking the stock performance of 500 large companies listed on stock exchanges in the United States.",
                "metadata": {"source": "financial_knowledge", "category": "indices"}
            },
            {
                "id": "doc2",
                "text": "Market capitalization refers to the total dollar market value of a company's outstanding shares of stock.",
                "metadata": {"source": "financial_knowledge", "category": "terminology"}
            },
            {
                "id": "doc3",
                "text": "The price-to-earnings ratio (P/E ratio) is the ratio of a company's share price to the company's earnings per share.",
                "metadata": {"source": "financial_knowledge", "category": "metrics"}
            },
            {
                "id": "doc4",
                "text": "Asia tech stocks include companies like TSMC, Samsung, Alibaba, and Sony, which are major technology players in the Asian market.",
                "metadata": {"source": "financial_knowledge", "category": "sectors"}
            },
            {
                "id": "doc5",
                "text": "Taiwan Semiconductor Manufacturing Company (TSMC) is the world's largest semiconductor foundry, producing chips for companies like Apple and NVIDIA.",
                "metadata": {"source": "company_profile", "category": "technology", "region": "asia"}
            },
            {
                "id": "doc6",
                "text": "Earnings surprises occur when a company's reported quarterly or annual profits are above or below analysts' expectations.",
                "metadata": {"source": "financial_knowledge", "category": "earnings"}
            },
            {
                "id": "doc7",
                "text": "Portfolio allocation refers to how an investment portfolio is divided among different asset classes, such as stocks, bonds, and cash.",
                "metadata": {"source": "financial_knowledge", "category": "portfolio"}
            }
        ]
        
        # Add documents to the store
        for doc in default_docs:
            self.documents[doc["id"]] = doc
    
    def add_document(self, document: Dict[str, Any]) -> str:
        """
        Add a document to the vector store.
        
        Args:
            document: Document to add
            
        Returns:
            Document ID
        """
        # Generate a document ID if not provided
        if "id" not in document:
            document["id"] = f"doc{len(self.documents) + 1}"
        
        # Add the document to the store
        self.documents[document["id"]] = document
        
        self.logger.info(f"Added document with ID: {document['id']}")
        
        return document["id"]
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Add multiple documents to the vector store.
        
        Args:
            documents: List of documents to add
            
        Returns:
            List of document IDs
        """
        document_ids = []
        
        for document in documents:
            document_id = self.add_document(document)
            document_ids.append(document_id)
        
        self.logger.info(f"Added {len(document_ids)} documents")
        
        return document_ids
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            Document or None if not found
        """
        return self.documents.get(document_id)
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            document_id: Document ID
            
        Returns:
            True if deleted, False if not found
        """
        if document_id in self.documents:
            del self.documents[document_id]
            self.logger.info(f"Deleted document with ID: {document_id}")
            return True
        else:
            self.logger.warning(f"Document not found: {document_id}")
            return False
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for documents matching the query.
        
        Args:
            query: Query string
            top_k: Number of results to return
            
        Returns:
            List of matching documents
        """
        self.logger.info(f"Searching for: {query} (top_k={top_k})")
        
        # In a real implementation, this would use vector similarity search
        # For this demo, we'll use simple keyword matching
        
        query_terms = query.lower().split()
        matches = []
        
        for doc_id, document in self.documents.items():
            text = document.get("text", "").lower()
            metadata = document.get("metadata", {})
            
            # Calculate a simple relevance score based on term frequency
            score = 0
            for term in query_terms:
                if term in text:
                    score += text.count(term)
                
                # Also check metadata
                for key, value in metadata.items():
                    if isinstance(value, str) and term in value.lower():
                        score += 1
            
            if score > 0:
                matches.append({
                    "id": doc_id,
                    "text": document.get("text", ""),
                    "metadata": metadata,
                    "score": score
                })
        
        # Sort by score (descending)
        matches.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top k results
        return matches[:top_k]
