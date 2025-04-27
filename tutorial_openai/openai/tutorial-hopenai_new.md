This tutorial demonstrates how to use the `hopenai.py` helper file to create
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
  import helpers.hopenai as hopenai
  import logging
  import os
  from typing import List

  # Set up logging
  logging.basicConfig(level=logging.INFO)

  # Set OpenAI API key
  os.environ["OPENAI_API_KEY"] = "<your_openai_api_key>"
  ```

# Travel Agent Chat Assistant

Create an AI travel assistant using the `hopenai.py` helper file that generates
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

# Coding Assistant

Create an AI assistant using the `hopenai.py` helper file that helps with coding
questions and follows best practices.

## Features
- Answers technical questions
- Provides code examples
- Follows coding style guides
- References documentation

## Example Usage

- Example
  ```python
  assistant = hopenai.get_coding_style_assistant(
      assistant_name="CodingAssistant",
      instructions="You are a helpful coding assistant. Answer technical questions clearly and concisely.",
      vector_store_name="coding_help_vector_store",
      file_paths=["../helpers_root/docs/coding/all.coding_style.how_to_guide.md"]
  )

  # Query the assistant
  question = "What are common python mistakes that I should keep in mind while writing code?"
  response_messages = hopenai.get_query_assistant(assistant, question)
  ```

- Assistant's Response:
  ```
    assistant: Here are some common mistakes to avoid when writing Python code:
    
    1. **Indentation Errors**: Python relies on indentation to define the structure of the code. Ensure consistent use of spaces or tabs.
    
    2. **Misusing Mutable Default Arguments**: Using mutable default arguments (like lists or dictionaries) can lead to unexpected behavior because they are shared across function calls. Instead, use `None` and initialize inside the function.
    
       ```python
       def my_function(arg=None):
           if arg is None:
               arg = []
       ```
    
    3. **Not Handling Exceptions**: Failing to handle exceptions can crash your program. Use try-except blocks to catch and handle exceptions gracefully.
    
       ```python
       try:
           # some code that may raise an exception
       except SomeException as e:
           print(e)
       ```
    
    4. **Overusing Global Variables**: Relying heavily on global variables can lead to code that is hard to debug and maintain. Instead, prefer passing parameters to functions.
    
    5. **Using `==` Instead of `is` for Comparisons**: Use `is` to check for identity (same object) and `==` for equality (same value). 
    
       ```python
       if my_list is not None:  # Correct for identity
       ```
    
    6. **Not Using `__name__ == "__main__"`**: To allow for code reuse, encapsulate script execution code in a `if __name__ == "__main__":` block.
    
    7. **Ignoring Python's Built-in Functions and Libraries**: Many common tasks can be handled by Python's built-in functions or libraries (like `itertools`, `collections`, etc.). Familiarize yourself with these to write more efficient code.
    
    8. **Failing to Close Files**: Always close files after you are done with them, or better yet, use a `with` statement to ensure files are properly closed.
    
       ```python
       with open('file.txt', 'r') as f:
           data = f.read()
       ```
    
    9. **Using `raw_input` in Python 2 Instead of `input` in Python 3**: If you are transitioning from Python 2 to 3, remember `raw_input()` is `input()` in Python 3.
    
    10. **Misunderstanding `for` loop scope**: Variables defined inside the loop are accessible outside the loop, unlike in some other programming languages.
    
    By keeping these common pitfalls in mind, you can write cleaner, more efficient, and error-free Python code.

# File Management

Tools for managing files using the `hopenai.py` helper file.

## Features
- List uploaded files
- View file information
- Delete files
- Batch operations

## Example Usage

  ```python
  # List all files
  client = hopenai.OpenAI()
  files_before = list(client.files.list())
  print("Uploaded files:")
  print_file_info(files_before)
  # Delete all files (with confirmation)
  hopenai.delete_all_files(ask_for_confirmation=False)
  # Verify deletion
  files_after = list(client.files.list())
  print("Files after deletion:")
  print_file_info(files_after)
  ```

- Assistant's Response:
  ```
  Uploaded files:
  {'id': 'file-QFUuXpobjoLCnLBaCX2HK5', 'created_at': datetime.datetime(2024, 12, 11, 20, 14), 'filename': 'all.coding_style.how_to_guide.md'}
  {'id': 'file-5m1CX8UeABBJtFATb3cLtz', 'created_at': datetime.datetime(2024, 12, 11, 19, 59, 4), 'filename': 'all.write_unit_tests.how_to_guide.md'}
  {'id': 'file-UhqL4yhYrFP8ziDmM3XzB1', 'created_at': datetime.datetime(2024, 12, 11, 19, 59, 4), 'filename': 'all.coding_style.how_to_guide.md'}
  {'id': 'file-VEzEvpmVfhgUTpH5dmWtxC', 'created_at': datetime.datetime(2024, 12, 11, 19, 59, 4), 'filename': 'all.imports_and_packages.how_to_guide.md'}

  Files after deletion:
  ...
  ```

