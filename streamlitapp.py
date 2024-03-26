import os
import json
import traceback
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain.callbacks import get_openai_callback
from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.MCQGen import generate_eval_chain
from src.mcqgenerator.logger import logging

with open('C:\\Users\\rachi\\OneDrive\\Desktop\\Gen_AI_Projects\\MCQ-Generator\\response.json', 'r') as file:
    response_from_json = json.load(file)

st.title("MCQs Generator Application Using GEN AI and Langchain")

with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Please upload a PDF File or Text File")
    mcq_count = st.number_input("Number of MCQs: ", min_value=3, max_value=50)
    subject = st.text_input("Name of the Topic: ", max_chars=20)
    tone = st.text_input("Difficulty Level of Questions: ", max_chars=20, placeholder="Moderate")
    button = st.form_submit_button("Create MCQs")

    if button and uploaded_file is not None and mcq_count and subject and tone: 
        with st.spinner("Loading..."):
            try:
                text = read_file(uploaded_file)
                with get_openai_callback() as cb:
                    response=generate_eval_chain(
                        {
                            "text": text,
                            "number": mcq_count,
                            "subject":subject,
                            "tone": tone,
                            "response_json": json.dumps(response_from_json)
                        }
                    )
            except Exception as e:
                traceback.print_exception(type(e),e,e.__traceback__)
                st.error("Error")

            else:
                print(f"Total Tokens: {cb.total_tokens}")
                print(f"Prompt Tokens: {cb.prompt_tokens}")
                print(f"Completion Tokens: {cb.completion_tokens}")
                print(f"Total Cost: {cb.total_cost}")
                if isinstance(response, dict):
                    quiz = response.get("quiz", None)
                    if quiz is not None:
                        table_data = get_table_data(quiz)
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.table(df)
                            st.text_area(label="Review", value = response["review"])
                        else:
                            st.error("Error in the table data")
                else:
                    st.write(response)

