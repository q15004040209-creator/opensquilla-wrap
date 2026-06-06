# opensquilla-wrap

> Python/TypeScript SDK wrapper for **[OpenSquilla](https://github.com/opensquilla/opensquilla)** — A token-efficient, microkernel AI agent for CLI, Web UI, and chat channels.

## What is OpenSquilla?

OpenSquilla is a **token-efficient AI agent** built around a local model router. A local model router sends each turn to a cheapest model that can handle it, while persistent memory, a layered sandbox, built-in web search, and on-device embeddings round out a single shared turn loop.

Every entry point — Web UI, CLI, and chat channels — runs through that same loop, so tool dispatch, retries, and decision logging behave identically everywhere. A pluggable provider layer speaks to OpenRouter, OpenAI, Anthropic, Ollama, DeepSeek, and 20+ other LLM providers with no code or config schema changes.

**Key features:**
- **Token-efficient:** Local model router picks the cheapest capable model per turn — dramatically reduces token costs
- **Microkernel architecture:** Thin core + layered sandbox + web search + on-device embeddings
- **Universal entry points:** Web UI, CLI, chat channels all share the same core loop
- **20+ LLM providers:** OpenRouter, OpenAI, Anthropic, Ollama, DeepSeek, Gemini, Qwen/DashScope, and more
- **Built-in web search:** Integrated search without external APIs
- **Persistent memory:** Layered sandbox for context continuity across sessions
- **Retry & decision logging:** Consistent behavior across all entry points

## What This Wrap Provides

This wrapper gives you **Python** and **TypeScript** SDKs to:

- Launch and configure OpenSquilla agents programmatically
- Route tasks to optimal models via the local model router
- Manage persistent memory and conversation context
- Integrate into AI pipelines, CLIs, and custom UIs

## Installation

```bash
# Python
pip install opensquilla-wrap

# Or from source
pip install .
```

```bash
# TypeScript / Node.js
npm install opensquilla-wrap
# or
yarn add opensquilla-wrap
```

## Python Demo

### Basic Usage

```python
import os
from opensquilla_wrap import OpenSquillaAgent

# Set your API key
os.environ["OPENROUTER_API_KEY"] = "sk-your-key"

# Initialize the agent
agent = OpenSquillaAgent(
    provider="openrouter",  # or "openai", "anthropic", "ollama", "deepseek"
    model="auto",           # "auto" = local router picks cheapest capable model
    web_search=True,        # Enable built-in web search
)

# Run a task
result = agent.run("What's the latest news about AI coding agents?")
print(result)
```

### With Specific Model and Memory

```python
import os
from opensquilla_wrap import OpenSquillaAgent

agent = OpenSquillaAgent(
    provider="openrouter",
    model="anthropic/claude-3-haiku",  # Specific model instead of "auto"
    memory_type="layered_sandbox",       # Persistent layered memory
)

# Multi-turn conversation with memory
agent.add_context("You are a Python expert helping with code review")
result = agent.run("Review the following code for security issues: ...")
print(result)

# Check memory state
print(f"Memory tokens used: {agent.get_memory_usage()}")
```

### Custom Provider Configuration

```python
from opensquilla_wrap import OpenSquillaAgent, ProviderConfig

# Configure multiple providers
config = ProviderConfig(
    openrouter={"api_key_env": "OPENROUTER_API_KEY"},
    deepseek={"api_key_env": "DEEPSEEK_API_KEY"},
    ollama={"base_url": "http://localhost:11434"},
)

agent = OpenSquillaAgent(
    providers=config,
    default_provider="openrouter",
    router_strategy="cheapest_capable",  # Pick cheapest model that can handle the task
)

# Route to specific provider
result = agent.run(
    "Explain quantum computing",
    provider="deepseek",
    model="deepseek-chat",
)
print(result)
```

## TypeScript Demo

```typescript
import { OpenSquillaAgent } from 'opensquilla-wrap';

// Initialize the agent
const agent = new OpenSquillaAgent({
  provider: 'openrouter',
  model: 'auto',  // Local router picks cheapest capable model
  webSearch: true,
  memoryType: 'layered_sandbox',
});

// Run a task
async function main() {
  const result = await agent.run('What are the best practices for TypeScript generics?');
  console.log('Result:', result);

  // Check memory usage
  console.log('Memory tokens:', agent.getMemoryUsage());
}

main().catch(console.error);
```

### Custom Providers (TypeScript)

```typescript
import { OpenSquillaAgent, ProviderConfig } from 'opensquilla-wrap';

const config = new ProviderConfig({
  openrouter: { apiKeyEnv: 'OPENROUTER_API_KEY' },
  deepseek: { apiKeyEnv: 'DEEPSEEK_API_KEY' },
  anthropic: { apiKeyEnv: 'ANTHROPIC_API_KEY' },
});

const agent = new OpenSquillaAgent({
  providers: config,
  defaultProvider: 'openrouter',
  routerStrategy: 'cheapest_capable',
});

// Route to specific provider
const result = await agent.run(
  'Write a Python decorator that caches function results',
  { provider: 'deepseek', model: 'deepseek-chat' }
);
console.log(result);
```

### Streaming Responses (TypeScript)

```typescript
import { OpenSquillaAgent } from 'opensquilla-wrap';

const agent = new OpenSquillaAgent({
  provider: 'openrouter',
  model: 'auto',
});

// Stream responses for real-time feedback
for await (const chunk of agent.runStream('Explain how transformers work')) {
  process.stdout.write(chunk);
}
console.log();
```

## How the Token-Efficient Router Works

OpenSquilla's local model router evaluates each turn and selects the **cheapest model** that can reliably handle the task:

1. **Task analysis** — Router classifies the turn by complexity (simple Q&A, code generation, reasoning, etc.)
2. **Model capability mapping** — Each configured model is mapped to task types it handles well
3. **Cost ranking** — Models are ranked by cost-per-token within each capability tier
4. **Selection** — Cheapest capable model is selected for the turn

This means simple tasks use cheap models (e.g., Haiku at ~$0.50/million tokens) while complex reasoning uses premium models — **without any configuration from the user**.

## Original Project

- **GitHub:** https://github.com/opensquilla/opensquilla
- **Docs:** https://opensquilla.ai/docs
- **License:** Apache 2.0

## License

Apache 2.0 License — see original project for details.