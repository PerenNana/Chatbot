from pydantic import BaseModel, Field
from langchain_core.tools import tool

class CalculatorInput(BaseModel):
    expression: str = Field(..., description="Mathematical expression to evaluate. Valid characters: 0123456789+-*/^(). **")

class CalculatorOutput(BaseModel):
    result: str = Field(..., description="Result of the calculation")

@tool(args_schema=CalculatorInput)
def calculator(expression: str) -> CalculatorOutput:
    """
    Performs basic arithmetic calculations. Usage: calculator(expression: str)
    If the user asks a math question, use the calculator tool to answer.
    DO NOT use function, only arithmetic expressions.
    E.g. for square root of 16 use "16 ** 0.5" instead of "sqrt(16)".
    """
    try:
        allowed = "0123456789+-*/^(). **"
        if not all(c in allowed for c in expression):
            return CalculatorOutput(result="Invalid characters in expression.")
        result = eval(expression, {"__builtins__": None}, {})
        return CalculatorOutput(result=str(result))
    
    except Exception as e:
        return CalculatorOutput(result=f"Error: {e}")
