import streamlit as st
import os
import pandas as pd

def table_view(component_key, height, TERMS, object_type, table_style, arciv, negotiator, DIRECTORIES, DATAPATH, data_options, UITERMS):
    # print(object_type, 1)
    with st.container(key=f"{component_key}_head", height="content"):
        title = "Character" if object_type == "Character" else TERMS[object_type]
        st.markdown(f"##### *{title} history*", text_alignment="left")
    # with st.container(border=True, key=f"{component_key}_main", height="stretch"):
        # st.markdown("hello there")
    with st.container(height="stretch"):

        # print(object_type, 2)
        def collect_data(reference):
            # for x in ["Character", "Tool"]
            data_reference = TERMS[reference]
            datafile = DATAPATH[data_reference]
            # files = [DATAPATH["CharReport"], DATAPATH["ToolReport"]]
        
            object_database = arciv.reader(datafile, join_path="data")

            return object_database
        


        # def data_upload(file_list):
        #     # df = pd.read_csv(file)
        #     # return df
        #     df_list = list()
        #     for file in file_list:
        #         report_path = os.path.join(DIRECTORIES["DataFolder"], file)
        #         df = pd.read_csv(report_path)
        #         # df[UITERMS["attempts"]] = pd.to_numeric(UITERMS["attempts"], errors="coerce")
        #         df_list.append(df)

        #     return df_list
        collected = dict()
        # print(object_type, 3)
        def data_to_df(object_database):
            rows = []

            for name, info in object_database.items():
                collected[name] = 0
                # attempts = dict()
                # pulls = info.get("Pull", {})
                for index, details in info[TERMS["Event"]].items():
                    date, idx = index.split("-")
                    if object_type == "Character": 
                        viewname = f"{name} C{collected[name]}"
                    else:
                        viewname = name
                    # attempt, source, state = ["-"]*3
                    attempt = details[TERMS["Attempt"]] if details[TERMS["Attempt"]] else None
                    source = details[TERMS["Source"]] if details[TERMS["Source"]] else None
                    state = details[TERMS["State"]] if details[TERMS["State"]] else None
                    rows.append({
                        "Date": date,
                        "Name": viewname,
                        "Index": idx,
                        TERMS["Attempt"]: attempt,
                        "Source": source,
                        TERMS["State"]: state
                    })
                    collected[name] += 1
            df = pd.DataFrame(rows)

            # df["Date"] = pd.to_datetime(df["Date"], format="%y%m%d")
            df = df.sort_values(["Date", "Index"], ascending=False).drop(columns=["Index", f"{TERMS["State"]}"]).fillna("")
            df[TERMS["Attempt"]] = pd.to_numeric(df[TERMS["Attempt"]], errors="coerce").astype("Int64")
            
            # df_display = df.copy()
            # df.style.set_properties(subset=[TERMS["Attempt"]], **{"text-align": "right"})
            return df
        

        if object_type == "Character":
            database = collect_data("Character")
        elif object_type == "Tool":
            database = collect_data("Tool")
        # for x in [0, 1]:
        # char_df, tool_df = data_to_df([char_database, tool_database][x])

        # print(object_type, 4)
        df = data_to_df(database)
        # tool_df = data_to_df(tool_database)

        # char_df[TERMS["Attempt"]] = char_df[TERMS["Attempt"]], errors="coerce"[TERMS["Attempt"]], errors="coerce").astype("Int64")
        # char_df[TERMS["Attempt"]] = pd.to_numeric(char_df[TERMS["Attempt"]], errors="coerce").astype("Int64")
        # tool_df[TERMS["Attempt"]] = pd.to_numeric(tool_df[TERMS["Attempt"]], errors="coerce").astype("Int64")

        # print("---")
        # print("df here")
        # print(char_df)
        # print("---")
        # df_char, df_tool = data_upload(files)
        # col_1, col_2 = st.columns(2, width="stretch")
        # with col_1:
            # st.markdown("---")
            # st.subheader(f"{UITERMS["datatable_char"]}")
        
        # config = st.column_config.DateColumn("Name")
        # print(object_type, 5)
        # st.html("<style> .st-key_table th {background-color: #ffffff </style>")
        # df = pd.DataFrame({f"Column {i}": [*"abcdef"] for i in range(5)})

        # st.dataframe(
        #     df.style.applymap(
        #         lambda _: "background-color: CornflowerBlue;", subset=([-1], slice(None))
        #     )
        # )
        st.dataframe(
            df.style.set_properties(
                subset=[TERMS["Attempt"]], 
                **{"text-align": "right"}
            )
            .set_properties(**{"background-color": table_style[1]}), 
            column_config={TERMS["Attempt"]: {"width": "xsmall"}},
            hide_index=True, 
            height="stretch",
            key="table"
        )
            # st.dataframe(char_df.style.set_properties(subset=[TERMS["Attempt"]], **{"text-aligh: 'right'}), hide_index=True, height="stretch")
        # else:
        #     st.dataframe(
        #         tool_df.style.set_properties(
        #             subset=[TERMS["Attempt"]], 
        #             **{"text-align": "right"}
        #         ), 
        #         column_config={TERMS["Attempt"]: {"width": "xsmall"}},
        #         hide_index=True, 
        #         height="stretch"
        #     )
        # print(object_type, 6)
        # with col_2:
        #     st.markdown("---")
        #     st.subheader(f"{UITERMS["datatable_tool"]}")
        #     st.dataframe(data=df_tool)

