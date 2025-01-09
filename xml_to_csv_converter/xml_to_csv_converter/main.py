import streamlit as st
import tempfile
import pathlib
import xml.etree.ElementTree as ET
from utils import convert_csv_to_xml, format_csv

# load Custom CSS
def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_path = pathlib.Path("assets/style.css")
load_css(css_path)



st.title("CSV To XML Converter")
st.header("Convert you csv files into XML ones")

# Create page variable in session
if 'page' not in st.session_state:
    st.session_state.page = "home"

if 'schema' not in st.session_state:
    st.session_state.schema = []


reference_file = None

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
    if  st.session_state.schema:
        option = st.selectbox( "What schema would you like to use?", st.session_state.schema, index=None, placeholder="Select schema...")
        if option:
            reference_file = option
            st.session_state.page = "custom"
            st.rerun()
    else:
        st.warning("No schema available. Please create a new schema first.")
        st.session_state.page = "home"
        st.rerun()
    


if st.session_state.page == "custom":
    if not reference_file:
        reference_file = st.file_uploader("Upload the reference CSV file", type=["csv","txt"], key="reference_csv")
        st.session_state.schema.append(reference_file)

    target_file = st.file_uploader("Upload the target CSV file", type=["csv","txt"], key="target_csv")

    # If files are uploaded
    if reference_file and target_file:
        # Save files and proceed with your logic
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as ref_temp:
            ref_temp.write(reference_file.getbuffer())
            reference_csv_path = ref_temp.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tgt_temp:
            tgt_temp.write(target_file.getbuffer())
            target_csv_path = tgt_temp.name

    col3, col4 = st.columns(2)
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
    
    with col4:
        if success:
            st.download_button("Download the XMl file", xml_file, "output.xml", key="xml_download")
            




