"""
Tool kit for project initialization wizard

Manages
- button functionality and enabling/disabling
- sending info to submitted info
- validation checks
"""

import streamlit as st

from utils.init import PAGES


def navigate(col_prev = None, col_next = None):
    """
    Navigation buttons
    - Disable previous for first page
    - Disable next for last page or incomplete form

    Args:
        col_prev (DeltaGenerator):
            Streamlit column instance
        col_next (DeltaGenerator):
            Streamlit column instance
    """
    if not col_prev and not col_next:
        col_prev, col_next = st.columns(2)

    # Previous
    prev_disabled = not st.session_state["page"] > 0
    if col_prev.button("Previous", key=f"prev_page", disabled=prev_disabled, width="stretch"):
        st.session_state["page"] -= 1
        st.session_state["page_incomplete"] = False
        st.session_state["page_initial_state"] = True
        st.rerun()

    # Next
    no_next = st.session_state["page"] == PAGES
    if st.session_state["page_incomplete"] or no_next:
        next_disabled = True
    else:
        next_disabled = False
    if col_next.button("Next", key=f"nex_page", disabled=next_disabled, width="stretch"):
        st.session_state["page"] += 1
        st.session_state["page_initial_state"] = True
        st.rerun()


def symbol_validation(word: str, strict: bool = False):
    """
    Validation of format of input text

    Args:
        word (str):
            value collected from text input field
        strict (bool):
            True for sensitive values (file names)

    Returns:
        msg (str):
            error message tool tip
    """
    msg = False
    if word:
        if not strict:
            valid_symbols = (
                "-", " ", "_", "–", "—", "'", '"', "&", ".", "*", "!", "?", "%", "§",
                "(", ")", "[", "]", "{", "}", "/", "+", "<", ">", "@", "#", "=")
            invalid_first = (" ")
        else:
            valid_symbols = ("-", " ")
            invalid_first = ("-", " ")
        max_length = 40
        min_length = 0
        length_check = len(word) > min_length and len(word) < max_length

        if length_check:
            if "  " in word:
                msg = "Double whitespace."
            if word[0] in invalid_first:
                msg = "Invalid first character."
            if not word.isalnum():
                for symbol in word:
                    if not symbol.isalnum() and symbol not in valid_symbols:
                        msg = "Invalid characters."
        else:
            msg = "Too long. "
    return msg


def check_duplicates(value_list, message=True):
    """Generates list stating whether corresponding consecutive value is a duplicate.  
    None-values are ignored, considered not-yet-filled."""
    collect = list()
    check = list()
    for value in value_list:
        if value is not None: check.append(value in collect)
        collect.append(value)
    if any(check):
        if message: st.warning("Multiples excluded")
        return True
    else:
        return False
    

def sync_used_terms(collection: dict, type: str|None = None):
    "Collects entered text fields which may cause conflict if re-used."
    if type: st.session_state["in_use"][type] = dict()
    for x, y in collection.items():
        if type:
            st.session_state["in_use"][type][x] = y
        else:
            st.session_state["in_use"][x] = y

def check_used_terms(control_values: dict, type: str|None = None):
    "Verifies that input in text field has not been used before."
    if type: 
        in_use = st.session_state["in_use"].get(type, {})
    else: 
        in_use = st.session_state["in_use"]
    for x, y in control_values.items():
        if y in st.session_state["in_use"].values():
            for a, b in in_use.items():
                if a == x: 
                    continue
                elif b == y:
                    st.warning(f"You have used the term '{y}' elsewhere.")
                    return False
    return True


def need_update(changed_page_format: str, is_changed_key: str, 
                all_required: bool = True, invalid_data: bool = False):
    """
    Upon changed value in input field, triggers change in states 
    and button appearance, and disables 'Next'.

    Args:
        changed_page_format (str): 
            format key for button highlight on page containing altered field
        is_changed_key (str): 
            control key for button enabling 
    """
    if not invalid_data:
        st.session_state["page_initial_state"] = False
        st.session_state[changed_page_format] = "primary"
        st.session_state[is_changed_key] = True
        if all_required:
            st.session_state["page_incomplete"] = True
    else:
        st.session_state[changed_page_format] = "primary"
        st.session_state[is_changed_key] = False


def apply(key: str, button_format_key: str, page_is_changed: str, 
          submission_key: str, submission: dict, 
          all_required: bool = True, invalid_input: bool = False):
    """
    Save button

    Args:
        key (str):
            button ID key
        button_format_key (str):
            format key, setting discrete or highlighted save button
        page_is_changed (str):
            control key, only activate upon changes
        submission_key (str):
            identifier for page submission
        all_required (bool):
            for False, incomplete form is tolerated
        invalid_input (bool):
            prevent faulty format submission
    """
    save_disabled = True
    if st.session_state[page_is_changed] and not invalid_input:
        if all_required:
            if all(st.session_state["checklists"][key]):
                save_disabled = False
        else:
            save_disabled = False
    st.button(
        "**Save**", 
        key=key, 
        on_click=submit, 
        args=(button_format_key, page_is_changed, submission_key, submission), 
        type=st.session_state[button_format_key], 
        disabled=save_disabled,
        width="stretch")
    

def submit(button_format_key: str, page_is_changed: str, 
           submission_key: str, submission: dict):
    """
    On click on save button:
    - collects page submission
    - resets discrete save button appearance 
    - sets 'Next' button blocking values False

    Args:
        button_format_key (str):
            format key, setting discrete or highlighted save button
        page_is_changed (str):
            control key for behavior upon change
        submission_key (str):
            identifier for page submission
        submission (dict):
            submission information
    """
    st.session_state[button_format_key] = "secondary"
    st.session_state[page_is_changed] = False
    st.session_state["submitted"][submission_key] = submission
    st.session_state["page_incomplete"] = False


def dev_tools(show_dev_tools: bool):
    "Developer options to show and clear session state."
    if show_dev_tools:
        if st.button("Clear"): clear()
        st.write(st.session_state)


def clear():
    "Clears session state of all keys."
    # print("\n----------------------")
    for key in st.session_state.keys():
        # print(key, st.session_state[key])
        del st.session_state[key]
    # print(st.session_state)
    st.rerun()


