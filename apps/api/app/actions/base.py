from abc import ABC, abstractmethod
from typing import Any


class ActionExecutor(ABC):

    @abstractmethod
    async def execute(
        self,
        action_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        pass

