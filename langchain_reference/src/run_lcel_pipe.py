import argparse
import langchain_core.prompts
import run_structured  
import config
from typing import cast
import langchain_core.output_parsers

ChatPromptTemplate = langchain_core.prompts.ChatPromptTemplate
StructuredAnswer = run_structured.StructuredAnswer
get_chat_model = config.get_chat_model
StrOutputParser = langchain_core.output_parsers.StrOutputParser

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--question", required=True)
    args = parser.parse_args()

    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer in 1 sentence ONLY."),
        ("human", "{question}"),
    ])

    structured_llm = llm.with_structured_output(StructuredAnswer)
    chain = prompt | llm | StrOutputParser()
    # out: StructuredAnswer = cast(StructuredAnswer, chain.invoke({"question": args.question}))
    out = chain.invoke({"question": args.question})
    # print(out.model_dump_json(indent=2))
    print(out)

if __name__ == "__main__":
    main()

