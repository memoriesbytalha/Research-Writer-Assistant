import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

try:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )
    print("Groq LLM initialized successfully.")
except Exception as e:
    print(f"Error initializing LLM: {e}")