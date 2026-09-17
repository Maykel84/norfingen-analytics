import streamlit as st

from data.db import get_last_refresh_time
from ui import page_clients, page_overview, page_time
from ui.components import nav_bar
from ui.i18n import t
from ui.theme import inject_global_css

st.set_page_config(page_title="Operational Intelligence", layout="wide", page_icon="◆")

if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "active_page" not in st.session_state:
    st.session_state.active_page = "overview"

st.markdown(inject_global_css(st.session_state.theme), unsafe_allow_html=True)

new_active, new_lang, new_theme = nav_bar(
    st.session_state.active_page, st.session_state.lang, st.session_state.theme, t
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
if rerun_needed:
    st.rerun()

lang = st.session_state.lang
theme = st.session_state.theme

if st.session_state.active_page == "overview":
    page_overview.render(lang, theme)
elif st.session_state.active_page == "time":
    page_time.render(lang, theme)
elif st.session_state.active_page == "clients":
    page_clients.render(lang, theme)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
last_refresh = get_last_refresh_time()
st.caption(f"{t('last_updated', lang)}: {last_refresh.strftime('%Y-%m-%d %H:%M')}")
