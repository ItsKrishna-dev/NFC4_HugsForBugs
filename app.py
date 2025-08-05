import streamlit as st
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.file_handlers import save_upload
from core.document_processor import DocumentProcessor
from core.summarizer import Summarizer
from core.rag_engine import RAGEngine
from utils.database import init_database

# Initialize database
init_database()

st.set_page_config(
    page_title="📄 AI Document Summarizer & Q&A",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if "documents_processed" not in st.session_state:
    st.session_state.documents_processed = False
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = None
if "processed_texts" not in st.session_state:
    st.session_state.processed_texts = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# Initialize processors
@st.cache_resource
def load_processors():
    processor = DocumentProcessor()
    summarizer = Summarizer()
    return processor, summarizer


try:
    processor, summarizer = load_processors()
except Exception as e:
    st.error(f"Error loading processors: {e}")
    st.stop()

# Main title
st.title("🤖 AI Document Summarizer & Q&A Assistant")
st.markdown("Upload documents and get intelligent summaries with contextual Q&A capabilities")

# Sidebar for file upload
with st.sidebar:
    st.header("📤 Upload Documents")

    uploaded_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'docx', 'txt', 'md', 'rtf'],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, TXT, MD, RTF"
    )

    if uploaded_files:
        st.write(f"Selected {len(uploaded_files)} file(s)")

        if st.button("🔄 Process Documents", type="primary"):
            with st.spinner("Processing documents..."):
                try:
                    processed_data = {}
                    all_chunks = []
                    metadatas = []

                    for file in uploaded_files:
                        # Save uploaded file
                        file_path = save_upload(file)

                        # Process document
                        result = processor.process(file_path)

                        if result["status"] == "processed":
                            # Get processed chunks from database
                            with processor.conn as conn:
                                cursor = conn.execute(
                                    "SELECT chunk_text FROM chunks WHERE document_id=? ORDER BY chunk_index",
                                    (result["doc_id"],)
                                )
                                chunks = [row[0] for row in cursor.fetchall()]

                            processed_data[file.name] = {
                                "text": "\n".join(chunks),
                                "chunks": chunks,
                                "result": result
                            }

                            # Collect for RAG
                            all_chunks.extend(chunks)
                            metadatas.extend([{"source": file.name}] * len(chunks))

                    # Build RAG engine
                    if all_chunks:
                        rag = RAGEngine()
                        rag.build_vector_store(all_chunks, metadatas)
                        rag.build_chain()

                        st.session_state.rag_engine = rag
                        st.session_state.processed_texts = processed_data
                        st.session_state.documents_processed = True

                        st.success(f"✅ Successfully processed {len(uploaded_files)} documents!")

                except Exception as e:
                    st.error(f"❌ Error processing documents: {str(e)}")

    # Display processing stats
    if st.session_state.documents_processed:
        st.subheader("📊 Processing Stats")
        stats = processor.get_processing_stats()
        st.metric("Total Documents", stats["total_documents"])
        st.metric("Total Chunks", stats["total_chunks"])
        st.metric("Total Characters", f"{stats['total_characters']:,}")

# Main content area
if not st.session_state.documents_processed:
    st.info("👆 Please upload and process documents using the sidebar to get started.")
else:
    tab1, tab2, tab3 = st.tabs(["📋 Document Summary", "💬 Q&A Chat", "📊 Document Analysis"])

    with tab1:
        st.header("📋 Document Summaries")

        for filename, data in st.session_state.processed_texts.items():
            with st.expander(f"📄 {filename}", expanded=True):
                st.subheader("Summary")
                try:
                    summary = summarizer.summarize(data["text"])
                    st.write(summary)
                except Exception as e:
                    st.error(f"Error generating summary: {e}")

                st.subheader("Document Stats")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Characters", len(data["text"]))
                with col2:
                    st.metric("Words", len(data["text"].split()))
                with col3:
                    st.metric("Chunks", len(data["chunks"]))

    with tab2:
        st.header("💬 Ask Questions")

        # Chat interface
        query = st.text_input(
            "Ask a question about your documents:",
            placeholder="e.g., What are the main points discussed in the documents?"
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            ask_button = st.button("🔍 Ask", type="primary")
        with col2:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()

        if ask_button and query and st.session_state.rag_engine:
            with st.spinner("Searching for answer..."):
                try:
                    response = st.session_state.rag_engine.ask(query)

                    # Add to chat history
                    st.session_state.chat_history.append({
                        "question": query,
                        "answer": response["result"]
                    })

                except Exception as e:
                    st.error(f"Error processing question: {e}")

        # Display chat history
        if st.session_state.chat_history:
            st.subheader("💬 Chat History")
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                with st.container():
                    st.markdown(f"**Q{len(st.session_state.chat_history) - i}:** {chat['question']}")
                    st.markdown(f"**A:** {chat['answer']}")
                    st.divider()

    with tab3:
        st.header("📊 Document Analysis")

        if st.session_state.processed_texts:
            # Document comparison
            st.subheader("Document Comparison")

            docs_data = []
            for filename, data in st.session_state.processed_texts.items():
                docs_data.append({
                    "Document": filename,
                    "Characters": len(data["text"]),
                    "Words": len(data["text"].split()),
                    "Chunks": len(data["chunks"])
                })

            import pandas as pd

            df = pd.DataFrame(docs_data)
            st.dataframe(df, use_container_width=True)

            # Overall stats
            st.subheader("Overall Statistics")
            total_chars = sum(len(data["text"]) for data in st.session_state.processed_texts.values())
            total_words = sum(len(data["text"].split()) for data in st.session_state.processed_texts.values())
            total_chunks = sum(len(data["chunks"]) for data in st.session_state.processed_texts.values())

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Characters", f"{total_chars:,}")
            with col2:
                st.metric("Total Words", f"{total_words:,}")
            with col3:
                st.metric("Total Chunks", total_chunks)

# Footer
st.markdown("---")
st.markdown("🚀 **AI Document Summarizer** - Built with Streamlit, LangChain, and Hugging Face")
