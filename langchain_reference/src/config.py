import os
import dataclasses
import functools
import pydantic

import dotenv
import langchain_openai
import langchain_anthropic # ChatAnthropic
import langchain_google_genai # ChatGoogleGenerativeAI
# import langchain_groq # ChatGroq
# import langchain_mistralai # ChatMistralAI
# import langchain_ollama # ChatOllama


dataclass = dataclasses.dataclass
lru_cache = functools.lru_cache
ChatOpenAI = langchain_openai.ChatOpenAI
ChatAnthropic = langchain_anthropic.ChatAnthropic
ChatGoogleGenerativeAI = langchain_google_genai.ChatGoogleGenerativeAI
# ChatGroq = langchain_groq.ChatGroq
# ChatMistralAI = langchain_mistralai.ChatMistralAI
# ChatOllama = langchain_ollama.ChatOllama
SecretStr = pydantic.SecretStr

# Load Variables
dotenv.load_dotenv()


# Immutable data class
@dataclass(frozen=True)
class Settings:
    provider: str
    model: str
    temperature: float
    timeout: float
    max_retries: int

def _need(name:str) -> str:
    v = os.getenv(name)
    if v is None or v == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return v

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        provider=os.getenv("LLM_PROVIDER", "openai"),
        model=os.getenv("LLM_MODEL", "gpt-5-nano"),
        temperature=float(os.getenv("LLM_TEMP", 0.2)),
        timeout=float(os.getenv("LLM_TIMEOUT", 60)),
        max_retries=int(os.getenv("LLM_MAX_RETRIES", 2)),

    )

@lru_cache(maxsize=1)
def get_chat_model():
    s = get_settings()

    # OpenAI-adjacent

    if s.provider == "openai":

        # READ API KEY.
        _need("OPENAI_API_KEY")

        # Return the chatmodel

        return ChatOpenAI(
            model=s.model,
            temperature=s.temperature,
            timeout=s.timeout,
            max_retries=s.max_retries,
        )
    
    if s.provider == "openai_compatible":

        # Secrets.
        base_url = _need("OPENAI_COMPAT_BASE_URL")
        api_key = _need("OPENAI_COMPAT_API_KEY")
        return ChatOpenAI(
            model=s.model,
            base_url=base_url,
            api_key=SecretStr(api_key),
            temperature=s.temperature,
            timeout=s.timeout,
            max_retries=s.max_retries,

        )
    
    if s.provider == "azure_openai_v1":

        # Secrets.
        azure_base = _need("AZURE_OPENAI_BASE_URL")
        azure_key = SecretStr(_need("AZURE_OPENAI_API_KEY"))

        return ChatOpenAI(
            model=s.model,
            base_url=azure_base,
            api_key=azure_key,
            temperature=s.temperature,
            timeout=s.timeout,
            max_retries=s.max_retries,

        )

    # Anthropic 
    
    if s.provider == "anthropic":

        # Secrets.
        _need("ANTHROPIC_API_KEY") 
        return ChatAnthropic(
            model_name=s.model,
            temperature=s.temperature,
            timeout=s.timeout,
            max_retries=s.max_retries,
            stop=None
            )
    
    # Google
    if s.provider in ("google", "gemini", "google_genai"):
        # Secrets.
        _need("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(
            model=s.model,
            temperature=s.temperature,
        )




    
    raise ValueError("TODO(*): expand support!")
