# How to use coding AI

The best applications for AI coding are:
- Generate boilerplate code (like 80-90%) of an entire task  
- Perform deterministic transformations (e.g., apply a certain style, add
  documentation to an existing piece of code)  
- Generate unit tests (at least the boilerplate)  
- Improve documentation of existing code  
- Explain code that you are not familiar with  
- Look up documentation (instead of Googling)  
- Infer type hints in existing code  
- Fix small localized bugs

What AI coding is not good (yet) for:

- Generate end-to-end applications (unless it's a throw-away prototype)  
  - The problem is that AI can generate 90% of the application, but the last 10%
    requires a lot of work and it's more difficult to explain than just doing it  
- Fix bugs due to the interactions of multiple complex components in the code

Our goal is:

- Not to replace our work with AI  
- Automate the repetitive tasks so that we can move fast  
- Have more fun by removing the boring part

## Our golden rule

- After using AI, you should be able to explain and understand the code as if it
  was entirely written by you  
- You need to understand the code line-by-line  
- If one asks you "what happens if I change this line", you should know the
  answer


## Guidelines:

- Start with clear intent: define the problem and what you want the AI to do
  (e.g., generate boilerplate, suggest optimizations).  
- Use AI for scaffolding, not final code: Let AI create the first draft, then
  review and refactor manually for readability, performance, and idiomatic style.  
- Demand explicit explanations: Ask the AI to explain its choices and logic,
  especially for unfamiliar patterns or complex implementations.  
- Integrate tests early: Auto-generate or manually write unit tests alongside AI
  code to validate correctness and edge cases.  
- Apply consistent style: Use linters, formatters, and enforce style guides
  (PEP8) to keep code human-readable.  
- Iterate in small pieces: Break down tasks into small, verifiable chunks so that
  each AI-generated block is easy to understand and debug.  
- Document while coding: Add meaningful docstrings and comments to bridge any
  AI-human comprehension gap.  
- Avoid over-reliance: Use AI as a pair programmer, not a replacement; regularly
  write code without it to stay sharp.  
- Focus on the architecture, write the interfaces first, and then use AI to fill
  up the code  
- Use a lot of OOP / classes to encapsulate components with clear and separate
  responsibilities
