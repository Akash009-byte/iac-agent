from strands import Agent
from strands.models.ollama import OllamaModel

# Create an Ollama model instance
ollama_model = OllamaModel(
    host="http://localhost:11434",              # Ollama server address
    model_id="qwen2.5-coder:3b"               # Specify which model to use
)

# Create an agent using the Ollama model
agent = Agent(model=ollama_model)

# Use the agent
agent("what is 2+2? (only give integer value)") # Prints model output to stdout by default