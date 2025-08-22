# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/5 23:08
@Author  : alexanderwu
@File    : github_api.py
"""
from __future__ import annotations
import os
import asyncio
from typing import Optional

from sydney import SydneyClient

from metagpt.configs.llm_config import LLMConfig, LLMType
from metagpt.provider.base_llm import BaseLLM
from metagpt.provider.llm_provider_registry import register_provider
from metagpt.utils.cost_manager import CostManager

@register_provider([LLMType.GITHUB])
class GitHubLLM(BaseLLM):
    """
    A class representing the GitHub Copilot language model.
    """

    def __init__(self, config: LLMConfig):
        """
        Initializes the GitHubLLM object.

        Args:
            config (LLMConfig): The configuration for the language model.
        """
        self.config = config
        self.cost_manager: Optional[CostManager] = None

    async def _achat_completion_stream(self, messages: list[dict], timeout=...):
        """
        Asynchronously chats with the language model in a streaming fashion.

        Args:
            messages (list[dict]): The list of messages in the chat.
            timeout (int, optional): The timeout for the request. Defaults to 600.

        Returns:
            str: The response from the language model.
        """
        async with SydneyClient(bing_cookies=os.environ.get("BING_COOKIES")) as sydney:
            prompt = messages[-1]["content"]
            response = ""
            async for token in sydney.ask_stream(prompt):
                response += token
            return response

    async def acompletion_text(self, messages: list[dict], stream=False, timeout=600) -> str:
        """
        Asynchronously completes the text using the language model.

        Args:
            messages (list[dict]): The list of messages in the chat.
            stream (bool, optional): Whether to use streaming. Defaults to False.
            timeout (int, optional): The timeout for the request. Defaults to 600.

        Returns:
            str: The completed text.
        """
        if stream:
            return await self._achat_completion_stream(messages, timeout=timeout)

        async with SydneyClient(bing_cookies=os.environ.get("BING_COOKIES")) as sydney:
            prompt = messages[-1]["content"]
            response, _ = await sydney.ask(prompt)
            return response

    def _update_costs(self, usage: dict):
        """
        Updates the costs based on the usage.

        Args:
            usage (dict): The usage dictionary.
        """
        if self.config.calc_usage:
            try:
                self.cost_manager.update_cost(
                    prompt_tokens=usage["prompt_tokens"],
                    completion_tokens=usage["completion_tokens"],
                    model=self.config.model,
                )
            except Exception as e:
                logger.error(f"Error updating costs: {e}")
