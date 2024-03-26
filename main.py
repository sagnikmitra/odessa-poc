def main():
    import streamlit as st
    st.set_page_config(layout="wide")
    st.title("Sagnik's Odessa POCs")
    # Radio button to choose Streamlit code
    choice = st.radio("Choose operation:", ("XAML Processor", "Sonar Issues Processor", "Regex Text Pattern Remover"))

    # Execute the chosen Streamlit code based on user's selection
    if choice == "XAML Processor":
        import streamlit as st
        import os
        from io import BytesIO
        import zipfile
        import datetime
        import pytz

        def detect_titles(xaml_content, file_name):
            titles = []
            new_xaml_content = ""
            lines_with_titles = []
            property_name = None
            for i, line in enumerate(xaml_content.split('\n'), start=1):
                if ' Title="' in line:
                    title_start = line.index(' Title="') + len(' Title="')
                    title_end = line.index('"', title_start)
                    title = line[title_start:title_end]
                    titles.append(title)
                    property_name = get_property_name(line)
                    new_line = replace_title_with_titlekey(line, file_name, property_name, title_end, title_start)
                    lines_with_titles.append((i, title, new_line, title_start))
                    new_xaml_content += new_line + "\n"
                else:
                    new_xaml_content += line + "\n"
            return lines_with_titles, new_xaml_content, titles

        def get_property_name(line):
            if ' Property="' in line:
                property_start = line.index(' Property="') + len(' Property="')
                property_end = line.index('"', property_start)
                return line[property_start:property_end]
            elif ' TextProperty="' in line:
                text_property_start = line.index(' TextProperty="') + len(' TextProperty="')
                text_property_end = line.index('"', text_property_start)
                return line[text_property_start:text_property_end]
            elif ' Name="' in line:
                name_property_start = line.index(' Name="') + len(' Name="')
                name_property_end = line.index('"', name_property_start)
                return line[name_property_start:name_property_end]
            elif ' Group="' in line:
                group_property_start = line.index(' Group="') + len(' Group="')
                group_property_end = line.index('"', group_property_start)
                return line[group_property_start:group_property_end]
            else:
                old_title_start = line.index(' Title="') + len(' Title="')
                old_title_end = line.index('"', old_title_start)
                old_title = line[old_title_start:old_title_end]
                return old_title.replace(" ", "")


        def replace_title_with_titlekey(line, file_name, property_name, title_end, title_start):
            if 'Title="' in line:
                if property_name:
                    new_line = line.replace('Title="', f'TitleKey="{file_name}.{property_name}.Title"')
                else:
                    new_line = line.replace('Title="', f'TitleKey="{file_name}.Text.Title"')
                end_index = new_line.index('"', new_line.index('TitleKey="') + len('TitleKey="'))
                new_line = new_line[:end_index] + new_line[end_index + (title_end-title_start+1):]    
                return new_line
            else:
                return line


        def generate_text_resource(lines_with_titles):
            text_resource_lines = set()  
            for line_number, title, line_content, _ in lines_with_titles:
                title_key = line_content.split('TitleKey="')[1].split('"')[0]
                text_resource_line = f'<TextResource Name="{title_key}" Value="{title}"/>'
                text_resource_lines.add(text_resource_line)
            return text_resource_lines


        def process_xaml_content(xaml_content, file_name, if_mode_of_input_entry):
            lines_with_titles, new_xaml_content, all_titles = detect_titles(xaml_content, file_name)
            if(if_mode_of_input_entry):
                st.subheader("Modified XAML Content:")
                st.code(new_xaml_content, language='xml')
                st.subheader("Generated Text Resource:")
                
            text_resource_lines = generate_text_resource(lines_with_titles)
            sorted_text_resource_lines = sorted(text_resource_lines) 
            xml_text = '\n'.join(sorted_text_resource_lines)
            
            if(if_mode_of_input_entry):
                st.code(xml_text, language='xml')
                st.subheader("Lines with the generated Title Keys:")
            
            table_data = []
            table_data.append(('Line Number', 'Old Title', 'New Title Key', 'Line Content Updated'))

            for line_number, title, new_line_content, _ in lines_with_titles:
                new_title_key = new_line_content.split('TitleKey="')[1].split('"')[0]
                table_data.append((line_number, title, new_title_key, new_line_content))

            if(if_mode_of_input_entry):   
                st.table(table_data)

            return all_titles, text_resource_lines, table_data


        st.title("XAML Title Detector")

        option = st.radio("Choose an option:", ("Upload File", "Enter File Content and Name"))

        if option == "Upload File":
            uploaded_files = st.file_uploader("Upload XAML Files", type=["xaml"], accept_multiple_files=True)

            if uploaded_files:
                all_files = []
                all_text_resources = set()
                all_table_data = []

                for uploaded_file in uploaded_files:
                    file_name = os.path.splitext(uploaded_file.name)[0] 
                    xaml_content = uploaded_file.getvalue().decode("utf-8") 

                    st.info(f"Processed {file_name}")
                    titles, text_resources, table_data = process_xaml_content(xaml_content, file_name, False)
                    
                    all_files.append((file_name, xaml_content))
                    all_text_resources.update(text_resources)
                    all_table_data.extend(table_data)

                if st.button("Download All Updated Files"):
                    zip_file = BytesIO()
                    file_name_string = ""
                    with zipfile.ZipFile(zip_file, 'w') as zipf:
                        for file_name, content in all_files:
                            updated_file_content = detect_titles(content, file_name)[1]
                            zipf.writestr(f"{file_name}.xaml", updated_file_content.encode())
                            file_name_string += "_" + file_name
                    zip_file.seek(0)
                    ist = pytz.timezone('Asia/Kolkata')
                    current_datetime = datetime.datetime.now(ist).strftime("%d%m%Y_%H%M%S")
                    zip_filename = f"Processed_XAML_Files_{current_datetime}{file_name_string}.zip"
                    st.download_button(label="Download", data=zip_file, file_name=zip_filename, mime="application/zip")
                    
                st.subheader("Collated Text Resources:")
                collated_xml_text = '\n'.join(all_text_resources)
                st.code(collated_xml_text, language='xml')

                st.subheader("Collated Table Data:")
                st.dataframe(all_table_data)


        elif option == "Enter File Content and Name":
            file_name = st.text_input("Enter File Name (without extension)")

            xaml_content = st.text_area("Paste your XAML content here")

            if st.button("Detect Titles"):
                process_xaml_content(xaml_content, file_name, True)
    elif choice == "Sonar Issues Processor":
        import streamlit as st
        import re
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

            text_data = st.text_area('Paste Text Data Here')

            if st.button('Process Data'):
                if text_data.strip() == '':
                    st.warning('Please paste some text data.')
                else:
                    processed_text = process_text_data(text_data)
                    dataframe = parse_text_data(processed_text)
                    st.dataframe(dataframe)

        if __name__ == '__main__':
            main()
    elif choice == "Regex Text Pattern Remover":
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


if __name__ == "__main__":
    main()
