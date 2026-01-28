import argparse
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config import get_chat_model

def read_questions(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    qs = [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]
    if not qs:
        raise SystemExit(f"Heh? No questions in {path}")
    return qs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-q","--questions", required=True, help="Path to a .txt file (one question per line)")
    parser.add_argument("--max-concurrency", type=int, default=5, help="Limit parallelism")
    args = parser.parse_args()

    qpath = Path(args.questions)
    if not qpath.exists():
        raise SystemExit(f"{qpath} does not exist tsk tsk do better")
    
    questions = read_questions(qpath)
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a concise tutor. Answer in 2-5 sentences."),
        ("human", "{question}"),
    ])

    chain = prompt | llm | StrOutputParser()
    inputs = [{"question": q} for q in questions]

    outputs = chain.batch(
        inputs,
        return_exceptions=True,
        config={"max_concurrency": args.max_concurrency},
    )

    for q, ans in zip(questions, outputs):
        if isinstance(ans, Exception):
            print(f"ERROR: {q}\n -> {type(ans).__name__}:{ans}\n")
        else:
            print(ans.strip())
            print("-----")

if __name__ == "__main__":
    main()