"""
OpenSquilla Python Wrapper
Wraps opensquilla/opensquilla as a Python SDK for token-efficient AI agents.
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, List, Optional, Union


@dataclass
class ProviderConfig:
    """Configuration for one or more LLM providers."""
    openrouter: Optional[Dict[str, Any]] = None
    openai: Optional[Dict[str, Any]] = None
    anthropic: Optional[Dict[str, Any]] = None
    deepseek: Optional[Dict[str, Any]] = None
    ollama: Optional[Dict[str, Any]] = None
    gemini: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {}
        for key, value in self.__dict__.items():
            if value is not None:
                result[key] = value
        return result


@dataclass
class AgentOptions:
    """Options for the OpenSquilla agent."""
    provider: str = "openrouter"
    model: str = "auto"
    api_key: Optional[str] = None
    web_search: bool = False
    memory_type: str = "layered_sandbox"
    max_retries: int = 3
    timeout: int = 120


class OpenSquillaAgent:
    """
    Python SDK for OpenSquilla.

    A token-efficient AI agent with a local model router that picks
    the cheapest capable model for each turn.

    Usage:
        agent = OpenSquillaAgent(provider="openrouter", model="auto")
        result = agent.run("What's the weather?")
        print(result)
    """

    def __init__(
        self,
        provider: str = "openrouter",
        model: str = "auto",
        api_key: Optional[str] = None,
        web_search: bool = False,
        memory_type: str = "layered_sandbox",
        max_retries: int = 3,
        timeout: int = 120,
        providers: Optional[ProviderConfig] = None,
        router_strategy: str = "cheapest_capable",
        binary_path: Optional[str] = None,
    ):
        self.provider = provider
        self.model = model
        self.api_key = api_key or self._resolve_api_key(provider)
        self.web_search = web_search
        self.memory_type = memory_type
        self.max_retries = max_retries
        self.timeout = timeout
        self.providers = providers
        self.router_strategy = router_strategy
        self.binary_path = binary_path or self._find_binary()
        self._context: List[Dict[str, str]] = []
        self._memory_tokens = 0

    def _resolve_api_key(self, provider: str) -> Optional[str]:
        """Resolve API key from environment for the given provider."""
        env_vars = {
            "openrouter": "OPENROUTER_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "ollama": None,  # No API key needed
        }
        env_name = env_vars.get(provider, "OPENROUTER_API_KEY")
        return os.environ.get(env_name)

    def _find_binary(self) -> str:
        """Look for opensquilla binary in PATH or common locations."""
        import shutil
        binary = shutil.which("opensquilla")
        if binary:
            return binary
        for candidate in [
            os.path.expanduser("~/.local/bin/opensquilla"),
            "/usr/local/bin/opensquilla",
            "C:\\Program Files\\OpenSquilla\\opensquilla.exe",
        ]:
            if os.path.isfile(candidate):
                return candidate
        return "opensquilla"

    def _build_env(self) -> Dict[str, str]:
        env = os.environ.copy()
        if self.api_key:
            env["OPENROUTER_API_KEY"] = self.api_key
        return env

    def add_context(self, text: str) -> None:
        """Add persistent context to the agent's memory."""
        self._context.append({"role": "system", "content": text})

    def get_memory_usage(self) -> int:
        """Return approximate token count for current memory."""
        total = sum(len(msg["content"]) // 4 for msg in self._context)
        return total + self._memory_tokens

    def run(self, task: str, provider: Optional[str] = None, model: Optional[str] = None) -> str:
        """
        Run a task synchronously and return the full response.

        Args:
            task: The task description for the agent
            provider: Override the default provider
            model: Override the default model

        Returns:
            The agent's full response as a string
        """
        chunks = []
        for chunk in self.run_stream(task, provider=provider, model=model):
            chunks.append(chunk)
        return "".join(chunks)

    def run_stream(self, task: str, provider: Optional[str] = None, model: Optional[str] = None) -> Any:
        """
        Run a task and yield response chunks as they arrive.

        Args:
            task: The task description for the agent
            provider: Override the default provider
            model: Override the default model

        Yields:
            Response text chunks
        """
        effective_provider = provider or self.provider
        effective_model = model or self.model

        # Build the command
        cmd = [self.binary_path, "chat", "--provider", effective_provider]
        if effective_model != "auto":
            cmd.extend(["--model", effective_model])
        if self.web_search:
            cmd.append("--web-search")
        if self.router_strategy:
            cmd.extend(["--router", self.router_strategy])

        # Add context to the command
        if self._context:
            context_json = json.dumps(self._context)
            cmd.extend(["--context", context_json])

        cmd.extend(["--", task])

        try:
            proc = subprocess.Popen(
                cmd,
                env=self._build_env(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = proc.communicate(timeout=self.timeout)

            if proc.returncode != 0:
                return f"[ERROR] OpenSquilla exited with code {proc.returncode}: {stderr.decode('utf-8', errors='replace')}"

            output = stdout.decode("utf-8", errors="replace")
            # Parse JSON response if available
            try:
                data = json.loads(output)
                if isinstance(data, dict) and "text" in data:
                    yield data["text"]
                elif isinstance(data, dict) and "response" in data:
                    yield data["response"]
                else:
                    yield output
            except json.JSONDecodeError:
                yield output

        except subprocess.TimeoutExpired:
            proc.kill()
            yield f"[TIMEOUT] Agent timed out after {self.timeout}s"
        except FileNotFoundError:
            yield "[ERROR] OpenSquilla binary not found. Install from https://github.com/opensquilla/opensquilla"

    async def run_async(self, task: str, **kwargs) -> str:
        """Async version of run()."""
        return await asyncio.to_thread(self.run, task, **kwargs)

    def chat(self, message: str) -> str:
        """Send a single chat message and return the response."""
        return self.run(message)


def demo():
    """Demonstrates the Python SDK usage."""
    print("🪲 OpenSquilla Python Demo")
    print("─" * 40)

    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Set OPENROUTER_API_KEY or OPENAI_API_KEY to run this demo")
        print()
        print("  export OPENROUTER_API_KEY=sk-...")
        print()
        print("Or set api_key when initializing:")
        print("  agent = OpenSquillaAgent(api_key='sk-...')")
        return

    agent = OpenSquillaAgent(provider="openrouter", model="auto", web_search=True)

    print(f"Provider: {agent.provider}")
    print(f"Model: {agent.model} (auto-router)")
    print(f"Web Search: {agent.web_search}")
    print()

    print("Type 'exit' to quit.\n")
    while True:
        task = input("You: ")
        if task.lower() in ("exit", "quit", "q"):
            break
        if not task.strip():
            continue

        print("Agent: ", end="", flush=True)
        response = agent.run(task, timeout=120)
        print(response)
        print()


if __name__ == "__main__":
    demo()