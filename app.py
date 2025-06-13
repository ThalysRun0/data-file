import streamlit as st
import pandas as pd
import random
import json
import io
import os

def simulate_action(source: pd.DataFrame):
    try:
        local_vars = {"df": source.copy()}
        exec(transform_texte, {}, local_vars)
        st.toast("Expression is valid", icon=":material/check:")
        st.session_state.current_simu = local_vars["df"]
    except Exception as e:
        st.error(f"Error : {e}")
        st.toast("Expression is invalid", icon=":material/dangerous:")

def save_pattern(pattern_name, file_name):
    print(os.path.dirname(__file__))
    with open(f"{pattern_name}.json", "w") as f:
        tmp = {}
        tmp['file_encoding'] = st.session_state.file_encoding[file_name]
        tmp['file_format'] = st.session_state.file_format[file_name]
        tmp['actions'] = st.session_state.actions[file_name]
        json.dump(tmp, f)
    st.toast("Pattern has been saved", icon=":material/check:")

def move_action(liste, index, direction=1):
    if direction != 0:
        new_index = (index + direction) % len(liste)
        element = liste.pop(index)
        liste.insert(new_index, element)

def update_simu_text(action):
    st.session_state.transform_texte = action

def read_file(file_name, file_format, decoding_format) -> pd.DataFrame:
    df = None
    if file_name in st.session_state.file_buffers:
        file_bytes = st.session_state.file_buffers[file_name]
        try:
            if file_format == "csv":
                df = pd.read_csv(io.BytesIO(file_bytes), encoding=decoding_format)
            elif file_format == "txt":
                df = pd.read_csv(io.BytesIO(file_bytes), delimiter="\t", encoding=decoding_format)
            elif file_format == "json":
                df = pd.read_json(io.BytesIO(file_bytes), encoding=decoding_format)
            elif file_format == "excel":
                df = pd.read_excel(io.BytesIO(file_bytes), engine='xlrd')
            else:
                st.error("Unsupported format")
                return None

            st.session_state.dataframes[file_name] = df
            st.session_state.file_encoding[file_name] = decoding_format
            st.session_state.file_format[file_name] = file_format
            st.toast("File has been converted to DataFrame.", icon=":material/check:")
        except Exception as e:
            st.error(f"Read Error : {e}")
            return None
    return df

st.set_page_config(layout="wide")

if "file_buffers" not in st.session_state:
    st.session_state.file_buffers = {}  # raw content
if "file_encoding" not in st.session_state:
    st.session_state.file_encoding = {}  # encoding format
if "file_format" not in st.session_state:
    st.session_state.file_format = {}  # reader format
if "dataframes" not in st.session_state:
    st.session_state.dataframes = {}    # dataframe
if "actions" not in st.session_state:
    st.session_state.actions = {}       # transformations
if "current_file" not in st.session_state:
    st.session_state.current_file = None
if "current_simu" not in st.session_state:
    st.session_state.current_simu = None
if "transform_texte" not in st.session_state:
    st.session_state.transform_texte = "df['A'] = df['A'] * 2"
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = str(random.randint(0, 100000))
if "show_pattern_loader" not in st.session_state:
    st.session_state.show_pattern_loader = False

uploaded_file = st.sidebar.file_uploader(" ", type=["csv", "txt", "xlsx", "xls"], accept_multiple_files=False, key=st.session_state.uploader_key)
if uploaded_file is not None:
    if uploaded_file.name not in st.session_state.file_buffers:
        content = uploaded_file.read()
        st.session_state.file_buffers[uploaded_file.name] = content
        st.session_state.actions[uploaded_file.name] = []
        st.session_state.current_file = uploaded_file.name
        st.session_state.uploader_key = str(random.randint(0, 100000)) # make the upload as new widget on each upload
        st.session_state.current_simu = None
        st.rerun()

with st.sidebar:
    if st.session_state.file_buffers:
        st.title("📂 Uploaded Files")
        col_del1, col_del2 = st.columns([1, 5], vertical_alignment="top")
        for file_key in list(st.session_state.file_buffers.keys()):
            with col_del1:
                if st.button("", icon=":material/delete:", key=f"delete_{file_key}"):
                    st.session_state.file_buffers.pop(file_key, None)
                    st.session_state.file_encoding.pop(file_key, None)
                    st.session_state.file_format.pop(file_key, None)
                    st.session_state.dataframes.pop(file_key, None)
                    st.session_state.actions.pop(file_key, None)
                    st.session_state.current_file = None
                    st.rerun()
            with col_del2:
                if st.button(file_key, key=file_key):
                    st.session_state.current_file = file_key
                    st.session_state.current_simu = None
    else:
        st.warning("No file selected")
        st.stop()

if st.session_state.current_file is None:
    st.warning("No file selected")
    st.stop()
