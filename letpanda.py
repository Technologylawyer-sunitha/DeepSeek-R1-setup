import streamlit as st
import sqlite3
import datetime
import ollama
import fitz  # PyMuPDF for PDFs
from docx import Document  # python-docx for DOCX

# Function to connect to the database
def get_db_connection():
    return sqlite3.connect('database.db')

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

# Function to extract text from DOCX
def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    return "\n".join([para.text for para in doc.paragraphs])

# Function to analyze clause using DeepSeek R1
def analyze_clause(clause):
    if not clause.strip():
        return "Please enter a contract clause for analysis."

    prompt = f"""
    You are a legal AI. Analyze the following contract clause and classify it:

    CLAUSE:
    {clause}

    Identify if this clause relates to:
    - Termination
    - Liability
    - Indemnification
    - Confidentiality
    - Payment
    - Other (Specify)

    Also, highlight potential risks in the clause and suggest improvements.
    """
    response = ollama.chat(model="deepseek-r1:1.5b", messages=[{"role": "user", "content": prompt}])
    return response['message']['content']

# Streamlit UI
st.set_page_config(layout="wide")
st.title("Your AI Lawyer")

uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx"])
clause = st.text_area("Paste your full contract or clause here", height=200)

if uploaded_file:
    file_type = uploaded_file.type
    if file_type == "application/pdf":
        clause = extract_text_from_pdf(uploaded_file)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        clause = extract_text_from_docx(uploaded_file)
    st.text_area("Extracted Text", clause, height=200)

if st.button("Analyze Clause"):
    with st.spinner("Analyzing..."):
        output = analyze_clause(clause)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save to SQLite
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO clause_analysis (clause, analysis, timestamp) VALUES (?, ?, ?)",
                      (clause, output, timestamp))
            conn.commit()

        st.subheader("📝 Analysis Output")
        st.write(output)

# Sidebar and Multiselect
st.sidebar.header("Risk analysis")
st.sidebar.header("Summarization")
st.sidebar.multiselect("Choose your contract clause", ["Liability", "Governing law"])


