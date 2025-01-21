import streamlit as st
import tempfile
import pathlib
import pickle
import os
import copy
import xml.etree.ElementTree as ET
from utils import convert_csv_to_xml, format_csv

# load Custom CSS
def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_path = pathlib.Path(__file__).parent / "assets/style.css"
load_css(css_path)

UPLOAD_DIR = "uploaded_files"
PERSISTENCE_FILE = "schema.pkl"

# Create the directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


# Save schema to file
def load_schema():
    if os.path.exists(PERSISTENCE_FILE) and os.path.getsize(PERSISTENCE_FILE) > 0:
        with open(PERSISTENCE_FILE, "rb") as file:
            loaded_list = pickle.load(file)
        return loaded_list 
    return []

# Save schema to file
def upload_schema():
    schema = st.session_state.schemas
    with open(PERSISTENCE_FILE, "wb") as f:
        pickle.dump(schema, f)

st.title("CSV To XML Converter")
st.header("Convert you csv files into XML ones")

# Create page variable in session
if 'page' not in st.session_state:
    st.session_state.page = "home"

# Initialize session state
if 'schemas' not in st.session_state:
    st.session_state.schemas = load_schema() if os.path.exists(PERSISTENCE_FILE) else []

if "reference" not in st.session_state:
    st.session_state.reference = None

if "target" not in st.session_state:
    st.session_state.target = None


if st.session_state.page == "home":
    col1, col2 = st.columns(2)
    with col1:
        button = st.button("Use an Existing Schema", key="Reuse")
        if button:
            st.session_state.page = "predefined"
            st.rerun()
    with col2:
        button = st.button("Create a New Schema", key="New")
        if button:
            st.session_state.page = "custom"
            st.rerun()

if st.session_state.page == "predefined":
    if  st.session_state.schemas:
        option = st.selectbox( "What schema would you like to use?", st.session_state.schemas, index=None, placeholder="Select schema...")
        if option:
            st.session_state.reference = option
            st.session_state.page = "custom"
            st.rerun()

        reset_button = st.button("Homepage",key='reset')
        if reset_button :
            st.session_state.page = "home"
            st.rerun()
        
    else:
        st.warning("No schema available. Please create a new schema first.")
        st.session_state.page = "home"
        st.rerun()
    

if st.session_state.get("page") == "custom":
    # Reference file upload
    if st.session_state.reference is None:
        reference_file = st.file_uploader("Upload the reference CSV file", type=["csv", "txt"], key="reference_csv")
        if reference_file :
            st.session_state.reference = copy.deepcopy(reference_file)

    # Target file upload
    if st.session_state.target is None:
        target_file = st.file_uploader("Upload the target CSV file", type=["csv", "txt"], key="target_csv")
        if target_file :
            st.session_state.target = copy.deepcopy(target_file)
    

    # Access reference and target files
    reference_file = st.session_state.reference
    target_file = st.session_state.target
    
    st.write("Reference File:", reference_file.name if reference_file else "No file uploaded")
    st.write("Target File:", target_file.name  if target_file else "No file uploaded")

    # Handle uploaded files
    print(reference_file and target_file)
    if reference_file and target_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as ref_temp:
            ref_temp.write(reference_file.getbuffer())
            reference_csv_path = ref_temp.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tgt_temp:
            tgt_temp.write(target_file.getbuffer())
            target_csv_path = tgt_temp.name

    col3, col4, col5 = st.columns(3)
    success = None

    with col3:
        button = st.button("Convert CSV to XML")
        if button :
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as xml_temp:
                xml_file_path = xml_temp.name
                output_path = xml_file_path.replace(".xml", "_processed.csv")
                format_csv(target_csv_path,reference_csv_path,output_path)
                xml_file = convert_csv_to_xml(output_path)
                success = st.success(f"Conversion successful! Download the XML file below.")

                # Update session state
                if reference_file not in st.session_state.schemas:
                    st.session_state.schemas.append(reference_file)
                    upload_schema()
                
                #reset the session state
                st.session_state.reference = None
                st.session_state.target = None
    
    with col4:
        if success:
            st.download_button("Download the XMl file", xml_file, "output.xml", key="xml_download")
    
    with col5:
        reset_button = st.button("Homepage",key='reset')
        if reset_button :
            st.session_state.page = "home"
            st.rerun()
        
            




