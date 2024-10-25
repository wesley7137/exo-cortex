
# Import necessary libraries
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.tools import BaseTool
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_community.utilities import SerpAPIWrapper
from langchain.schema import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from langchain_core.pydantic_v1 import BaseModel, Field

class CalculatorInput(BaseModel):
    expression: str = Field(description="Mathematical expression to evaluate")

def calculate(expression: str) -> float:
    """Evaluate a mathematical expression."""
    try:
        return eval(expression)
    except Exception as e:
        return f"Error: {str(e)}"

calculator_tool = StructuredTool.from_function(
    func=calculate,
    name="Calculator",
    description="Useful for performing mathematical calculations",
    args_schema=CalculatorInput,
    return_direct=True
)


# Define the CalculatorAgentTool
class CalculatorAgentTool(BaseTool):
    name = "calculator_agent_tool"
    description = "An agent that can perform calculations to answer mathematical questions."

    class InputSchema(BaseModel):
        question: str = Field(..., description="The mathematical question to calculate.")

    def _run(self, chat_model, question: str) -> str:
        # Initialize the calculator tool
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
