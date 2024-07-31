import streamlit as st
import sqlparse
import re

st.title("SQL Beautifier and Formatter")

# List of important comments to find and format
important_comments = [
    "--IMPORTANT: Please check the values in the DB prior to running drop statements",
    "--IMPORTANT: Please provide manual update statements for column",
    "--Default run scripts below--",
    "/*Any SP execution which needed as part of core.releasescript.sql goes here*/"
]

def format_with_comments(sql_code, comments):
    # Add newlines around specific comments
    for comment in comments:
        if comment in sql_code:
            if comment == "/*Any SP execution which needed as part of core.releasescript.sql goes here*/":
                sql_code = sql_code.replace(comment, f"\n{comment}\n\n")
            else:
                sql_code = sql_code.replace(comment, f"\n{comment}\n")

    # Find column names after the specific comment and add newlines
    pattern = r'--IMPORTANT: Please provide manual update statements for column\s+(\w+)'
    sql_code = re.sub(pattern, lambda m: f"--IMPORTANT: Please provide manual update statements for column {m.group(1)}\n", sql_code, flags=re.IGNORECASE)

    # Ensure that END and GO are on separate lines
    sql_code = re.sub(r'\s*( GO )\s*', r'<br>\1<br>', sql_code, flags=re.IGNORECASE)
    
    # Replace multiple newlines with a single newline
    sql_code = re.sub(r'\n+', '\n', sql_code).strip()

    # Format SQL code with sqlparse
    formatted_sql = sqlparse.format(sql_code, reindent=True, keyword_case='upper')
    
    # Convert to HTML for proper newline rendering
    formatted_sql = formatted_sql.replace('\n', '<br>')
    
    return formatted_sql

# Larger input text area for SQL code
sql_code = st.text_area("Enter your SQL code here:", height=400)

if st.button("Beautify SQL"):
    if sql_code.strip() == "":
        st.warning("Please enter some SQL code to beautify.")
    else:
        formatted_sql_with_comments = format_with_comments(sql_code, important_comments)
        # Display beautified SQL code with HTML formatting
        formatted_sql_with_comments.replace("\n\n","\n")
        html_content = f'<pre>{formatted_sql_with_comments}</pre>'
        st.html(html_content)
        st.markdown(f'<pre>{formatted_sql_with_comments}</pre>', unsafe_allow_html=True)

if st.button("Download SQL"):
    if sql_code.strip() == "":
        st.warning("Please enter some SQL code to download.")
    else:
        formatted_sql_with_comments = format_with_comments(sql_code, important_comments)
        st.download_button(
            label="Download SQL file",
            data=formatted_sql_with_comments,
            file_name="beautified_sql.sql",
            mime="text/sql"
        )
