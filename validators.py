"""Validation helpers for user input and country timezone data, using regex."""

import re


# Allows Unicode names such as Côte d'Ivoire, Bosnia and Herzegovina, and
# Timor-Leste while rejecting numbers, underscores, and control characters.
COUNTRY_NAME_PATTERN = re.compile(r"(?:[^\W\d_]|[ .,'()\-]){2,80}", re.UNICODE)
COUNTRY_CODE_PATTERN = re.compile(r"^[A-Za-z]{2}$")
TIMEZONE_PATTERN = re.compile(r"UTC([+-])(\d{2}):(\d{2})")


def validate_country_name(country_name):
    """Return a clean country name or raise a useful validation error."""
    cleaned = country_name.strip()
    if not COUNTRY_NAME_PATTERN.fullmatch(cleaned):
        raise ValueError(
            "Enter a country name with 2–80 letters. Numbers and unsupported symbols are not allowed."
        )
    return cleaned


def validate_country_code(country_code):
    """Return a clean, uppercase 2-letter country code (e.g. NG, US, GB)."""
    cleaned = country_code.strip()
    if not COUNTRY_CODE_PATTERN.fullmatch(cleaned):
        raise ValueError("Country code must be exactly 2 letters, e.g. NG or US.")
    return cleaned.upper()


def validate_timezone(timezone_name):
    """Return a valid UTC offset in the form UTC+01:00 or UTC-03:30."""
    match = TIMEZONE_PATTERN.fullmatch(timezone_name)
    if not match:
        raise ValueError("Timezone must use the format UTC+HH:MM or UTC-HH:MM.")

    sign, hours_text, minutes_text = match.groups()
    hours, minutes = int(hours_text), int(minutes_text)
    if (
        minutes > 59
        or hours > 14
        or (sign == "+" and hours == 14 and minutes != 0)
        or (sign == "-" and hours > 12)
    ):
        raise ValueError("Timezone offset must be between UTC-12:00 and UTC+14:00.")
    return timezone_name


def timezone_to_minutes(timezone_name):
    """Convert a validated UTC offset to its number of minutes from UTC."""
    validated = validate_timezone(timezone_name)
    match = TIMEZONE_PATTERN.fullmatch(validated)
    sign, hours_text, minutes_text = match.groups()
    offset = int(hours_text) * 60 + int(minutes_text)
    return offset if sign == "+" else -offset
