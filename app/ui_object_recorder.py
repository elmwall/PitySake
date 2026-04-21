import streamlit as st
import datetime

def register_object(arciv, negotiator, DIRECTORIES, DATAPATH, data_options, TERMS, attempts):

    def update_object(object_type, name, new_data, is_static, for_deletion=False, for_renaming=False):
        datafile = DATAPATH[object_type]
        
        # print(attempts)
        backup_frequency = [101, 31, 11, 2]
        # print(is_static)
        if arciv.backup(negotiator, backup_frequency, object_type[:6]+"_data"): 
            updated_library, action_verification = arciv.join_data(new_data, name, for_deletion, for_renaming, other_file=datafile, join_path="data", need_sorting=True, is_static=is_static)
        if updated_library:
            # print("data ok")
            # print(new_data)
            arciv.writer(updated_library, other_file=datafile, join_path="data")
            print(f"\nLibrary updated, {action_verification}!\n")

    with st.container(width=935, height=400):
        for x in ["tool", "attribute", "origin", "name", "state"]:
            if x not in st.session_state: st.session_state[x] = None
        disable_extras = False
        form_complete = False
        name_done, tool_done, attribute_done, origin_done, state_done = [False]*5
        st.subheader("Update library", text_alignment="center")
        options_type = ["Character", TERMS["Tool"]]
        col_type, col_reg_setting, col_save = st.columns([0.14, 0.66, 0.2], vertical_alignment="center")
        # with col_title:
        with col_type:
            type = st.radio("Object type", options_type, key="type", label_visibility="collapsed")
        with col_reg_setting:
            options_reg = ["Add completely new", f"New {TERMS["Event"].lower()} of old", "Delete entry", "Rename entry", f"Delete {TERMS["Event"].lower()}"]
            st.pills("Registration setting", options_reg, default=options_reg[0], key="regset", label_visibility="collapsed")
        with col_save:
            st.markdown("")
            # print(st.session_state["tool"], st.session_state["attribute"], st.session_state["origin"])
            disable_extras = st.session_state["type"] == TERMS["Tool"]
            
            if st.session_state["name"]: name_done = True
            if st.session_state["tool"]: tool_done = True
            if not disable_extras:
                if st.session_state["attribute"]: attribute_done = True
                if st.session_state["origin"]: origin_done = True
            else:
                attribute_done, origin_done = True, True
            if not st.session_state["state"]:
                if st.session_state["source"] == TERMS["Standard source"]: state_done = True
            else:
                state_done = True
            # print(disable_extras)
            # print()
            # for x in [name_done, tool_done, attribute_done, origin_done, state_done]:
            #     print(x)
            # print()
            # if st.session_state["name"]:
            #     print("test", not st.session_state["state"], not st.session_state["source"])
            #     if not st.session_state["state"] and not st.session_state["source"] == TERMS["Standard source"]:
            #         if not st.session_state["attribute"] or not st.session_state["origin"] or not st.session_state["tool"]:
            #             if st.session_state["tool"] and disable_extras:
            #                 form_complete = True
            #         else:
            #             form_complete = True

            if all([name_done, tool_done, attribute_done, origin_done, state_done]):
                object_type = TERMS[f"CLI{st.session_state["type"]}"]
                name = st.session_state["name"].capitalize()
                new_data = dict()
                new_data[name] = dict()
                for x in ["origin", "attribute", "tool"]:
                    new_data[name][TERMS[x.capitalize()]] = st.session_state[x]
                n=0 ########
                # print("hello", st.session_state["state"])
                attempt_data = {
                    f"{st.session_state["date"].strftime("%y%m%d")}-{n}": {
                        TERMS["Source"]: st.session_state["source"],
                        TERMS["Attempt"]: st.session_state["attempt"],
                        "State": st.session_state["state"]
                    }
                }

                new_data[name][TERMS["Attempt"]] = attempt_data
                is_static = True if st.session_state["regset"] == options_reg[1] else False
                # print(is_static, "reg", st.session_state["regset"], options_reg[1])
                
                st.button(f"Save", key="save", type="primary", on_click=update_object, args=(object_type, name, new_data, is_static), width="stretch")
            else:
                st.button(f"Save", key="save", type="secondary", width="stretch")
            
        
        st.space()
        #TODO
        # st.markdown("select type ... enter previous ... enter pity")
        col_name, col_date = st.columns([0.8, 0.2])

        with col_name:
            if "type" not in st.session_state: 
                st.session_state["type"] = options_type[0]
                # type = options_type[0]
            if st.session_state["regset"] == options_reg[0]:
                name = st.text_input("Name", key="name", placeholder=f"Enter new {st.session_state["type"].lower()}", label_visibility="collapsed")
            else:
                data_reference = TERMS["Character"] if st.session_state["type"] == "Character" else st.session_state["type"]
                datafile = DATAPATH[data_reference]
                object_database = arciv.reader(datafile, join_path="data")
                options_object = object_database.keys()
                # print(options_object)
                name = st.selectbox(f"{st.session_state["type"]}s", options_object, index=None, placeholder=f"Select {st.session_state["type"].lower()}", key="name", label_visibility="collapsed")
            

            def columns():
                return st.columns([0.1, 0.9], vertical_alignment="center")
            
            with st.container():
                st.space()
                col_label, col_options = columns()
                col_label.markdown(TERMS["Tool"])
                options_tool = data_options[TERMS["Character"]][TERMS["Tool"]]
                tool = col_options.pills("Tool", options=options_tool, key="tool", label_visibility="collapsed", width="stretch")

            with st.container():
                st.markdown("<style>.thin-divider {height: 1px; margin: 0.8rem 0 1.4rem; border: 0; border-top: 1px solid #444954}</style><div class='thin-divider'></div>", unsafe_allow_html=True)
                col_label, col_options = columns()
                col_label.markdown(TERMS["Attribute"])
                options_attribute = data_options[TERMS["Character"]][TERMS["Attribute"]]
                attribute = col_options.pills("Attribute", options_attribute, key="attribute", disabled=disable_extras, label_visibility="collapsed", width="stretch")

            with st.container():
                st.markdown("<div class='thin-divider'></div>", unsafe_allow_html=True)
                col_label, col_options = columns()
                col_label.markdown(TERMS["Origin"])
                options_origin = data_options[TERMS["Character"]][TERMS["Origin"]]
                origin = col_options.pills("Origin", options_origin, key="origin", disabled=disable_extras, label_visibility="collapsed", width="stretch")

        with col_date:
            
            # type = st.selectbox("Object type", options_type, index=0, label_visibility="collapsed")
            min_date = data_options["Value limits"]["Date"][0]
            min_date = datetime.datetime(
                int("20"+min_date[0:2]),
                int(min_date[2:4]), 
                int(min_date[4:6]))
            date = st.date_input("First received", value="today", min_value=min_date, key="date", label_visibility="collapsed")
            
            # if not st.session_state["source"]: st.session_state["source"] = f"Character {TERMS["Temp"]}"
            def update_source_state():
                source = st.session_state["source"]
                if source == TERMS["Temp"]:
                    source = f"Character {source}" if st.session_state["type"] == "Character" else f"{TERMS["Tool"]} {source}"
                elif source == TERMS["Standard source"]:
                    st.session_state["state"] = None
                st.session_state["attempt"] = attempts[source][TERMS["Attempt"]]
                return source
            
            options_source = data_options["Source"]
            st.selectbox(f"{TERMS["Source"]}", options_source, index=0, key="source", on_change=update_source_state, label_visibility="visible")
            source = update_source_state()
            # if source == TERMS["Temp"]:
            #     source = f"Character {source}" if st.session_state["type"] == "Character" else f"{TERMS["Tool"]} {source}"

            options_state = data_options["State alternatives"]
            no_chance = st.session_state["source"] == TERMS["Standard source"]
            # print("no chance", no_chance)
            
            # if no_chance:
            #     option_state = [None]
            #     st.session_state["state"] = None
            # else:
            # data_options["State alternatives"]
            #     st.selectbox("Success", options_state, index=0, key="state", disabled=no_chance, label_visibility="collapsed")
            #     # st.session_state["state"] = None
            # else:
            st.selectbox("Success", options_state, index=0, key="state", placeholder="Win or loose?", disabled=no_chance, label_visibility="collapsed")
                # st.session_state["state"] = None

            # print(st.session_state["state"])
            limit = attempts[source]["Limit"]
            # limit_init_val = adjust_attempt()
            attempt_value = st.number_input(f"{TERMS["Attempt"]}", min_value=0, max_value=limit, key="attempt")


            





