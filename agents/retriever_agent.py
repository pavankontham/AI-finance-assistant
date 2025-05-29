"""
Retriever agent for RAG operations.
"""
import os
import logging
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import faiss

from agents.base_agent import BaseAgent
from data_ingestion.vector_store import VectorStore

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetrieverAgent(BaseAgent):
    """
    Agent for handling retrieval augmented generation operations.
    Uses FAISS for efficient vector storage and retrieval.
    """
    
    def __init__(self, agent_id: str = "retriever_agent", agent_name: str = "Retriever Agent",
                vector_store: Optional[VectorStore] = None):
        """
        Initialize the retriever agent.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_name: Human-readable name for the agent
            vector_store: VectorStore instance to use
        """
        super().__init__(agent_id, agent_name)
        
        # Initialize vector store
        self.vector_store = vector_store or VectorStore()
        
        # Initialize sentence transformer model for embeddings
        try:
            self.model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            self.model = None
            
        # Create default index if it doesn't exist
        self.ensure_default_index()
    
    def ensure_default_index(self):
        """Create default index if it doesn't exist."""
        try:
            if not self.vector_store.index_exists("default"):
                logger.info("Creating default vector index")
                self.vector_store.create_index("default")
                
                # Add some initial financial knowledge
                initial_docs = [
                    {
                        "text": "The S&P 500 is a stock market index tracking the stock performance of 500 large companies listed on stock exchanges in the United States.",
                        "metadata": {"source": "financial_knowledge", "category": "indices"}
                    },
                    {
                        "text": "Market capitalization refers to the total dollar market value of a company's outstanding shares of stock.",
                        "metadata": {"source": "financial_knowledge", "category": "terminology"}
                    },
                    {
                        "text": "The price-to-earnings ratio (P/E ratio) is the ratio of a company's share price to the company's earnings per share.",
                        "metadata": {"source": "financial_knowledge", "category": "metrics"}
                    },
                    {
                        "text": "Asia tech stocks include companies like TSMC, Samsung, Alibaba, and Sony, which are major technology players in the Asian market.",
                        "metadata": {"source": "financial_knowledge", "category": "sectors"}
                    }
                ]
                self.vector_store.add_documents("default", initial_docs)
        except Exception as e:
            logger.error(f"Error ensuring default index: {e}")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and perform retrieval operations.
        
        Args:
            input_data: Dictionary containing input parameters
                - action: Action to perform (e.g., 'search', 'add_documents')
                - parameters: Parameters for the action
            
        Returns:
            Dictionary containing operation results
        """
        action = input_data.get('action', '')
        parameters = input_data.get('parameters', {})
        
        logger.info(f"Processing {action} with parameters: {parameters}")
        
        result = {}
        
        try:
            if action == 'search':
                index_name = parameters.get('index_name', 'default')
                query = parameters.get('query', '')
                k = parameters.get('k', 5)
                
                if not query:
                    return {"error": "Query parameter is required"}
                
                search_results = self.vector_store.search(index_name, query, k)
                result = {"results": search_results}
            
            elif action == 'add_documents':
                index_name = parameters.get('index_name', 'default')
                documents = parameters.get('documents', [])
                
                if not documents:
                    return {"error": "Documents parameter is required"}
                
                doc_ids = self.vector_store.add_documents(index_name, documents)
                result = {"count": len(doc_ids), "doc_ids": doc_ids}
            
            elif action == 'delete_documents':
                index_name = parameters.get('index_name', 'default')
                doc_ids = parameters.get('doc_ids', [])
                
                if not doc_ids:
                    return {"error": "Document IDs parameter is required"}
                
                success = self.vector_store.delete_documents(index_name, doc_ids)
                result = {"success": success, "count": len(doc_ids)}
            
            elif action == 'create_index':
                index_name = parameters.get('index_name', '')
                
                if not index_name:
                    return {"error": "Index name parameter is required"}
                
                success = self.vector_store.create_index(index_name)
                result = {"success": success, "index_name": index_name}
            
            elif action == 'retrieve_and_generate':
                # This is a more complex action that combines retrieval and generation
                index_name = parameters.get('index_name', 'default')
                query = parameters.get('query', '')
                k = parameters.get('k', 5)
                prompt_template = parameters.get('prompt_template', '')
                
                if not query:
                    return {"error": "Query parameter is required"}
                
                if not prompt_template:
                    return {"error": "Prompt template parameter is required"}
                
                # Search for relevant documents
                search_results = self.vector_store.search(index_name, query, k)
                
                # Extract text from search results
                contexts = [result['text'] for result in search_results]
                
                # Format prompt with contexts
                formatted_prompt = prompt_template.replace('{contexts}', '\n\n'.join(contexts))
                formatted_prompt = formatted_prompt.replace('{query}', query)
                
                result = {
                    "search_results": search_results,
                    "prompt": formatted_prompt
                }
            
            else:
                result = {"error": f"Unknown action: {action}"}
        
        except Exception as e:
            logger.error(f"Error processing {action}: {e}")
            result = {"error": str(e)}
        
        return result
    
    def retrieve_information(self, query: str, k: int = 5) -> Dict[str, Any]:
        """
        Retrieve relevant information for a query.
        This is the main method called by the orchestrator.
        
        Args:
            query: The user's query
            k: Number of results to return
            
        Returns:
            Dictionary with retrieved information
        """
        try:
            logger.info(f"Retrieving information for query: {query}")
            
            # Search for relevant information in the vector store
            search_results = self.vector_store.search("default", query, k)
            
            # Extract relevant information
            information = []
            for result in search_results:
                information.append({
                    "text": result["text"],
                    "relevance": result["score"],
                    "source": result.get("metadata", {}).get("source", "unknown"),
                    "category": result.get("metadata", {}).get("category", "general")
                })
            
            return {
                "success": True,
                "information": information,
                "count": len(information)
            }
        except Exception as e:
            logger.error(f"Error retrieving information: {e}")
            return {
                "success": False,
                "information": [],
                "count": 0,
                "error": str(e)
            }
    
    async def search_knowledge(self, query: str, index_name: str = 'default', k: int = 5) -> List[Dict[str, Any]]:
        """
        Search knowledge base for relevant information.
        
        Args:
            query: Search query
            index_name: Name of the index to search
            k: Number of results to return
            
        Returns:
            List of relevant document dictionaries
        """
        try:
            return self.vector_store.search(index_name, query, k)
        
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return []
    
    async def add_to_knowledge(self, documents: List[Dict[str, Any]], index_name: str = 'default') -> List[int]:
        """
        Add documents to knowledge base.
        
        Args:
            documents: List of document dictionaries with text and metadata
            index_name: Name of the index to add to
            
        Returns:
            List of document IDs
        """
        try:
            return self.vector_store.add_documents(index_name, documents)
        
        except Exception as e:
            logger.error(f"Error adding to knowledge: {e}")
            return []
            
    def update_knowledge_from_sources(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update knowledge base with new information from various sources.
        
        Args:
            sources: List of dictionaries containing source information
            
        Returns:
            Dictionary with update results
        """
        try:
            documents = []
            for source in sources:
                source_type = source.get("type", "")
                content = source.get("content", "")
                metadata = source.get("metadata", {})
                
                if source_type and content:
                    # Add source type to metadata
                    metadata["source_type"] = source_type
                    metadata["timestamp"] = datetime.now().isoformat()
                    
                    # Create document
                    document = {
                        "text": content,
                        "metadata": metadata
                    }
                    
                    documents.append(document)
            
            # Add documents to knowledge base
            if documents:
                doc_ids = self.vector_store.add_documents("default", documents)
                return {
                    "success": True,
                    "count": len(doc_ids),
                    "doc_ids": doc_ids
                }
            else:
                return {
                    "success": False,
                    "count": 0,
                    "error": "No valid documents to add"
                }
        
        except Exception as e:
            logger.error(f"Error updating knowledge: {e}")
            return {
                "success": False,
                "error": str(e)
            } 