import os
import base64
import json
import PyPDF2 
import streamlit as st
from langchain.llms import OpenAI
from langchain import PromptTemplate

from langchain.text_splitter import CharacterTextSplitter 
from constants import openai_key
from langchain.chains import LLMChain

    
os.environ['OPENAI_API_KEY'] = openai_key

#streamlit framework
def add_logo_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    style = '''
            <style>
            .logo {
                position: absolute;
                top: -50px;
                left: -247px;
                z-index: 0;
            }

            </style>
            '''
    logo = f'<img class="logo" src="data:image/png;base64,{encoded_string}" width="120">'

    st.markdown(style, unsafe_allow_html=True)

    st.empty().markdown(logo, unsafe_allow_html=True)

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"png"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )

add_logo_from_local(os.path.join(os.path.dirname(__file__), "images\logo.png"))
add_bg_from_local('image.png')

st.title('**Entity Recognition**')

with st.form('my_form'):
    uploaded_pdf = st.file_uploader(label='Upload PDF:', type='pdf')
    submitted = st.form_submit_button('Submit')

template = '''You are an asssistant whose goal is to extract the following entities:
         Given text:
            "{passage}"
            
        Find the following entities:
        1. Percentage Entity
        2. Corporate Entity
        2. Monetary Entity
        3. Location Entity
        4. Date Entity

        Format the output as JSON with the following information:
        Entity Name,
        Entity Type,
        Start Index of Entity,
        End Index of Entity

        strictly use the following keys in json
        Entity_Name,
        Entity_Type,
        Start_Index,
        End_Index

        '''

entity_prompt = PromptTemplate(
    input_variables=['passage'],
    template=template
)

llm = OpenAI(temperature=0)
chain = LLMChain(llm=llm, prompt=entity_prompt, verbose=True, output_key='entity')

  
def read_pdf(file): 
    pdf_reader = PyPDF2.PdfReader(file) 
    num_pages = len(pdf_reader.pages) 
    text = '' 
    for page_num in range(num_pages): 
        page = pdf_reader.pages[page_num] 
        text += page.extract_text() 
    return text

def split_text(text): 
    text_splitter = CharacterTextSplitter(
        separator="\n", 
        chunk_size=800, 
        chunk_overlap=200, 
        length_function=len) 
    splitted_texts = text_splitter.split_text(text) 
    return splitted_texts

if submitted and uploaded_pdf: 
    pdf_text = read_pdf(uploaded_pdf)
    # Split the text into chunks    
    text_chunks = split_text(pdf_text)

    # Extract entities from each text chunk
    entities = []
    for chunk in text_chunks:
        result = chain.run(passage=chunk)
        entities.append(result)

    json_data = json.dumps(entities, indent=4)

    st.download_button(
        label="Download JSON File",
        data=json_data.encode("utf-8"),
        file_name="extracted_entities.json",
        mime='application/json'
    )

    # Display entities in an expander
    st.subheader('Extracted Entities')
    for i, entity in enumerate(entities, 1):
        with st.expander(f'Entity {i}'):
            st.text(f'Entity: {entity}, Type: {chain.output_key}')





