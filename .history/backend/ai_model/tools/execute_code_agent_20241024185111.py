from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import subprocess
import tempfile
import os



class PythonExecutorAgentTool(BaseTool):
    name: str = "python_executor_agent_tool"
    description: str = "An agent that can execute Python code safely and return the output."

    class InputSchema(BaseModel):
        code: str = Field(..., description="The Python code to execute.")

    def _run(self, code: str) -> str:
        # Create a temporary file to store the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            # Execute the code in a subprocess with a timeout
            result = subprocess.run(
                ['python', temp_file_path],
                capture_output=True,
                text=True,
                timeout=10  # 10 seconds timeout
            )
            
            # Check if there was an error
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            
            return result.stdout
        except subprocess.TimeoutExpired:
            return "Error: Execution timed out"
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    async def _arun(self, code: str) -> str:
        raise NotImplementedError("Async method not implemented.")



execute_code_agent_tool = PythonExecutorAgentTool()
