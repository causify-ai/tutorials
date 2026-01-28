import argparse
import config


parser = argparse.ArgumentParser()
get_chat_model = config.get_chat_model

def main():
    parser.add_argument("-q", "--question", required=True, help="Your question to the LLM")
    args = parser.parse_args()
    question = args.question

    chat_model = get_chat_model()
    response = chat_model.invoke(question) # invoke passes the query

    print(response.content) # content has the answer
    print(f"Structured Output:\n{response}")

if __name__ == "__main__":
    main()
