# Coding agents

## Claude code

### Introduction

- **Install and configure**
  - Follow the set-up from https://docs.anthropic.com/en/docs/claude-code/setup

- **What is Claude Code?**
  - Specialized capability of Claude for software development tasks
  - Designed to help with:
    - Writing code from scratch
    - Debugging existing code
    - Explaining code logic
    - Converting code between languages
    - Generating tests and documentation

- **Core Use Cases**
  - **Explain**
    - Break down code line-by-line
    - Clarify complex algorithms
  - **Write**
    - Generate functions, classes, modules
    - Follow user style guides and constraints
  - **Transform**
    - Refactor code for readability or performance
    - Convert code to different frameworks/languages
  - **Complete**
    - Fill in partial implementations
    - Suggest alternative solutions
  - **Test**
    - Generate unit tests
    - Identify edge cases

- **Strengths**
  - Handles long code files and complex projects
  - Maintains conversational context for iterative coding
  - Produces clear, well-commented code
  - Supports multiple programming languages

- **How It Works**
- Uses context window to “read” entire files if needed
- Retains history to apply consistent style/logic
- Can work with multiple files at once

- **Best Practices**
  - Provide clear instructions:
    - Define programming language
    - Specify libraries, versions, frameworks
    - Share input/output expectations
  - Break requests into steps for complex tasks
  - Ask for explanations alongside generated code to verify intent

- **Limitations**
  - May produce non-compiling code — always test
  - Can hallucinate libraries or functions — verify usage
  - May require iterative refinement for large systems

### Coding with Claude code

