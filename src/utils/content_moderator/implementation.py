import httpx
from .abstract import AbstractContentModerator
from src.core.configs.content_moderator_config import ContentModeratorConfig


class ContentModerator(AbstractContentModerator):
    def __init__(self, config: ContentModeratorConfig):
        self._config = config

    async def moderate_text(self, text: str) -> bool:
        """
        Sends the text to the moderation API asynchronously and determines if it is appropriate.

        :param text: The text to be analyzed.
        :return: True if the text is safe, False if it should be flagged.
        """
        url = "https://api.sightengine.com/1.0/text/check.json"
        data = {
            'text': text,
            'mode': 'ml',
            'lang': 'en',
            'models': 'general,self-harm',
            'api_user': self._config.api_user,
            'api_secret': self._config.api_secret,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=data)
                response_data = response.json()

                if response_data.get('status') == 'success':
                    moderation_classes = response_data.get('moderation_classes', {})

                    # Check if any category exceeds the threshold of 0.60
                    for category, score in moderation_classes.items():
                        if category in moderation_classes.get('available', []) and score > 0.60:
                            return False  # Content should be flagged

                return True  # Content is safe
        except Exception as e:
            # Handle exception (you could log the error or raise an alert here)
            print(f"Error during moderation check: {e}")
            return False