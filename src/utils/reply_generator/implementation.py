import google.generativeai as genai
from src.core.configs.reply_generator_config import generation_config, chat_history
from src.core.settings import settings


genai.configure(api_key=settings.gemini_api_key)

from .abstract import AbstractReplyGenerator


class ReplyGenerator(AbstractReplyGenerator):
    """
    Generates answers to prompts using Gemini AI
    """
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

    async def generate_reply(self, prompt: str) -> str:
        chat_session = self.model.start_chat(history=chat_history)
        response = await chat_session.send_message_async(prompt)
        return response.text
