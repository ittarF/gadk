import os
from litellm import completion
import litellm
from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

os.environ["OPENROUTER_API_KEY"] = "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"

agent_openai = LlmAgent(
    model=LiteLlm(model="openrouter/openrouter/quasar-alpha"), # LiteLLM model string format
    name="openrouter_agent",
    instruction="You are a helpful assistant.",
    # ... other agent parameters
)