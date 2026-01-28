import argparse
import langchain_core.prompts
import langchain_core.output_parsers
import langchain_core.runnables

import config

ChatPromptTemplate = langchain_core.prompts.ChatPromptTemplate
StrOutputParser = langchain_core.output_parsers.StrOutputParser
RunnableParallel = langchain_core.runnables.RunnableParallel
get_chat_model = config.get_chat_model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--text", required=True)
    args = parser.parse_args()

    llm = get_chat_model()

    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", "You have one goal in life: Crisp, accurate summaries."),
        ("human", "Summarize the following text in 4-6 bullets:\n\n{text}"),
    ])

    risks_prompt = ChatPromptTemplate.from_messages([
        ("system", "You identify risks and failure modes."),
        ("human", "List potential risks, caveats, or uncertainties in the text:\n\n{text}"),
    ])

    summary_chain = summary_prompt | llm | StrOutputParser()
    risk_chain = risks_prompt | llm | StrOutputParser()

    parallel = RunnableParallel(
        summary=summary_chain,
        risks = risk_chain,
    )

    out = parallel.invoke(
        {"text": args.text},
        # Runnable config can control concurrency through max_concurrency
        config={"max_concurrency": 2},
    )

    print(f"\n------SUMMARY--------\n\n{out['summary']}")
    print(f"\n------RISKS--------\n\n{out['risks']}")

if __name__ == "__main__":
    main()
