import json
import os
import re
from typing import Any

try:
    from google import genai
except ImportError:
    genai = None


class AIService:
    """
    Central Gemini integration.

    The project documentation specifies Gemini for Q&A, summarization,
    quizzes and learning paths. The original document also mentions
    LaMini-Flan-T5 for explanations. This implementation keeps the
    explanation feature in the same API surface while using Gemini by
    default so the application works without a large local model.
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.client = None

        if self.api_key and genai is not None:
            self.client = genai.Client(api_key=self.api_key)

    @property
    def configured(self) -> bool:
        return self.client is not None

    def _missing_key_message(self) -> str:
        return (
            "Gemini is not configured. Create a .env file and set "
            "GEMINI_API_KEY=your_key, then restart the server."
        )

    async def _generate(self, prompt: str) -> str:
        if not self.configured:
            return self._missing_key_message()

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            text = getattr(response, "text", None)
            if not text:
                return "The AI returned an empty response. Please try again."
            return text.strip()
        except Exception as exc:
            return f"AI request failed: {type(exc).__name__}: {exc}"

    async def qa(self, question: str) -> str:
        prompt = f"""
You are EduGenie, a student-friendly educational assistant.
Answer the question accurately and concisely.
Use simple language, short sections, and examples when useful.
Do not invent facts. If the question is ambiguous, state the assumption.

Question:
{question}
"""
        return await self._generate(prompt)

    async def explain(self, topic: str) -> str:
        prompt = f"""
Explain the following topic to a beginner.
Use this structure:
1. Simple definition
2. How it works
3. Small example
4. Key points to remember

Topic:
{topic}
"""
        return await self._generate(prompt)

    @staticmethod
    def _extract_json(text: str) -> Any:
        cleaned = re.sub(r"```(?:json)?", "", text, flags=re.I).strip()
        cleaned = cleaned.replace("```", "").strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.S)
            if not match:
                raise
            return json.loads(match.group(1))

    async def quiz(self, passage: str) -> Any:
        prompt = f"""
Create exactly 3 multiple-choice questions from the educational text below.
Return ONLY valid JSON. No markdown and no extra text.

JSON format:
{{
  "questions": [
    {{
      "question": "string",
      "options": ["A", "B", "C", "D"],
      "answer": "A",
      "explanation": "short explanation"
    }}
  ]
}}

The answer field must be exactly one of A, B, C, or D.

Educational text:
{passage}
"""
        raw = await self._generate(prompt)
        if raw.startswith("Gemini is not configured") or raw.startswith("AI request failed"):
            return {"error": raw}

        try:
            data = self._extract_json(raw)
            if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
                raise ValueError("Invalid quiz structure")
            return data
        except Exception:
            return {
                "error": "The AI returned an invalid quiz format. Please try again.",
                "raw": raw,
            }

    async def summarize(self, passage: str) -> str:
        prompt = f"""
Summarize this educational passage for quick revision.
Keep the important facts and meaning.
Use a short heading followed by concise bullet points.
Avoid adding information not present in the passage.

Passage:
{passage}
"""
        return await self._generate(prompt)

    async def learning_path(self, topic: str, level: str) -> str:
        prompt = f"""
Create a personalized learning path for the topic "{topic}".
Learner level: {level}.

Include:
- Learning goal
- Beginner to advanced sequence
- Suggested timeline
- Practice tasks
- Revision checkpoints
- Useful resource types (videos, documentation, books, practice sites)
- A final mini-project or assessment

Keep it practical and easy for a student to follow.
"""
        return await self._generate(prompt)
