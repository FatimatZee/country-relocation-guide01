"""Data models used throughout Country Compass."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote_plus


@dataclass
class Country:
    """A normalised country record returned by the REST Countries API."""

    name: str
    official_name: str
    capital: str = "Not listed"
    region: str = "Not listed"
    subregion: str = "Not listed"
    population: int = 0
    languages: list[str] = field(default_factory=list)
    currencies: list[str] = field(default_factory=list)
    timezones: list[str] = field(default_factory=list)
    flag: str = "🌍"
    code: str = "—"
    maps_url: str = ""

    @classmethod
    def from_api_response(cls, raw: dict[str, Any]) -> "Country":
        """Turn a REST Countries v5 response object into a safe Country record."""
        if not isinstance(raw, dict):
            raise ValueError("Country data must be an object.")

        names = _as_mapping(raw.get("names")) or _as_mapping(raw.get("name"))
        name = _as_text(names.get("common"), default="")
        if not name:
            raise ValueError("Country data does not include a common name.")

        flag_data = raw.get("flag")
        codes = _as_mapping(raw.get("codes"))
        return cls(
            name=name,
            official_name=_as_text(names.get("official"), default=name),
            capital=", ".join(_capital_names(raw.get("capitals", raw.get("capital")))) or "Not listed",
            region=_as_text(raw.get("region")),
            subregion=_as_text(raw.get("subregion")),
            population=_as_nonnegative_int(raw.get("population")),
            languages=_language_names(raw.get("languages")),
            currencies=_currency_names(raw.get("currencies")),
            timezones=_string_list(raw.get("timezones")),
            flag=_as_text(
                _as_mapping(flag_data).get("emoji") if isinstance(flag_data, dict) else flag_data,
                default="🌍",
            ),
            code=_as_text(codes.get("alpha_2") or raw.get("cca2"), default="—"),
            maps_url=f"https://www.google.com/maps/search/?api=1&query={quote_plus(name)}",
        )

    def to_dict(self) -> dict[str, Any]:
        """Make this country safe to store in a JSON file."""
        return asdict(self)


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_text(value: Any, *, default: str = "Not listed") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_as_text(item, default="") for item in value if _as_text(item, default="")]


def _capital_names(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    capitals: list[str] = []
    for item in value:
        name = _as_text(_as_mapping(item).get("name") if isinstance(item, dict) else item, default="")
        if name:
            capitals.append(name)
    return capitals


def _language_names(value: Any) -> list[str]:
    if isinstance(value, dict):  # REST Countries v3 compatibility for saved or mocked data.
        return [_as_text(name, default="") for name in value.values() if _as_text(name, default="")]
    if not isinstance(value, list):
        return []
    languages: list[str] = []
    for item in value:
        language = _as_text(_as_mapping(item).get("name") if isinstance(item, dict) else item, default="")
        if language:
            languages.append(language)
    return languages


def _currency_names(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return []
    currencies: list[str] = []
    for code, details in value.items():
        if not isinstance(code, str):
            continue
        name = _as_text(_as_mapping(details).get("name"), default=code)
        currencies.append(f"{name} ({code})")
    return currencies


def _as_nonnegative_int(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


@dataclass
class RelocationGuide:
    """A guide generated for one country and one user goal."""

    country_name: str
    country_code: str
    purpose: str
    overview: str
    tips: list[str] = field(default_factory=list)
    checklist: list[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Make this guide safe to store in a JSON file."""
        return asdict(self)
