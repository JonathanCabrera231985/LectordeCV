import sys
import os

# Fix para PyInstaller --noconsole (donde stdout/stderr son None)
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import json
import traceback
import webbrowser
import threading
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import google.generativeai as genai
import pypdf
import docx
from dotenv import load_dotenv

# Configuración de logs para evitar errores en modo sin consola
LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": False,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
            "use_colors": False,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}

# Configuración de rutas para PyInstaller
def get_resource_path(relative_path):
    """ Obtiene la ruta absoluta para recursos, compatible con PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_exe_dir():
    """ Obtiene el directorio donde reside el ejecutable o el script """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def load_config():
    """ Carga la API Key desde un archivo externo config.txt con soporte para diferentes codificaciones """
    config_path = os.path.join(get_exe_dir(), "config.txt")
    if os.path.exists(config_path):
        try:
            # utf-8-sig maneja archivos con o sin BOM (común en Windows/PowerShell)
            with open(config_path, "r", encoding="utf-8-sig") as f:
                for line in f:
                    if "GEMINI_API_KEY=" in line:
                        return line.split("=")[1].strip()
        except Exception as e:
            print(f"Error leyendo config.txt: {e}")
    return None

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        reader = pypdf.PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print("Error extracting PDF:", e)
    return text

def fill_docx_template(template_path: str, data: dict, output_path: str):
    doc = docx.Document(template_path)
    try:
        # 1. Información Personal
        if len(doc.tables) > 0:
            doc.tables[0].cell(0, 1).text = str(data.get("nombre", "No especificado"))
            doc.tables[0].cell(1, 1).text = str(data.get("pais", "No especificado"))
        
        # 2. Información Complementaria
        if len(doc.tables) > 1:
            doc.tables[1].cell(0, 1).text = str(data.get("anios_experiencia", "No especificado"))

        # 3. Educación
        if len(doc.tables) > 2:
            edu = data.get("educacion", {})
            univ = edu.get("universidad", {})
            doc.tables[2].cell(1, 1).text = str(univ.get("institucion", "No especificado"))
            doc.tables[2].cell(1, 2).text = str(univ.get("titulo", "No especificado"))
            doc.tables[2].cell(1, 3).text = str(univ.get("fechas", "No especificado"))
            
            post = edu.get("postgrado", {})
            doc.tables[2].cell(2, 1).text = str(post.get("institucion", "No especificado"))
            doc.tables[2].cell(2, 2).text = str(post.get("titulo", "No especificado"))
            doc.tables[2].cell(2, 3).text = str(post.get("fechas", "No especificado"))

        # 4. Certificaciones
        if len(doc.tables) > 3:
            certs = data.get("certificaciones", [])
            table = doc.tables[3]
            for i, cert in enumerate(certs):
                if i < len(table.rows) - 1:
                    row = table.rows[i+1]
                else:
                    row = table.add_row()
                row.cells[0].text = str(cert.get("nombre", "No especificado"))
                row.cells[1].text = str(cert.get("institucion", "No especificado"))
                row.cells[2].text = str(cert.get("horas", "No especificado"))
                row.cells[3].text = str(cert.get("fecha", "No especificado"))

        # 5. Logros
        if len(doc.tables) > 4:
            logros = data.get("logros", [])
            table = doc.tables[4]
            for i, ach in enumerate(logros):
                if i < len(table.rows) - 1:
                    row = table.rows[i+1]
                else:
                    row = table.add_row()
                row.cells[0].text = str(ach.get("nombre", "No especificado"))
                row.cells[1].text = str(ach.get("descripcion", "No especificado"))
                row.cells[2].text = str(ach.get("fecha", "No especificado"))
                row.cells[3].text = str(ach.get("herramientas", "No especificado"))

        # 6. Experiencia Laboral
        def fill_exp(table, emp_data):
            try:
                table.cell(0, 0).text = f"Nombre de la Institución: {emp_data.get('empresa', 'N/E')}"
                if len(table.rows[0].cells) > 1:
                    table.cell(0, 1).text = f"Fecha de ingreso: {emp_data.get('fecha_ingreso', 'N/E')}"
                if len(table.rows[0].cells) > 2:
                    table.cell(0, 2).text = f"Fecha de finalización del contrato: {emp_data.get('fecha_salida', 'N/E')}"
                if len(table.rows) > 1:
                    table.cell(1, 0).text = f"Posición: {emp_data.get('cargo', 'N/E')}"
                if len(table.rows) > 2:
                    table.cell(2, 0).text = f"Principales funciones: {emp_data.get('funciones', 'N/E')}"
            except Exception as e:
                print("Error filling exp row:", e)
                
        exps = data.get("experiencia", [])
        if len(exps) > 0 and len(doc.tables) > 5:
            fill_exp(doc.tables[5], exps[0])
        if len(exps) > 1 and len(doc.tables) > 6:
            fill_exp(doc.tables[6], exps[1])

        # 7. Autoevaluación
        auto = data.get("autoevaluacion", {})
        if len(doc.tables) > 7:
            t = doc.tables[7]
            t.cell(1, 0).text = str(auto.get("gestion_proyectos", "N/E"))
            t.cell(1, 1).text = str(auto.get("mitigacion_riesgos", "N/E"))
            t.cell(1, 2).text = str(auto.get("agilismo", "N/E"))
            t.cell(1, 3).text = str(auto.get("cloud", "N/E"))
            t.cell(1, 4).text = str(auto.get("ingenieria_procesos", "N/E"))

        if len(doc.tables) > 8:
            t = doc.tables[8]
            t.cell(1, 0).text = str(auto.get("ms_project", "N/E"))
            t.cell(1, 1).text = str(auto.get("jira", "N/E"))
            t.cell(1, 2).text = str(auto.get("planner", "N/E"))
            t.cell(1, 3).text = str(auto.get("scrum", "N/E"))
            t.cell(1, 4).text = str(auto.get("bpm", "N/E"))
            t.cell(1, 5).text = str(auto.get("power_bi", "N/E"))
            t.cell(1, 6).text = str(auto.get("crm", "N/E"))

        if len(doc.tables) > 9:
            t = doc.tables[9]
            t.cell(1, 0).text = str(auto.get("salesforce", "N/E"))
            t.cell(1, 1).text = str(auto.get("workflow", "N/E")) + " / " + str(auto.get("automatizacion", "N/E"))
            t.cell(1, 2).text = str(auto.get("ibm_filenet", "N/E"))
            t.cell(1, 3).text = str(auto.get("stakeholders", "N/E"))

        doc.save(output_path)
    except Exception as e:
        print("Error filling template:", traceback.format_exc())
        raise Exception("Error procesando docx: " + str(e))

PROMPT_JSON = """
Actúa como un asistente técnico de reclutamiento especializado en la automatización de documentos para SIPECOM S.A.
Extrae la información del siguiente CV y devuelve EXCLUSIVAMENTE un JSON válido sin markdown (`{}`).
Si un dato no existe, coloca "No especificado".
Extructura JSON esperada:
{
  "nombre": "Nombre completo",
  "pais": "Pais de residencia",
  "anios_experiencia": "X años",
  "educacion": {
    "universidad": {"institucion": "...", "titulo": "...", "fechas": "..."},
    "postgrado": {"institucion": "...", "titulo": "...", "fechas": "..."}
  },
  "certificaciones": [
    {"nombre": "...", "institucion": "...", "horas": "...", "fecha": "..."}
  ],
  "logros": [
    {"nombre": "...", "descripcion": "...", "fecha": "...", "herramientas": "..."}
  ],
  "experiencia": [
    {"empresa": "...", "fecha_ingreso": "...", "fecha_salida": "...", "cargo": "...", "funciones": "..."}
  ],
  "autoevaluacion": {
    "gestion_proyectos": "8",
    "mitigacion_riesgos": "7",
    "agilismo": "N/E",
    "cloud": "N/E",
    "ingenieria_procesos": "8",
    "ms_project": "N/E",
    "jira": "N/E",
    "planner": "N/E",
    "scrum": "N/E",
    "bpm": "N/E",
    "power_bi": "8",
    "crm": "N/E",
    "salesforce": "N/E",
    "workflow": "N/E",
    "automatizacion": "7",
    "ibm_filenet": "N/E",
    "stakeholders": "8"
  }
}

