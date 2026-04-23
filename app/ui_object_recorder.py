import streamlit as st
import datetime

def register_object(arciv, negotiator, DIRECTORIES, DATAPATH, data_options, TERMS, attempts):

    



    with st.container(border=True, width=1000, height="content"):
        def update_source_state():
            source = st.session_state["source"]
            if source == TERMS["Temp"]:
                source = f"Character {source}" if st.session_state["type"] == "Character" else f"{TERMS["Tool"]} {source}"
            elif source == TERMS["Standard source"]:
                st.session_state["state"] = None
            st.session_state["attempt"] = attempts[source][TERMS["Attempt"]]
            return source

        def collect_database(set_type):
            if set_type == "Character":
                data_reference = TERMS["Character"]
            else:
                data_reference = set_type
            datafile = DATAPATH[data_reference]
            object_database = arciv.reader(datafile, join_path="data")
            return object_database

        
        # def make_columns(left_size, right_size):
        #     return st.columns([left_size, right_size], vertical_alignment="center")

        presets = {
            "tool": None,
            "attribute": None,
            "origin": None,
            "name": None,
            "type": "Character",
            "state": data_options["State alternatives"][0],
            "source": TERMS["Temp"],
            "attempt": attempts[f"Character {TERMS["Temp"]}"][TERMS["Attempt"]],
            "date": datetime.date.today()
        }
        for x, y in presets.items():
            if x not in st.session_state:
                st.session_state[x] = y
            elif not st.session_state[x]: 
                st.session_state[x] = y
        
        object_database = collect_database(st.session_state["type"])
        options_tool = data_options[TERMS["Character"]][TERMS["Tool"]]
        options_object = object_database.keys()
        options_attribute = data_options[TERMS["Character"]][TERMS["Attribute"]]
        options_origin = data_options[TERMS["Character"]][TERMS["Origin"]]
        
        
        options_reg = dict()
        add_new, options_reg[add_new] = "Add completely new", [False, False, False]
        add_event, options_reg[add_event] = f"New {TERMS["Event"].lower()} of old", [True, False, False]
        del_entry, options_reg[del_entry] = "Delete entry", [False, True, False]
        edit_entry, options_reg[edit_entry] = "Edit details", [False, False, True]
        del_event, options_reg[del_event] = f"Delete {TERMS["Event"].lower()}", [True, False, False]
        # options_reg = [add_new, add_event, del_entry, edit_entry, del_event]
        # print(options_regi)

        # tool_default = None
        # attribute_default = None
        # origin_default = None

        selector_column_size = [0.1, 0.9]

        disable_extras = False
        # object_exists = False
        options_type = ["Character", TERMS["Tool"]]

        st.subheader("Update library", text_alignment="center")
            
        # st.space()
        col_object_info, col_event_info = st.columns([0.8, 0.2], vertical_alignment="top")
        with col_object_info:
            
            
            with st.container(width="stretch", height=60, vertical_alignment="center"):
                col_label, col_options = st.columns(selector_column_size, vertical_alignment="center")
                col_label.markdown("TO DO")
                reg_setting = col_options.pills("Registration setting", list(options_reg.keys()), default=list(options_reg.keys())[0], key="regset", label_visibility="collapsed")
            
            # if reg_setting == f"New {TERMS["Event"].lower()} of old":

            def collect_object_info():
                # object_database = collect_database(st.session_state["type"])
                name = st.session_state["name"]
                if name not in object_database.keys():
                    pass
                elif name and not reg_setting == list(options_reg.keys())[0]:
                    settings = object_database[name]
                    if st.session_state["type"] == "Character":
                        st.session_state["tool"] = settings[TERMS["Tool"]]
                        st.session_state["attribute"] = settings[TERMS["Attribute"]]
                        st.session_state["origin"] = settings[TERMS["Origin"]]
                    else:
                        # print(settings)
                        st.session_state["tool"] = settings["Type"]


            col_name, col_type = st.columns([5, 5], vertical_alignment="center")
            with col_name:
                if reg_setting == list(options_reg.keys())[0]:
                    st.text_input("Name", key="name", placeholder=f"Enter new {st.session_state["type"].lower()}", label_visibility="collapsed")
                else:
                    st.selectbox(f"{st.session_state["type"]}s", options_object, index=None, placeholder=f"Select {st.session_state["type"].lower()}", key="name", on_change=collect_object_info, label_visibility="collapsed")



            with col_type:
                # st.radio("Object type", options_type, key="type", label_visibility="collapsed")
                type_selected = st.pills("Object type", options_type, key="type", label_visibility="collapsed")
                disable_extras = type_selected == TERMS["Tool"]
            
            with st.container(width="stretch", height=60, vertical_alignment="center"):
                col_label, col_options = st.columns(selector_column_size, vertical_alignment="center")
                col_label.markdown(TERMS["Tool"])
                
                col_options.pills("Tool", options=options_tool, key="tool", label_visibility="collapsed", width="stretch")
                

            with st.container(width="stretch", height=60, vertical_alignment="center"):
                col_label, col_options = st.columns(selector_column_size, vertical_alignment="center")
                col_label.markdown(TERMS["Attribute"])
                
                col_options.pills("Attribute", options_attribute, key="attribute", disabled=disable_extras, label_visibility="collapsed", width="stretch")

            with st.container(width="stretch", height=60, vertical_alignment="center"):
                col_label, col_options = st.columns(selector_column_size, vertical_alignment="center")
                col_label.markdown(TERMS["Origin"])
                
                col_options.pills("Origin", options_origin, key="origin", disabled=disable_extras, label_visibility="collapsed", width="stretch")

        with col_event_info:
            # with st.container(border=False, width="stretch", height=60, vertical_alignment="bottom"):
            values = dict()
            for x in presets.keys():
                values[x] = st.session_state[x]
            values["date"] = st.session_state["date"]
            object_exists = True if st.session_state["name"] in object_database.keys() else False
            data_is_valid = False
            if st.session_state["regset"] == list(options_reg.keys())[0] and object_exists:
                data_is_valid, save_button_msg = False, "Already in library"
            elif st.session_state["regset"] == list(options_reg.keys())[2]:
                data_is_valid, save_button_msg = True, f"Delete {st.session_state["type"]}"
            elif st.session_state["regset"] == list(options_reg.keys())[4]:
                save_button_msg = f"Delete {TERMS["Event"]}"
                if len(object_database[st.session_state["name"]][TERMS["Event"]]) > 0:
                    data_is_valid = True
            else:
                data_is_valid, save_button_msg = True, "Save"
            # print(st.session_state["regset"], object_exists)
            object_database = collect_database(st.session_state["type"])
            is_tool = values["type"] == TERMS["Tool"]
            data_is_collected, name, new_data, new_event, event_date = _save_data(TERMS, values, data_is_valid, save_button_msg, is_tool)
            # data_is_collected, name, new_data = _save_data(TERMS, st.session_state["name"], st.session_state["tool"], st.session_state["attribute"], st.session_state["origin"], st.session_state["state"], st.session_state["source"], st.session_state["attempt"])
            if data_is_collected: 
                # def event_index(yymmdd, keylist):
                #     return f"{yymmdd}-{len(keylist)-1}"

                # is_static = True if st.session_state["regset"] == list(options_reg.keys())[1] else False
                object_type = TERMS[f"CLI{st.session_state["type"]}"]
                
                if st.session_state["regset"] == list(options_reg.keys())[3]:
                    new_data[name][TERMS["Event"]] = object_database[name][TERMS["Event"]]
                elif st.session_state["regset"] in [list(options_reg.keys())[0], list(options_reg.keys())[1], list(options_reg.keys())[4]]:
                    # print(name)
                    event_data = dict() if st.session_state["regset"] == list(options_reg.keys())[0] else object_database[name][TERMS["Event"]]
                    if st.session_state["regset"] != list(options_reg.keys())[4]: 
                        event_data[f"{event_date}"] = new_event
                    else:
                        event_data.pop(event_date)
                    adjusted_data = dict()
                    event_data = dict(sorted(event_data.items()))
                    if len(event_data.keys()) > 0:
                        n = 0
                        for x, y in event_data.items():
                            adjusted_data[f"{x[:6]}-{n}"] = y
                            n =+ 1
                            
                    new_data[name][TERMS["Event"]] = adjusted_data
                # elif st.session_state["regset"] == list(options_reg.keys())[0]:
                #     event_data[f"{event_date}-0"] = new_event
                #     new_data[name][TERMS["Event"]] = event_data
                # print(new_data)
                _update_object(arciv, negotiator, DATAPATH, name, object_type, new_data, options_reg[reg_setting])

            date_min = data_options["Value limits"]["Date"][0]
            date_min = datetime.datetime(
                int("20"+date_min[0:2]),
                int(date_min[2:4]), 
                int(date_min[4:6]))
            date_min = datetime.date.today()
            
            disable_dates = False
            if st.session_state["regset"] == list(options_reg.keys())[4]:
                options_dates = list()
                date_default = 0
                disable_dates = True
                if st.session_state["name"]: 
                    options_dates = object_database[st.session_state["name"]][TERMS["Event"]].keys()
                    disable_dates = False
                    # st.session_state["date"] = None
                    # date_default = len(options_dates) - 1
                st.selectbox(f"Select date", options_dates, key="date", disabled=disable_dates, label_visibility="collapsed")
            else:
                # print(st.session_state["date"])
                # if st.session_state["date"] is str(): st.session_state["date"] = datetime.date.today()
                # print(st.session_state["date"])
                try:
                    date = st.session_state["date"].strftime("%y%m%d")
                except:
                    st.session_state["date"] = datetime.date.today()
                st.date_input("First received", min_value=date_min, max_value=date_min, key="date", label_visibility="collapsed")
                
            
            options_source = data_options["Source"]
            st.selectbox(f"{TERMS["Source"]}", options_source, index=0, key="source", on_change=update_source_state, label_visibility="visible")
            source = update_source_state()

            options_state = data_options["State alternatives"]
            no_chance = st.session_state["source"] == TERMS["Standard source"]

            st.selectbox("Success", options_state, index=0, key="state", placeholder="Win or loose?", disabled=no_chance, label_visibility="collapsed")

            limit = attempts[source]["Limit"]

            st.number_input(f"{TERMS["Attempt"]}", min_value=0, max_value=limit, key="attempt")


            
