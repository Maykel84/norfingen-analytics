import streamlit as st

from data.db import get_last_refresh_time
from semantic.metrics import get_available_years
from ui import page_clients, page_operations, page_overview, page_time, page_today
from ui.components import nav_bar
from ui.i18n import t
from ui.theme import inject_global_css

st.set_page_config(page_title="Norfingen Analytics", layout="wide", page_icon="◆")

if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "active_page" not in st.session_state:
    st.session_state.active_page = "today"
if "global_year" not in st.session_state:
    st.session_state.global_year = "all"

st.markdown(inject_global_css(st.session_state.theme), unsafe_allow_html=True)

# Streamlit Community Cloud's free tier sleeps an unused app; the first
# visitor after that has to wait for the container to wake (tens of
# seconds) on top of a cold st.cache_data/engine — nothing in app code can
# shorten that, but showing a spinner immediately (before the first query
# even runs) means the wait reads as "loading" rather than a blank page
# that looks broken.
with st.spinner(t("app_starting", st.session_state.lang)):
    years = get_available_years()
new_active, new_lang, new_theme, new_year = nav_bar(
    st.session_state.active_page, st.session_state.lang, st.session_state.theme, t,
    years=years, selected_year=st.session_state.global_year,
)
rerun_needed = False
if new_active != st.session_state.active_page:
    st.session_state.active_page = new_active
    rerun_needed = True
if new_lang != st.session_state.lang:
    st.session_state.lang = new_lang
    rerun_needed = True
if new_theme != st.session_state.theme:
    st.session_state.theme = new_theme
    rerun_needed = True
if new_year != st.session_state.global_year:
    st.session_state.global_year = new_year
    rerun_needed = True
if rerun_needed:
    st.rerun()

lang = st.session_state.lang
theme = st.session_state.theme
selected_year = None if st.session_state.global_year == "all" else int(st.session_state.global_year)

if st.session_state.active_page == "today":
    page_today.render(lang, theme)
elif st.session_state.active_page == "overview":
    page_overview.render(lang, theme, selected_year)
elif st.session_state.active_page == "time":
    page_time.render(lang, theme, selected_year)
elif st.session_state.active_page == "clients":
    page_clients.render(lang, theme, selected_year)
elif st.session_state.active_page == "operations":
    page_operations.render(lang, theme, selected_year)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
last_refresh = get_last_refresh_time()
st.caption(f"{t('last_updated', lang)}: {last_refresh.strftime('%Y-%m-%d %H:%M')}")