# Vector Store Operations

Manage and utilize vector stores for efficient document retrieval using the
`hopenai.py` helper file.

## Features
- Create vector stores
- Upload document batches
- Monitor upload status
- Query stored documents

## Example Usage

  ```python
  vector_store_name = "batch_vector_store"
  file_paths = [
      "../helpers_root/docs/coding/all.imports_and_packages.how_to_guide.md",
      "../helpers_root/docs/coding/all.write_unit_tests.how_to_guide.md",
      "../helpers_root/docs/coding/all.coding_style.how_to_guide.md"
  ]

  # Create and upload
  vector_store = client.beta.vector_stores.create(name=vector_store_name)
  file_streams = [open(path, "rb") for path in file_paths]
  file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
      vector_store_id=vector_store.id,
      files=file_streams
  )
  ```

# Code Generation with Testing

Create an AI assistant using the `hopenai.py` helper file that generates both
code and corresponding unit tests.

## Features
- Follows PEP 8 standards
- Generates comprehensive unit tests
- Handles edge cases
- Includes documentation

## Example Usage

  ```python
  # Create specialized assistant
  coding_assistant = hopenai.get_coding_style_assistant(
      assistant_name="CodeAndTestAssistant",
      instructions="""
      You are a coding assistant trained to write Python code and unit tests.
      Follow PEP 8 standards and write comprehensive tests.
      """,
      vector_store_name=vector_store_name
  )

  # Generate code and tests
  task = """
  Write a Python function `calculate_area` that computes the area of a rectangle 
  given its width and height. Then, write unit tests to verify its functionality.
  """
  response = hopenai.get_query_assistant(coding_assistant, task)
  ```

- Assistant's Response:
  ```
  assistant: Here's the Python function `calculate_area` that computes the area of a rectangle given its width and height, along with unit tests to verify its functionality.
    
    ### Python Function
    
    ```python
    def calculate_area(width: float, height: float) -> float:
        """Calculate the area of a rectangle.
    
        Args:
            width (float): The width of the rectangle.
            height (float): The height of the rectangle.
    
        Returns:
            float: The area of the rectangle.
    
        Raises:
            ValueError: If width or height is negative.
        """
        if width < 0 or height < 0:
            raise ValueError("Width and height must be non-negative.")
        
        return width * height
    ```
    
    ### Unit Tests
    
    Below are the unit tests for the `calculate_area` function using the `unittest` framework.
    
    ```python
    import unittest
    
    class TestCalculateArea(unittest.TestCase):
        
        def test_positive_dimensions(self):
            self.assertEqual(calculate_area(5, 10), 50)
            self.assertEqual(calculate_area(2.5, 4), 10)
            self.assertEqual(calculate_area(0, 0), 0)
    
        def test_zero_dimensions(self):
            self.assertEqual(calculate_area(0, 5), 0)
            self.assertEqual(calculate_area(5, 0), 0)
    
        def test_negative_dimensions(self):
            with self.assertRaises(ValueError):
                calculate_area(-1, 5)
            with self.assertRaises(ValueError):
                calculate_area(5, -1)
            with self.assertRaises(ValueError):
                calculate_area(-1, -1)
    
    if __name__ == '__main__':
        unittest.main()
    ```
    
- The `calculate_area` function takes two parameters, `width` and `height`, and
  calculates the area by multiplying these two values. It also raises a
  `ValueError` if either of the values is negative.
- The test cases cover:
  - Normal positive dimensions.
  - Zero dimensions.
  - Negative values, which should raise exceptions.

You can run the tests using a Python environment that supports `unittest`.

# Assistant Management

Tools for managing AI assistants using the `hopenai.py` helper file.

## Features
- List existing assistants
- View assistant details
- Delete assistants
- Batch operations

## Example Usage

  ```python
  # List assistants
  assistants = client.beta.assistants.list()

  # Delete assistants
  hopenai.delete_all_assistants(ask_for_confirmation=True)
  ```

- Refer to the Jupyter Notebook for a more comprehensive tutorial
- Make sure that helpers module is properly initialized and updated
- Always handle your API key securely
- Monitor API usage and costs
- Test generated code thoroughly before production use
- Keep vector stores organized and maintained
- Regularly clean up unused files and assistants
