import os
import re
import logging
import hashlib
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import sqlite3
from datetime import datetime

# Document processing libraries
import PyPDF2
from docx import Document
import fitz  # PyMuPDF - better than PyPDF2 for complex PDFs
from bs4 import BeautifulSoup

# LangChain components
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document as LangChainDocument
from langchain.schema import Document as BaseDocument

# Embeddings and vector operations
from sentence_transformers import SentenceTransformer
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Advanced document processing pipeline for multiple file formats
    with intelligent chunking, metadata extraction, and caching.
    """

    def __init__(self,
                 cache_dir: str = "data/processed",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize the document processor with configuration options.

        Args:
            cache_dir: Directory for caching processed documents
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between consecutive chunks
            embedding_model: Sentence transformer model for embeddings
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize text splitter with optimal settings
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)

        # Supported file extensions
        self.supported_formats = {'.pdf', '.docx', '.txt', '.md', '.rtf'}

        # Initialize database for metadata
        self._init_metadata_db()

    def _init_metadata_db(self):
        """Initialize SQLite database for document metadata."""
        db_path = self.cache_dir / "metadata.db"
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_hash TEXT UNIQUE NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                processed_at TIMESTAMP,
                total_chunks INTEGER,
                total_chars INTEGER,
                language TEXT,
                summary TEXT
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                chunk_index INTEGER,
                chunk_text TEXT,
                chunk_length INTEGER,
                embedding_vector BLOB,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        self.conn.commit()

    def get_file_hash(self, file_content: bytes) -> str:
        """Generate SHA-256 hash for file content."""
        return hashlib.sha256(file_content).hexdigest()

    def is_document_cached(self, file_hash: str) -> bool:
        """Check if document is already processed and cached."""
        cursor = self.conn.execute(
            "SELECT id FROM documents WHERE file_hash = ?",
            (file_hash,)
        )
        return cursor.fetchone() is not None

    def extract_text_from_pdf(self, file_path: str) -> Tuple[str, Dict]:
        """
        Extract text from PDF using PyMuPDF for better accuracy.

        Args:
            file_path: Path to PDF file

        Returns:
            Tuple of (extracted_text, metadata)
        """
        try:
            doc = fitz.open(file_path)
            text_content = ""
            metadata = {
                'page_count': len(doc),
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'pages': []
            }

            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                text_content += f"\n--- Page {page_num + 1} ---\n{page_text}"

                # Store page-level metadata
                metadata['pages'].append({
                    'page_number': page_num + 1,
                    'char_count': len(page_text),
                    'word_count': len(page_text.split())
                })

            doc.close()
            logger.info(f"Successfully extracted text from PDF: {len(text_content)} characters")
            return text_content, metadata

        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            # Fallback to PyPDF2
            return self._extract_pdf_fallback(file_path)

    def _extract_pdf_fallback(self, file_path: str) -> Tuple[str, Dict]:
        """Fallback PDF extraction using PyPDF2."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""

                metadata = {
                    'page_count': len(pdf_reader.pages),
                    'title': pdf_reader.metadata.get('/Title', '') if pdf_reader.metadata else '',
                    'author': pdf_reader.metadata.get('/Author', '') if pdf_reader.metadata else '',
                    'pages': []
                }

                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text_content += f"\n--- Page {page_num + 1} ---\n{page_text}"

                    metadata['pages'].append({
                        'page_number': page_num + 1,
                        'char_count': len(page_text),
                        'word_count': len(page_text.split())
                    })

                return text_content, metadata

        except Exception as e:
            logger.error(f"Fallback PDF extraction failed: {str(e)}")
            return "", {}

    def extract_text_from_docx(self, file_path: str) -> Tuple[str, Dict]:
        """
        Extract text from DOCX file with structure preservation.

        Args:
            file_path: Path to DOCX file

        Returns:
            Tuple of (extracted_text, metadata)
        """
        try:
            doc = Document(file_path)
            text_content = ""

            # Extract paragraphs with structure
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_content += para.text + "\n\n"
                    paragraphs.append({
                        'text': para.text,
                        'style': para.style.name if para.style else 'Normal'
                    })

            # Extract tables
            tables_data = []
            for table in doc.tables:
                table_text = "\n--- TABLE ---\n"
                for row in table.rows:
                    row_text = " | ".join([cell.text for cell in row.cells])
                    table_text += row_text + "\n"
                text_content += table_text + "\n"
                tables_data.append(table_text)

            metadata = {
                'paragraph_count': len(paragraphs),
                'table_count': len(tables_data),
                'core_properties': {
                    'title': doc.core_properties.title or '',
                    'author': doc.core_properties.author or '',
                    'created': str(doc.core_properties.created) if doc.core_properties.created else '',
                    'modified': str(doc.core_properties.modified) if doc.core_properties.modified else ''
                }
            }

            logger.info(f"Successfully extracted text from DOCX: {len(text_content)} characters")
            return text_content, metadata

        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            return "", {}

    def extract_text_from_txt(self, file_path: str) -> Tuple[str, Dict]:
        """
        Extract text from TXT file with encoding detection.

        Args:
            file_path: Path to TXT file

        Returns:
            Tuple of (extracted_text, metadata)
        """
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']

            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        text_content = file.read()

                    metadata = {
                        'encoding': encoding,
                        'line_count': len(text_content.split('\n')),
                        'word_count': len(text_content.split()),
                        'char_count': len(text_content)
                    }

                    logger.info(f"Successfully extracted text from TXT: {len(text_content)} characters")
                    return text_content, metadata

                except UnicodeDecodeError:
                    continue

            logger.error("Could not decode text file with any standard encoding")
            return "", {}

        except Exception as e:
            logger.error(f"Error extracting TXT text: {str(e)}")
            return "", {}

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters while preserving structure
        text = re.sub(r'[^\w\s\-\.\,\!\?\:\;\(\)\[\]\{\}\"\'\/\\\@\#\$\%\^\&\*\+\=\<\>\~\`]', ' ', text)

        # Normalize line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    def create_intelligent_chunks(self, text: str, metadata: Dict) -> List[LangChainDocument]:
        """
        Create intelligent chunks with preserved context and metadata.

        Args:
            text: Clean text to chunk
            metadata: Document metadata

        Returns:
            List of LangChain Document objects
        """
        # Split text into chunks
        text_chunks = self.text_splitter.split_text(text)

        documents = []
        for i, chunk in enumerate(text_chunks):
            # Create enhanced metadata for each chunk
            chunk_metadata = {
                **metadata,
                'chunk_index': i,
                'chunk_length': len(chunk),
                'chunk_word_count': len(chunk.split()),
                'total_chunks': len(text_chunks)
            }

            # Create LangChain document
            doc = LangChainDocument(
                page_content=chunk,
                metadata=chunk_metadata
            )
            documents.append(doc)

        logger.info(f"Created {len(documents)} intelligent chunks")
        return documents

    def generate_embeddings(self, chunks: List[LangChainDocument]) -> np.ndarray:
        """
        Generate embeddings for document chunks.

        Args:
            chunks: List of document chunks

        Returns:
            NumPy array of embeddings
        """
        texts = [chunk.page_content for chunk in chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)

        logger.info(f"Generated embeddings for {len(chunks)} chunks")
        return embeddings

    def save_to_cache(self, file_hash: str, filename: str, file_size: int,
                      file_type: str, chunks: List[LangChainDocument],
                      embeddings: np.ndarray, metadata: Dict) -> int:
        """
        Save processed document and embeddings to cache.

        Args:
            file_hash: File hash identifier
            filename: Original filename
            file_size: File size in bytes
            file_type: File extension
            chunks: Processed document chunks
            embeddings: Generated embeddings
            metadata: Document metadata

        Returns:
            Document ID
        """
        # Insert document record
        cursor = self.conn.execute('''
            INSERT INTO documents (filename, file_hash, file_size, file_type, 
                                 processed_at, total_chunks, total_chars, language, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            filename,
            file_hash,
            file_size,
            file_type,
            datetime.now().isoformat(),
            len(chunks),
            sum(len(chunk.page_content) for chunk in chunks),
            metadata.get('language', 'unknown'),
            metadata.get('summary', '')
        ))

        document_id = cursor.lastrowid

        # Insert chunk records
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            self.conn.execute('''
                INSERT INTO chunks (document_id, chunk_index, chunk_text, 
                                  chunk_length, embedding_vector)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                document_id,
                i,
                chunk.page_content,
                len(chunk.page_content),
                embedding.tobytes()
            ))

        self.conn.commit()
        logger.info(f"Saved document to cache with ID: {document_id}")
        return document_id

    def process_document(self, file_path: str, filename: str = None) -> Dict:
        """
        Main method to process a document through the complete pipeline.

        Args:
            file_path: Path to the document file
            filename: Original filename (optional)

        Returns:
            Dictionary containing processing results
        """
        if filename is None:
            filename = os.path.basename(file_path)

        # Get file info
        file_size = os.path.getsize(file_path)
        file_ext = Path(file_path).suffix.lower()

        # Check if supported format
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")

        # Generate file hash
        with open(file_path, 'rb') as f:
            file_content = f.read()
        file_hash = self.get_file_hash(file_content)

        # Check cache
        if self.is_document_cached(file_hash):
            logger.info(f"Document already cached: {filename}")
            return {'status': 'cached', 'file_hash': file_hash}

        # Extract text based on file type
        if file_ext == '.pdf':
            text, metadata = self.extract_text_from_pdf(file_path)
        elif file_ext == '.docx':
            text, metadata = self.extract_text_from_docx(file_path)
        elif file_ext in ['.txt', '.md']:
            text, metadata = self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Extraction not implemented for: {file_ext}")

        if not text:
            raise ValueError("No text could be extracted from the document")

        # Clean text
        clean_text = self.clean_text(text)

        # Add file metadata
        metadata.update({
            'filename': filename,
            'file_size': file_size,
            'file_type': file_ext,
            'file_hash': file_hash,
            'original_char_count': len(text),
            'clean_char_count': len(clean_text)
        })

        # Create chunks
        chunks = self.create_intelligent_chunks(clean_text, metadata)

        # Generate embeddings
        embeddings = self.generate_embeddings(chunks)

        # Save to cache
        document_id = self.save_to_cache(
            file_hash, filename, file_size, file_ext,
            chunks, embeddings, metadata
        )

        return {
            'status': 'processed',
            'document_id': document_id,
            'file_hash': file_hash,
            'chunks_count': len(chunks),
            'metadata': metadata,
            'chunks': chunks,
            'embeddings': embeddings
        }

    def load_cached_document(self, file_hash: str) -> Dict:
        """
        Load a cached document by file hash.

        Args:
            file_hash: Hash of the cached document

        Returns:
            Dictionary containing cached document data
        """
        # Get document metadata
        cursor = self.conn.execute(
            "SELECT * FROM documents WHERE file_hash = ?",
            (file_hash,)
        )
        doc_row = cursor.fetchone()

        if not doc_row:
            raise ValueError("Document not found in cache")

        # Get chunks
        cursor = self.conn.execute(
            "SELECT chunk_text, embedding_vector FROM chunks WHERE document_id = ? ORDER BY chunk_index",
            (doc_row[0],)
        )
        chunk_rows = cursor.fetchall()

        # Reconstruct chunks and embeddings
        chunks = []
        embeddings = []

        for chunk_text, embedding_blob in chunk_rows:
            # Reconstruct LangChain document
            doc = LangChainDocument(
                page_content=chunk_text,
                metadata={'file_hash': file_hash}
            )
            chunks.append(doc)

            # Reconstruct embedding
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            embeddings.append(embedding)

        return {
            'status': 'loaded',
            'chunks': chunks,
            'embeddings': np.array(embeddings),
            'metadata': {
                'filename': doc_row[1],
                'file_hash': doc_row[2],
                'total_chunks': doc_row[6],
                'total_chars': doc_row[7]
            }
        }

    def get_processing_stats(self) -> Dict:
        """Get statistics about processed documents."""
        cursor = self.conn.execute('''
            SELECT 
                COUNT(*) as total_documents,
                SUM(total_chunks) as total_chunks,
                SUM(total_chars) as total_chars,
                AVG(total_chunks) as avg_chunks_per_doc
            FROM documents
        ''')

        stats = cursor.fetchone()
        return {
            'total_documents': stats[0],
            'total_chunks': stats[1],
            'total_characters': stats[2],
            'average_chunks_per_document': round(stats[3], 2) if stats[3] else 0
        }

    def cleanup_cache(self, days_old: int = 30):
        """Clean up cache entries older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days_old)

        # Get old document IDs
        cursor = self.conn.execute(
            "SELECT id FROM documents WHERE processed_at < ?",
            (cutoff_date.isoformat(),)
        )
        old_doc_ids = [row[0] for row in cursor.fetchall()]

        # Delete chunks first (foreign key constraint)
        for doc_id in old_doc_ids:
            self.conn.execute("DELETE FROM chunks WHERE document_id = ?", (doc_id,))

        # Delete documents
        self.conn.execute(
            "DELETE FROM documents WHERE processed_at < ?",
            (cutoff_date.isoformat(),)
        )

        self.conn.commit()
        logger.info(f"Cleaned up {len(old_doc_ids)} old documents from cache")
