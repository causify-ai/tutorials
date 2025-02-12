"""
Import as:

import DATA605.project_description as dprodesc
"""

import helpers.hgoogle_file_api as hgofiapi
import helpers.hopenai as hopenai

# Constants
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1Ez5uRvOgvDMkFc9c6mI21kscTKnpiCSh4UkUh_ifLIw/edit?gid=0#gid=0"
PROMPT_DOC_URL = "https://docs.google.com/document/d/1c4oyCmvb-r5FHHL0enRQEEfsQ-shR3F7uvFVXMdeJSg/edit?tab=t.0#heading=h.a4upg2qbwqkb"
MARKDOWN_FILE_PATH = "DATA605_Projects.md"


def read_google_sheet(url):
    credentials = hgofiapi.get_credentials()
    df = hgofiapi.read_google_file(url, credentials=credentials)
    return df

def generate_project_description(project_name, difficulty):
    prompt = f"Generate a project description for '{project_name}' with difficulty level '{difficulty}'."
    description = hopenai.get_completion(prompt, model="gpt-4o-mini")
    return description

def create_markdown_file(df, markdown_file_path):
    with open(markdown_file_path, "w") as md_file:
        md_file.write("# DATA605 Projects\n\n")
        for index, row in df.iterrows():
            project_name = row["Project Name"]
            difficulty = row["Difficulty"]
            description = generate_project_description(project_name, difficulty)
            md_file.write(f"## {project_name}\n")
            md_file.write(f"**Difficulty:** {difficulty}\n\n")
            md_file.write(f"{description}\n\n")

def main():
    # Read the Google Sheet
    df = read_google_sheet(GOOGLE_SHEET_URL)

    # Create the markdown file
    create_markdown_file(df, MARKDOWN_FILE_PATH)
    print(f"Markdown file created at {MARKDOWN_FILE_PATH}")


if __name__ == "__main__":
    main()
