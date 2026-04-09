"""
Azure OpenAI API client for generating credit narratives.

Reference: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/switching-endpoints
Reference: https://python.plainenglish.io/using-azure-openai-with-python-a-step-by-step-guide-415d5850169b
"""

from openai import AzureOpenAI
import config


class AzureOpenAIClient:
    """Wrapper for Azure OpenAI API."""

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
        # Reference: https://learn.microsoft.com/en-us/fabric/data-science/ai-services/how-to-use-openai-python-sdk
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
            max_tokens: Maximum tokens in response

        Returns:
            Generated text

        Reference: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/responses
        """
        try:
            # Azure OpenAI uses deployment name instead of model name
            # Reference: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/switching-endpoints
            response = self.client.chat.completions.create(
                model=self.deployment_name,  # This is the deployment name in Azure
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
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.95
            )

            return response.choices[0].message.content

        except Exception as e:
            # Fallback to template if API fails
            print(f"⚠️  Azure OpenAI API error: {str(e)}")
            return f"Credit decision processed. Status: approved/rejected based on transaction history."


def get_azure_openai_client() -> AzureOpenAIClient:
    """
    Get or create Azure OpenAI client singleton.

    Returns:
        AzureOpenAIClient instance
    """
    if not hasattr(get_azure_openai_client, "_instance"):
        get_azure_openai_client._instance = AzureOpenAIClient()
    return get_azure_openai_client._instance
