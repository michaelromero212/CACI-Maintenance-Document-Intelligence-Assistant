"""Unit tests for AI functionality."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from pydantic import ValidationError

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes.ai import (
    get_llm_client,
    AIChatRequest,
    AIAnalyzeRequest,
    AIStatusResponse,
    AIChatResponse,
    AIAnalyzeResponse,
)


class TestLLMClient:
    """Tests for LLM client functionality."""
    
    def test_client_singleton(self):
        """Test that get_llm_client returns same instance."""
        client1 = get_llm_client()
        client2 = get_llm_client()
        assert client1 is client2
    
    def test_client_has_model(self):
        """Test that client has model attribute."""
        llm = get_llm_client()
        assert hasattr(llm, 'model')
        assert llm.model is not None
    
    def test_client_has_is_available_method(self):
        """Test that client has is_available method."""
        llm = get_llm_client()
        assert hasattr(llm, 'is_available')
        assert callable(llm.is_available)
    
    def test_client_has_generate_method(self):
        """Test that client has generate method."""
        llm = get_llm_client()
        assert hasattr(llm, 'generate')
        assert callable(llm.generate)


class TestAIChatRequestValidation:
    """Tests for AIChatRequest input validation."""
    
    def test_valid_message(self):
        """Test that valid message is accepted."""
        request = AIChatRequest(message="What are common maintenance tasks?")
        assert request.message == "What are common maintenance tasks?"
    
    def test_message_stripped(self):
        """Test that message whitespace is stripped."""
        request = AIChatRequest(message="  test message  ")
        assert request.message == "test message"
    
    def test_empty_message_rejected(self):
        """Test that empty message is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AIChatRequest(message="")
        assert "Message cannot be empty" in str(exc_info.value)
    
    def test_whitespace_message_rejected(self):
        """Test that whitespace-only message is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AIChatRequest(message="   ")
        assert "Message cannot be empty" in str(exc_info.value)
    
    def test_short_message_rejected(self):
        """Test that very short messages are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AIChatRequest(message="ab")
        assert "at least 3 characters" in str(exc_info.value)
    
    def test_long_message_rejected(self):
        """Test that messages over 5000 chars are rejected."""
        long_message = "x" * 5001
        with pytest.raises(ValidationError) as exc_info:
            AIChatRequest(message=long_message)
        assert "5000 characters" in str(exc_info.value)
    
    def test_valid_context(self):
        """Test that valid context values are accepted."""
        valid_contexts = ["maintenance", "general", "analysis"]
        for ctx in valid_contexts:
            request = AIChatRequest(message="test message", context=ctx)
            assert request.context == ctx.lower()
    
    def test_invalid_context_rejected(self):
        """Test that invalid context is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AIChatRequest(message="test message", context="invalid")
        assert "Context must be one of" in str(exc_info.value)
    
    def test_default_context(self):
        """Test that default context is maintenance."""
        request = AIChatRequest(message="test message")
        assert request.context == "maintenance"


class TestAIAnalyzeRequestValidation:
    """Tests for AIAnalyzeRequest input validation."""
    
    def test_valid_analysis_types(self):
        """Test that valid analysis types are accepted."""
        valid_types = ["summary", "risks", "priorities"]
        for atype in valid_types:
            request = AIAnalyzeRequest(
                document_id="00000000-0000-0000-0000-000000000000",
                analysis_type=atype
            )
            assert request.analysis_type == atype.lower()
    
    def test_invalid_analysis_type_rejected(self):
        """Test that invalid analysis type is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AIAnalyzeRequest(
                document_id="00000000-0000-0000-0000-000000000000",
                analysis_type="invalid_type"
            )
        assert "analysis_type must be one of" in str(exc_info.value)
    
    def test_case_insensitive_analysis_type(self):
        """Test that analysis type is case-insensitive."""
        request = AIAnalyzeRequest(
            document_id="00000000-0000-0000-0000-000000000000",
            analysis_type="SUMMARY"
        )
        assert request.analysis_type == "summary"
    
    def test_default_analysis_type(self):
        """Test that default analysis type is summary."""
        request = AIAnalyzeRequest(
            document_id="00000000-0000-0000-0000-000000000000"
        )
        assert request.analysis_type == "summary"


class TestResponseModels:
    """Tests for response model structures."""
    
    def test_ai_status_response_fields(self):
        """Test AIStatusResponse has all required fields."""
        response = AIStatusResponse(
            status="connected",
            model="test-model",
            has_token=True,
            response_time_ms=100.5,
            last_check="2024-01-15T10:00:00Z",
            message="Test message"
        )
        assert response.status == "connected"
        assert response.model == "test-model"
        assert response.has_token is True
        assert response.response_time_ms == 100.5
    
    def test_ai_chat_response_fields(self):
        """Test AIChatResponse has all required fields."""
        response = AIChatResponse(
            response="This is the AI response",
            processing_time_ms=1500.0
        )
        assert response.response == "This is the AI response"
        assert response.processing_time_ms == 1500.0
        assert response.tokens_used is None  # Optional field
    
    def test_ai_analyze_response_fields(self):
        """Test AIAnalyzeResponse has all required fields."""
        response = AIAnalyzeResponse(
            document_id="test-doc-id",
            analysis_type="summary",
            analysis="This is the analysis",
            processing_time_ms=2000.0
        )
        assert response.document_id == "test-doc-id"
        assert response.analysis_type == "summary"
        assert response.analysis == "This is the analysis"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
