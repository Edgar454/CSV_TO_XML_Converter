import pandas as pd
import re
import io

import csv
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

def format_csv(csv_path:str , reference_path:str , output_path:str) -> None:

  """
  Function to format a target csv as another one using only the informations they contains , it isn't an universal function
  but rather work with specific files\n
  Arguments
  --------
  csv_path : path to the csv to process , the one without heading
  reference_path : path to the reference csv used as reference for the formatting ,the one with heading
  output_path : path to the output csv
  """

  # loading the datasets
  try:
    target_raw_df = pd.read_csv(csv_path)
    reference_raw_df = pd.read_csv(reference_path)
    print(f"Number of initial columns in:\n reference: {reference_raw_df.shape[1]}\tfile_to_process:{target_raw_df.shape[1]}")
  except Exception as e:
    print(f"Files loading failed due to {e}")
    pass

  try:
    # Delete columns where all the observations are empty
    reference_df = reference_raw_df.dropna(axis=1, how='all')
    target_df = target_raw_df.dropna(axis=1, how='all')
    print(f"Number of columns in the dataframe after empty value removal:\nreference: {reference_df.shape[1]}\t processed file:{target_df.shape[1]}")

    # Deletion of column that are copies of others
    reference_df = reference_df.T.drop_duplicates(keep = 'first').T
    target_df = target_df.T.drop_duplicates(keep = 'first').T
    print(f"Number of columns in the dataframe after the columns duplicate removal:\nreference: {reference_df.shape[1]}\t processed file:{target_df.shape[1]}")

    # Sometimes , some columns in the target seems to contain the same informations as other but fragmented , it is likely due to an error , let's delete the fragments
    #  pattern to detect corrupted columns
    pattern = r'\b[0-9]+%\xa0\S+\b(?!\s+[0-9]+%\xa0)' #eg:95% cotton

    corrupted_cols = []
    for col in target_df.columns:
        if re.search(pattern, col) and len(re.findall(r'\d+%\xa0\S+', col)) == 1:
            if '<br>' not in col:  # Exclude columns containing <br>
                corrupted_cols.append(col)

    # the pattern don't match arabic so we must remove it manually
    corrupted_cols.extend(['قطن\xa095%', 'إيلاستين\xa05%','24/11/13'])
    target_df = target_df.drop(columns=corrupted_cols)
    print(f"Number of columns in the dataframe after the erroned columns removal:\nreference: {reference_df.shape[1]}\t processed file:{target_df.shape[1]}")
  except Exception as e:
    print(f"Files cleaning failed due to {e}")
    pass

  try :
    # Matching the 2 csv columns
    # the positions have been checked manually since the was no regex matching the content
    col_dict_rem = {}
    reference_columns = list(reference_df.columns)

    col_pos = list(reference_columns)[-12:]
    for j , csv_col in enumerate(col_pos) :
      col_dict_rem[76-11+j] = csv_col

    col_pos = list(reference_columns)[-25:-13]
    for j , csv_col in enumerate(col_pos) :
      col_dict_rem[76-23+j] = csv_col

    for j , csv_col in zip([39,40] , reference_columns[34:36] ) :
      col_dict_rem[j] = csv_col

    for j , csv_col in zip(range(34,39) , reference_columns[34:39] ) :
        col_dict_rem[j] = csv_col

    for j , csv_col in zip([31,32] , reference_columns[23:25] ) :
      col_dict_rem[j] = csv_col

    for j , csv_col in zip([29,30] , reference_columns[18:20] ) :
      col_dict_rem[j] = csv_col

    interest_columns = list(reference_columns[11:16]).copy()
    interest_columns.remove('CareCodeID')
    for j , csv_col in zip(range(25,29) , interest_columns) :
        col_dict_rem[j] = csv_col

    for j , csv_col in zip(range(22,25) , reference_columns[7:10] ) :
      col_dict_rem[j] = csv_col

    for j , csv_col in zip([20,21] , reference_columns[2:4] ) :
      col_dict_rem[j] = csv_col

    col_dict_rem.update({
      2 : 'WorksOrderno',
      3 : 'QtyOrdered',
      4 : 'Cust_Name',
      5 : 'Deliverydate',
      10 : 'Item_number',
      13 :'CarePhrase1',
      14: 'CarePhrase2',
      })
    
    ## 1st condition if they share at least one value then it's likely they are the same column
    col_dict  = {} # we will use a dictionnary with position in the target as the keys

    for csv_col in reference_df.columns:
      unique_csv_values = reference_df[csv_col].unique()
      for j , text_col in enumerate(target_df.columns):
        unique_text_values = target_df[text_col].unique()
        if set(unique_csv_values).intersection(unique_text_values):
          col_dict[j] = csv_col
          break

    col_dict.update(col_dict_rem)
  except Exception as e:
    print(f"Column matching failed due to {e}")
    pass

  # Deriving the target columns names from our dictionnary
  target_colnames = [col_dict[i] if i in col_dict.keys() else f'unk_{i}' for i in range(target_df.shape[1])]
  
  # modifying wrong column names 
  try:
    size_dec_index = target_colnames.index('Field975')
    fasteningtext_index = target_colnames.index('Field983')
    target_colnames[size_dec_index] = 'Size-Description'
    target_colnames[fasteningtext_index] = 'INCLUDEFASTENINGTEXT'
  except Exception as e:
    print(f"Column names modification failed due to {e}")
    pass


  # saving the cleaned reference target
  reference_df.to_csv(reference_path, index = False)
  print(f"Number of columns in the dataframe after cleaning:\nreference: {reference_df.shape[1]}\t processed file:{target_df.shape[1]}")


  # labeling and saving the target
  target_df.columns = target_colnames
  target_df.to_csv(output_path, index = False)


def sanitize_tag_name(name: str) -> str:
    """Sanitize a string to be a valid XML tag name."""
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Remove any invalid characters
    name = re.sub(r"[^a-zA-Z0-9_\-.]", "", name)
    return name

def convert_csv_to_xml(csv_file: str) -> io.BytesIO:
    """Convert CSV file to XML."""
    with open(csv_file, 'r', newline='', encoding='utf-8', errors='replace') as csvfile:
        reader = csv.DictReader(csvfile)
        root = ET.Element('SUPPLIERS')
        for row in reader:
            item = ET.SubElement(root, 'SUPPLIER')
            for key, value in row.items():
                # Sanitize the column name for XML tag
                sanitized_key = sanitize_tag_name(key)
                child = ET.SubElement(item, sanitized_key)
                # Escape and clean text
                child.text = escape(value) if value else ""
        tree = ET.ElementTree(root)

        # Write the XML file
        xml_data = io.BytesIO()
        tree.write(xml_data, encoding='utf-8', xml_declaration=True)
        return xml_data.getvalue()
  



def xml_formatter(input_file_path:str , output_file_path:str) -> None:
  """
  Function to format an xml file\n
  Arguments
  --------
  input_file_path : path to the xml file to format
  output_file_path : path to the output file
  """
  # Load the XML file
  tree = ET.parse(input_file_path)
  root = tree.getroot()

  # Function to format XML elements vertically
  def format_xml_vertically(element, level=0):
      indent = "\n" + "    " * level
      if len(element):
          element.text = (element.text or "").strip()
          element.text = indent + "    "
          for child in element:
              format_xml_vertically(child, level + 1)
          element.tail = indent
      else:
          element.text = (element.text or "").strip()
          element.tail = indent

  # Apply formatting
  for child in root:
      format_xml_vertically(child)

  # Write the formatted XML to a new file
  tree.write(output_file_path, encoding='utf-8', xml_declaration=True)
