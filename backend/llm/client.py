"""Hugging Face LLM client for text generation."""

import os
import json
import re
from typing import Optional, Dict, Any, List
from huggingface_hub import InferenceClient


class LLMClient:
    """
    Client for interacting with Hugging Face Inference API.
    
    Uses free Mistral-7B-Instruct model by default.
    """
    
    DEFAULT_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
    
    def __init__(self, model: Optional[str] = None):
        """
        Initialize LLM client.
        
        Args:
            model: Hugging Face model ID (defaults to Mistral-7B)
        """
        self.model = model or self.DEFAULT_MODEL
        self.token = os.getenv("HF_TOKEN")
        
        if self.token:
            self.client = InferenceClient(token=self.token)
        else:
            self.client = InferenceClient()
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.1
    ) -> str:
        """
        Generate text response from the LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (lower = more deterministic)
            
        Returns:
            Generated text response
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat_completion(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Log error and return empty for graceful degradation
            print(f"LLM generation error: {e}")
            return ""
    
    async def extract_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Generate and parse JSON response.
        
        Args:
            prompt: User prompt requesting JSON output
            system_prompt: Optional system context
            
        Returns:
            Parsed JSON as list of dicts, or None on failure
        """
        response = await self.generate(prompt, system_prompt)
        
        if not response:
            return None
        
        return self._parse_json_response(response)
    
    def _parse_json_response(self, text: str) -> Optional[List[Dict[str, Any]]]:
        """
        Parse JSON from LLM response, handling common issues.
        """
        # Try direct parse first
        try:
            result = json.loads(text)
            if isinstance(result, list):
                return result
            elif isinstance(result, dict):
                return [result]
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code block
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
                if isinstance(result, list):
                    return result
                elif isinstance(result, dict):
                    return [result]
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON array in text
        array_match = re.search(r'\[[\s\S]*\]', text)
        if array_match:
            try:
                result = json.loads(array_match.group(0))
                if isinstance(result, list):
                    return result
            except json.JSONDecodeError:
                pass
        
        return None
    
    def is_available(self) -> bool:
        """Check if the LLM service is available."""
        try:
            # Quick test with minimal tokens
            response = self.client.chat_completion(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except:
            return False