# def _save_data(TERMS, namevar, toolvar, attributevar, originvar, statevar, sourcevar, attemptvar):
#     name_done, tool_done, attribute_done, origin_done, state_done = [False]*5

def _save_data(TERMS, values, data_is_valid, save_button_msg, is_tool):
    name_done, tool_done, attribute_done, origin_done, state_done = [False]*5
    if data_is_valid:
        # st.markdown("")
        disable_extras = values["type"] == TERMS["Tool"]
        
        if values["name"]: name_done = True
        if values["tool"]: tool_done = True
        if not disable_extras:
            if values["attribute"]: attribute_done = True
            if values["origin"]: origin_done = True
        else:
            attribute_done, origin_done = True, True
        if not values["state"]:
            if values["source"] == TERMS["Standard source"]: state_done = True
        else:
            state_done = True
    # st.markdown("<style>.st-key-save .stButton {line-height: 0 !important; display: flex !important; align-items: flex-start !important;}</style>", unsafe_allow_html=True)
    # st.markdown("<style>.st-key-save .stButton button {height: 60px; margin: 0; vertical-align: top;}</style>", unsafe_allow_html=True)
    # st.markdown("<style>.st-key-save button p {font-size: 1.7rem;}</style>", unsafe_allow_html=True)
    if all([name_done, tool_done, attribute_done, origin_done, state_done]):
        # object_type = TERMS[f"CLI{st.session_state["type"]}"]
        name = values["name"].title()
        new_data = dict()
        new_data[name] = dict()
        if not is_tool:
            new_data[name][TERMS["Origin"]] = values["origin"]
            new_data[name][TERMS["Attribute"]] = values["attribute"]
        new_data[name][TERMS["Tool"]] = values["tool"]
        # for x, y in {"origin": values["origin"], "attribute": values["attribute"], "tool": values["tool"]}.items():
        #     new_data[name][TERMS[x.title()]] = y

        
        attempt_data = {
            TERMS["Source"]: values["source"],
            TERMS["Attempt"]: values["attempt"],
            "State": values["state"]
        }

        # new_data[name][TERMS["Event"]] = attempt_data
        # is_static = True if st.session_state["regset"] == options_reg[1] else False
        data_is_collected = st.button(f"{save_button_msg}", key="save", type="primary", width="stretch")
        
        # if not is_index_date:
        #     try:
        #         date = values["date"].strftime("%y%m%d")
        #     except:
        #         date = datetime.date.today()

        
        return data_is_collected, name, new_data, attempt_data, values["date"]
    
    else:
        # st.markdown("<style>.st-key-save button p {font-size: 1.7rem;}</style>", unsafe_allow_html=True)
        st.button(f"{save_button_msg}", key="save", type="secondary", width="stretch")
        return False, None, None, None, None


def _update_object(arciv, negotiator, DATAPATH, name, object_type, new_data, edit_setting):
    # edit_setting = {
    #     "add_new": [False, False, False],
    #     "add_event": [True, False, False],
    #     "del_entry": [False, True, False],
    #     "edit_old": [False, False, True],
    #     "del_event": [False, False, True]
    # }
    is_static, for_deletion, for_renaming = edit_setting

    
    datafile = DATAPATH[object_type]
    backup_frequency = [101, 31, 11, 2]

    if arciv.backup(negotiator, backup_frequency, object_type[:6]+"_data"): 
    # if True:
        updated_library, action_verification = arciv.join_data(new_data, name, for_deletion, for_renaming, other_file=datafile, join_path="data", need_sorting=True, is_static=is_static)
    if updated_library:
        arciv.writer(updated_library, other_file=datafile, join_path="data")
        print(f"\nLibrary updated, {action_verification}!\n")