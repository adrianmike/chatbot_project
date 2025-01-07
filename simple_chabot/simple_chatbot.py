# versiune finala modificata cu titlu si descriere
#Here is your updated application with an improved title, a description of the app, information about the technologies used to develop it, and examples of questions users can ask:

import streamlit as st
from langchain_ollama import ChatOllama

# App Title
st.title("💬 Mini Chat Assistant")

# App Description
st.write("""
### About this App
Welcome to the Mini Chat Assistant! This application allows you to ask any questions or make statements, and it provides intelligent responses using cutting-edge natural language processing (NLP) technology. 
It leverages **LangChain** for conversational capabilities and the **Ollama** platform for efficient model hosting.
""")

# Technologies Used
st.write("""
**Technologies Used:**
- [LangChain](https://langchain.com): A framework for building applications with large language models (LLMs).
- [Ollama](https://ollama.com): A platform for hosting and serving LLMs efficiently.
- [Streamlit](https://streamlit.io/): A Python library for creating interactive web applications.
""")

# User Examples
st.write("""
### Examples of Questions You Can Ask:
- "What is the capital of France?"
- "Can you summarize the plot of 'To Kill a Mockingbird'?"
- "Explain the Pythagorean theorem."
- "Write a code in Python for calculate square root from 1024."
- "What are the benefits of using AI in education?"
""")

# Input Form
with st.form("llm-form"):
    text = st.text_area("Enter your question or statement:")
    submit = st.form_submit_button("Submit")

# Function to Generate Responses
def generate_response(input_text):
    # model = ChatOllama(model="llama3.2:1b", base_url="http://localhost:11434/")
    model = ChatOllama(model="smollm", base_url="http://localhost:11434/")
    response = model.invoke(input_text)
    return response.content

# Chat History
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if submit and text:
    with st.spinner("Generating response..."):
        response = generate_response(text)
        st.session_state["chat_history"].append({"user": text, "ollama": response})
        st.write(response)

# Display Chat History
st.write("## Chat History")
for chat in reversed(st.session_state["chat_history"]):
    st.write(f"**User**: {chat['user']}")
    st.write(f"**Virtual Assistant**: {chat['ollama']}")
    st.write("---")
