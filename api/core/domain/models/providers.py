from enum import StrEnum


# Providers are ordered by priority, meaning
# that the higher the provider is in the enum the more
# changes it will get to be selected
class Provider(StrEnum):
    FIREWORKS = "fireworks"
    # Anthropic is the default provider for Anthropic models
    # Bedrock is ok but it throttles instead of returning 429s
    # Which is very inconvenient
    ANTHROPIC = "anthropic"
    AMAZON_BEDROCK = "amazon_bedrock"
    # OpenAI is the default provider for OpenAI models
    # We tried Azure for a while but it is no way reliable
    OPEN_AI = "openai"
    AZURE_OPEN_AI = "azure_openai"
    GOOGLE = "google"
    GROQ = "groq"
    MISTRAL_AI = "mistral_ai"
    GOOGLE_GEMINI = "google_gemini"
    X_AI = "xai"
