"""
Basic RAG Engine - Simple and stable implementation
"""

import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFacePipeline
from transformers import pipeline
from langchain.prompts import PromptTemplate

@dataclass
class BasicRAGResponse:
    """Simple RAG response"""
    answer: str
    sources: List[Dict[str, Any]]
    timestamp: datetime

class BasicRAGEngine:
    """
    Basic RAG Engine - Simple and stable implementation
    """
    
    def __init__(self, embed_model: str = "all-MiniLM-L6-v2"):
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embed_model,
            model_kwargs={'device': 'cpu'}
        )
        
        # Vector store and chain
        self.vector_store = None
        self.chain = None
        
        # Simple stats
        self.total_queries = 0

    def build_vector_store(self, chunks: List[str], metadatas: List[Dict[str, Any]]):
        """Build vector store"""
        self.vector_store = Chroma.from_texts(
            texts=chunks,
            embedding=self.embeddings,
            metadatas=metadatas
        )
        logging.info(f"Vector store built with {len(chunks)} chunks")

    def build_chain(self):
        """Build basic QA chain"""
        try:
            # Simple pipeline
            llm = HuggingFacePipeline(
                pipeline=pipeline(
                    "text2text-generation", 
                    model="google/flan-t5-base", 
                    max_length=512,
                    device=-1,  # CPU only
                    do_sample=True,
                    temperature=0.3
                )
            )
            
            # Simple retriever
            retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 4}
            )
            
            # Simple prompt
            prompt_template = PromptTemplate(
                template="""Answer the question based on the context.

Context: {context}

Question: {question}

Answer:""",
                input_variables=["context", "question"]
            )
            
            self.chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={
                    "prompt": prompt_template
                }
            )
            
            logging.info("Basic QA chain built successfully")
            
        except Exception as e:
            logging.error(f"Failed to build chain: {e}")
            raise

    def ask(self, query: str) -> BasicRAGResponse:
        """Simple ask method"""
        try:
            self.total_queries += 1
            
            # Get answer from chain
            chain_response = self.chain({"query": query})
            answer = chain_response.get("result", "I couldn't find a relevant answer.")
            
            # Get sources
            sources = []
            source_documents = chain_response.get("source_documents", [])
            if source_documents:
                for i, doc in enumerate(source_documents[:3]):
                    source_info = doc.metadata.get('source', 'Unknown document')
                    sources.append({
                        "source": source_info,
                        "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                        "index": i + 1
                    })
            
            return BasicRAGResponse(
                answer=answer,
                sources=sources,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logging.error(f"Error in basic ask: {e}")
            return BasicRAGResponse(
                answer=f"Sorry, I encountered an error: {str(e)}",
                sources=[],
                timestamp=datetime.now()
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get basic stats"""
        return {
            "total_queries": self.total_queries,
            "vector_store_size": len(self.vector_store.get()["documents"]) if self.vector_store else 0
        }

    @staticmethod
    def free_gpu_memory():
        """Free GPU memory (no-op for CPU-only)"""
        pass 