"""Country comparison logic, including timezone difference calculations."""

from __future__ import annotations

from models import Country
from validators import timezone_to_minutes


class CountryComparator:
    """Compare two different countries without depending on the user interface."""

    def __init__(self, first: Country, second: Country) -> None:
        if first.code == second.code:
            raise ValueError("Choose two different countries to compare.")
        self.first = first
        self.second = second

    def comparison_rows(self) -> list[dict[str, str]]:
        """Return facts in a shape that Streamlit can display as a table."""
        return [
            {"Detail": "Capital", self.first.name: self.first.capital, self.second.name: self.second.capital},
            {"Detail": "Population", self.first.name: f"{self.first.population:,}", self.second.name: f"{self.second.population:,}"},
            {"Detail": "Region", self.first.name: self._location(self.first), self.second.name: self._location(self.second)},
            {"Detail": "Languages", self.first.name: self._items(self.first.languages), self.second.name: self._items(self.second.languages)},
            {"Detail": "Currencies", self.first.name: self._items(self.first.currencies), self.second.name: self._items(self.second.currencies)},
            {"Detail": "Time zones", self.first.name: self._items(self.first.timezones), self.second.name: self._items(self.second.timezones)},
        ]

    def timezone_difference_minutes(self) -> int | None:
        """Return second country minus first country, using each first listed timezone."""
        if not self.first.timezones or not self.second.timezones:
            return None
        try:
            first_offset = timezone_to_minutes(self.first.timezones[0])
            second_offset = timezone_to_minutes(self.second.timezones[0])
        except ValueError:
            return None
        return second_offset - first_offset

    def timezone_message(self) -> str:
        """Explain the timezone difference in plain language for the app."""
        difference = self.timezone_difference_minutes()
        if difference is None:
            return "Timezone comparison is unavailable because one country has no valid listed timezone."
        if difference == 0:
            return f"{self.first.name} and {self.second.name} are in the same listed timezone."

        hours, minutes = divmod(abs(difference), 60)
        amount = f"{hours} hour{'s' if hours != 1 else ''}"
        if minutes:
            amount += f" {minutes} minutes"
        direction = "ahead of" if difference > 0 else "behind"
        return f"{self.second.name} is {amount} {direction} {self.first.name}."

    @staticmethod
    def _items(items: list[str]) -> str:
        return ", ".join(items) if items else "Not listed"

    @staticmethod
    def _location(country: Country) -> str:
        return " · ".join(part for part in [country.region, country.subregion] if part != "Not listed") or "Not listed"
