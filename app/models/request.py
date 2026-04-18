import re
from pydantic import BaseModel, Field, field_validator

class ChatRequest(BaseModel):
    message: str = Field(...,min_length=1, max_length=2000, description="The user's message to AI assistant")

    @field_validator("message")
    @classmethod
    def validate_message(cls, v:str) -> str:
        normalized = v.strip()

        if not normalized:
            raise ValueError("Message cannot be empty or whitespace")
        
        injection_patterns = [
             r"(?i)(ignore\s+previous|ignore\s+above|forget\s+your\s+instructions)",
            r"(?i)(system\s*prompt|reveal\s+your\s+instructions|show\s+your\s+prompt)",
            r"(?i)(you\s+are\s+now|new\s+instructions|override\s+previous)",
            r"(?i)(<\s*script|javascript:|on\w+\s*=)",
        ]

        for pattern in injection_patterns:
            if re.search(pattern, normalized):
                raise ValueError("Message contains malicious prompt injection content")

        if re.match(r"^[\W_]+$", normalized):
            raise ValueError("Message must contain actual text content")
        
        return normalized
    
class ChatResponse(BaseModel):
    answer: str = Field(..., min_length=1, description="The AI assistant's answer")
    sources: list[str] = Field(default_factory=list, description="List of source documents used to generate the answer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the answer between 0 and 1")
    tokens_used: int = Field(..., ge=0, description="Number of tokens used to generate the answer")