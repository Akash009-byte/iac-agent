from strands import Agent, tool
from strands_tools import calculator, current_time
from strands.models.ollama import OllamaModel

# Define a custom tool as a Python function using the @tool decorator
@tool
def letter_counter(word: str, letter: str) -> int:
    """
    Count occurrences of a specific letter in a word.

    Args:
        word (str): The input word to search in
        letter (str): The specific letter to count

    Returns:
        int: The number of occurrences of the letter in the word
    """
    if not isinstance(word, str) or not isinstance(letter, str):
        return 0

    if len(letter) != 1:
        raise ValueError("The 'letter' parameter must be a single character")

    return word.lower().count(letter.lower())

ollama_model = OllamaModel(
    host="http://localhost:11434",  # Ollama server address
    # model_id="qwen2.5-coder:3b"                     # Specify which model to use
    model_id="llama3.1:8b",
    temperature=0.7,
    max_tokens=1000,
)

# Create an agent with tools from the community-driven strands-tools package
# as well as our custom letter_counter tool
agent = Agent(model=ollama_model, tools=[calculator, current_time, letter_counter])

# Ask the agent a question that uses the available tools
message = """
I have 3 requests:

1. What is the time right now?
2. Calculate 5 / 3
3. Tell me how many letter R's are in the word "strawberry" 🍓
"""
response = agent(message)
print(response)