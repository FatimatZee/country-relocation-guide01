"""Reusable Streamlit user-interface components for Country Compass."""

from __future__ import annotations

import streamlit as st

from comparison import CountryComparator
from models import Country, RelocationGuide


def apply_theme() -> None:
    """Apply the app's calm green visual theme."""
    st.markdown(
        """<style>
        .stApp { background: #f7faf8; }
        .block-container { max-width: 1100px; padding-top: 2.5rem; }
        h1, h2, h3 { color: #153b2e; }
        div[data-testid='stMetric'] {
            background: white; border: 1px solid #d9e8e0;
            padding: 14px; border-radius: 12px;
        }
        </style>""",
        unsafe_allow_html=True,
    )


def render_country_card(country: Country) -> None:
    """Display a country profile with the facts a traveller or mover needs first."""
    st.markdown(f"## {country.flag} {country.name}")
    st.caption(country.official_name)
    first, second, third = st.columns(3)
    first.metric("Population", f"{country.population:,}")
    second.metric("Region", country.region)
    third.metric("Country code", country.code)

    left, right = st.columns(2)
    with left:
        st.markdown("#### Everyday essentials")
        st.write(f"**Capital:** {country.capital}")
        st.write(f"**Currencies:** {_display_items(country.currencies)}")
        st.write(f"**Languages:** {_display_items(country.languages)}")
    with right:
        st.markdown("#### Location & time")
        st.write(f"**Region:** {_location(country.region, country.subregion)}")
        st.write(f"**Time zones:** {_display_items(country.timezones)}")
        if country.maps_url:
            st.link_button("Open in Google Maps", country.maps_url)


def render_comparison(comparator: CountryComparator) -> None:
    """Display a country comparison table and timezone explanation."""
    first, second = comparator.first, comparator.second
    st.subheader(f"{first.flag} {first.name}  vs  {second.flag} {second.name}")
    st.dataframe(comparator.comparison_rows(), hide_index=True, use_container_width=True)
    st.success(comparator.timezone_message())
    if len(first.timezones) > 1 or len(second.timezones) > 1:
        st.caption("The timezone summary uses each country's first listed timezone.")


def render_guide(guide: RelocationGuide) -> None:
    """Display an AI guide with readable tips and interactive checklist items."""
    st.subheader(f"{guide.purpose} guide: {guide.country_name}")
    st.write(guide.overview)

    if guide.tips:
        st.markdown("#### Helpful tips")
        for tip in guide.tips:
            st.write(f"• {tip}")

    if guide.checklist:
        st.markdown("#### Your checklist")
        for index, item in enumerate(guide.checklist):
            st.checkbox(item, key=f"checklist_{guide.generated_at}_{guide.country_code}_{index}")


def render_saved_places(countries: list[Country]) -> None:
    """Render a compact saved-country list, suitable for the sidebar."""
    if not countries:
        st.caption("Save a country to build your shortlist.")
        return
    for country in countries:
        st.write(f"{country.flag} {country.name}")


def _display_items(items: list[str]) -> str:
    return ", ".join(items) if items else "Not listed"


def _location(region: str, subregion: str) -> str:
    return " · ".join(part for part in [region, subregion] if part != "Not listed") or "Not listed"
"""Reusable Streamlit user-interface components for Country Compass."""

from __future__ import annotations

import streamlit as st

from comparison import CountryComparator
from models import Country, RelocationGuide


def apply_theme() -> None:
    """Apply the app's calm green visual theme."""
    st.markdown(
        """<style>
        .stApp { background: #f7faf8; }
        .block-container { max-width: 1100px; padding-top: 2.5rem; }
        h1, h2, h3 { color: #153b2e; }
        div[data-testid='stMetric'] {
            background: white; border: 1px solid #d9e8e0;
            padding: 14px; border-radius: 12px;
        }
        </style>""",
        unsafe_allow_html=True,
    )


def render_country_card(country: Country) -> None:
    """Display a country profile with the facts a traveller or mover needs first."""
    st.markdown(f"## {country.flag} {country.name}")
    st.caption(country.official_name)
    first, second, third = st.columns(3)
    first.metric("Population", f"{country.population:,}")
    second.metric("Region", country.region)
    third.metric("Country code", country.code)

    left, right = st.columns(2)
    with left:
        st.markdown("#### Everyday essentials")
        st.write(f"**Capital:** {country.capital}")
        st.write(f"**Currencies:** {_display_items(country.currencies)}")
        st.write(f"**Languages:** {_display_items(country.languages)}")
    with right:
        st.markdown("#### Location & time")
        st.write(f"**Region:** {_location(country.region, country.subregion)}")
        st.write(f"**Time zones:** {_display_items(country.timezones)}")
        if country.maps_url:
            st.link_button("Open in Google Maps", country.maps_url)


def render_comparison(comparator: CountryComparator) -> None:
    """Display a country comparison table and timezone explanation."""
    first, second = comparator.first, comparator.second
    st.subheader(f"{first.flag} {first.name}  vs  {second.flag} {second.name}")
    st.dataframe(comparator.comparison_rows(), hide_index=True, use_container_width=True)
    st.success(comparator.timezone_message())
    if len(first.timezones) > 1 or len(second.timezones) > 1:
        st.caption("The timezone summary uses each country's first listed timezone.")


def render_guide(guide: RelocationGuide) -> None:
    """Display an AI guide with readable tips and interactive checklist items."""
    st.subheader(f"{guide.purpose} guide: {guide.country_name}")
    st.write(guide.overview)

    if guide.tips:
        st.markdown("#### Helpful tips")
        for tip in guide.tips:
            st.write(f"• {tip}")

    if guide.checklist:
        st.markdown("#### Your checklist")
        for index, item in enumerate(guide.checklist):
            st.checkbox(item, key=f"checklist_{guide.generated_at}_{guide.country_code}_{index}")


def render_saved_places(countries: list[Country]) -> None:
    """Render a compact saved-country list, suitable for the sidebar."""
    if not countries:
        st.caption("Save a country to build your shortlist.")
        return
    for country in countries:
        st.write(f"{country.flag} {country.name}")


def _display_items(items: list[str]) -> str:
    return ", ".join(items) if items else "Not listed"


def _location(region: str, subregion: str) -> str:
    return " · ".join(part for part in [region, subregion] if part != "Not listed") or "Not listed"
