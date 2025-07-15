# ---
# jupyter:
#   jupytext:
#     formats: py:percent,ipynb
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# #!sudo /venv/bin/pip install openai

# %%
# %load_ext autoreload
# %autoreload 2
# %matplotlib inline

# %%
import logging
import os
import pandas as pd

import ck_marketing.linkedin.linkedin_utils as cmliliut
import helpers.hdbg as hdbg
import helpers.henv as henv
import helpers.hopenai as hopenai
import helpers.hpandas as hpandas
import helpers.hprint as hprint

# %%
hdbg.init_logger(verbosity=logging.WARNING)

_LOG = logging.getLogger(__name__)

_LOG.info("%s", henv.get_system_signature()[0])

hprint.config_notebook()

# %% [markdown]
# # Load the CSV file with names.
#
# - Expects a CSV file with two columns, `first_name` and `last_name`

# %%
file_path = "/shared_data/dev/ck_marketing/clean_up_names.csv"
# Create a df with the csv file in the filepath.
df = pd.read_csv(file_path)
# Drop the first row as it is empty.
df = df.drop(index=0)
# Replace NaNs with empty string.
df = df.fillna("")
column_names = ["first_name", "last_name"]
df[column_names] = df[column_names].astype(str)
_LOG.info("df with names = \n %s", hpandas.df_to_str(df, log_level=logging.INFO))

# %% [markdown]
# # Apply transformation on first/last name separately.


# %%
# Define a wrapper function to handle precedence of nicknames.
def process_names(row) -> pd.Series:
    first_name_cleaned, first_nickname = cmliliut.clean_first_last_name(
        row["first_name"], last_name_only=False
    )
    last_name_cleaned, last_nickname = cmliliut.clean_first_last_name(
        row["last_name"], last_name_only=True
    )
    # Choose the nickname with precedence given to the first name.
    return pd.Series([first_name_cleaned, last_name_cleaned, first_nickname, last_nickname])


# Apply the processing function.
df_first_last = df.copy()
df_first_last[
    ["cleaned_first_name", "cleaned_last_name", "first_nickname", "last_nickname"]
] = df_first_last.apply(process_names, axis=1)
_LOG.info(
    "Separate transformation =\n %s",
    hpandas.df_to_str(df_first_last, log_level=logging.WARNING),
)


# %% [markdown]
# # Apply transformation using LLM (OpenAI API)


# %%
# Define the prompt for splitting full names.
prompt = """
You will receive a list of names, each numbered like "1:", "2:", etc.
For each name:
1. Remove any special characters, emojis, and unnecessary whitespace.
2. Normalize the casing: properly capitalize the first and last names.
3. Remove all titles (e.g., Dr., Mr., Mrs., Ms., Prof.).
4. Properly handle hyphenated names (e.g., "Mary-Jane" should remain hyphenated).
5. Extract the cleaned first name and last name separately.
6. If there is a nickname or alias in parentheses, quotes, or similar notation, do NOT include it in the cleaned first or last name, but retain it separately for reference. (Pronouns like "she/her," "he/him," etc. are not aliases.)
7. If the input name cannot be parsed into valid components (e.g., no clear first and last name), mark it as invalid.
8. Return the output in the following format:
   <row_number>: First name: <first_name>, Last name: <last_name>, Nickname: <nickname>

   - If no nickname is found, use: Nickname: None
   - If the name is invalid, return: <row_number>: Invalid input.
"""
df_ai_transform = df.copy()
# Prepare the input column with full names.
df_ai_transform["input"] = "First Name: " + df_ai_transform["first_name"] + "  Last Name: " + df_ai_transform["last_name"]
# Define the models to use.
models = [
    "gpt-4o-mini",
]
# Apply the transformation using each model.
chunk_size=50
df_sliced = df_ai_transform[:10]
for model in models:
    input_col = "input"
    response_col = model
    allow_overwrite = True
    df_sliced = hopenai.apply_prompt_to_dataframe(
        df_sliced, 
        prompt, 
        model, 
        input_col, 
        response_col, 
        chunk_size=chunk_size,
        allow_overwrite=allow_overwrite
    )

# %%
# Extract first and last names from the responses.
for model in models:
    df_ai_transform[f"{model}_first_name"] = df_ai_transform[model].str.extract(r"First name:\s*(.*?),")
    df_ai_transform[f"{model}_last_name"] = df_ai_transform[model].str.extract(r"Last name:\s*(.*),")
    df_ai_transform[f"{model}_nickname"] = df_ai_transform[model].str.extract(r"Nickname:\s*(.*)")
# Drop unnecessary intermediate columns.
cols_to_drop = models 
df_ai_transform.drop(columns=cols_to_drop, inplace=True)
df_sliced.head(100)

# %% [markdown]
# # Serialize

# %%
dst_folder_path = "/shared_data/dev/ck_marketing/"
df_full_name.to_csv(dst_folder_path + "transformed_names.full_names.csv")
df_first_last.to_csv(dst_folder_path + "transformed_names.seperate.csv")
df_sliced.to_csv(dst_folder_path + "transformed_names.llm.csv")
