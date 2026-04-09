"""
AI client factory for generating credit narratives.
Supports both Claude (Anthropic) and Azure OpenAI.

Reference: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/switching-endpoints
"""

from anthropic import Anthropic
from openai import AzureOpenAI
import config


class ClaudeClient:
    """Wrapper for Anthropic Claude API."""

    def __init__(self):
        self.api_key = config.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = Anthropic(api_key=self.api_key)
        self.model = config.CLAUDE_MODEL

    def generate_narrative(self, prompt: str, max_tokens: int = 200) -> str:
        """
        Generate text using Claude API.

        Args:
            prompt: The prompt to send to Claude
            max_tokens: Maximum tokens in response

        Returns:
            Generated text
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                timeout=30.0,  # 30 second timeout to prevent hanging
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return message.content[0].text

        except TimeoutError:
            print(f"⚠️  Claude API timeout after 30 seconds")
            return f"Credit decision processed. Status: approved/rejected based on transaction history."
        except Exception as e:
            print(f"⚠️  Claude API error: {str(e)}")
            return f"Credit decision processed. Status: approved/rejected based on transaction history."


class AzureOpenAIClient:
    """
    Wrapper for Azure OpenAI API.

    Reference: https://learn.microsoft.com/en-us/fabric/data-science/ai-services/how-to-use-openai-python-sdk
    Reference: https://python.plainenglish.io/using-azure-openai-with-python-a-step-by-step-guide-415d5850169b
    """

    def __init__(self):
        """Initialize Azure OpenAI client with configuration."""
        self.endpoint = config.AZURE_AI_PROJECT_ENDPOINT
        self.api_key = config.AZURE_API_KEY
        self.api_version = config.AZURE_API_VERSION
        self.deployment_name = config.AZURE_AI_MODEL_DEPLOYMENT_NAME

        if not self.endpoint:
            raise ValueError("AZURE_AI_PROJECT_ENDPOINT environment variable not set")
        if not self.api_key:
            raise ValueError("AZURE_API_KEY environment variable not set")

        # Initialize Azure OpenAI client
        # Note: Azure OpenAI uses deployment names, not model names
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )

    def generate_narrative(self, prompt: str, max_tokens: int = 200) -> str:
        """
        Generate text using Azure OpenAI API.

        Args:
            prompt: The prompt to send to Azure OpenAI
            max_tokens: Maximum tokens in response (for compatibility)

        Returns:
            Generated text

        Note: Uses max_completion_tokens for newer Azure models (GPT-4+)
        """
        try:
            # Newer Azure OpenAI models use max_completion_tokens instead of max_tokens
            # Reference: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/responses
            response = self.client.chat.completions.create(
                model=self.deployment_name,  # Deployment name in Azure
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful financial assistant that explains credit decisions clearly and concisely."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=max_tokens,  # Updated for newer Azure models
                temperature=0.7,
                top_p=0.95,
                timeout=30.0  # 30 second timeout to prevent hanging
            )

            return response.choices[0].message.content

        except TimeoutError:
            print(f"⚠️  Azure OpenAI API timeout after 30 seconds")
            return f"Credit decision processed. Status: approved/rejected based on transaction history."
        except Exception as e:
            print(f"⚠️  Azure OpenAI API error: {str(e)}")
            return f"Credit decision processed. Status: approved/rejected based on transaction history."


def get_ai_client():
    """
    Get AI client based on AI_PROVIDER environment variable.

    Returns:
        ClaudeClient or AzureOpenAIClient instance

    Environment Variables:
        AI_PROVIDER: "claude" (default) or "azure"
    """
    provider = config.AI_PROVIDER.lower()

    if provider == "azure":
        if not hasattr(get_ai_client, "_azure_instance"):
            get_ai_client._azure_instance = AzureOpenAIClient()
        return get_ai_client._azure_instance
    else:  # Default to Claude
        if not hasattr(get_ai_client, "_claude_instance"):
            get_ai_client._claude_instance = ClaudeClient()
        return get_ai_client._claude_instance


# Backward compatibility
def get_claude_client() -> ClaudeClient:
    """Get Claude client (backward compatibility)."""
    if not hasattr(get_claude_client, "_instance"):
        get_claude_client._instance = ClaudeClient()
    return get_claude_client._instance
