
import streamlit as st
from openai import OpenAI

from pypdf import PdfReader
from tempfile import NamedTemporaryFile


def init_state():
    st.session_state['resume_text'] = ""
    st.session_state.initialized = True
    st.session_state.llm_response = None
    st.session_state.question = None

def read_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    number_of_pages = len(reader.pages)
    page = reader.pages[0]
    text = page.extract_text()
    return text

def upload_callback():
    uploaded_file = st.session_state['file_uploader']
    if not uploaded_file or not uploaded_file.getbuffer():
        return
    with NamedTemporaryFile(dir='.', suffix='.pdf') as f:
        f.write(uploaded_file.getbuffer())
        st.session_state['resume_text'] = read_pdf(f.name)

def submit_callback():
    document = st.session_state.resume_text
    question = st.session_state.question
    if not question:
        question = "Given a resume below, ask 10 questions that a HR would most likely to ask."

    messages = [
        {
            "role": "user",
            "content": f"{question} \n\n -- \n\n {document}",
        }
    ]

    # Generate an answer using the OpenAI API.
    stream = st.session_state.client.chat.completions.create(
        model="gpt-4o", #"gpt-3.5-turbo",
        messages=messages,
        stream=True,
    )

    # Stream the response to the app using `st.write_stream`.
    #st.write_stream(stream)
    st.session_state.llm_response = stream

def page_main():
    if 'initialized' not in st.session_state:
        init_state()

    # Show title and description.
    st.title("📄 Resume Deep Dive")
    # st.write(
    #     "Upload a document below and ask a question about it – GPT will answer! "
    #     "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    # )

    # Ask user for their OpenAI API key via `st.text_input`.
    # Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
    # via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.", icon="🗝️")
    else:

        # Create an OpenAI client.
        st.session_state.client = OpenAI(api_key=openai_api_key)

        # Let the user upload a file via `st.file_uploader`.
        uploaded_file = st.file_uploader(
            "Upload a document (.txt or .md)",
            type=("txt", "md", "pdf"),
            on_change=upload_callback,
            key='file_uploader'
        )

        resume_txt = st.text_area(
            "Input text",
            placeholder="Resume text",
            key='resume_text'
        )

        question = st.text_area(
            "Now ask a question about the document!",
            #placeholder="Given this resume, ask 10 questions that a HR would most likely to ask.",
            disabled=not st.session_state.resume_text,
            key='question'
        )

        btn_submit = st.button("Submit", on_click=submit_callback, help="Submit the question")
        if st.session_state.llm_response:
            st.write_stream(st.session_state.llm_response)

page_main()