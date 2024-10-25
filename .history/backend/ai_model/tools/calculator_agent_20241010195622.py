
# Import necessary libraries
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.tools import BaseTool
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.utilities import SerpAPIWrapper
from langchain.tools import Calculator
from langchain.schema import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)
from pydantic import BaseModel, Field


# Define the CalculatorAgentTool
class CalculatorAgentTool(BaseTool):
    name = "calculator_agent_tool"
    description = "An agent that can perform calculations to answer mathematical questions."

    class InputSchema(BaseModel):
        question: str = Field(..., description="The mathematical question to calculate.")

    def _run(self, chat_model, question: str) -> str:
        # Initialize the calculator tool
        calculator_tool = Calculator()
        # Initialize the agent with the calculator tool
        tools = [calculator_tool]
        agent = initialize_agent(
            tools,
            chat_model,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
        )
        result = agent.run(question)
        return result

    async def _arun(self, question: str) -> str:
        raise NotImplementedError("Async method not implemented.")
    
calculator_agent_tool = CalculatorAgentTool()
