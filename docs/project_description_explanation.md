# Explanation: `project_description.py`

<!-- toc -->

- [Introduction and motivation](#introduction-and-motivation)
- [Core Concepts](#core-concepts)
- [How It Works](#how-it-works)
- [Design Rationale](#design-rationale)
- [Trade-offs and Alternatives](#trade-offs-and-alternatives)

<!-- tocstop -->

## Introduction and motivation

- This tool automates the generation of academic project descriptions by
  integrating Google Sheets input with OpenAI API.
- It addresses the need for scalable, consistent, and high-quality project
  documentation based on dynamic student or faculty input.
- It is intended to streamline and automate project generation and
  documentation.

## Core Concepts

- **Google Sheets Integration:** Uses Google Sheets as the dynamic data source
  for project names and difficulty levels.
- **Prompt Engineering:** A pre-defined prompt template guides GPT to produce
  structured project descriptions.
- **Markdown Generation:** Outputs the generated content into a formatted
  Markdown file for easy distribution.
- **Helper Modules:** External utility modules (`hgoogle_file_api`, `hopenai`,
  `hio`) abstract authentication, I/O, and API interaction.

## How It Works

- The script follows this control flow:

  ```markdown
  [Google Sheet URL] → read_google_sheet() → [DataFrame of projects] → loop →
  Create prompt and feed into GPT → [GPT-generated text] → create_markdown_file()
  → [Markdown output]
  ```

- Key Functions:
  - `read_google_sheet(url)`: Reads spreadsheet and returns a pandas DataFrame.
  - `generate_project_description(project_name, difficulty)`: Sends input to
    GPT-4o-mini model and returns generated text.
  - `create_markdown_file(df, markdown_file_path)`: Iterates over the DataFrame,
    generates description for each row, and writes it to a Markdown file.

## Design Rationale

- **Automation Focus:** Built to minimize manual work for faculty managing large
  project datasets.
- **Modular Helpers:** Offloading I/O and API logic to separate modules makes
  this script easier to maintain or port.
- **GPT as Content Generator:** Using GPT-4o-mini allows flexibility and
  high-quality text output with minimal prompt tuning.

## Trade-offs and Alternatives

- **Current Approach:**
  - Advantages:
    - Automated, reproducible, and scalable.
    - Maintains separation of logic (reading input, generating content, writing
      file).
  - Drawbacks:
    - Dependent on OpenAI and Google APIs (connectivity and API keys required).
    - Limited error handling and logging for individual failures.

- **Alternative Approach:**
  - Using a GUI-based application or Jupyter notebook for manual review and
    editing.
    - Advantages:
      - Allows user customization and validation at each step.
    - Drawbacks:
      - Slower and less scalable; not suitable for batch generation.
