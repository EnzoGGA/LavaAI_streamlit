import streamlit as st

if st.button("Home"):
    st.switch_page("main.py")
if st.button("Page 1"):
    st.switch_page("pages/page_1.py")