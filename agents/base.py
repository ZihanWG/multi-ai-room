"""Base interface shared by all discussion agents."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Common base class for all agents."""

    def __init__(self, name: str, role_prompt: str) -> None:
        self.name = name
        self.role_prompt = role_prompt

    @abstractmethod
    def run(self, *args: str, **kwargs: str) -> str:
        """Run the agent and return its response as plain text."""

        raise NotImplementedError
