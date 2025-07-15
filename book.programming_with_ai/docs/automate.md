# Tasks and automation

- We want to use LLMs to increase the productivity of the team and the uniformity
  of our code base

- The main tasks that we believe should be automated are:

## Automate (part of the) code reviews

- E.g., the stuff we complain about all the time, not the architectural stuff
- Use GitHub Copilot

```bash
> llm_transform.py -i helpers/hdbg.py -o - -p code_review_correctness
helpers/hdbg.py:41: Remove the unnecessary newline at the end of the return value of `_line`. The newline can be managed outside of the function if needed.
helpers/hdbg.py:50: Add documentation for the `chars` parameter in the `_frame` function docstring.
```

## Automate fixing the lints

- Example workflow:

  ```
  > i lint
  > llm_apply_cfile.py --cfile linter_warnings.txt -p code_apply_linter_instructions -v INFO
  ```

## Write (boilerplate) unit tests

- Use Cursor
- llm_transform.py

## Format the code

- E.g., improve existing comments, adding comments, improve docstrings
- Solution:
  - Use llm_transform.py to add TODOs and / or fix it

## Search our knowledge base

- Solution: Dify or our homebrew solution

## Format our knowledge base

- Solution: llm_transform.py

## Use coverage to make sure the code is properly tested

## Use metrics on GitHub to measure how collaborators are performing

- We want to make things available for all the team independently of the set up

- E.g., VSCode, PyCharm, vim

- We want to support multiple LLMs (including ones that run locally for privacy / cost savings)
