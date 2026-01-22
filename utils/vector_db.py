"""
Vector database operations for duplicate detection and RAG
"""
import os
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
from config import Config


class VectorDatabase:
    """Vector database for storing and retrieving interview preparation data"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Config.VECTOR_DB_PATH
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="interview_prep",
            metadata={"description": "Interview preparation questions and responses"}
        )
    
    def add_interview_prep(
        self,
        domain: str,
        difficulty: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """Add interview preparation content to vector database"""
        # Create document ID
        import hashlib
        doc_id = hashlib.md5(f"{domain}_{difficulty}_{content[:100]}".encode()).hexdigest()
        
        # Prepare metadata
        doc_metadata = {
            "domain": domain,
            "difficulty": difficulty,
            **(metadata or {})
        }
        
        # Add to collection
        self.collection.add(
            documents=[content],
            ids=[doc_id],
            metadatas=[doc_metadata]
        )
        
        return doc_id
    
    def search_similar(
        self,
        query: str,
        n_results: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """Search for similar interview preparation content"""
        # Convert filter_dict to ChromaDB where clause format
        where_clause = None
        if filter_dict:
            # ChromaDB requires $and operator for multiple filters
            conditions = []
            for key, value in filter_dict.items():
                conditions.append({key: {"$eq": value}})
            if len(conditions) == 1:
                where_clause = conditions[0]
            elif len(conditions) > 1:
                where_clause = {"$and": conditions}
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def check_duplicate(
        self,
        domain: str,
        difficulty: str,
        content: str,
        similarity_threshold: float = 0.8
    ) -> Tuple[bool, Optional[Dict]]:
        """Check if similar content already exists"""
        # Search for similar content
        similar = self.search_similar(
            query=content,
            n_results=1,
            filter_dict={"domain": domain, "difficulty": difficulty}
        )
        
        if similar and similar[0].get("distance"):
            # ChromaDB uses cosine distance, lower is more similar
            # Convert to similarity score (1 - distance)
            similarity = 1 - similar[0]["distance"]
            if similarity >= similarity_threshold:
                return True, similar[0]
        
        return False, None
    
    def get_context_for_rag(
        self,
        job_description: str,
        domain: str,
        n_results: int = 3
    ) -> str:
        """Get relevant context for RAG based on job description"""
        results = self.search_similar(
            query=job_description,
            n_results=n_results,
            filter_dict={"domain": domain}
        )
        
        if not results:
            return ""
        
        # Combine results into context
        context_parts = [result["content"] for result in results]
        return "\n\n---\n\n".join(context_parts)
    
    def clear_collection(self):
        """Clear all documents from collection"""
        # Delete collection and recreate
        self.client.delete_collection(name="interview_prep")
        self.collection = self.client.get_or_create_collection(
            name="interview_prep",
            metadata={"description": "Interview preparation questions and responses"}
        )
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        count = self.collection.count()
        return {
            "total_documents": count,
            "collection_name": "interview_prep"
        }
