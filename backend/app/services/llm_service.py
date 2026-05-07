"""LLM Service — Groq API integration for AI extraction and generation."""

import json
import logging
from typing import Optional
import httpx
from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Groq client
_client: Optional[Groq] = None


def get_groq_client() -> Optional[Groq]:
    """Get or create the Groq client."""
    global _client
    if _client is None and settings.GROQ_API_KEY:
        try:
            # Create explicit httpx client without proxies to avoid initialization errors
            http_client = httpx.Client(
                timeout=30.0,
            )
            _client = Groq(api_key=settings.GROQ_API_KEY, http_client=http_client)
        except Exception as e:
            # Fallback: try simple initialization
            logger.warning(f"Failed to create Groq client with httpx: {e}, trying simple init")
            _client = Groq(api_key=settings.GROQ_API_KEY)
    return _client


def call_llm(prompt: str, system_prompt: str = "", temperature: float = 0.1, max_tokens: int = 4096) -> str:
    """
    Call the Groq LLM API.

    Args:
        prompt: User prompt
        system_prompt: System instructions
        temperature: Creativity level (0-1)
        max_tokens: Maximum response length

    Returns:
        LLM response text
    """
    client = get_groq_client()
    if client is None:
        logger.warning("Groq client not available, returning demo data")
        return ""

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq API call failed: {e}")
        raise


def call_llm_text(prompt: str, system_prompt: str = "", temperature: float = 0.3) -> str:
    """Call LLM and return plain text (no JSON mode)."""
    client = get_groq_client()
    if client is None:
        return ""

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=2048,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq API call failed: {e}")
        raise


def parse_llm_json(response: str) -> dict:
    """Parse JSON from LLM response, handling potential formatting issues."""
    if not response:
        return {}

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find JSON object in text
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

    logger.warning(f"Failed to parse LLM JSON response: {response[:200]}")
    return {}

def chunk_text(text: str, max_chars: int = 12000) -> list[str]:
    """Simple character/word-based text chunker."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) > max_chars:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1 # +1 for space
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks
