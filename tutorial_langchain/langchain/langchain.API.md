# LangChain API Tutorial

<!-- toc -->

- [Introduction](#introduction)
- [Architecture Overview](#architecture-overview)
  * [1. Prompts](#1-prompts)
  * [2. Chains](#2-chains)
  * [3. Retrieval](#3-retrieval)
  * [4. Agents](#4-agents)
- [Setting Up](#setting-up)
  * [Building and Running the Docker Container](#building-and-running-the-docker-container)
  * [Dependencies](#dependencies)
- [Message Handling](#message-handling)
  * [Why This Is Important](#why-this-is-important)
- [Custom Prompts](#custom-prompts)
  * [Example Use Case](#example-use-case)
- [Chains](#chains)
  * [Example Workflow](#example-workflow)
  * [Why Chains Matter:](#why-chains-matter)
- [Retrieval with FAISS](#retrieval-with-faiss)
  * [Example Use Case](#example-use-case-1)
  * [Key Features](#key-features)
- [Building a QA System](#building-a-qa-system)
  * [Why This Matters](#why-this-matters)
- [Agents and Tools](#agents-and-tools)
  * [Example Use Case](#example-use-case-2)

<!-- tocstop -->

## Introduction

LangChain is a framework designed to make language model-based application
development intuitive and modular. By abstracting components like prompts,
workflows, and retrieval, it allows you to focus on solving problems rather than
low-level integration. It simplifies the development of language model-powered
applications by providing tools for prompt creation, chaining tasks, and
integrating retrieval mechanisms. This tutorial explores LangChain's core
capabilities through examples, helping you understand how to design intelligent
workflows. More documentation details can be found at
[LangChain Documentation](https://python.langchain.com/docs/introduction/).

This tutorial explores:

- Creating structured prompts for conversational AI.
- Combining prompts and models into reusable workflows.
- Using retrieval mechanisms like FAISS to enhance context.
- Building flexible agents for decision-making.

## Architecture Overview

LangChain is built around four key components:

![alt text](/image.png)

### 1. Prompts

Prompts define the interaction between users and the language model. With
LangChain, prompts are dynamic and parameterized, enabling reuse across
different contexts. Examples include:

- Single-turn question answering.
- Context-aware summarization.

### 2. Chains

Chains represent workflows. They connect prompts, models, and output parsers in
a pipeline, ensuring consistent processing. Chains help automate multi-step
tasks.

### 3. Retrieval

Retrieval mechanisms allow you to augment your model's responses with external
data. For example:

- Searching documents for relevant context using FAISS or similar tools.
- Passing the retrieved data to the model for more informed responses.

### 4. Agents

Agents can dynamically decide which tools or actions to use based on the input.
This flexibility is crucial for creating adaptable systems.

## Setting Up

### Building and Running the Docker Container

1. **Activate virtual environment:**
   ```bash
   > source dev_scripts_tutorial_langchain/thin_client/setenv.sh
   ```
2. **Build Docker Image:**
   ```bash
   > i docker_build_local_image --version 1.0.0
   ```
3. **Run Container:**
   ```bash
   > i docker_bash --skip-pull --stage local --version 1.0.0
   ```
4. **Launch Jupyter Notebook:**
   ```bash
   > i docker_jupyter --skip-pull --stage local --version 1.0.0 -d
   ```

### Dependencies

To start, ensure you have:

1. Installed LangChain and necessary dependencies.
2. Configured your OpenAI API key.

The `ChatOpenAI` model serves as the backbone for generating responses in this
tutorial. It's configured with a low temperature (`0`) to ensure deterministic
outputs.

## Message Handling

![alt text](/image-1.png)

LangChain provides `SystemMessage` and `HumanMessage` to structure
conversations. These objects enable fine-grained control:

- **SystemMessage**: Defines the assistant's behavior or scope.
- **HumanMessage**: Represents user input.

### Why This Is Important

By explicitly defining roles, you can control the assistant's responses,
ensuring relevance and accuracy.

## Custom Prompts

![alt text](/image-2.png)

Prompts are critical in defining the tasks a language model performs. LangChain
provides the `ChatPromptTemplate` for creating structured prompts. These prompts
allow dynamic input formatting, making them reusable for various applications.

### Example Use Case

Imagine creating a system to analyze patient reviews for hospitals. You can
define a prompt template that:

1. Provides clear instructions to the assistant.
2. Dynamically includes the review context and question.

This modularity ensures clarity and consistency across tasks.

## Chains

Chains are reusable workflows that link prompts, models, and parsers. They
simplify complex operations, such as:

- Processing user queries.
- Generating structured outputs.

### Example Workflow

A chain could:

1. Format user input using a prompt.
2. Pass the formatted input to the language model.
3. Parse the output into a structured format (e.g., text, JSON).

### Why Chains Matter:

Chains reduce boilerplate code, making your application more maintainable and
modular.

## Retrieval with FAISS

![alt text](/image-5.png)

Retrieval mechanisms like FAISS allow you to augment language models with
external data. FAISS (Facebook AI Similarity Search) is an efficient library for
dense vector search, making it ideal for retrieving relevant documents or
embeddings.

### Example Use Case

You might have a collection of patient reviews stored as embeddings in FAISS.
When a user queries, the system retrieves the top-matching reviews, enhancing
the assistant's ability to answer.

### Key Features

- **Embedding Creation:** Convert text into vector representations.
- **Similarity Search:** Quickly find the closest matches to a query.

## Building a QA System

![alt text](/image-4.png)

Combining retrieval with chains allows you to build a robust QA system. The
workflow might look like this:

1. **Retrieve Context:** Use FAISS to fetch relevant documents based on user
   queries.
2. **Format Input:** Pass the retrieved context and user query to a prompt
   template.
3. **Generate Response:** Use the language model to create a detailed answer.

### Why This Matters

This approach improves accuracy by grounding responses in factual data, reducing
the risk of hallucination.

## Agents and Tools

![alt text](/image-3.png)

Agents are flexible systems capable of deciding which tools or workflows to use
dynamically. LangChain agents can:

1. Combine multiple tools, such as retrieval mechanisms or APIs.
2. Use decision logic to select the appropriate tool based on the input.

### Example Use Case

An agent could:

1. Use FAISS to retrieve documents.
2. Summarize the retrieved content.
3. Provide additional insights or suggest further reading.

This dynamic capability makes agents ideal for complex, multi-step tasks.
