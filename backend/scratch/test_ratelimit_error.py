import os
import google.generativeai as genai
from google.api_core import exceptions
import asyncio

async def test_quota_error():
    API_KEY = "AIzaSyDrY5qC3049u4n2hgC9U4i2KyyN1UjiXTk" 
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')
    try:
        # Intencionalmente spam para provocar un 429
        for i in range(30):
            response = model.generate_content("hello")
            print(f"Success {i}")
    except Exception as e:
        print("Módulo de la excepción:", type(e).__module__)
        print("Clase de la excepción:", type(e).__name__)
        print("Error content:", str(e))

asyncio.run(test_quota_error())
