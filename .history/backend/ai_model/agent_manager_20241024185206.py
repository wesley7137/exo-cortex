from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import DeepLake
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.tools import BaseTool
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.schema import (
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from pydantic import BaseModel, Field
from .tools.agents import web_search_agent_tool,  execute_code_agent_tool
from models import User
from utils.database import db
import os

class AgentManager:
    def __init__(self, user_id):
        self.user = self.get_user(user_id)
        self.setup_agent()

    def get_user(self, user_id):
        return User.query.get(user_id)

    def setup_agent(self):
        # Set up embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': False}
        )

        # Set up DeepLake
        self.vectorstore = DeepLake(
            dataset_path=f"hub://{self.user.username}/{self.user.preferences.get('deeplake_dataset_name', 'default_dataset')}",
            read_only=True,
            embedding_function=self.embeddings,
            token=self.user.secrets.get('activeloop_token')
        )
        self.retriever = self.vectorstore.as_retriever()

        # Initialize chat model based on user preference
        self.chat_model = self.get_chat_model()

        # Set up tools based on user preferences
        self.tools = self.get_user_tools()

        # Bind tools to chat model
        self.chat_model_with_tools = self.chat_model.bind_tools(self.tools)

        # Initialize conversation history
        self.conversation_history = []

    def get_chat_model(self):
        model_preference = self.user.preferences.get('model_preference', 'openai')
        
        if model_preference == 'openai':
            return ChatOpenAI(
                model_name=self.user.preferences.get('openai_model', 'gpt-3.5-turbo'),
                temperature=self.user.preferences.get('temperature', 0),
                openai_api_key=self.user.secrets.get('openai_api_key')
            )
        elif model_preference == 'anthropic':
            return ChatAnthropic(
                model=self.user.preferences.get('anthropic_model', 'claude-3-opus-20240229'),
                anthropic_api_key=self.user.secrets.get('anthropic_api_key')
            )
        elif model_preference == 'ollama':
            return ChatOllama(
                model=self.user.preferences.get('ollama_model', 'llama3.1'),
                base_url=f"http://{os.getenv('OLLAMA_HOST', '127.0.0.1')}:{os.getenv('OLLAMA_PORT', '11434')}"
            )
        else:
            raise ValueError(f"Unsupported model preference: {model_preference}")

    def get_user_tools(self):
        tools = []
        user_tools = self.user.preferences.get('tools', [])
        
        if 'web_search' in user_tools:
            tools.append(web_search_agent_tool)
        if 'calculator' in user_tools:
            tools.append(calculator_agent_tool)
        if 'execute_code' in user_tools:
            tools.append(execute_code_agent_tool)
        
        # Add more tools based on user preferences
        
        return tools

    def chat_with_model(self, user_input: str) -> str:
        # Append user input to conversation history
        self.conversation_history.append(HumanMessage(content=user_input))

        # Retrieve context from vector store
        relevant_docs = self.retriever.get_relevant_documents(user_input)
        context = "\n".join([doc.page_content for doc in relevant_docs])

        # Create system prompt with context
        system_prompt = self.user.preferences.get('system_prompt', "You are a helpful assistant.")
        if context:
            system_prompt += f"\nUse the following context to help answer the user's question:\n{context}"

        # Prepare messages
        messages = [SystemMessage(content=system_prompt)] + self.conversation_history

        # Send messages to chat model
        response = self.chat_model_with_tools(messages)

        # Handle tool calls if any
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                for tool in self.tools:
                    if tool.name == tool_call['name']:
                        tool_output = tool.run(**tool_call['args'])
                        tool_message = Tool(
                            content=tool_output,
                            tool_name=tool.name,
                            tool_call_id=tool_call['id'],
                        )
                        self.conversation_history.append(tool_message)
                        final_response = self.chat_model_with_tools(messages + [tool_message])
                        self.conversation_history.append(final_response)
                        return final_response.content
        else:
            self.conversation_history.append(response)
            return response.content

def get_agent_manager(user_id):
    return AgentManager(user_id)