- From [https://www.anthropic.com/engineering/claude-code-best-practices](https://www.anthropic.com/engineering/claude-code-best-practices)

- Claude Code
  - Command line for agentic coding
  - Provide model access without forcing workflows

#### 1. Customize your setup

- Claude Code automatically pulls context into prompts

- `CLAUDE.md` is pulled in at the beginning of each context
  - Common bash commands
  - Code style guidelines
  - Testing instructions
  - Repo etiquette
  - Dev env set up

- It can be in each dir of the repo and in your home folder

- You need to tune your `CLAUDE.md` by iterating on its effectiveness
  - Use prompt improver
  - Tune instructions
    - E.g., `IMPORTANT` and `YOU MUST` to improve adherence

- Claude Code requests permission for any action that might modify your system
  - It prioritize safety
  - You can customize `allowlist` in `.claude/settings.json`
    ```bash
    > more .claude/settings.local.json
    {
      "permissions": {
        "allow": [
          "Bash(find:*)",
          "Bash(invoke --list)",
          "Bash(grep:*)",
          "Bash(ls:*)",
          "WebFetch(domain:github.com)",
          "Bash(python -m mypy:*)",
          "Bash(python:*)",
          "Bash(invoke git_branch_create -i 903)",
          "Bash(gh pr create:*)",
          "Bash(gh pr view:*)",
          "Bash(invoke git_branch_create *)",
          "Bash(git add:*)",
          "Bash(git push:*)",
          "Bash(git commit:*)"
        ],
        "deny": []
      }
    }
    ```

#### 2. Give Claude more tools

- You can give Claude more tools
  - Knows and Unix tools
  - Knows GitHub `gh` CLI
  - Knows MCP and REST APIs
  - Give your tools name and usage examples
  - Document used tools in `CLAUDE.md`

- Curate list of allowed tools
  - `.claude/settings.json`

- Store prompt templates in Markdown files in `.claude/commands`
  - Are available as `/` commands (you can pass commands)
  - E.g., for `.claude/commands/fix_gh_issue.md`, you can run
    `/project:fix_gh_issue 1234`

#### 3. Try common workflows

- **Explore**
  - Ask to read relevant files (but tell it not to write any code)
    - E.g., `read logging.py`
    - E.g., `read the file that handles logging`
  - Codebase Q&A
    - Use for learning and exploration
    - Ask questions like in pair programming

- **Plan**
  - Claude tends to jump to coding a solution
  - Asking Claude to plan first improves performance for the tasks that require
    thinking upfront
  - Ask to make a plan for how to approach a specific problem
    - Use the word `think` < `think hard` < `ultrathink` to allocate thinking
      budget
    - Create a markdown doc with its plan

- **Code**
- Ask to implement solution in code
  - Ask to verify how reasonable is the solution or pieces
- Ask to commit and create a PR
  - Ask to update `README` and changelog

- **TDD development**
  - Test-driven development (TDD) becomes powerful with agentic coding
    - Claude performs best when it has a clear target to iterate against
  - Ask to write tests based on expected input / output pairs
    - Be explicit asking to avoid creating mock implementations for functionalities
      that don't exist yet
  - Tell to run the tests and confirm they fail
    - Often helpful to tell not to write implementation
  - Ask to commit tests when satisfied with them
  - Ask to write code that passes the tests, without modifying the tests
    - Tell to keep going until all tests pass
  - Ask to commit code when satisfied

- Use Claude to interact with Git
  - E.g.,
    ```bash
    > echo "How to show the Git history of last 5 commits" | claude -p
    `git log --oneline -5`
    ```
  - "Write a commit message"
  - "Resolve rebase conflicts"
  
- Use to interact with GitHub
  - Create PRs
  - Fix failing builds 
  - Fix linter warnings

- Read and write Jupyter notebooks
  - Have CC and .ipynb opened in VS code
  - "Make data visualization aesthetically pleasing"

#### 4. Optimize your workflow

- Be specific and give clear directions to avoid iterations
  - Bad: Add tests for `foo.py`
  - Good: write a new test case for `foo.py`, covering edge case where ..., avoid
    mocks

- Use images when working with design mocks for UI and visual charts for analysis

- Give URLs to fetch and read
  - "Brainstorm fixes for https://github.com/..."

- You can get better results by being an active collaborator and guiding
  - Explain the task thoroughly
  - Course correct

- To course correct:
  - Ask to make a plan
  - Press escape to interrupt
  - Double-escape to jump back in history and edit a previous prompt
  - Ask to undo changes

- Use `/clear` to keep context focused during long sessions

- Use a checklists for complex workflows
  - E.g., when fixing lint errors, tell to run the lint command, write all
    resulting errors to a md checklist
  - Instruct to address each issue one by one, fixing and verifying before
    checking it off and moving to the next one

#### 5. Use headless mode to automate infra

- Use `-p` flag to have Claude interact with CI, pre-commit hooks, automation
  scripts
  - E.g., triage a new issue created in a repo
- Use as a linter
  - Identify typos, stale comments, misleading function or var names

#### 6. Multi-Claude workflows

- It is better to have a single instance handle everything
  - Have one Claude write code
  - Start a second Claude in another terminal
  - Have a second Claude review the first Claude's work
- Create multiple checkouts of your repo
  - E.g., `git clone` the same repo in multiple directories
- Use `git worktrees`

### References
- https://www.anthropic.com/claude-code
- https://www.anthropic.com/engineering/claude-code-best-practices
- https://news.ycombinator.com/item?id=43735550
// https://github.com/anthropics/anthropic-cookbook
// https://github.com/anthropics/courses
// https://docs.anthropic.com/en/docs/claude-code/tutorials

# OpenAI Codex
./notes/cs.openai.txt

# Aider

// ./notes/IN_PROGRESS.cs.aider.txt
// ~~https://aider.chat/~~
// [~~https://github.com/Aider-AI/aider~~](https://github.com/Aider-AI/aider)
// ~~Free~~
// # **Aider**
// 
// ## **Installing**
// 
// \> pip install aider-chat
// 
// In case of Unable to list files in git repo: \[Errno 24\] Too many open files
// \> ulimit \-n 8192
// 
// \> aider \--model sonnet \--api-key anthropic=$ANTHROPIC\_KEY
// 
// [https://aider.chat/docs/faq.html\#can-i-use-aider-in-a-large-mono-repo](https://aider.chat/docs/faq.html#can-i-use-aider-in-a-large-mono-repo)
// 
// Tie the output to a markdown
// \> aider \--model sonnet \--api-key anthropic=$ANTHROPIC\_KEY \--chat-history-file aider\_chat.md

# Google CLI

// https://blog.google/technology/developers/introducing-gemini-cli-open-source-ai-agent/

# IDEs

- The goal of this guide is to inspire users to be more productive using AI
  tools, successfully accomplish initial set-up. For detailed documentation
  follow the suggested links

## GitHub Copilot

### Confirm you have access to a license

1. Visit https://github.com/settings/copilot
2. The page should read that **GitHub Copilot Business is active for your
   account**
   - If not, contact the Infra team / GP

### VSCode set-up

1. Open a new VSCode window and open the extensions marketplace with
   `CMD + Shift + X`
2. Install 2 extensions
   - GitHub Copilot
   - GitHub Copilot Chat
3. VSCode might prompt you to sign in using your GH account via a notification
   window in the bottom right, unless you are already signed in
   - You can also sign in by clicking the "Accounts" button in the bottom left
     of the window

- Reference document: https://code.visualstudio.com/docs/copilot/setup

- After successfully logging in, Copilot should automatically start suggesting
  code
  - If it doesn't visit the troubleshooting page
    https://docs.github.com/en/copilot/troubleshooting-github-copilot/troubleshooting-common-issues-with-github-copilot

### Copilot Code suggestions

- Reference document:
  https://docs.github.com/en/copilot/using-github-copilot/getting-code-suggestions-in-your-ide-with-github-copilot

- The following steps will provide an example for resolution of issue
  https://github.com/cryptokaizen/cmamp/issues/9451 using GitHub Copilot
- In this GH issue we want to add tests for the function
  `datapull/common/universe/universe.py::get_vendor_universe_as_asset_ids`
- Go to the file `datapull/common/universe/test/test_universe.py`
  - If there is a test called `Test_get_vendor_universe_as_assert_ids` you can
    delete it for this example

- For example, suppose we want to add new test cases, typing
  `class Test_get_vendor_universe_as_assert_ids(` and Copilot suggests code
  <img src="figs/improve_productivity_using_ai/image1.png" style="" />

- We can use the mouse to control the generated code or use
  - `TAB` accepts the suggestion
  - `Control + →` will accept only the next word (useful if the suggested code
    is only "kind-of" correct)
  - `Alt + [` / `Alt + ]` show previous / next suggestion, since usually Copilot
    generates multiple ones
  - For a full list of shortcuts refer to the reference docs in the note above

- It is also possible to describe a test in natural language
  <img src="figs/improve_productivity_using_ai/image2.png" style="" />

### Copilot Chat

- Reference document:
  https://docs.github.com/en/copilot/using-github-copilot/asking-github-copilot-questions-in-your-ide

1. You can access the chat in the activity bar on the left
   - If you don't see the icon, right-click on the activity bar and enable
     "Chat"

2. Apart from the general ChatGPT like capabilities, Copilot chat offers unique
   features related to coding
   - **Chat participants**
     - `@workspace` has context about the code in the current workspace, this
       helps Copilot consider the project structure
     - You can also specify "this file" when engineering a prompt for the tab
       you have opened
   - **Chat context**
     - You can use so-called chat variables to include more context; a chat
       variable is accessed via `#`,
       - `#file` adds additional context from a given file
         - E.g. `#file:datapull/common/data/universe.py`
   - **Slash commands**
     - Provide shortcuts to commonly used features
       - E.g. `/tests` to generate unit tests for the selected code

3. For a quick suggestion, you can use inline chat using current line or a
   selection and `CMD + i`
   <img src="figs/improve_productivity_using_ai/image3.png" style="" />
   <img src="figs/improve_productivity_using_ai/image4.png" style="" />

4. Right clicking in a window or on a selection `Copilot` offers quick actions
   of Copilot similar to slash commands, such as:
   - `Explain this`
   - `Fix this`
   - `Generate docs`
   - `Generate tests`

### Tips & Tricks

- The entry point of the GitHub copilot documentation is
  https://docs.github.com/en/copilot
- Tips on prompt engineering:
  https://docs.github.com/en/copilot/using-github-copilot/prompt-engineering-for-github-copilot
- Example prompts:
  https://docs.github.com/en/copilot/using-github-copilot/example-use-cases/example-prompts-for-copilot-chat

- For detailed documentation of integrating VSCode and Copilot:
  https://code.visualstudio.com/docs/copilot/overview

## ChatGPT

## Cursor

## Devin

// https://simonwillison.net/2025/Apr/16/

// https://simonwillison.net/series/using-llms/
// https://simonwillison.net/series/llms-annual-review/

// New tools to try
// Try refact.ai** Try [https://refact.ai/](https://refact.ai/) $10

// ## Devin

// ## Codeium

// ## Rope
// Experiment with Rope to refactor Python code
// [https://rope.readthedocs.io/en/latest/index.html](https://rope.readthedocs.io/en/latest/index.html)

// Our tools
// llm_transform.py: a tool we have developed that process files through a prompt and / or with vim
// llm_apply_cfile.py
