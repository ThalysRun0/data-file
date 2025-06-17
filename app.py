import streamlit as st
import pandas as pd
import chardet
import random
import json
import io
import os, sys

if "pattern_name" not in st.session_state:
    st.session_state.pattern_name = {}              # pattern name
if "file_buffers" not in st.session_state:
    st.session_state.file_buffers = {}              # raw content
if "file_detected_encoding" not in st.session_state:
    st.session_state.file_detected_encoding = {}    # encoding format
if "file_encoding" not in st.session_state:
    st.session_state.file_encoding = {}             # encoding format
if "file_format" not in st.session_state:
    st.session_state.file_format = {}               # reader format
if "file_format_options" not in st.session_state:
    st.session_state.file_format_options = {}       # options format
if "dataframes" not in st.session_state:
    st.session_state.dataframes = {}                # dataframe
if "actions" not in st.session_state:
    st.session_state.actions = {}                   # transformations
if "conversions" not in st.session_state:
    st.session_state.conversions = {}               # column conversion
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
if "update_conv_type" not in st.session_state:
    st.session_state.update_conv_type = ""

available_types = ['int', 'float', 'str', 'bool', 'datetime']

def modify_col_type(name):
    st.session_state.update_conv_type = name

def convert_type(name, type_str):
    if type_str == 'int':
        return f"df['{name}'] = pd.to_numeric(df['{name}'], errors='coerce').astype('Int64')"
    elif type_str == 'float':
        return f"df['{name}'] = pd.to_numeric(df['{name}'], errors='coerce')"
    elif type_str == 'str':
        return f"df['{name}'] = df['{name}'].astype(str)"
    elif type_str == 'bool':
        return f"df['{name}'] = df['{name}'].astype(bool)"
    elif type_str == 'datetime':
        return f"df['{name}'] = pd.to_datetime(df['{name}'], errors='coerce')"
    else:
        return ""

def simulate_action(source: pd.DataFrame, action):
    if action != "":
        try:
            local_vars = {"df": source.copy()}
            exec("import pandas as pd; " + action, {}, local_vars)
            st.toast("Expression is valid", icon=":material/check:")
            st.session_state.current_simu = local_vars["df"]
        except Exception as e:
            st.error(f"Error : {e}")
            st.toast("Expression is invalid", icon=":material/dangerous:")
    else:
        st.toast("Nothing to simulate", icon=":material/dangerous:")

def add_action(action):
    if action != "":
        st.session_state.actions[file_name].append(action)
        st.toast("Added to transformation list", icon=":material/info:")
    else:
        st.toast("Nothing to add", icon=":material/dangerous:")

def save_pattern(pattern_name, file_name):
    params_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "params")
    if not os.path.exists(params_dir):
        os.makedirs(params_dir)
    with open(f"{params_dir}/{pattern_name}.json", "w") as f:
        tmp = {}
        tmp['file_detected_encoding'] = st.session_state.file_detected_encoding[file_name]
        tmp['file_encoding'] = st.session_state.file_encoding[file_name]
        tmp['file_format'] = st.session_state.file_format[file_name]
        tmp['file_format_options'] = st.session_state.file_format_options[file_name]
        tmp['actions'] = st.session_state.actions[file_name]
        tmp['conversions'] = st.session_state.conversions[file_name]
        json.dump(tmp, f)
    st.session_state.pattern_name[file_name] = pattern_name
    st.toast("Pattern has been saved", icon=":material/check:")

def move_action(liste, index, direction=1):
    if direction != 0:
        new_index = (index + direction) % len(liste)
        element = liste.pop(index)
        liste.insert(new_index, element)

def update_simu_text(action):
    st.session_state.transform_texte = action

def read_file(file_name, file_format, decoding_format, sep=",") -> pd.DataFrame:
    df = None
    if file_name in st.session_state.file_buffers:
        file_bytes = st.session_state.file_buffers[file_name]
        try:
            if file_format == "csv":
                df = pd.read_csv(io.BytesIO(file_bytes), encoding=decoding_format, sep=sep)
            elif file_format == "txt":
                df = pd.read_csv(io.BytesIO(file_bytes), delimiter="\t", encoding=decoding_format, sep=sep)
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

def get_encoding(content):
    return chardet.detect(content).get("encoding", "utf-8")

def apply_encoding(content):
    st.session_state.file_encoding[file_name] = get_encoding(content)

st.set_page_config(layout="wide")

