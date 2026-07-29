"""Client for fetching country information from REST Countries."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests

from exceptions import CountryAPIError
from models import Country
from validators import validate_country_name


class CountryAPIClient:
    """Fetch and normalise country records from the REST Countries v5 API."""

    BASE_URL = "https://api.restcountries.com/countries/v5"
    FIELDS = (
        "names.common,names.official,capitals,region,subregion,population,"
        "languages,currencies,timezones,flag.emoji,codes.alpha_2"
    )

    def __init__(self, session: requests.Session | None = None, api_key: str | None = None) -> None:
        self._load_environment()
        self.session = session or requests.Session()
        self.api_key = api_key or os.getenv("REST_COUNTRIES_API_KEY")

    def search(self, country_name: str) -> Country:
        """Find one country by name, preferring an exact match over a substring match."""
        clean_name = validate_country_name(country_name)
        if not self.api_key:
            raise CountryAPIError(
                "Add REST_COUNTRIES_API_KEY to your .env file before searching for a country."
            )

        results = self._get_results(clean_name)
        if not results:
            raise CountryAPIError(f"No country matching '{clean_name}' was found.")
        try:
            return Country.from_api_response(self._best_match(results, clean_name))
        except (TypeError, ValueError) as exc:
            raise CountryAPIError("The country service returned incomplete data. Please try again.") from exc

    def _get_results(self, country_name: str) -> list[dict[str, Any]]:
        params = {"q": country_name, "limit": 25, "response_fields": self.FIELDS}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = self.session.get(
                f"{self.BASE_URL}/name",
                params=params,
                headers=headers,
                timeout=12,
            )
        except requests.RequestException as exc:
            raise CountryAPIError(
                "Country information is unavailable. Check your internet connection and try again."
            ) from exc

        if response.status_code == 404:
            return []
        if response.status_code in {401, 403}:
            raise CountryAPIError("The country-data API key was rejected. Check REST_COUNTRIES_API_KEY and try again.")
        try:
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise CountryAPIError("The country service returned an unexpected response. Please try again.") from exc

        data = payload.get("data") if isinstance(payload, dict) else None
        results = data.get("objects") if isinstance(data, dict) else None
        if not isinstance(results, list):
            raise CountryAPIError("The country service returned an unexpected response. Please try again.")
        return [item for item in results if isinstance(item, dict)]

    @staticmethod
    def _best_match(results: list[dict[str, Any]], country_name: str) -> dict[str, Any]:
        """Prefer an exact common or official name over a substring search result."""
        target = country_name.casefold()
        for item in results:
            names = item.get("names") or item.get("name") or {}
            if isinstance(names, dict) and any(
                isinstance(value, str) and value.casefold() == target
                for value in (names.get("common"), names.get("official"))
            ):
                return item
        return results[0]

    @staticmethod
    def _load_environment() -> None:
        """Load the project .env file without overwriting deployment variables."""
        try:
            from dotenv import load_dotenv
        except ImportError:
            return
        load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=False)