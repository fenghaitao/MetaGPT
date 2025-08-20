#!/usr/bin/env python
"""
Example usage of GitHub Copilot provider in MetaGPT

This example shows how to configure and use the GitHub Copilot provider
for LLM interactions within the MetaGPT framework.
"""

import asyncio
from metagpt.configs.llm_config import LLMConfig, LLMType
from metagpt.provider.github_copilot_api import GitHubCopilotLLM


async def main():
    """Example of using GitHub Copilot provider"""
    
    # Configuration for GitHub Copilot (using LiteLLM with OAuth2)
    config = LLMConfig(
        api_type=LLMType.GITHUB_COPILOT,
        # No API key needed - GitHub Copilot uses OAuth2 authentication
        model="gpt-4o",  # Available: gpt-4o, gpt-4.1, gpt-5-mini, gpt-5 (github_copilot/ prefix added automatically)
        # max_token will be auto-set based on model capabilities from TOKEN_MAX
        temperature=0.0,
        calc_usage=True,
        timeout=600
    )
    
    # Initialize the provider
    llm = GitHubCopilotLLM(config)
    
    print("GitHub Copilot Provider Configuration (LiteLLM-based):")
    print(f"  Model: {llm.model}")
    print(f"  API Type: {llm.config.api_type}")
    print(f"  Uses LiteLLM: True")
    print()
    
    # Example 1: Simple question
    try:
        print("Example 1: Simple question")
        response = await llm.aask("What is Python?")
        print(f"Response: {response[:200]}...")
        print()
    except Exception as e:
        print(f"Note: This would work with a valid API key. Error: {e}")
        print()
    
    # Example 2: Code generation
    try:
        print("Example 2: Code generation")
        messages = [
            {"role": "user", "content": "Write a Python function to calculate fibonacci numbers"}
        ]
        code_response = await llm.aask_code(messages)
        print(f"Code response: {code_response}")
        print()
    except Exception as e:
        print(f"Note: This would work with a valid API key. Error: {e}")
        print()
    
    # Example 3: Message formatting
    print("Example 3: Message formatting")
    messages = [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Explain list comprehensions in Python"}
    ]
    formatted = llm.format_msg(messages)
    print(f"Formatted messages: {formatted}")
    print()
    
    print("✓ GitHub Copilot provider examples completed!")


if __name__ == "__main__":
    asyncio.run(main())