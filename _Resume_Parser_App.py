#installation 
#pip install langchain_openai langchain-google-genai python-dotenv streamlit
#pip install -U langchain-community 

#step 1; Imports
import os
from dotenv import load_dotenv
import json
import streamlit as st

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_core.prompts import PromptTemplate


#step 2:  config / LLM 
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash',
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

PROMPT_TEMPLATE = """
You are an expert resume parser. 
Given the resume text, extract the following fields and return a single valid JSON:
{{
    "Name": "",
    "Email": "",
    "Phone": "",
    "Skills": [],
    "Experience": [],
    "Education": [],
    "Certifications": [],
    "Projects": [],
    "LinkedIn": "",
    "Languages": []
}}

Rules:
- If a field cannot be found, set its value to "No idea".
- Return only the JSON (no extra commentary).
- Keep lists as arrays.
- Keep Experience and Projects as arrays of short strings.

Resume Text:
{text}
"""

prompt = PromptTemplate(
    template=PROMPT_TEMPLATE,
    input_variables=["text"]
)
 # step 4; Streamlit UI 
import streamlit as st

def main():
    st.set_page_config(
        page_title='Resume Parser',
        page_icon='📄',
        layout='centered'
    )
    
    st.title("Resume Parser - LangChain")
    
    st.write("Upload a resume file (PDF, DOCX, TXT) to parse:")

    # File uploader
  # ---------------- FILE UPLOADER (FIXED VERSION) ------------------

import tempfile
import streamlit as st

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])

text = ""

if uploaded_file is not None:

    # PDF FILE
    if uploaded_file.type == "application/pdf":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        text = "\n\n".join([doc.page_content for doc in documents])

    # DOCX FILE
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        from langchain_community.document_loaders import Docx2txtLoader
        loader = Docx2txtLoader(tmp_path)
        text = loader.load()[0].page_content

    # TXT FILE
    elif uploaded_file.type == "text/plain":
        text = uploaded_file.getvalue().decode("utf-8")

    # WRONG FILE TYPE
    else:
        st.error("Unsupported file type")
        text = ""
    # SHOW OUTPUT
    # ------------------------------------
    if text:
     st.subheader("Extracted Text:")
    st.write(text)

    if st.button("Ask LLM"):
      with st.spinner("Sending to LLM..."):
        formatted_prompt = prompt.format(text=text)
        response = llm.invoke(formatted_prompt)

        try:
           parsed__json = json.loads(response.content)
           st.json(parsed__json)

        except json.JSONDecodeError:
           st.write(response.content)
           

        #st.subheader("Parsed Resume JSON:")
        #st.json(response.content)


# Python main
if __name__ == "__main__":
    main()


