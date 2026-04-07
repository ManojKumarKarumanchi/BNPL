"""Claude API client for generating credit narratives."""

from anthropic import Anthropic
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
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return message.content[0].text

        except Exception as e:
            # Fallback to template if API fails
            return f"Credit decision processed. Status: approved/rejected based on transaction history."
