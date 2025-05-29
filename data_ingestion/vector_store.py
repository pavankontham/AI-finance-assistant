"""
Module for managing vector embeddings and retrieval.
"""
import os
import logging
import json
import pickle
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import hashlib
import faiss
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """
    Class for managing vector embeddings and retrieval using FAISS and sentence-transformers.
    """
    
    def __init__(self, vector_db_path: Optional[str] = None):
        """
        Initialize the VectorStore with storage path.
        
        Args:
            vector_db_path: Path to store vector database files
        """
        # Get configuration from environment or use defaults
        self.vector_db_path = vector_db_path or os.getenv("VECTOR_DB_PATH", "./vector_db")
        
        # Create directory if it doesn't exist
        os.makedirs(self.vector_db_path, exist_ok=True)
        
        # Initialize embedding model
        try:
            model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Initialized embedding model {model_name} with dimension {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Error initializing embedding model: {e}")
            self.model = None
            self.embedding_dim = 384  # Default dimension for all-MiniLM-L6-v2
        
        # Initialize indexes
        self.indexes = {}
        self.document_maps = {}
        self.load_indexes()
    
    def load_indexes(self):
        """
        Load existing indexes from disk.
        """
        try:
            # Check for index metadata file
            metadata_path = os.path.join(self.vector_db_path, "index_metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                # Load each index mentioned in metadata
                for index_name, index_info in metadata.items():
                    index_path = os.path.join(self.vector_db_path, f"{index_name}.faiss")
                    if os.path.exists(index_path):
                        try:
                            # Load FAISS index
                            self.indexes[index_name] = faiss.read_index(index_path)
                            logger.info(f"Loaded FAISS index: {index_name}")
                            
                            # Load document map
                            doc_map_path = os.path.join(self.vector_db_path, f"{index_name}_docmap.json")
                            if os.path.exists(doc_map_path):
                                with open(doc_map_path, 'r') as f:
                                    self.document_maps[index_name] = json.load(f)
                        except Exception as e:
                            logger.error(f"Error loading index {index_name}: {e}")
        except Exception as e:
            logger.error(f"Error loading indexes: {e}")
    
    def save_indexes(self):
        """
        Save indexes to disk.
        """
        try:
            # Create metadata with information about each index
            metadata = {}
            for index_name, index in self.indexes.items():
                metadata[index_name] = {
                    "count": index.ntotal,
                    "dimension": index.d,
                    "updated_at": datetime.now().isoformat()
                }
                
                # Save the FAISS index
                index_path = os.path.join(self.vector_db_path, f"{index_name}.faiss")
                faiss.write_index(index, index_path)
                
                # Save document map
                if index_name in self.document_maps:
                    doc_map_path = os.path.join(self.vector_db_path, f"{index_name}_docmap.json")
                    with open(doc_map_path, 'w') as f:
                        json.dump(self.document_maps[index_name], f)
            
            # Save metadata
            metadata_path = os.path.join(self.vector_db_path, "index_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
                
            logger.info(f"Saved {len(self.indexes)} indexes to {self.vector_db_path}")
        except Exception as e:
            logger.error(f"Error saving indexes: {e}")
    
    def index_exists(self, index_name: str) -> bool:
        """
        Check if an index exists.
        
        Args:
            index_name: Name of the index to check
            
        Returns:
            True if the index exists, False otherwise
        """
        return index_name in self.indexes
    
    def create_index(self, index_name: str) -> bool:
        """
        Create a new index.
        
        Args:
            index_name: Name of the index to create
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a new FAISS index
            dimension = self.embedding_dim
            index = faiss.IndexFlatL2(dimension)  # L2 distance
            
            # Create a new document map
            self.indexes[index_name] = index
            self.document_maps[index_name] = {}
            
            logger.info(f"Created new FAISS index: {index_name} with dimension {dimension}")
            return True
        except Exception as e:
            logger.error(f"Error creating index {index_name}: {e}")
            return False
    
    def add_documents(self, index_name: str, documents: List[Dict[str, Any]]) -> List[int]:
        """
        Add documents to an index.
        
        Args:
            index_name: Name of the index
            documents: List of document dictionaries with 'text' and 'metadata' fields
            
        Returns:
            List of document IDs
        """
        if not self.model:
            logger.error("Embedding model not available")
            return []
            
        if index_name not in self.indexes:
            if not self.create_index(index_name):
                return []
        
        try:
            # Extract text for embedding
            texts = [doc['text'] for doc in documents]
            
            # Generate embeddings
            embeddings = self.model.encode(texts)
            
            # Convert to float32 for FAISS
            embeddings = np.array(embeddings).astype('float32')
            
            # Get next document ID
            next_id = len(self.document_maps[index_name])
            
            # Add to FAISS index
            index = self.indexes[index_name]
            index.add(embeddings)
            
            # Update document map
            doc_ids = []
            for i, doc in enumerate(documents):
                doc_id = next_id + i
                self.document_maps[index_name][str(doc_id)] = {
                    'text': doc['text'],
                    'metadata': doc.get('metadata', {})
                }
                doc_ids.append(doc_id)
            
            logger.info(f"Added {len(documents)} documents to index {index_name}")
            
            # Save updated indexes
            self.save_indexes()
            
            return doc_ids
        except Exception as e:
            logger.error(f"Error adding documents to index {index_name}: {e}")
            return []
    
    def search(self, index_name: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents in an index.
        
        Args:
            index_name: Name of the index
            query: Query text
            k: Number of results to return
            
        Returns:
            List of document dictionaries with text, metadata, and score
        """
        if not self.model:
            logger.error("Embedding model not available")
            return []
            
        if index_name not in self.indexes:
            logger.error(f"Index {index_name} not found")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])[0].astype('float32')
            query_embedding = np.array([query_embedding])
            
            # Search the index
            index = self.indexes[index_name]
            distances, indices = index.search(query_embedding, k)
            
            # Convert to list of dictionaries
            results = []
            for i, idx in enumerate(indices[0]):
                if idx != -1:  # FAISS returns -1 for empty slots
                    doc_data = self.document_maps[index_name].get(str(idx), {})
                    if doc_data:
                        # Convert distance to similarity score (1 - normalized distance)
                        distance = distances[0][i]
                        max_distance = 100.0  # Arbitrary large value for normalization
                        similarity = 1.0 - min(distance / max_distance, 1.0)
                        
                        results.append({
                            'text': doc_data.get('text', ''),
                            'metadata': doc_data.get('metadata', {}),
                            'score': float(similarity),
                            'id': int(idx)
                        })
            
            return results
        except Exception as e:
            logger.error(f"Error searching index {index_name}: {e}")
            return []
    
    def delete_documents(self, index_name: str, doc_ids: List[int]) -> bool:
        """
        Delete documents from an index.
        
        Args:
            index_name: Name of the index
            doc_ids: List of document IDs to delete
            
        Returns:
            True if successful, False otherwise
        """
        if index_name not in self.indexes:
            logger.error(f"Index {index_name} not found")
            return False
        
        try:
            # FAISS doesn't support direct deletion, so we need to rebuild the index
            # First, collect all documents except the ones to delete
            doc_map = self.document_maps[index_name]
            remaining_docs = []
            
            for doc_id_str, doc_data in doc_map.items():
                if int(doc_id_str) not in doc_ids:
                    remaining_docs.append({
                        'text': doc_data['text'],
                        'metadata': doc_data.get('metadata', {})
                    })
            
            # Create a new index with the same name
            self.indexes.pop(index_name)
            self.document_maps.pop(index_name)
            self.create_index(index_name)
            
            # Add remaining documents back
            if remaining_docs:
                self.add_documents(index_name, remaining_docs)
            
            logger.info(f"Deleted {len(doc_ids)} documents from index {index_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents from index {index_name}: {e}")
            return False 