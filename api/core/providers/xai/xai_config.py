from typing import Literal

from pydantic import BaseModel

from core.domain.models.models import Model
from core.domain.models.providers import Provider
from core.providers.base.utils import ThinkingModelMap, ThinkingModelPair

THINKING_MODEL_MAP: ThinkingModelMap = {
    Model.GROK_3_MINI_BETA_HIGH_REASONING_EFFORT: ThinkingModelPair("grok-3-mini-beta", "high"),
    Model.GROK_3_MINI_BETA_LOW_REASONING_EFFORT: ThinkingModelPair("grok-3-mini-beta", "low"),
    Model.GROK_3_MINI_FAST_BETA_LOW_REASONING_EFFORT: ThinkingModelPair("grok-3-mini-fast-beta", "low"),
    Model.GROK_3_MINI_FAST_BETA_HIGH_REASONING_EFFORT: ThinkingModelPair("grok-3-mini-fast-beta", "high"),
}


class XAIConfig(BaseModel):
    provider: Literal[Provider.X_AI] = Provider.X_AI

    url: str = "https://api.x.ai/v1/chat/completions"
    api_key: str

    def __str__(self):
        return f"XAIConfig(url={self.url}, api_key={self.api_key[:4]}****)"
