"""
core/summarizer.py -- Corrected Gemini API version
"""

import os
import logging
import re
from typing import List, Dict
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ------------------------------------------------------------------ #
# 1. Corrected Gemini API Helper                                    #
# ------------------------------------------------------------------ #

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    "Your_API_KEY_HERE"
)

def _gemini_complete(prompt: str,
                     model: str = "gemini-1.5-flash",
                     max_tokens: int = 150) -> str:
    """
    Corrected Gemini API call using generateContent endpoint.
    """
    # CORRECTED: Use generateContent instead of generateText
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    
    # CORRECTED: Use proper payload format
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.2
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        # CORRECTED: Extract text from proper response structure
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            parts = data["candidates"][0]["content"]["parts"]
            if len(parts) > 0:
                return parts[0]["text"].strip()
        return ""
        
    except Exception as e:
        logging.error("Gemini API call failed: %s", e)
        return ""

# ------------------------------------------------------------------ #
# 2. Summarizer class (same public API as before)                   #
# ------------------------------------------------------------------ #

class Summarizer:
    def __init__(self,
                 model: str = "gemini-1.5-flash",
                 chunk_size: int = 2_000,
                 chunk_overlap: int = 200):
        self.model = model
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        logging.info("Summarizer initialized - model: %s", model)

    def summarize(self,
                  text: str,
                  max_len: int = 150,
                  min_len: int = 40) -> str:
        """
        Quick single-string summary (behaves like the old method).
        """
        if not text or not text.strip():
            return ""

        chunks = self.splitter.split_text(text)
        summaries: List[str] = []

        for idx, chunk in enumerate(chunks):
            prompt = (
                "You are a helpful assistant. Summarize the following passage "
                f"in {min_len}-{max_len} words, keeping all key facts:\n\n{chunk}"
            )
            summary = _gemini_complete(prompt, self.model, max_tokens=max_len)
            if summary:
                summaries.append(summary)
            else:
                # Fallback: first sentence
                first_sentence = chunk.split(".")[0] + "."
                summaries.append(first_sentence)
            logging.debug("Chunk %s summarized (%s chars)", idx, len(chunk))

        return " ".join(summaries).replace("  ", " ").strip()

    def summarize_with_sections(self,
                                text: str,
                                max_len: int = 150,
                                min_len: int = 40) -> Dict:
        """
        Section-aware summarization (same output structure as before).
        """
        if not text or not text.strip():
            return {"overall_summary": "", "sections": [], "total_sections": 0}

        # Detect sections
        sections = self._detect_sections(text)
        
        # Overall summary
        overall_prompt = (
            "Provide an executive summary of the following document "
            f"in {min_len}-{max_len} words:\n\n{text}"
        )
        overall_summary = _gemini_complete(overall_prompt,
                                           self.model,
                                           max_tokens=max_len)

        # Per-section summaries
        section_summaries = []
        for title, body in sections:
            if not body.strip():
                continue
            prompt = (
                f"Summarize the section titled '{title}' "
                f"in {min_len}-{max_len} words:\n\n{body}"
            )
            summ = _gemini_complete(prompt, self.model, max_tokens=max_len)
            section_summaries.append({
                "title": title,
                "content": body.strip()[:600] + ("…" if len(body) > 600 else ""),
                "summary": summ,
                "word_count": len(body.split()),
                "char_count": len(body)
            })

        return {
            "overall_summary": overall_summary,
            "sections": section_summaries,
            "total_sections": len(section_summaries)
        }

    @staticmethod
    def _detect_sections(text: str) -> List[tuple]:
        """
        Enhanced header detector for sections.
        """
        lines = text.split("\n")
        sections = []
        current_section = None
        current_content = []
        
        # Common section headers to look for
        common_headers = [
            "introduction", "abstract", "executive summary", "overview",
            "background", "literature review", "methodology", "methods",
            "results", "findings", "discussion", "analysis", "conclusion",
            "recommendations", "implications", "future work", "references",
            "bibliography", "appendix", "acknowledgments", "summary",
            "challenges", "opportunities", "impact", "benefits", "risks",
            "implementation", "strategy", "approach", "framework", "model",
            "case study", "examples", "applications", "limitations"
        ]
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check if this line looks like a section header
            is_header = False
            header_title = None
            
            if line_stripped:
                # Check for common headers (case-insensitive)
                line_lower = line_stripped.lower()
                for header in common_headers:
                    if header in line_lower and len(line_stripped) < 100:
                        is_header = True
                        header_title = line_stripped
                        break
                
                # Check for numbered sections (e.g., "1. Introduction", "2. Methods")
                if not is_header and re.match(r'^\d+[\.\)]\s+[A-Za-z]', line_stripped):
                    is_header = True
                    header_title = line_stripped
                
                # Check for any numbered sections (more flexible)
                if not is_header and re.match(r'^\d+[\.\)]\s+', line_stripped):
                    is_header = True
                    header_title = line_stripped
                
                # Check for roman numeral sections (e.g., "I. Introduction", "II. Methods")
                if not is_header and re.match(r'^[IVX]+\.\s+[A-Z]', line_stripped):
                    is_header = True
                    header_title = line_stripped
                
                # Check for all-caps headers (e.g., "INTRODUCTION", "METHODS")
                if not is_header and (line_stripped.isupper() and len(line_stripped) < 50):
                    is_header = True
                    header_title = line_stripped
                
                # Check for title-case headers that don't end with punctuation
                if not is_header and (len(line_stripped) > 0 and len(line_stripped) < 80 and 
                                    line_stripped[0].isupper() and 
                                    not line_stripped.endswith(('.', ':', ';')) and
                                    not line_stripped.isdigit()):
                    # Additional check: should have mostly title case
                    words = line_stripped.split()
                    if len(words) <= 5:  # Short enough to be a header
                        title_case_count = sum(1 for word in words if word[0].isupper())
                        if title_case_count >= len(words) * 0.7:  # 70% title case
                            is_header = True
                            header_title = line_stripped
            
            if is_header and header_title:
                # Save previous section if it has content
                if current_section and current_content:
                    content_text = "\n".join(current_content).strip()
                    if content_text:
                        sections.append((current_section, content_text))
                
                # Start new section
                current_section = header_title
                current_content = []
            else:
                # Add line to current section content
                current_content.append(line)
        
        # Add the last section if it has content
        if current_section and current_content:
            content_text = "\n".join(current_content).strip()
            if content_text:
                sections.append((current_section, content_text))
        
        # If no sections found, treat the whole document as one section
        if not sections:
            return [("Document", text)]
        
        return sections
