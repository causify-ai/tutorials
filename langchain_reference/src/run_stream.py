import argparse
import sys

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config import get_chat_model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-q","--question", required=True)
    args = parser.parse_args()

    llm = get_chat_model()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a concise tutor. Answer clearly."),
        ("human", "{question}"),
    ])

    chain = prompt | llm | StrOutputParser()

    # Stream chunks as they arrive.
    chunks = []

    for chunk in chain.stream({"question": args.question}):
        chunks.append(chunk)
        sys.stdout.write(chunk)
        sys.stdout.flush()

    # have the final answer built
    final = "".join(chunks)
    # use final downstream

if __name__ == "__main__":
    main()