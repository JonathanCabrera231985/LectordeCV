import requests
import json
import os

url = 'http://localhost:8000/api/generate'
cv_file = r'c:\Users\jcabrera\TalentoWEB\Antonio Fernandez cv.pdf'
template_file = r'c:\Users\jcabrera\TalentoWEB\SDE_Project Manager Plantilla.docx'
output_file = r'c:\Users\jcabrera\TalentoWEB\backend\scratch\test_upload_output.docx'

files = {
    'cv': ('Antonio Fernandez cv.pdf', open(cv_file, 'rb')),
    'template': ('SDE_Project Manager Plantilla.docx', open(template_file, 'rb'))
}

try:
    response = requests.post(url, files=files)
    print("Status code:", response.status_code)
    
    if response.status_code == 200:
        with open(output_file, 'wb') as f:
            f.write(response.content)
        print(f"Success! Saved document to: {output_file}")
        
        # Parse content-disposition to see if safe_name worked
        print("Content-Disposition:", response.headers.get('content-disposition', 'Not Found'))
    else:
        print("Error details:")
        print(response.text)
except Exception as e:
    print("Request failed:", e)
finally:
    for f in files.values():
        f[1].close()
