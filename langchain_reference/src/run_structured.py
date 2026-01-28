import pydantic
import langchain_openai
import argparse
from typing import cast, TypeAlias, Annotated


BaseModel = pydantic.BaseModel
Field = pydantic.Field
ValidationError = pydantic.ValidationError
ChatOpenAI = langchain_openai.ChatOpenAI
Confidence: TypeAlias = Annotated[float, Field(ge=0.0,le=1.0, description="0.0 to 1.0")]

class StructuredAnswer(BaseModel):
    answer: str = Field(description="The final answer.")
    assumptions: list[str] = Field(description="Assumptions made.")
    confidence: Confidence

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--question", required=True)
    args = parser.parse_args()

    chatbot = ChatOpenAI(model='gpt-5-nano', temperature=0.2)

    # Schematic Out.
    structured_bot = chatbot.with_structured_output(StructuredAnswer)

    try:
        out: StructuredAnswer = cast(StructuredAnswer, structured_bot.invoke(args.question))
    except ValidationError as e:
        # Fail.
        raise SystemExit(f"Junk outputted")
    
    print(out.model_dump_json)

if __name__ == "__main__":
    main()

