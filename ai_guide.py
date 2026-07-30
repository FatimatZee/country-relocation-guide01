"""Gemini-powered travel, study, and relocation guides."""

from __future__ import annotations

import os
import re
from pathlib import Path

from exceptions import GuideGenerationError
from models import Country, RelocationGuide


ALLOWED_PURPOSES = {"travel", "study", "relocate"}


class GeminiGuideGenerator:
    """Generate practical country guides with Google's Gemini API."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self._load_environment()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        self._client = None

    def generate(self, country: Country, purpose: str) -> RelocationGuide:
        """Create a structured guide from verified country facts and a user goal."""
        goal = purpose.strip().lower()
        if goal not in ALLOWED_PURPOSES:
            raise ValueError("Choose Travel, Study, or Relocate for the guide type.")
        if not self.api_key:
            raise GuideGenerationError("Add GEMINI_API_KEY to your .env file before generating a guide.")

        try:
            response = self._get_client().models.generate_content(
                model=self.model,
                contents=self._build_prompt(country, goal),
            )
            response_text = (response.text or "").strip()
        except GuideGenerationError:
            raise
        except Exception as exc:
            raise GuideGenerationError("Gemini could not generate a guide right now. Please try again.") from exc

        if not response_text:
            raise GuideGenerationError("Gemini returned an empty guide. Please try again.")
        return self._parse_response(country, goal, response_text)

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from google import genai
        except ImportError as exc:
            raise GuideGenerationError(
                "Gemini support is not installed. Run: python -m pip install -r requirements.txt"
            ) from exc
        self._client = genai.Client(api_key=self.api_key)
        return self._client

    @staticmethod
    def _load_environment() -> None:
        """Load the project .env file when python-dotenv is installed."""
        try:
            from dotenv import load_dotenv
        except ImportError:
            return
        load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=False)

    @staticmethod
    def _build_prompt(country: Country, purpose: str) -> str:
        return f"""Create a concise, practical {purpose} guide for {country.name}.

Use only these verified country facts:
- Capital: {country.capital}
- Region: {country.region}, {country.subregion}
- Languages: {', '.join(country.languages) or 'Not listed'}
- Currencies: {', '.join(country.currencies) or 'Not listed'}
- Timezones: {', '.join(country.timezones) or 'Not listed'}

Write in this exact format:
Overview:
Two or three helpful sentences.

Tips:
- Five practical preparation tips.

Checklist:
- Five first-week or packing checklist items.

Do not invent visa requirements, laws, medical advice, crime statistics, costs, or safety facts. Tell the user to check official sources for those topics."""

    @staticmethod
    def _parse_response(country: Country, purpose: str, text: str) -> RelocationGuide:
        sections: dict[str, list[str]] = {"overview": [], "tips": [], "checklist": []}
        active_section = "overview"
        bullet_pattern = re.compile(r"^(?:[-*•]|\d+[.)])\s*")

        for raw_line in text.splitlines():
            line = raw_line.strip()
            heading = line.replace("*", "").rstrip(":").strip().casefold()
            if heading in sections:
                active_section = heading
            elif line:
                sections[active_section].append(bullet_pattern.sub("", line).strip())

        overview = " ".join(sections["overview"]).strip() or text
        return RelocationGuide(
            country_name=country.name,
            country_code=country.code,
            purpose=purpose.title(),
            overview=overview,
            tips=sections["tips"],
            checklist=sections["checklist"],
        )
