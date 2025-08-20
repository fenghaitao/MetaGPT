# GitHub Copilot Provider

The GitHub Copilot provider enables MetaGPT to use GitHub Copilot's API for LLM interactions. This provider uses LiteLLM to handle GitHub Copilot's authentication and API specifics automatically.

## Features

- **LiteLLM Integration**: Uses LiteLLM for robust GitHub Copilot API support
- **Automatic Authentication**: LiteLLM handles GitHub Copilot authentication and headers
- **Simplified Configuration**: No need to manage custom headers or endpoints
- **Model Support**: Supports GitHub Copilot's available models (gpt-4o, gpt-4.1, gpt-5-mini, gpt-5)
- **Streaming Support**: Full support for streaming responses
- **Cost Management**: Token counting and usage tracking

## Prerequisites

Before using the GitHub Copilot provider, you need to install LiteLLM:

```bash
pip install litellm
```

## Configuration

### Basic Configuration

Create a configuration file or update your existing `config2.yaml`:

```yaml
llm:
  api_type: "github_copilot"
  # No API key needed - GitHub Copilot uses OAuth2 authentication
  model: "gpt-4o"  # github_copilot/ prefix added automatically
  temperature: 0.0
  calc_usage: true
  timeout: 600
```

### Configuration Options

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| `api_type` | Must be set to "github_copilot" | Required |
| `model` | Model to use (prefix added automatically) | "github_copilot/gpt-4o" |
| `temperature` | Sampling temperature | 0.0 |
| `calc_usage` | Calculate token usage | true |
| `timeout` | Request timeout in seconds | 600 |

**Note**: 
- No API key is required - GitHub Copilot uses OAuth2 authentication
- The `github_copilot/` prefix is automatically added to model names if not present

### Available Models

- `gpt-4o` (recommended) → `github_copilot/gpt-4o`
- `gpt-4.1` → `github_copilot/gpt-4.1`
- `gpt-5-mini` → `github_copilot/gpt-5-mini`
- `gpt-5` → `github_copilot/gpt-5`

The `github_copilot/` prefix is automatically added by the provider.

## Usage Examples

### Basic Usage

```python
import asyncio
from metagpt.configs.llm_config import LLMConfig, LLMType
from metagpt.provider.github_copilot_api import GitHubCopilotLLM

async def main():
    config = LLMConfig(
        api_type=LLMType.GITHUB_COPILOT,
        # No API key needed - uses OAuth2 authentication
        model="gpt-4o"
    )
    
    llm = GitHubCopilotLLM(config)
    response = await llm.aask("What is Python?")
    print(response)

asyncio.run(main())
```

### Using with MetaGPT Registry

```python
from metagpt.configs.llm_config import LLMConfig, LLMType
from metagpt.provider.llm_provider_registry import create_llm_instance

config = LLMConfig(
    api_type=LLMType.GITHUB_COPILOT,
    # No API key needed - uses OAuth2 authentication
    model="gpt-4o"
)

llm = create_llm_instance(config)
```

### Code Generation

```python
messages = [
    {"role": "user", "content": "Write a Python function to calculate fibonacci numbers"}
]
code_response = await llm.aask_code(messages)
print(code_response)
```

## Authentication Setup

1. Ensure you have GitHub Copilot access through your GitHub account
2. Make sure you're logged into GitHub CLI or have GitHub authentication set up
3. LiteLLM will automatically handle OAuth2 authentication with GitHub Copilot
4. No additional API keys or tokens are required

## Technical Details

### LiteLLM Integration

The provider uses LiteLLM to handle GitHub Copilot API integration:

- **Authentication**: LiteLLM automatically handles GitHub Copilot authentication
- **Headers**: All required headers are managed by LiteLLM
- **Model Mapping**: Automatic model name prefixing with `github_copilot/`
- **Error Handling**: Robust error handling through LiteLLM

### Authentication

The provider uses OAuth2 authentication through LiteLLM:

- **No API keys required**: GitHub Copilot uses OAuth2 flow
- **Automatic authentication**: LiteLLM handles the OAuth2 process
- **GitHub CLI integration**: Works with existing GitHub authentication

### Inheritance

The `GitHubCopilotLLM` class inherits from `BaseLLM` and implements:

- Streaming responses via `_achat_completion_stream`
- Standard completion via `_achat_completion`
- Token counting and cost management
- Message formatting and processing
- Timeout and error handling

## Troubleshooting

### Common Issues

1. **Authentication Error**: Ensure you're logged into GitHub and have Copilot access
2. **OAuth2 Flow**: Make sure GitHub CLI is authenticated or OAuth2 flow is completed
3. **Model Not Found**: Verify the model name is supported by GitHub Copilot
4. **Rate Limiting**: GitHub Copilot may have different rate limits than OpenAI

### Debug Mode

Enable debug logging to see detailed request/response information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Example Configuration File

See `config/examples/github-copilot.yaml` for a complete configuration example.

## Integration with MetaGPT Roles

The GitHub Copilot provider can be used with any MetaGPT role that uses LLM functionality:

```python
from metagpt.roles.engineer import Engineer
from metagpt.configs.llm_config import LLMConfig, LLMType

config = LLMConfig(
    api_type=LLMType.GITHUB_COPILOT,
    # No API key needed - uses OAuth2 authentication
    model="gpt-4o"
)

engineer = Engineer(llm_config=config)
```
