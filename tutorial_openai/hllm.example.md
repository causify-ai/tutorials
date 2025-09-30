This tutorial demonstrates how to use the `hllm.py` helper file to create
various AI-powered applications using Python and Jupyter Notebook.

# Setup and Initialization
Before starting, ensure you are using our Docker environment.

## Prerequisites
1. **Sign up:** Create an OpenAI account at [OpenAI](https://www.openai.com/).
2. **API Key:** Obtain an API key from the "View API Keys" section.
3. **Set Environment Variable:** Store the key securely as an environment variable.
   ```bash
   > export OPENAI_API_KEY="<your_api_key_here>"
   ```

### Import required libraries

- Import required libraries in the notebook:
  ```python
  import helpers.hllm as hllm
  import logging
  import os
  from typing import List

  # Set up logging
  logging.basicConfig(level=logging.INFO)

  # Set OpenAI API key
  os.environ["OPENAI_API_KEY"] = "<your_openai_api_key>"
  ```

# Travel Agent Chat Assistant

Create an AI travel assistant using the `hllm.py` helper file that generates
personalized trip itineraries.

## Features
- Generate detailed day-by-day itineraries
- Consider budget constraints
- Account for transportation preferences
- Include popular attractions and food recommendations
- Factor in seasonal timing and tourist traffic

## Example Usage

- Example usage
  ```python
  # Define prompts and instructions
  user_prompt = """
  I am visiting New York City for 3 days. Please create a detailed itinerary, 
  including popular attractions, food recommendations, and evening activities.
  Constraints:
  - Dates: December 24-27
  - Budget: $400 (excluding hotel and flight)
  - Transportation: Subway and walking
  - Location: Hotel near Newark Penn station
  """

  system_instructions = """
  You are a travel assistant specializing in creating personalized travel itineraries.
  Your recommendations should balance sightseeing, food, and leisure activities.
  """

  # Generate itinerary
  trip_plan = hopenai.get_completion(
      user=user_prompt,
      system=system_instructions,
      model="gpt-4o-mini",
      temperature=0.7
  )
  ```

- The assistant response is

  ```
    3-Day New York City Trip Itinerary:
    Here’s a detailed 3-day itinerary for your trip to New York City from December 24th to 27th. This itinerary balances sightseeing, food, and leisure activities while considering your budget and travel preferences.
    
    ### Day 1: December 24th (Christmas Eve)
    
    **Morning:**
    - **Breakfast:** Start your day at **Ess-a-Bagel** (approx. $5-10). Enjoy a classic New York bagel with cream cheese.
    - **Visit Central Park:** Take the subway to **59th St – Columbus Circle** (approx. $2.75). Walk around the park, see the winter scenery, and visit the **Bethesda Terrace**. (2-3 hours)
    
    **Afternoon:**
    - **Lunch:** Head to **The Halal Guys** (approx. $10) for a famous street food experience. 
    - **Visit the Museum of Modern Art (MoMA):** Take the subway from **59th St to 53rd St** (approx. $2.75). Admission is $25. Spend around 2-3 hours exploring the exhibits.
    
    **Evening:**
    - **Dinner:** Try **Joe's Pizza** in Greenwich Village (approx. $3-5 per slice).
    - **Evening Activity:** Walk around **Times Square** to see the lights and holiday decorations. It's a bustling area, perfect for soaking in the Christmas spirit. Free activity, but be prepared for crowds!
    
    **Estimated Day 1 Total:** $56.50 + subway fares = approximately $65
    
    ---
    
    ### Day 2: December 25th (Christmas Day)
    
    ... 
    ---
    
    ### Summary of Estimated Costs
    - **Day 1 Total:** $65
    - **Day 2 Total:** $95
    - **Day 3 Total:** $80
    - **Total Activities Cost:** $240
    - **Subway Fare (approx. $2.75 each way for 6 trips):** $33
    - **Overall Total:** Approximately $273
    
    ### Remaining Budget
    You will have around $127 left from your $400 budget, allowing for any extra snacks, souvenirs, or additional activities.
    
    ### Tips
    - Purchase a **MetroCard** for subway travel to save money.
    - Check for any changes in opening hours or availability due to the holiday season.
    - Be prepared for colder weather; dress warmly!
    
    Enjoy your trip to New York City!
    ```


# Vector Store Operations

Manage and utilize vector stores for efficient document retrieval using the
`hllm.py` helper file.

## Features
- Create vector stores
- Upload document batches
- Monitor upload status
- Query stored documents

## Example Usage

  ```python
  # Upload files to a vector store.
vector_store_name = "batch_vector_store"
file_paths = [
    "/Users/indro/src/tutorials1/helpers_root/docs/tools/all.imports_and_packages.how_to_guide.md", 
    "/Users/indro/src/tutorials1/helpers_root/docs/tools/unit_test/all.write_unit_tests.how_to_guide.md",
             "/Users/indro/src/tutorials1/helpers_root/docs/code_guidelines/all.coding_style.how_to_guide.md"]  # Example paths

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
  ```

- The assistant response is
  ```
  According to the coding guidelines, using `from pathlib import Path` is not recommended. The guideline suggests starting with `import`, such as `import library.sublibrary as short_name`, to avoid maintenance issues, potential name collisions, and debugging difficulties.
  ```

# DataFrame Operations

Pass an entire DataFrame of prompts to the LLM to efficiently get prompts answered.

## Example Usage
```python
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
```
- The assistant response is
  ```
                                            question  \
  0            Summarize: Attention is all you need.   
  1      Summarize: Diffusion models in 2 sentences.   
  2  Summarize: Convnets vs Transformers for vision.   

                                              summary  
  0  "Attention is All You Need" introduces the Tra...  
  1  Diffusion models are generative models that le...  
  2  Convnets (Convolutional Neural Networks) excel...  
  ```

# Cost Tracking

Track costs both prompt-wise and project-wise.

## Example Usage

```python
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
```

- Output:
  ```
  cost=$0.000010
  cost=$0.000040
  cost=$0.000054
  Custom tracker total: $ 0.00010409999999999998
  ```