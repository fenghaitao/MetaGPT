# -*- coding: utf-8 -*-
"""
@Time    : 2023/5/5 23:08
@Author  : alexanderwu
@File    : test_github_api.py
"""
import pytest
from unittest.mock import AsyncMock, patch

from metagpt.configs.llm_config import LLMConfig, LLMType
from metagpt.provider.github_api import GitHubLLM

@pytest.mark.asyncio
async def test_github_llm_acompletion_text():
    """
    Test the acompletion_text method of the GitHubLLM class.
    """
    config = LLMConfig(api_type=LLMType.GITHUB, model="gpt-4.1")
    llm = GitHubLLM(config)

    messages = [{"role": "user", "content": "Hello, world!"}]
    expected_response = "Hello, world! I am a language model."

    with patch("metagpt.provider.github_api.SydneyClient") as MockSydneyClient:
        mock_sydney_instance = MockSydneyClient.return_value.__aenter__.return_value
        mock_sydney_instance.ask = AsyncMock(return_value=(expected_response, None))

        response = await llm.acompletion_text(messages)

        assert response == expected_response
        mock_sydney_instance.ask.assert_called_once_with("Hello, world!")
