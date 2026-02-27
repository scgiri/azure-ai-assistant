from openai import AzureOpenAI

from config.settings import AzureOpenAISettings


def create_azure_openai_client(settings: AzureOpenAISettings) -> AzureOpenAI:
    return AzureOpenAI(
        api_key=settings.api_key,
        api_version=settings.api_version,
        azure_endpoint=settings.endpoint,
    )
