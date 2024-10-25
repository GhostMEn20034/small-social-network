from abc import ABC, abstractmethod

class AbstractContentModerator(ABC):
    @abstractmethod
    async def moderate_text(self, text: str) -> bool:
        """
        Sends the text to the moderation API asynchronously and determines if it is appropriate.

        :param text: The text to be analyzed.
        :return: True if the text is safe, False if it should be flagged.
        """
        pass
