import streamlit as st
import re

CORRECT_PASSWORD = "sagnik"

def process_text_data(text_data):
    
    lines = text_data.split("\n")

    filtered_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith('Portal_Feature/') or \
           line.endswith('Why is this an issue?ROSLYN') or \
           line.endswith('Why is this an issue?') or \
           re.match(r'^L\d+', line) or \
           'Code Smell' in line or \
           'Bug' in line or \
           'Vulnerability' in line:
            filtered_lines.append(line)

    formatted_text = "\n".join(filtered_lines)

    return formatted_text


def parse_text_data(text):
    lines = text.split('\n')
    table = []
    current_file = None
    current_issue = None
    current_line_number = None
    current_is_roslyn = None
    current_issue_type = None
    parse_issue_type = False

    for line in lines:
        if line.startswith('Portal_Feature/') and line.endswith('.cs'):
            current_file = line.split('/')[-1]
        elif current_file and line.strip():
            if not current_issue:
                current_issue = line.strip()
            elif current_issue and not current_line_number:
                parts = line.strip().split()
                current_line_number = parts[0]
                current_is_roslyn = "Yes" if "ROSLYN" in current_issue else "No"
                parse_issue_type = True
            elif parse_issue_type:
                current_issue_type = line.strip()
                table.append((current_file, current_issue.replace("ROSLYN",""), current_line_number, current_is_roslyn, current_issue_type))
                current_issue = None
                current_line_number = None
                current_is_roslyn = None
                current_issue_type = None
                parse_issue_type = False

    table.insert(0, ("File Name", "Issue Description", "Line Number", "Is ROSLYN Marked?", "Issue Type"))

    return table


def main():
    st.title('Sonar Issues Processor')

    password = st.text_input("Password:", type="password")

    if password.lower() == CORRECT_PASSWORD:
        
        text_data = st.text_area('Paste Text Data Here')

        if st.button('Process Data'):
            if text_data.strip() == '':
                st.warning('Please paste some text data.')
            else:
                processed_text = process_text_data(text_data)
                dataframe = parse_text_data(processed_text)
                st.dataframe(dataframe)
    elif password != "":
        st.warning("Incorrect password. Please try again.")

if __name__ == '__main__':
    main()
