import os
import dotenv

dotenv.load_dotenv()

OPENCODE_GO_BASE = "https://opencode.ai/zen/go/v1"


def get_llm(model: str = "deepseek-v4-flash"):
    from langchain_openai import ChatOpenAI

    go_key = os.getenv("OPENCODE_GO_API_KEY")

    if go_key:
        return ChatOpenAI(
            model=model,
            api_key=go_key,
            base_url=OPENCODE_GO_BASE,
            temperature=0,
            max_tokens=4096,
        )

    raise RuntimeError(
        "No LLM API key found. Set OPENCODE_GO_API_KEY in your .env file.\n"
        "Get one at https://opencode.ai/auth"
    )