CV A ANALIZAR:
"""

@app.post("/api/generate")
async def generate_cv(
    cv: UploadFile = File(...),
    template: UploadFile = File(...),
    api_key: str = Form(None)
):
    try:
        # Prioridad de API KEY: Formulario > config.txt > .env
        final_api_key = api_key if api_key and api_key.strip() else load_config()
        if not final_api_key:
            final_api_key = os.getenv("GEMINI_API_KEY")

        if not final_api_key:
            raise HTTPException(status_code=400, detail="API Key no encontrada. Por favor, configúrala en el archivo config.txt")

        # Carpeta temp local de ejecución
        base_temp = os.path.join(get_exe_dir(), "temp")
        os.makedirs(base_temp, exist_ok=True)
        
        cv_path = os.path.join(base_temp, cv.filename)
        with open(cv_path, "wb") as f:
            f.write(await cv.read())
            
        template_path = os.path.join(base_temp, template.filename)
        with open(template_path, "wb") as f:
            f.write(await template.read())

        # Extract Text
        cv_text = extract_text_from_pdf(cv_path)

        # Call Gemini
        genai.configure(api_key=final_api_key)
        model = genai.GenerativeModel('gemini-flash-latest', generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(PROMPT_JSON + cv_text)
        
        parsed_data = json.loads(response.text)

        output_filename = f"SOLICITUD_{parsed_data.get('nombre', 'Generada').replace(' ', '_')}.docx"
        output_path = os.path.join(base_temp, output_filename)

        # Fill DOCX
        fill_docx_template(template_path, parsed_data, output_path)

        return FileResponse(output_path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename=output_filename)

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Servir Frontend
frontend_path = get_resource_path("frontend/dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

def open_browser():
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    import uvicorn
    # Iniciar navegador en un hilo separado
    threading.Timer(1.5, open_browser).start()
    # Usamos LOG_CONFIG explícito con use_colors=False para evitar el error isatty
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=LOG_CONFIG)
