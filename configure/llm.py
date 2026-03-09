import getpass
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# GOOGLE API KEY
try:
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")
        print("Google AI API key set successfully.")
except Exception as e:
    print(f"Error setting Google API key: {e}")

# Initialize Gemini
try:
    llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")
    print("Google AI LLM initialized successfully.")
except Exception as e:
    print(f"Error initializing LLM: {e}")


# TAVILY API KEY
try:
    if "TAVILY_API_KEY" not in os.environ:
        os.environ["TAVILY_API_KEY"] = getpass.getpass("Enter your Tavily API key: ")
        print("Tavily API key set successfully.")
except Exception as e:
    print(f"Error setting Tavily API key: {e}")


# Initialize Tavily
try:
    tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    print("Tavily client initialized successfully.")
except Exception as e:
    print(f"Error initializing Tavily client: {e}")