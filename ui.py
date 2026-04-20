import os

import pandas as pd
import streamlit as st

# # from settings.config import UITERMS, DIRECTORIES, DATAPATH, SETTINGS
from app import Archivist

is_demo = False
if is_demo:
    from demo_settings.config import TERMS, UITERMS, DIRECTORIES, DATAPATH, SETTINGS
else:
    from settings.config import TERMS, UITERMS, DIRECTORIES, DATAPATH, SETTINGS

settings_file = os.path.join(DIRECTORIES["UIFolder"], SETTINGS["UISettings"])
arciv = Archivist(DIRECTORIES, DATAPATH, settings_file)
# # options = arciv.reader()

st.set_page_config(layout="wide")

st.title(f"*{UITERMS["title"]}*", text_alignment="center")
# st.markdown(f"*{UITERMS["subtitle"]}*")

# def data_upload(file_list):
#     # df = pd.read_csv(file)
#     # return df
#     df_list = list()
#     for file in file_list:
#         report_path = os.path.join(DIRECTORIES["DataFolder"], file)
#         df = pd.read_csv(report_path)
#         df[UITERMS["attempts"]] = pd.to_numeric(UITERMS["attempts"], errors="coerce")
#         df_list.append(df)

#     return df_list

# files = [DATAPATH["CharReport"], DATAPATH["MiscReport"], DATAPATH["ToolReport"]]
# df_char, df_misc, df_tool = data_upload(files)


attempts = arciv.reader(other_file="progress_data.json", join_path="data")
# st.subheader(f"Current {UITERMS["attempts"]}")
# st.markdown(
#     f"""
#     | {TERMS["Source"]} | {TERMS["Attempt"]} |
#     |-|-|
#     | {TERMS["Temp"]} | {attempts[f"Character {TERMS["Temp"]}"][TERMS["Attempt"]]} |
#     | {TERMS["Mix"]} | {attempts[TERMS["Mix"]][TERMS["Attempt"]]} |
#     | {TERMS["Standard source"]} | {attempts[f"{TERMS["Tool"]} {TERMS["Temp"]}"][TERMS["Attempt"]]} |
# """)

# def checking():
#     print("check")
# state = st.checkbox("Check", value=True, on_change=checking)

data_options = arciv.reader(other_file="data_options.json", join_path="data")
# select = st.selectbox("attribute", options=data_options[TERMS["Character"]][TERMS["Origin"]])

# # Initialize session state if it doesn't exist
# if 'count' not in st.session_state:
#     st.session_state.count = 0

st.markdown("""
    <style>
    .st-key-green_btn button {
        background-color: #262730;
        color: white;
        border: none;
    }
    .st-key-green_btn button:hover {
        background-color: #353942;
    }
    </style>
""", unsafe_allow_html=True)

instr = """
    <style>
    .st-key-XXX button {
        background-color: transparent;
        border: none;
    }
    </style>
"""



st.header(f"{TERMS["Attempt"]}")


col_main1, col_main2 = st.columns(2)

def apply_status(category, status_val):
    attempts[category][TERMS["Attempt"]] = status_val
    # print(attempts)
    arciv.writer(attempts, other_file=DATAPATH["Progress"], join_path="data")


with col_main1:
    

    for i, category in enumerate(attempts.keys()):
        print(category, attempts[category][TERMS["Attempt"]])
        # st.subheader(category)
        col_cat, col_number, col_10, col_slider, col_apply = st.columns([0.21, 0.15, 0.07, 0.45, 0.10], gap="xxsmall", vertical_alignment="bottom")

        label_key = f'label_{i}'
        slider_key = f'slider_{i}'
        num_key = f'num_{i}'
        shared_key = f'val_{i}'
        button_key = f'but_{i}'
        add10_key = f'add10_{i}'

        if shared_key not in st.session_state: value=st.session_state[shared_key] = attempts[category][TERMS["Attempt"]]
        # if num_key not in st.session_state: st.session_state[f"num_{i}"] = attempts[category][TERMS["Attempt"]]

        def sync_from_num(idx=i):
            new_val = st.session_state[f"num_{idx}"]
            st.session_state[f"val_{idx}"] = new_val
            st.session_state[f"slider_{idx}"] = new_val

        def sync_from_slider(idx=i):
            new_val = st.session_state[f"slider_{idx}"]
            st.session_state[f"val_{idx}"] = new_val
            st.session_state[f"num_{idx}"] = new_val

        def increment_counter(idx=i, increment_value=10):
            st.session_state[f"val_{idx}"] += increment_value
            st.session_state[f"num_{idx}"] += increment_value 
            st.session_state[f"slider_{idx}"] += increment_value 

        instr.replace("XXX", button_key)
        st.markdown(instr.replace("XXX", label_key), unsafe_allow_html=True)

        with col_cat:
            st.button(category, key=label_key)
        with col_number:
            st.number_input("Number", min_value=0, max_value=90, key=num_key, value=st.session_state[shared_key], on_change=sync_from_num, label_visibility="collapsed")
        with col_10:
            if st.session_state[shared_key] < 80:
                st.button("**+ 10**", key=add10_key, width="stretch", on_click=increment_counter)
            else:
                st.button("**+ 10**", key=add10_key, width="stretch")
        with col_slider:
            st.slider("Slider", min_value=0, max_value=90, key=slider_key, value=st.session_state[shared_key], on_change=sync_from_slider, label_visibility="collapsed")
        with col_apply:
            st.button(f"Apply", key=button_key, type="primary", on_click=apply_status, args=(category, st.session_state[shared_key]))



# st.write(f"Current Value: {st.session_state.slider_val}")

# st.write('Count = ', st.session_state.count)

# col_1, col_2, col_3 = st.columns(3, width="stretch")
# with col_1:
#     st.markdown("---")
#     st.subheader(f"{UITERMS["datatable_char"]}")
#     st.dataframe(data=df_char)

# with col_2:
#     st.markdown("---")
#     st.subheader(f"{UITERMS["datatable_tool"]}")
#     st.dataframe(data=df_tool)

# with col_3:
#     st.markdown("---")
#     st.subheader(f"{UITERMS["datatable_misc"]}")
#     st.dataframe(data=df_misc)



