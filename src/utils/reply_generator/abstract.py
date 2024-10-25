from abc import ABC, abstractmethod


class AbstractReplyGenerator(ABC):

    @abstractmethod
    async def generate_reply(self, prompt: str) -> str:
        pass
