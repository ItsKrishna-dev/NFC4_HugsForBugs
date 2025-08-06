"""
Basic Chat Interface - Simple and stable implementation
"""

import streamlit as st
from typing import Dict, Any
from datetime import datetime

class BasicChatInterface:
    """Simple chat interface for basic RAG engine"""
    
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
        
        # Initialize session state for chat
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
    
    def render_chat_interface(self):
        """Render the basic chat interface"""
        st.header("💬 Document Q&A")
        
        # Chat messages display
        for message in st.session_state.chat_messages:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            else:
                st.chat_message("assistant").write(message["content"])
                
                # Show sources if available
                if message.get("sources"):
                    with st.expander("📚 Sources"):
                        for source in message["sources"]:
                            st.markdown(f"**{source['source']}**")
                            st.markdown(f"_{source['content']}_")
        
        # Chat input
        if prompt := st.chat_input("Ask a question about your documents..."):
            # Add user message
            st.chat_message("user").write(prompt)
            st.session_state.chat_messages.append({
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now()
            })
            
            # Get response from RAG engine
            with st.spinner("Thinking..."):
                response = self.rag_engine.ask(prompt)
                
                # Add assistant message
                st.chat_message("assistant").write(response.answer)
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": response.answer,
                    "sources": response.sources,
                    "timestamp": datetime.now()
                })
                
                # Show sources
                if response.sources:
                    with st.expander("📚 Sources"):
                        for source in response.sources:
                            st.markdown(f"**{source['source']}**")
                            st.markdown(f"_{source['content']}_")
    
    def clear_chat(self):
        """Clear chat history"""
        st.session_state.chat_messages = []
    
    def get_chat_stats(self) -> Dict[str, Any]:
        """Get chat statistics"""
        return {
            "total_messages": len(st.session_state.chat_messages),
            "user_messages": len([m for m in st.session_state.chat_messages if m["role"] == "user"]),
            "assistant_messages": len([m for m in st.session_state.chat_messages if m["role"] == "assistant"])
        } 