else:
    file_name = st.session_state.current_file
    st.title(f"Selected file : `{file_name}`")
    col_pat1, col_pat2, col_pat3 = st.columns([3, 1, 1], vertical_alignment="bottom")

    with col_pat1:
        pattern_name = st.text_input("Read pattern name", value="any_naming_idea")

    with col_pat2:
        if st.button("Load existing read pattern", icon=":material/settings_backup_restore:"):
            st.session_state.show_pattern_loader = True

        if st.session_state.show_pattern_loader:
            uploaded_file = st.file_uploader("Choose read pattern file", type="json")
            if uploaded_file is not None:
                config = json.load(uploaded_file)
                st.session_state.file_encoding[file_name] = config['file_encoding']
                st.session_state.file_format[file_name] = config['file_format']
                st.session_state.actions[file_name] = config['actions']
                st.session_state.show_pattern_loader = False
                st.toast("Pattern has been loaded", icon=":material/info:")

    with col_pat3:
        st.button("Save current read pattern", icon=":material/save:", key="save_patter_top", on_click=save_pattern, args=[pattern_name, file_name])

    col1, col2, col3 = st.columns([1, 1, 1], vertical_alignment="bottom")
    with col1:
        tmp_encoding_value = "utf-8"
        if file_name is not None:
            if file_name in st.session_state.file_encoding:
                tmp_encoding_value = st.session_state.file_encoding[file_name]
        decoding_format = st.text_input("encoding", value=tmp_encoding_value)
    with col2:
        file_format_available = ["csv", "txt", "json", "excel"]
        tmp_file_format_value = "csv"
        if file_name is not None:
            if file_name in st.session_state.file_format:
                tmp_file_format_value = st.session_state.file_format[file_name]
        file_format = st.selectbox("format", file_format_available, index=file_format_available.index(tmp_file_format_value))
    with col3:
        st.button("Apply read parameters", icon=":material/read_more:", on_click=read_file, args=[file_name, file_format, decoding_format])

    if file_name in st.session_state.dataframes:
        with st.expander("infos", expanded=False):
            buffer = io.StringIO()
            st.session_state.dataframes[file_name].info(buf=buffer)
            st.text(buffer.getvalue())

        with st.expander("Preview", expanded=True):
            st.subheader("Dataframe preview :")
            st.dataframe(st.session_state.dataframes[file_name])

        with st.expander("columns", expanded=True):
            colonnes_selectionnees = st.multiselect(
                "🔍 Select Columns to Use :",
                options=st.session_state.dataframes[file_name].columns.tolist(),
                default=[],
                help="Type name or part to filter the columns"
            )
            if colonnes_selectionnees:
                if st.button("Add as a selection Action"):
                    col_select = ""
                    for col in colonnes_selectionnees:
                        col_select.join(f"\"{col}\", ")
                    update_simu_text(f"df=df[{colonnes_selectionnees}]")

        st.subheader("💡 Simulate a transformation action")
        transform_texte = st.text_area("Code pandas (ex: df['A'] = df['A'] * 2)", help="https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.htmlw", key=f"transform_texte")

        col_simu1, col_simu2, col_simu3 = st.columns([1, 1, 1], vertical_alignment="center")
        with col_simu1:
            if st.button("Add as a new action", icon=":material/add:", key=f"add_{file_name}"):
                st.session_state.actions[file_name].append(transform_texte)
                st.toast("Added to transformation list", icon=":material/info:")

        with col_simu2:
            st.button("Simulate on source", icon=":material/stream:", key=f"simulate_{file_name}", on_click=simulate_action, args=[st.session_state.dataframes[file_name]])

        with col_simu3:
            if st.session_state.current_simu is not None:
                st.button("Apply this step on current simulated data", icon=":material/texture_add:", key=f"apply_{file_name}", on_click=simulate_action, args=[st.session_state.current_simu])

        if st.session_state.current_simu is not None:
            st.dataframe(st.session_state.current_simu)

        st.subheader("📜 Transform action list")
        for i, action in enumerate(st.session_state.actions[file_name]):
            col_code1, col_code2, col_code3, col_code4, col_code5 = st.columns([1, 20, 1, 1, 1], vertical_alignment="center")
            with col_code1:
                st.button(f"{i+1}", on_click=update_simu_text, args=[action])
            with col_code2:
                st.code(f"{action}", language="python")
            with col_code3:
                st.button("", icon=":material/arrow_upward:", key=f"up_action_{i}", on_click=move_action, args=[st.session_state.actions[file_name], i, -1])
            with col_code4:
                st.button("", icon=":material/arrow_downward:", key=f"down_action_{i}", on_click=move_action, args=[st.session_state.actions[file_name], i, 1])
            with col_code5:
                if st.button("", icon=":material/delete:", key=f"delete_{i}"):
                    st.session_state.actions[file_name].pop(i)
                    st.rerun()

        if st.button("Apply all actions on raw", key=f"run_{file_name}"):
            df = read_file(file_name, file_format, decoding_format)
            try:
                local_vars = {"df": df.copy()}
                for action in st.session_state.actions[file_name]:
                    exec(action, {}, local_vars)
                st.session_state.dataframes[file_name] = local_vars["df"]
                st.rerun()
            except Exception as e:
                st.error(f"Error : {e}")

        st.html("<hr>")

        st.button("Save current read pattern", icon=":material/save:", key="save_patter_bottom", on_click=save_pattern, args=[pattern_name, file_name])