from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from weather_tool import get_weather
from calculator_tool import calculator
import os

class SearchSummary(BaseModel):
    query: str = Field(..., description="The search query")
    summary: str = Field(..., description="A concise summary of the search results")


load_dotenv()
tavily_api_key = os.getenv("...")

weather_tool = get_weather
_tavily_tool_instance = TavilySearch(max_results=2, tavily_api_key=tavily_api_key)

def tavily_search_wrapper(query: str) -> SearchSummary:
    """
    Performs a web search using Tavily and returns a structured summary.
    """
    result = _tavily_tool_instance.run(query)
    return SearchSummary(query=query, summary=result)

tools = [tavily_search_wrapper, calculator, weather_tool]