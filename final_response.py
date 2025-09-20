from pydantic import BaseModel, Field

class FinalResponse(BaseModel):
    # Describe the final response schema
    english_answer: str = Field(..., description="A human-readable summary of the calculation result")
    german_answer: str = Field(..., description="Eine menschenlesbare Zusammenfassung des Berechnungsergebnisses")