with st.sidebar:
    uploaded_file = st.file_uploader(" ", type=["csv", "txt", "xlsx", "xls"], accept_multiple_files=False, key=st.session_state.uploader_key)
    if uploaded_file is not None:
        if uploaded_file.name not in st.session_state.file_buffers:
            content = uploaded_file.read()
            detected_encoding = get_encoding(content)
            detected_encoding = "utf-8" if None == detected_encoding else detected_encoding
            st.session_state.file_detected_encoding[uploaded_file.name] = detected_encoding
            st.session_state.file_encoding[uploaded_file.name] = detected_encoding
            st.session_state.file_buffers[uploaded_file.name] = content
            st.session_state.actions[uploaded_file.name] = []
            st.session_state.conversions[uploaded_file.name] = []
            st.session_state.pattern_name[uploaded_file.name] = ""
            st.session_state.current_file = uploaded_file.name
            st.session_state.uploader_key = str(random.randint(0, 100000)) # make the upload as new widget on each upload
            st.session_state.current_simu = None
            st.rerun()

    if st.session_state.file_buffers:
        st.title("📂 Uploaded Files")
        for file_key in list(st.session_state.file_buffers.keys()):
            col_del1, col_del2 = st.columns([1, 5], vertical_alignment="top")
            with col_del1:
                if st.button("", icon=":material/delete:", key=f"delete_{file_key}"):
                    st.session_state.file_buffers.pop(file_key, None)
                    st.session_state.file_detected_encoding.pop(file_key, None)
                    st.session_state.file_encoding.pop(file_key, None)
                    st.session_state.file_format.pop(file_key, None)
                    st.session_state.file_format_options.pop(file_key, None)
                    st.session_state.dataframes.pop(file_key, None)
                    st.session_state.actions.pop(file_key, None)
                    st.session_state.conversions.pop(file_key, None)
                    st.session_state.current_file = None
                    st.rerun()
            with col_del2:
                if st.button(file_key, key=file_key, help=f"Detected encoding: {st.session_state.file_detected_encoding[file_key]}"):
                    st.session_state.current_file = file_key
                    st.session_state.current_simu = None
            tmp_icon = ":material/warning:" if st.session_state.file_encoding[file_key] != st.session_state.file_detected_encoding[file_key] else ":material/check:"
            tmp_color = "orange" if st.session_state.file_encoding[file_key] != st.session_state.file_detected_encoding[file_key] else "green"
            st.badge(st.session_state.file_encoding[file_key] if st.session_state.file_encoding[file_key] == st.session_state.file_detected_encoding[file_key] else st.session_state.file_detected_encoding[file_key]
                , icon=tmp_icon
                , color=tmp_color)

    else:
        st.warning("No file imported")
        st.stop()

if st.session_state.current_file is None:
    st.warning("No file selected")
    st.stop()
