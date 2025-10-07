# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: client_venv.helpers
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## 0. Setup and Initialization
# Before diving into use cases, we should initialize the notebook with the required setup:

# %%
# Import the helper script.
import helpers.hllm as hllm
import pandas as pd
# Set up logging for debugging.
import logging
logging.basicConfig(level=logging.INFO)

# Set OpenAI API key.
import os
from typing import List, Tuple

# %%
os.environ["OPENAI_API_KEY"] = "<your_api_key_here>"

# %% [markdown]
# ## 1. Travel Agent chat assistant: 
# #### Goal: Cretae a chat agent that will help the user to create an itinary to visit New York Trip considering all the constraints.

# %%
# Define the prompt for the travel assistant
user_prompt = """
I am visiting New York City for 3 days. Please create a detailed itinerary, 
including popular attractions, food recommendations, and some evening activities.
I already booked flight tickets and hotel near Newark penn station.
Constraints:
1) Dates: from 24th to 27th Dec.
1) My budget for travel is around $400 excluding hotel and flight.
2) I am planning to travel through subway and for rest of the trip I am planning to walk.
3) Also, take into account traffic and tourist rush at popular places.
"""

# Define the system instructions for the assistant
system_instructions = """
You are a travel assistant specializing in creating personalized travel itineraries.
Your recommendations should balance sightseeing, food, and leisure activities considering provided constraints.
Provide details like the time required for activities and approximate costs where possible.
"""

# Use the get_completion method to generate the trip plan
trip_plan = hllm.get_completion(
    user_prompt=user_prompt,
    system_prompt=system_instructions,
    model="gpt-4o-mini",
    temperature=0.7  # Slightly increase temperature for creative outputs
)

# Print the generated trip itinerary
print("3-Day New York City Trip Itinerary:")
print(trip_plan)

# %% [markdown]
# ## 2. Batch Upload to Vector Store and Query
# #### Goal: Add multiple files to a vector store for RAG

# %%
# Upload files to a vector store.
vector_store_name = "batch_vector_store"
file_paths = [
    "../helpers_root/docs/tools/all.imports_and_packages.how_to_guide.md", 
    "../helpers_root/docs/tools/unit_test/all.write_unit_tests.how_to_guide.md",
             "../helpers_root/docs/code_guidelines/all.coding_style.how_to_guide.md"]  # Example paths

question = "Is `from pathlib import Path` a correct import according to the coding guidelines?"

# Create or find vector store.
llm = hllm.LLMClient(model="gpt-4o")
llm.create_client()
client = llm.client
vector_store = client.vector_stores.create(name=vector_store_name)

# Upload files to the vector store.
file_streams = [open(path, "rb") for path in file_paths]
file_batch = client.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
)

if file_batch.status != "completed" or file_batch.file_counts.failed > 0:
    raise RuntimeError(f"Ingestion not ready: status={file_batch.status}, counts={file_batch.counts}")

resp = client.responses.create(
    model="gpt-4o",
    input=question,
    tools=[{
        "type": "file_search",
        "vector_store_ids": [vector_store.id],
    }],
)

# Extract the assistant's text.
out_text = getattr(resp, "output_text", "")

# Best-effort extraction of cited sources from output annotations.
sources: List[Tuple[str, str]] = []
for item in getattr(resp, "output", []) or []:
    for part in getattr(item, "content", []) or []:
        if getattr(part, "type", "") == "output_text":
            annotations = getattr(getattr(part, "text", None), "annotations", []) or []
            for ann in annotations:
                if getattr(ann, "type", "") == "file_citation":
                    file_id = ann.file_citation.file_id
                    fobj = client.files.retrieve(file_id)
                    sources.append((fobj.filename, file_id))


# Display file batch status
print("\n=== ANSWER ===\n", out_text)

if sources:
    print("\n=== SOURCES ===")
    for name, fid in sources:
        print(f"- {name}  ({fid})")

# %% [markdown]
# ## 3. Apply Prompt to DataFrame
# #### Goal: Run prompts batch-wise on a lot of data

# %%
df = pd.DataFrame({"question": [
    "Summarize: Attention is all you need.",
    "Summarize: Diffusion models in 2 sentences.",
    "Summarize: Convnets vs Transformers for vision.",
]})

df_out = hllm.apply_prompt_to_dataframe(
    df=df,
    prompt="Summarize each item in one sentence.",
    model="gpt-4o-mini",
    input_col="question",
    response_col="summary",
    chunk_size=3,
    allow_overwrite=True, 
)
print(df_out.head())

# %% [markdown]
# ## 3. Use the Cost Tracker
# #### Goal: Find the cumulative or individual costs of your LLM jobs

# %%
tracker = hllm.LLMCostTracker()
txt = hllm.get_completion(
    "Say hello in 10 words.",
    system_prompt="You are terse.",
    model="gpt-4o-mini",
    cache_mode="NORMAL",
    temperature=0.1,
    max_tokens=1000,
    print_cost=True,            
    cost_tracker=tracker,       
)

txt2 = hllm.get_completion(
    "Say hello in 50 words.",
    system_prompt="You are terse.",
    model="gpt-4o-mini",
    cache_mode="NORMAL",
    temperature=0.1,
    max_tokens=1000,
    print_cost=True,         
    cost_tracker=tracker,       
)

txt3 = hllm.get_completion(
    "Say hello in 70 words.",
    system_prompt="You are terse.",
    model="gpt-4o-mini",
    cache_mode="NORMAL",
    temperature=0.1,
    max_tokens=1000,
    print_cost=True,           
    cost_tracker=tracker,      
)

print("Custom tracker total: $", tracker.get_current_cost())
tracker.end_logging_costs()
