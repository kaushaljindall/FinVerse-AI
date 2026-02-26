"""
FinVerse AI — Multi-Layer LLM Fallback Provider
Primary: Gemini → Secondary: Groq → Tertiary: OpenAI
Gracefully degrades through providers if one fails.
"""

import asyncio
import logging
from typing import Optional, AsyncGenerator

logger = logging.getLogger(__name__)


class LLMProvider:
    """
    Multi-fallback LLM provider.
    Tries Gemini first, falls back to Groq, then OpenAI.
    """

    def __init__(self, settings):
        self.settings = settings
        self._providers = []
        self._init_providers()

    def _init_providers(self):
        """Initialize available LLM providers in priority order."""
        # Primary: Gemini
        if self.settings.GOOGLE_API_KEY:
            self._providers.append({
                "name": "gemini",
                "model": self.settings.GEMINI_MODEL,
                "init": self._init_gemini,
            })

        # Secondary: Groq (Llama 3)
        if self.settings.GROQ_API_KEY:
            self._providers.append({
                "name": "groq",
                "model": self.settings.GROQ_MODEL,
                "init": self._init_groq,
            })

        # Tertiary: OpenAI
        if self.settings.OPENAI_API_KEY:
            self._providers.append({
                "name": "openai",
                "model": self.settings.OPENAI_MODEL,
                "init": self._init_openai,
            })

        if not self._providers:
            logger.warning("⚠️ No LLM API keys configured! Set GOOGLE_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY")

    def _init_gemini(self):
        """Initialize Google Gemini client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.settings.GOOGLE_API_KEY)
            return genai.GenerativeModel(self.settings.GEMINI_MODEL)
        except Exception as e:
            logger.error(f"Failed to init Gemini: {e}")
            return None

    def _init_groq(self):
        """Initialize Groq client."""
        try:
            from groq import Groq
            return Groq(api_key=self.settings.GROQ_API_KEY)
        except Exception as e:
            logger.error(f"Failed to init Groq: {e}")
            return None

    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            return OpenAI(api_key=self.settings.OPENAI_API_KEY)
        except Exception as e:
            logger.error(f"Failed to init OpenAI: {e}")
            return None

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> tuple[str, str]:
        """
        Generate a response, trying each provider in order.
        Returns: (response_text, provider_name)
        """
        errors = []
        for provider in self._providers:
            try:
                name = provider["name"]
                logger.info(f"🧠 Trying LLM: {name} ({provider['model']})")

                if name == "gemini":
                    result = await self._generate_gemini(prompt, system_prompt, temperature, max_tokens)
                elif name == "groq":
                    result = await self._generate_groq(prompt, system_prompt, temperature, max_tokens, provider["model"])
                elif name == "openai":
                    result = await self._generate_openai(prompt, system_prompt, temperature, max_tokens, provider["model"])
                else:
                    continue

                if result:
                    logger.info(f"✅ LLM response from: {name}")
                    return result, name

            except Exception as e:
                error_msg = f"{provider['name']}: {str(e)}"
                errors.append(error_msg)
                logger.warning(f"⚠️ LLM fallback — {error_msg}")
                continue

        error_summary = "; ".join(errors) if errors else "No LLM providers configured"
        return f"I apologize, but I'm unable to process your request right now. All language model providers are unavailable. Errors: {error_summary}", "none"

    async def _generate_gemini(self, prompt: str, system_prompt: str, temperature: float, max_tokens: int) -> Optional[str]:
        """Generate with Google Gemini."""
        import google.generativeai as genai
        genai.configure(api_key=self.settings.GOOGLE_API_KEY)

        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        model = genai.GenerativeModel(
            self.settings.GEMINI_MODEL,
            system_instruction=system_prompt if system_prompt else None,
        )

        full_prompt = prompt
        response = await asyncio.to_thread(
            model.generate_content, full_prompt, generation_config=generation_config
        )

        if response and response.text:
            return response.text
        return None

    async def _generate_groq(self, prompt: str, system_prompt: str, temperature: float, max_tokens: int, model: str) -> Optional[str]:
        """Generate with Groq (Llama 3)."""
        from groq import Groq
        client = Groq(api_key=self.settings.GROQ_API_KEY)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if response and response.choices:
            return response.choices[0].message.content
        return None

    async def _generate_openai(self, prompt: str, system_prompt: str, temperature: float, max_tokens: int, model: str) -> Optional[str]:
        """Generate with OpenAI."""
        from openai import OpenAI
        client = OpenAI(api_key=self.settings.OPENAI_API_KEY)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if response and response.choices:
            return response.choices[0].message.content
        return None