else:
    file_name = st.session_state.current_file

    col_pat1, col_pat2, col_pat3 = st.columns([3, 1, 1], vertical_alignment="bottom")
    with col_pat1:
        pattern_name = st.text_input("Read pattern name", value=st.session_state.pattern_name[file_name])

    with col_pat2:
        if st.button("Load existing read pattern", icon=":material/settings_backup_restore:"):
            st.session_state.show_pattern_loader = True

        if st.session_state.show_pattern_loader:
            uploaded_file = st.file_uploader("Choose read pattern file", type="json")
            if uploaded_file is not None:
                config = json.load(uploaded_file)
                st.session_state.file_detected_encoding[file_name] = config['file_detected_encoding']
                st.session_state.file_encoding[file_name] = config['file_encoding']
                st.session_state.file_format[file_name] = config['file_format']
                st.session_state.file_format_options[file_name] = config['file_format_options']
                st.session_state.actions[file_name] = config['actions']
                st.session_state.conversions[file_name] = config['conversions']
                st.session_state.pattern_name[file_name] = os.path.splitext(os.path.basename(uploaded_file.name))[0]
                st.session_state.show_pattern_loader = False
                st.toast("Pattern has been loaded", icon=":material/info:")
                st.rerun()

    with col_pat3:
        st.button("Save current read pattern", icon=":material/save:", key="save_patter_top", on_click=save_pattern, args=[pattern_name, file_name])

    st.html("<hr>")
    col_read1, col_read2 = st.columns([1, 10], vertical_alignment="bottom")
    with col_read1:
        st.button("", icon=":material/autorenew:", key="detect_encoding", on_click=apply_encoding, args=[st.session_state.file_buffers[file_name]], help="Detect encoding of the file")
    with col_read2:
        st.title(f"`{file_name}`")
    with st.expander("Read parameters", expanded=True):
        col1, col2 = st.columns([1, 1], vertical_alignment="bottom")
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

        st.html("<hr>")
        sep = ","
        if file_format == "csv":
            sep = st.text_input("Separator", value=",", help="Character used to separate values in the CSV file")
        st.button("Apply read parameters", icon=":material/read_more:", on_click=read_file, args=[file_name, file_format, decoding_format, sep])

    if file_name in st.session_state.dataframes:
        with st.expander("infos", expanded=False):
            buffer = io.StringIO()
            st.session_state.dataframes[file_name].info(buf=buffer)
            st.text(buffer.getvalue())

        with st.expander("Preview", expanded=True):
            st.dataframe(st.session_state.dataframes[file_name])

        with st.expander("Columns", expanded=True):
            colonnes_to_convert = st.multiselect(
                "🔍 Select columns",
                options=st.session_state.dataframes[file_name].columns.tolist(),
                default=[],
                help="Type name or part to filter the columns"
            )
            if colonnes_to_convert:
                if st.button("Add as Selection action", icon=":material/add_circle:"):
                    col_select = ""
                    for col in colonnes_to_convert:
                        col_select.join(f"\"{col}\", ")
                    add_action(f"df=df[{colonnes_to_convert}]")

        with st.expander("Types", expanded=False):
            colonnes_to_modify = st.selectbox("Select column", 
                                            options=st.session_state.dataframes[file_name].columns.tolist(), 
                                            help="Type name or part to filter the columns")
            current_type = str(st.session_state.dataframes[file_name][colonnes_to_modify].dtype)
            col_conv1, col_conv2 = st.columns([1, 3], vertical_alignment="bottom")
            with col_conv1:
                new_type = st.selectbox(
                    f"{colonnes_to_modify} (actual type : {current_type})",
                    options=available_types,
                    index=available_types.index('str') if current_type not in available_types else available_types.index(current_type),
                    key=f"add_conv_{colonnes_to_modify}",
                )
            with col_conv2:
                if st.button("", icon=":material/add:", key=f"add_col_convert"):
                    st.session_state.conversions[file_name].append({"name": colonnes_to_modify, 
                                                                    "from": str(st.session_state.dataframes[file_name][colonnes_to_modify].dtype), 
                                                                    "to": new_type,
                                                                    "action": convert_type(colonnes_to_modify, new_type)})
            if len(st.session_state.conversions[file_name]) > 0:
                with st.container(border=True):
                    for i, conv in enumerate(st.session_state.conversions[file_name]):
                        col_convdyn1, col_convdyn2, col_convdyn3 = st.columns([1, 1, 4], vertical_alignment="bottom")
                        with col_convdyn1:
                            st.text(conv['name'])
                        with col_convdyn2:
                            new_type_dyn = st.selectbox(
                                "unitary conversion",
                                options=available_types,
                                index=available_types.index('str') if conv['to'] not in available_types else available_types.index(conv['to']),
                                key=f"update_conv_{i}_{colonnes_to_modify}",
                                on_change=modify_col_type, args=[conv['name']],
                                label_visibility='hidden'
                            )
                        with col_convdyn3:
                            if st.button("", icon=":material/delete:", key=f"delete_convert_col_{i}"):
                                st.session_state.conversions[file_name].pop(i)
                                st.rerun()

                    if st.session_state.update_conv_type != "":
                        if file_name in st.session_state.conversions:
                            index = 0
                            for i, conv in enumerate(st.session_state.conversions[file_name]):
                                if st.session_state.update_conv_type in conv:
                                    index = i
                                    break

                            st.session_state.conversions[file_name][i]['to'] = new_type_dyn
                            st.session_state.conversions[file_name][i]['action'] = convert_type(st.session_state.update_conv_type, new_type_dyn)
                        st.session_state.update_conv_type = ""
                        st.rerun()

                    if len(st.session_state.conversions[file_name]) > 0:
                        if st.button("Delete all", icon=":material/delete:", key=f"delete_convert"):
                            st.session_state.conversions[file_name] = []
                            st.rerun()
                        if st.button("Add as Conversion action", icon=":material/add_circle:"):
                            for conv in st.session_state.conversions[file_name]:
                                add_action(conv['action'])
                    #st.code(st.session_state.conversions[file_name])

        with st.expander("Actions", expanded=True):
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

            if st.button("Apply all actions on raw", icon=":material/texture_add:", key=f"run_{file_name}"):
                df = read_file(file_name, file_format, decoding_format)
                try:
                    local_vars = {"df": df.copy()}
                    for action in st.session_state.actions[file_name]:
                        exec(action, {}, local_vars)
                    st.session_state.current_simu = local_vars["df"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Error : {e}")

        with st.expander("Simulate", expanded=True):
            transform_texte = st.text_area("Pandas code (ex: df['A'] = df['A'] * 2)", help="https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html", key=f"transform_texte")

            col_simu1, col_simu2, col_simu3 = st.columns([1, 1, 1], vertical_alignment="center")
            with col_simu1:
                st.button("Add as new action", icon=":material/add_circle:", key=f"add_{file_name}", on_click=add_action, args=[transform_texte])

            with col_simu2:
                st.button("Simulate on source", icon=":material/stream:", key=f"simulate_{file_name}", on_click=simulate_action, args=[st.session_state.dataframes[file_name], transform_texte])

            with col_simu3:
                if st.session_state.current_simu is not None:
                    st.button("Apply as next step on current simulated data", icon=":material/texture_add:", key=f"apply_{file_name}", on_click=simulate_action, args=[st.session_state.current_simu, transform_texte])

            if st.session_state.current_simu is not None:
                st.dataframe(st.session_state.current_simu)

        st.html("<hr>")

        st.button("Save current read pattern", icon=":material/save:", key="save_patter_bottom", on_click=save_pattern, args=[pattern_name, file_name])