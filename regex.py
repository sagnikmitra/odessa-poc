import streamlit as st
import re
import os

def remove_pattern(text):
    """
    Function to remove strings matching the pattern .<7 digit numbers>Z
    """
    pattern = r'\.\d{7}Z '  # Pattern to match .<7 digit numbers>Z
    return re.sub(pattern, '', text)

def main():
    st.title("Regex Text Pattern Remover")
    
    uploaded_file = st.file_uploader("Upload a file", type=['txt'])
    
    if uploaded_file is not None:
        file_contents = uploaded_file.getvalue().decode("utf-8")
        
        modified_text = remove_pattern(file_contents)
        
        # Extract filename without extension from uploaded file
        filename_without_extension = os.path.splitext(uploaded_file.name)[0]
        # Create new filename for modified file
        modified_filename = filename_without_extension + "_updated.txt"
        st.download_button(label="Download Modified Text",
                               data=modified_text,
                               file_name=modified_filename,
                               mime="text/plain")

if __name__ == "__main__":
    main()
