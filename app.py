"""Country Relocation and Culture Guide Streamlit entry point."""

from __future__ import annotations

import streamlit as st

from ai_guide import GeminiGuideGenerator
from comparison import CountryComparator
from country_api import CountryAPIClient
from exceptions import CountryAPIError, GuideGenerationError, StorageError
from storage import StorageManager
from ui_components import (
    apply_theme,
    render_comparison,
    render_country_card,
    render_guide,
    render_saved_places,
)


@st.cache_data(ttl=3600, show_spinner=False)
def find_country(country_name: str):
    """Fetch a country once per hour, instead of on every Streamlit rerun."""
    return CountryAPIClient().search(country_name)


def show_sidebar(storage: StorageManager) -> None:
    """Show the local shortlist without allowing a storage error to stop the app."""
    with st.sidebar:
        st.header("Your saved places")
        try:
            render_saved_places(storage.load_favourites())
        except StorageError as exc:
            st.warning(str(exc))


def explore_tab(storage: StorageManager) -> None:
    query = st.text_input("Country name", placeholder="e.g. Nigeria, Japan, Canada")
    if st.button("Find country", type="primary"):
        try:
            country = find_country(query)
            previous_country = st.session_state.get("current_country")
            if previous_country is None or previous_country.code != country.code:
                st.session_state.pop("current_guide", None)
            st.session_state.current_country = country
        except (ValueError, CountryAPIError) as exc:
            st.error(str(exc))

    country = st.session_state.get("current_country")
    if not country:
        return

    render_country_card(country)
    if st.button("Save to my shortlist"):
        try:
            added = storage.save_favourite(country)
            st.success("Saved to your shortlist." if added else "This country is already saved.")
        except StorageError as exc:
            st.error(str(exc))


def compare_tab(storage: StorageManager) -> None:
    st.write("Compare two places before you decide where to travel, study, or move.")
    left, right = st.columns(2)
    first_name = left.text_input("First country", placeholder="e.g. Nigeria", key="compare_first")
    second_name = right.text_input("Second country", placeholder="e.g. United Kingdom", key="compare_second")
    if st.button("Compare countries", type="primary"):
        try:
            first, second = find_country(first_name), find_country(second_name)
            st.session_state.comparison = CountryComparator(first, second)
        except (ValueError, CountryAPIError) as exc:
            st.session_state.pop("comparison", None)
            st.error(str(exc))

    comparator = st.session_state.get("comparison")
    if not comparator:
        return

    render_comparison(comparator)
    if st.button("Save this comparison"):
        try:
            storage.save_comparison(
                comparator.first,
                comparator.second,
                comparator.timezone_message(),
            )
            st.success("Comparison saved locally.")
        except StorageError as exc:
            st.error(str(exc))


def guide_tab(storage: StorageManager) -> None:
    country = st.session_state.get("current_country")
    if not country:
        st.info("First search for a country in the Explore tab.")
        return

    purpose = st.selectbox(
        "Guide type",
        ("Travel", "Study", "Relocate"),
        key="guide_purpose",
        accept_new_options=False,
        filter_mode=None,
    )
    if st.button("Generate my guide", type="primary"):
        try:
            with st.spinner("Creating your guide…"):
                st.session_state.current_guide = GeminiGuideGenerator().generate(country, purpose)
        except (ValueError, GuideGenerationError) as exc:
            st.error(str(exc))

    guide = st.session_state.get("current_guide")
    if not guide:
        return

    render_guide(guide)
    if st.button("Save this guide"):
        try:
            storage.save_guide(guide)
            st.success("Guide saved locally.")
        except StorageError as exc:
            st.error(str(exc))


def checklist_tab(storage: StorageManager) -> None:
    country = st.session_state.get("current_country")
    if not country:
        st.info("First search for a country in the Explore tab.")
        return

    st.subheader(f"Country checklist: {country.name}")
    st.write("Add the tasks you need for this country. One task per line.")
    with st.form(f"country_checklist_form_{country.code}", clear_on_submit=True):
        title = st.text_input("Checklist title", value="My relocation checklist")
        items_text = st.text_area(
            "Checklist items",
            placeholder="Check passport expiry\nResearch neighbourhoods\nNotify my bank",
            height=180,
        )
        submitted = st.form_submit_button("Add to country checklist", type="primary")

    if submitted:
        try:
            storage.save_checklist(country, title, items_text.splitlines())
            st.success("Added to this country checklist.")
        except (ValueError, StorageError) as exc:
            st.error(str(exc))

    try:
        checklists = storage.load_checklists(country.code)
    except StorageError as exc:
        st.error(str(exc))
        return

    if not checklists:
        st.info("No checklist items yet. Add your first one above.")
        return

    st.markdown("#### Your country checklist")
    for checklist in checklists:
        st.markdown(f"**{checklist['title']}**")
        for item_index, item in enumerate(checklist["items"]):
            st.checkbox(
                item,
                key=f"country_checklist_{country.code}_{checklist['saved_at']}_{item_index}",
            )


def app() -> None:
    st.set_page_config(page_title="Country Relocation and Culture Guide", page_icon="🧭", layout="wide")
    apply_theme()
    storage = StorageManager()

    st.title("🧭 Country Relocation and Culture Guide")
    st.write("Explore countries, compare your options, and plan a confident move or visit.")

    explore, compare, ai_guide, checklist = st.tabs(
        ["Explore a country", "Compare countries", "AI guide", "Country checklist"]
    )
    with explore:
        explore_tab(storage)
    with compare:
        compare_tab(storage)
    with ai_guide:
        guide_tab(storage)
    with checklist:
        checklist_tab(storage)

    # This is deliberately rendered after the tabs. Button actions in the tabs
    # write first, so the sidebar sees the updated shortlist on the same rerun.
    show_sidebar(storage)


if __name__ == "__main__":
    app()
