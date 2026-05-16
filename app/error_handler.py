"""
Tools for error management
"""

import streamlit as st


@st.dialog("Error")
def notify(message:str, stage:str | None=None, 
           name:str | None=None, info_list:list | None = None, 
           file:str | None=None, backup:str | None = None):
    """
    User notification of error.
    """

    st.error(message)

    info = str()
    if stage: info += f"Stage: {stage}:  \n"
    if name: info += f"Name: {name}  \n"
    if file: info += f"File: {file}  \n"
    if backup: info += f"Backup file: {backup}  \n"
    if info_list:
        for x in info_list:
            info += f"- {x}  "

    st.markdown(info)

    if st.button("Ok"): st.rerun()