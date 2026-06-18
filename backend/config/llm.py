from functools import lru_cache
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_mistralai import ChatMistralAI
from config.settings import settings


def _build_llm() -> BaseChatModel:
    """Instantiate the LLM based on `default_llm_provider` in settings."""
    provider = settings.default_llm_provider.lower()

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set in .env or environment.")
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
        )

    if provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set in .env or environment.")
        return ChatAnthropic(
            model=settings.anthropic_model,
            api_key=settings.anthropic_api_key,
        )

    if provider == "mistral":
        if not settings.mistral_api_key:
            raise ValueError("MISTRAL_API_KEY is not set in .env or environment.")
        return ChatMistralAI(
            model=settings.mistral_model,
            api_key=settings.mistral_api_key,
        )

    raise ValueError(
        f"Unsupported LLM provider: '{provider}'. "
        "Choose from: 'openai', 'anthropic', 'mistral'."
    )


@lru_cache(maxsize=1)
def get_llm() -> BaseChatModel:
    """
    Returns a cached LLM instance. The instance is created once and reused
    across all calls, avoiding repeated instantiation overhead.
    """
    return _build_llm()
