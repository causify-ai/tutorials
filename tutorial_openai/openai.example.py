# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python (client_venv.helpers)
#     language: python
#     name: client_venv_helpers
# ---

# %% [markdown]
# ## Using OpenAI API.
#
#     While accessing ChatGPT through the OpenAI portal is engaging, you can also interact with it programmatically using their API. Let’s use an API key and handle everything directly in Python!

# %% [markdown]
# ## Install and import modules

# %%
# try:
import openai
# except ImportError:
#     # !pip install openai

# %%
# %load_ext autoreload
# %autoreload 2

# %%
import pprint
import logging
import os
import urllib
from PIL import Image
import matplotlib.pyplot as plt
import io
from typing import List, Tuple, Dict

# %% [markdown]
# ### Getting ready
# 1. First go to the OpenAI website, signing up for an account, and obtaining an API key from the View API Keys section.
# 2. Set your API key as an environment variable.

# %%
os.environ["OPENAI_API_KEY"] = "<your_api_key_here>"

# %% [markdown]
# ## Question answering using ChatGPT Agent ##

# %%
# Create an agent.
agent = openai.OpenAI()


# %%
# Example function for querying the assistant
def get_assistant_response(
    model: str, 
    messages: List[Dict[str, str]], 
    temperature: float = 0.7, 
    max_tokens: int = 150
) -> str:
    """
    Queries the OpenAI API to get a response from the assistant.

    param model: model to use, e.g., "gpt-4".
    param messages: list of messages defining the conversation.
    param temperature: sampling temperature, controls randomness.
    param max_tokens: maximum number of tokens for the response.

    Returns: assistant's response.
    """
    response = agent.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content



# %%
# Example scenario: Customer inquiry about product return policy
messages = [
    {"role": "system", "content": "You are a friendly and professional customer support assistant."},
    {"role": "user", "content": "Hi, I need to return a product I purchased last week. Can you tell me the process?"}
]

response  = get_assistant_response(
    model="gpt-4o-mini",  # Use a robust model for nuanced conversations
    messages=messages
)

print("Assistant's Response:")
print(response)

# %%
# Escalation for complex issues
follow_up = [
    {"role": "system", "content": "You are a customer support assistant. If the issue is complex, provide a response and escalate to a human agent."},
    {"role": "user", "content": "The product I received is damaged, and I need it replaced immediately."}
]

response = get_assistant_response(
    model="gpt-4o-mini",
    messages=follow_up,
    temperature=0.6
)

print("\nEscalation Scenario:")
print(response)


# %% [markdown]
# ### Coding Assistant

# %%
def query_coding_agent(task: str, model_name: str = "gpt-4o-mini") -> str:
    """
    Interacts with the coding assistant to complete a given task.
    
    param task: detailed description of the coding task or question.
    param model_name: name of the model to use.

    Returns: assistant's response.
    """
    try:
        # Step 1: Create the coding assistant
        coding_agent = agent.beta.assistants.create(
            model=model_name,
            name="Coding Assistant",
            description="An AI assistant skilled in programming, debugging, and code documentation.",
            instructions="You are a helpful coding assistant. You are an expert in Python, JavaScript, and debugging common errors. Assist the user by generating code snippets, fixing errors, and explaining concepts in simple terms."
        )
    
        # Step 2: Create a thread for the task (conversation with the assistant)
        thread = agent.beta.threads.create()

        # Step 3: Send the coding task to the assistant
        message = agent.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=task
        )

        # Step 4: Run the assistant to execute the task and get the response
        run = agent.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=coding_agent.id,
            instructions="Please respond with the solution to the user's coding problem."
        )

        # Step 5: Check if the task was completed and retrieve the assistant's response
        if run.status == 'completed':
            messages = agent.beta.threads.messages.list(
                thread_id=thread.id
            )
            # Return the first message from the assistant's response
            return messages.data[0].content[0].text.value
        else:
            return f"Task not completed. Status: {run.status}"

    except Exception as e:
        return f"An error occurred: {str(e)}"


# %% [markdown]
# ### Example: Generating a Python function

# %%
task_description = "Write a Python function to calculate the factorial of a number using recursion."
response = query_coding_agent(task_description)
print("Response from Coding Agent:")
print(response)

# %% [markdown]
# ### Example: Advanced Features
#
# Expand the assistant’s capabilities:
# #### Debugging Errors
#
# Provide a code snippet with an error and ask for fixes.

# %%
debug_task = """
Here is my code:
def add_numbers(a, b):
print(a + b)

I'm getting an IndentationError. Can you fix it?
"""
debug_response = query_coding_agent(debug_task)
print("Debugging Response:")
print(debug_response)


# %% [markdown]
# #### Code Refactoring
#
# Ask the assistant to optimize inefficient code.

# %%
refactor_task = """
Here is my code:
numbers = [1, 2, 3, 4, 5]
sum = 0
for num in numbers:
    sum += num
print(sum)

Can you refactor it to use a more Pythonic approach?
"""
refactor_response = query_coding_agent(refactor_task)
print("Refactored Code:")
print(refactor_response)

# %% [markdown]
# ### 3. Documentation Drafting
#
# Request documentation for a given function.

# %%
doc_task = """
Can you write docstrings for this Python function?

def greet_user(name):
    print(f"Hello, {name}!")
"""
doc_response = query_coding_agent(doc_task)
print("Generated Docstring:")
print(doc_response)


# %% [markdown]
# ### Using DALL-E for Image Creation with OpenAI
#
# OpenAI offers access to its DALL-E model through an API. DALL-E is a multimodal version of GPT-3, containing 12 billion parameters, designed to convert text descriptions into images. It has been trained on a vast collection of text-image pairs sourced from the web (including Wikipedia), allowing it to generate images based on written prompts. This model is accessible through the same API.

# %%
def generate_image(prompt: str):
    com = agent.images.generate(prompt=prompt, n=1, size="512x512")
    url = com.data[0].url
    image_data = urllib.request.urlopen(url).read()
    image_file = io.BytesIO(image_data)
    image = Image.open(image_file)
    frame1 = plt.gca()
    frame1.axes.xaxis.set_ticklabels([])
    frame1.axes.yaxis.set_ticklabels([])
    plt.xticks([])
    plt.yticks([])
    #Display the image
    plt.imshow(image)
    plt.show()


# %%
prompt = "A futuristic cyberpunk cityscape at night, with neon lights reflecting off wet streets, flying cars, and towering skyscrapers, in a vibrant color palette."

generate_image(prompt)
