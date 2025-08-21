#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2025/08/21 07:00
@Author  : rovo-dev
@File    : github_copilot_api.py
@Desc    : GitHub Copilot API provider using LiteLLM
"""
from __future__ import annotations

import os
from typing import Optional

try:
    import litellm
    from litellm import acompletion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

from metagpt.configs.llm_config import LLMConfig, LLMType
from metagpt.const import USE_CONFIG_TIMEOUT
from metagpt.logs import log_llm_stream, logger
from metagpt.provider.base_llm import BaseLLM
from metagpt.provider.llm_provider_registry import register_provider
from metagpt.utils.cost_manager import CostManager
from metagpt.utils.token_counter import count_message_tokens, count_output_tokens, TOKEN_MAX


@register_provider([LLMType.GITHUB_COPILOT])
class GitHubCopilotLLM(BaseLLM):
    """GitHub Copilot API provider using LiteLLM
    
    This provider uses LiteLLM to interface with GitHub Copilot's API,
    which handles authentication and headers automatically.
    """

    def __init__(self, config: LLMConfig):
        if not LITELLM_AVAILABLE:
            raise ImportError(
                "LiteLLM is required for GitHub Copilot provider. "
                "Install it with: pip install litellm"
            )
        
        self.config = config
        self._init_client()
        self.cost_manager: Optional[CostManager] = None

    def _init_client(self):
        """Initialize the GitHub Copilot client with LiteLLM"""
        # Supported GitHub Copilot models
        supported_models = ["gpt-4o", "gpt-4.1", "gpt-5-mini", "gpt-5"]
        
        # Set default model if not provided
        if not self.config.model:
            self.config.model = "github_copilot/gpt-4o"
        elif not self.config.model.startswith("github_copilot/"):
            # Validate model is supported
            if self.config.model not in supported_models:
                raise ValueError(
                    f"Unsupported GitHub Copilot model: {self.config.model}. "
                    f"Supported models: {', '.join(supported_models)}"
                )
            # Ensure model has the github_copilot/ prefix for LiteLLM
            self.config.model = f"github_copilot/{self.config.model}"
        else:
            # Extract base model name and validate
            base_model = self.config.model.replace("github_copilot/", "")
            if base_model not in supported_models:
                raise ValueError(
                    f"Unsupported GitHub Copilot model: {base_model}. "
                    f"Supported models: {', '.join(supported_models)}"
                )
        
        self.model = self.config.model
        self.pricing_plan = self.config.pricing_plan or self.model
        
        # Note: max_token handling is now done in _get_max_tokens() method following base LLM pattern
        
        # Configure LiteLLM settings
        litellm.set_verbose = False  # Set to True for debugging
        if self.config.proxy:
            litellm.proxy = self.config.proxy

    async def _achat_completion(self, messages: list[dict], timeout=USE_CONFIG_TIMEOUT):
        """Async chat completion using LiteLLM"""
        kwargs = self._cons_kwargs(messages, timeout=self.get_timeout(timeout))
        
        try:
            response = await acompletion(**kwargs)
            self._update_costs(response.usage)
            return response
        except Exception as e:
            logger.error(f"GitHub Copilot API error: {e}")
            raise

    async def acompletion(self, messages: list[dict], timeout=USE_CONFIG_TIMEOUT):
        """Asynchronous completion interface"""
        return await self._achat_completion(messages, timeout=self.get_timeout(timeout))

    async def _achat_completion_stream(self, messages: list[dict], timeout=USE_CONFIG_TIMEOUT) -> str:
        """Async streaming chat completion using LiteLLM"""
        kwargs = self._cons_kwargs(messages, timeout=self.get_timeout(timeout), stream=True)
        
        collected_messages = []
        usage = None
        
        try:
            response = await acompletion(**kwargs)
            async for chunk in response:
                if hasattr(chunk, 'choices') and chunk.choices:
                    choice = chunk.choices[0]
                    if hasattr(choice, 'delta') and choice.delta.content:
                        content = choice.delta.content
                        log_llm_stream(content)
                        collected_messages.append(content)
                    
                    # Check for usage information
                    if hasattr(chunk, 'usage') and chunk.usage:
                        usage = chunk.usage
            
            log_llm_stream("\n")
            full_content = "".join(collected_messages)
            
            # Calculate usage if not provided
            if not usage:
                usage = self._calc_usage(messages, full_content)
            
            self._update_costs(usage)
            return full_content
            
        except Exception as e:
            logger.error(f"GitHub Copilot streaming error: {e}")
            raise

    def _get_max_tokens(self, messages: list[dict]) -> int:
        """Get max tokens for the model, using TOKEN_MAX lookup or config default"""
        # Use model-specific limit from TOKEN_MAX if available, otherwise use config
        model_max_tokens = TOKEN_MAX.get(self.model, self.config.max_token)
        return model_max_tokens

    def _cons_kwargs(self, messages: list[dict], timeout=USE_CONFIG_TIMEOUT, **extra_kwargs) -> dict:
        """Construct kwargs for LiteLLM completion"""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self._get_max_tokens(messages),
            "temperature": self.config.temperature,
            "timeout": self.get_timeout(timeout),
        }
        
        # Add required headers for GitHub Copilot IDE authentication
        extra_headers = {
            "Editor-Version": "vscode/1.85.0",
            "Copilot-Integration-Id": "vscode-chat"
        }
        kwargs["extra_headers"] = extra_headers
        
        # Add optional parameters
        if self.config.top_p != 1.0:
            kwargs["top_p"] = self.config.top_p
        if self.config.frequency_penalty != 0.0:
            kwargs["frequency_penalty"] = self.config.frequency_penalty
        if self.config.presence_penalty != 0.0:
            kwargs["presence_penalty"] = self.config.presence_penalty
        if self.config.stop:
            kwargs["stop"] = self.config.stop
        
        if extra_kwargs:
            kwargs.update(extra_kwargs)
        
        return kwargs

    async def acompletion_text(self, messages: list[dict], stream=False, timeout=USE_CONFIG_TIMEOUT) -> str:
        """Asynchronous completion returning text"""
        if stream:
            return await self._achat_completion_stream(messages, timeout=timeout)
        
        response = await self._achat_completion(messages, timeout=self.get_timeout(timeout))
        return self.get_choice_text(response)

    def get_choice_text(self, response) -> str:
        """Extract text from LiteLLM response"""
        if hasattr(response, 'choices') and response.choices:
            return response.choices[0].message.content or ""
        return ""

    def _normalize_model_name(self, model_name: str) -> str:
        """Remove provider prefix from model name if present."""
        if model_name.startswith("github_copilot/"):
            return model_name[len("github_copilot/") :]
        return model_name

    def _calc_usage(self, messages: list[dict], response: str):
        """Calculate token usage"""
        if not self.config.calc_usage:
            return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        try:
            normalized_model = self._normalize_model_name(self.pricing_plan)
            prompt_tokens = count_message_tokens(messages, normalized_model)
            completion_tokens = count_output_tokens(response, normalized_model)
            return {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            }
        except Exception as e:
            logger.warning(f"Usage calculation failed: {e}")
            return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
