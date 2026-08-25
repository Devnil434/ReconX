import json

from openai import OpenAI

from app.core.config import settings


class OpenAIProvider:

    def __init__(self):

        self.client = OpenAI(
            api_key=settings.openai_api_key
        )

        self.model = settings.openai_model

    def investigate(
        self,
        system_prompt: str,
        user_prompt: str,
    ):

        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_prompt,
        )

        return response.output_text