"""Local JSON storage for Country Compass data."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from exceptions import StorageError
from models import Country, RelocationGuide


class StorageManager:
    """Save and retrieve user data in JSON files inside one data folder."""

    def __init__(self, data_directory: Path | None = None) -> None:
        self.data_directory = data_directory or Path(__file__).with_name("data")

    def load_favourites(self) -> list[Country]:
        """Load all saved countries as Country objects."""
        records = self._read_records("favourites.json")
        try:
            return [Country(**record) for record in records]
        except (TypeError, ValueError) as exc:
            raise StorageError("Saved favourites contain invalid country data.") from exc

    def save_favourite(self, country: Country) -> bool:
        """Save a country once. Returns False when it was already in the shortlist."""
        records = self._read_records("favourites.json")
        if any(record.get("code") == country.code for record in records):
            return False
        records.append(country.to_dict())
        self._write_records("favourites.json", records)
        return True

    def remove_favourite(self, country_code: str) -> bool:
        """Remove a saved country by its two-letter country code."""
        records = self._read_records("favourites.json")
        remaining = [record for record in records if record.get("code") != country_code]
        if len(remaining) == len(records):
            return False
        self._write_records("favourites.json", remaining)
        return True

    def save_guide(self, guide: RelocationGuide) -> None:
        """Append an AI-generated guide to the local guide history."""
        records = self._read_records("guides.json")
        records.append(guide.to_dict())
        self._write_records("guides.json", records)

    def save_checklist(self, country: Country, title: str, items: list[str]) -> None:
        """Save a personal travel, study, or relocation checklist."""
        clean_items = [item.strip() for item in items if item.strip()]
        if not clean_items:
            raise ValueError("Add at least one checklist item before saving.")
        records = self._read_records("checklists.json")
        records.append(
            {
                "country_name": country.name,
                "country_code": country.code,
                "title": title.strip() or "My checklist",
                "items": clean_items,
                "saved_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        self._write_records("checklists.json", records)

    def load_checklists(self, country_code: str) -> list[dict[str, Any]]:
        """Load valid checklist records for one country, newest first."""
        records = self._read_records("checklists.json")
        country_checklists: list[dict[str, Any]] = []
        for record in records:
            if record.get("country_code") != country_code:
                continue
            title = record.get("title")
            items = record.get("items")
            saved_at = record.get("saved_at")
            if (
                not isinstance(title, str)
                or not isinstance(items, list)
                or not all(isinstance(item, str) and item.strip() for item in items)
                or not isinstance(saved_at, str)
            ):
                raise StorageError("Saved country checklist data has an invalid format.")
            country_checklists.append(
                {"title": title, "items": items, "saved_at": saved_at}
            )
        return list(reversed(country_checklists))

    def save_comparison(self, first: Country, second: Country, timezone_message: str) -> None:
        """Save the essential result of a two-country comparison."""
        records = self._read_records("comparisons.json")
        records.append(
            {
                "first_country": first.to_dict(),
                "second_country": second.to_dict(),
                "timezone_message": timezone_message,
                "saved_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        self._write_records("comparisons.json", records)

    def _read_records(self, filename: str) -> list[dict[str, Any]]:
        path = self.data_directory / filename
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"Could not read saved data from {filename}.") from exc
        if not isinstance(data, list) or not all(isinstance(record, dict) for record in data):
            raise StorageError(f"Saved data in {filename} has an invalid format.")
        return data

    def _write_records(self, filename: str, records: list[dict[str, Any]]) -> None:
        try:
            self.data_directory.mkdir(parents=True, exist_ok=True)
            path = self.data_directory / filename
            temporary_path = self.data_directory / f"{filename}.tmp"
            temporary_path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
            temporary_path.replace(path)
        except OSError as exc:
            raise StorageError(f"Could not save data to {filename}.") from exc

