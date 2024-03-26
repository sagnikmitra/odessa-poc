import streamlit as st

# Importing the provided Streamlit codes
from xaml import main as xaml_main
from sonar import main as sonar_main
from regex import main as regex_main

def main():
    st.title("Choose operation")
    
    # Radio button to choose Streamlit code
    choice = st.radio("Choose Streamlit Code:", ("XAML Processor", "Sonar Issues Processor", "Regex Text Pattern Remover"))

    # Execute the chosen Streamlit code based on user's selection
    if choice == "XAML Processor":
        xaml_main()
    elif choice == "Sonar Issues Processor":
        sonar_main()
    elif choice == "Regex Text Pattern Remover":
        regex_main()

if __name__ == "__main__":
    main()
