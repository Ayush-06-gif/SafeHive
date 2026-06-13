"""
AI Client — Wrapper for the Groq API and Gemini fallback using LangChain.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Initialize the Groq LLM
groq_llm = None
try:
    groq_llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.1-8b-instant", 
        temperature=0.7,
    )
except Exception as e:
    print(f"Warning: Failed to initialize ChatGroq. Check API key. Error: {e}")

# Initialize the Gemini Fallback LLM
gemini_llm = None
google_key = os.getenv("GOOGLE_API_KEY")
if google_key:
    try:
        gemini_llm = ChatGoogleGenerativeAI(
            api_key=google_key,
            model="gemini-1.5-flash",
            temperature=0.7,
        )
    except Exception as e:
        print(f"Warning: Failed to initialize Gemini fallback. Error: {e}")
else:
    print("Notice: GOOGLE_API_KEY not found in .env. Gemini fallback will be disabled.")

# Create the fallback chain
if groq_llm and gemini_llm:
    llm = groq_llm.with_fallbacks([gemini_llm])
elif groq_llm:
    llm = groq_llm
elif gemini_llm:
    llm = gemini_llm
else:
    llm = None

async def call_llm(prompt: str) -> str:
    """
    Call the LLM with a simple text prompt.
    Returns the string response.
    """
    if not groq_llm and not gemini_llm:
        raise ValueError("No LLM is initialized. Check your API keys in the .env file.")

    # 1. Try Groq first
    if groq_llm:
        try:
            response = await groq_llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            print(f"Groq encountered an error: {e}")
            if gemini_llm:
                print("Automatically switching to Gemini fallback...")
            else:
                print("Gemini fallback not available (missing GOOGLE_API_KEY).")
                raise e

    # 2. Try Gemini if Groq failed (or if Groq wasn't initialized)
    if gemini_llm:
        try:
            response = await gemini_llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            print(f"Gemini encountered an error: {e}")
            raise e
            
    raise Exception("Failed to get a response from any LLM.")
