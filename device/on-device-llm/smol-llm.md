smollm-360M-instruct-add-basics-Q8_0-GGUF
This model was converted to GGUF format from

using llama.cpp via the ggml.ai's

space.
Refer to the

for more details on the model.

Use with llama.cpp
Install llama.cpp through brew (works on Mac and Linux)

brew install llama.cpp

Invoke the llama.cpp server or the CLI.

CLI:
llama-cli --hf-repo HuggingFaceTB/smollm-360M-instruct-add-basics-Q8_0-GGUF --hf-file smollm-360m-instruct-add-basics-q8_0.gguf -p "The meaning to life and the universe is"
Server:
llama-server --hf-repo HuggingFaceTB/smollm-360M-instruct-add-basics-Q8_0-GGUF --hf-file smollm-360m-instruct-add-basics-q8_0.gguf -c 2048
Note: You can also use this checkpoint directly through the

listed in the Llama.cpp repo as well.

Step 1: Clone llama.cpp from GitHub.

git clone https://github.com/ggerganov/llama.cpp
Step 2: Move into the llama.cpp folder and build it with LLAMA_CURL=1 flag along with other hardware-specific flags (for ex: LLAMA_CUDA=1 for Nvidia GPUs on Linux).

cd llama.cpp && LLAMA_CURL=1 make
Step 3: Run inference through the main binary.

./llama-cli --hf-repo HuggingFaceTB/smollm-360M-instruct-add-basics-Q8_0-GGUF --hf-file smollm-360m-instruct-add-basics-q8_0.gguf -p "The meaning to life and the universe is"
or

./llama-server --hf-repo HuggingFaceTB/smollm-360M-instruct-add-basics-Q8_0-GGUF --hf-file smollm-360m-instruct-add-basics-q8_0.gguf -c 2048
