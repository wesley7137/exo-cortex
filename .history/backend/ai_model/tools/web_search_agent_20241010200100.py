# Import necessary libraries
from langchain.tools import BaseTool
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.utilities import SerpAPIWrapper
from pydantic import BaseModel, Field


# Define the WebSearchAgentTool
class WebSearchAgentTool(BaseTool):
    name = "web_search_agent_tool"
    description = "An agent that can search the web and return information to answer the user's question."
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
    class InputSchema(BaseModel):
        query: str = Field(..., description="The query to search for.")

    def _run(self, chat_model, query: str) -> str:
        # Initialize the search tool (ensure you have your SERPAPI_API_KEY set)
        search_tool = SerpAPIWrapper()
        # Initialize the agent with the search tool
        tools = [
            Tool(
                name="Search",
                func=search_tool.run,
                description="Searches the web for information.",
            )
        ]
        agent = initialize_agent(
            tools,
            chat_model,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
        )
        result = agent.run(query)
        return result

    async def _arun(self, chat_model, query: str) -> str:
        raise NotImplementedError("Async method not implemented.")
    
web_search_agent_tool = WebSearchAgentTool()
