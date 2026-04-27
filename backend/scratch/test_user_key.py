import os
import google.generativeai as genai
from google.api_core import exceptions

def test_key():
    API_KEY = "AIzaSyBjdmEyfUdcYvUrv92oHI4oVl3xuBYdvYk"
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        response = model.generate_content("test")
        print("Key is valid!")
        print(response.text)
    except Exception as e:
        print(f"Error type: {type(e)}")
        print(f"Error message: {e}")

if __name__ == "__main__":
    test_key()
