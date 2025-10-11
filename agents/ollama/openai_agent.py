from strands import Agent,  tool
from strands.models.openai import OpenAIModel
from strands_tools import calculator, current_time


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
    print(f"Counting letter {letter} in word {word}")
    print("9999999")

    if len(letter) != 1:
        raise ValueError("The 'letter' parameter must be a single character")

    return word.lower().count(letter.lower())

model = OpenAIModel(
    client_args={
        "api_key": "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",
    },
    model_id="gpt-4o",
    params={
        "max_tokens": 1000,
        "temperature": 0.7,
    }
)

# Create an agent with tools from the community-driven strands-tools package
# as well as our custom letter_counter tool
agent = Agent(model=model, tools=[calculator, current_time, letter_counter])

# Ask the agent a question that uses the available tools
message = """
I have 3 requests:

1. What is the time right now?
2. Calculate 5 / 3
3. Tell me how many letter R's are in the word "strawberry" 🍓
"""
agent(message)

