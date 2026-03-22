"""
Import as:

import src.config.config as cconf
"""

import dataclasses
import functools
import os

import dotenv
import langchain_anthropic
import langchain_google_genai
import langchain_openai
import pydantic

dataclass = dataclasses.dataclass
lru_cache = functools.lru_cache
ChatOpenAI = langchain_openai.ChatOpenAI
ChatAnthropic = langchain_anthropic.ChatAnthropic
ChatGoogleGenerativeAI = langchain_google_genai.ChatGoogleGenerativeAI
SecretStr = pydantic.SecretStr

dotenv.load_dotenv()


@dataclass(frozen=True)
class Settings:
    """
    Store model provider settings.
    """

    provider: str
    model: str
    temperature: float
    timeout: float
    max_retries: int


def _need(name: str) -> str:
    """
    Read a required environment variable.

    :param name: environment variable name
    :return: environment variable value
    """
    value = os.getenv(name)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Build settings from environment variables.

    :return: configured settings
    """
    settings = Settings(
        provider=os.getenv("LLM_PROVIDER", "openai"),
        model=os.getenv("LLM_MODEL", "gpt-5-nano"),
        temperature=float(os.getenv("LLM_TEMP", 0.2)),
        timeout=float(os.getenv("LLM_TIMEOUT", 60)),
        max_retries=int(os.getenv("LLM_MAX_RETRIES", 2)),
    )
    return settings


@lru_cache(maxsize=1)
def get_chat_model(*, model: str | None = None) -> object:
    """
    Build the configured chat model client.

    :param model: optional model override
    :return: langchain chat model client
    """
    settings = get_settings()
    model_name = settings.model if model is None else model
    provider = settings.provider
    if provider == "openai":
        _need("OPENAI_API_KEY")
        chat_model = ChatOpenAI(
            model=model_name,
            temperature=settings.temperature,
            timeout=settings.timeout,
            max_retries=settings.max_retries,
        )
    elif provider == "openai_compatible":
        base_url = _need("OPENAI_COMPAT_BASE_URL")
        api_key = _need("OPENAI_COMPAT_API_KEY")
        chat_model = ChatOpenAI(
            model=model_name,
            base_url=base_url,
            api_key=SecretStr(api_key),
            temperature=settings.temperature,
            timeout=settings.timeout,
            max_retries=settings.max_retries,
        )
    elif provider == "azure_openai_v1":
        azure_base = _need("AZURE_OPENAI_BASE_URL")
        azure_key = SecretStr(_need("AZURE_OPENAI_API_KEY"))
        chat_model = ChatOpenAI(
            model=model_name,
            base_url=azure_base,
            api_key=azure_key,
            temperature=settings.temperature,
            timeout=settings.timeout,
            max_retries=settings.max_retries,
        )
    elif provider == "anthropic":
        _need("ANTHROPIC_API_KEY")
        chat_model = ChatAnthropic(
            model_name=model_name,
            temperature=settings.temperature,
            timeout=settings.timeout,
            max_retries=settings.max_retries,
            stop=None,
        )
    elif provider in ("google", "gemini", "google_genai"):
        _need("GOOGLE_API_KEY")
        chat_model = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=settings.temperature,
        )
    else:
        raise ValueError(f"Unsupported provider='{provider}'")
    return chat_model
