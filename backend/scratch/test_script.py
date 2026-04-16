import sys
import os

# Add backend to path to import fill_docx_template
sys.path.append(r"c:\Users\jcabrera\TalentoWEB\backend")

from main import fill_docx_template

data = {
    "nombre": "Test User",
    "pais": "Ecuador",
    "anios_experiencia": "10 años",
    "educacion": {
        "universidad": {"institucion": "UTPL", "titulo": "Ingeniero", "fechas": "2010-2015"},
        "postgrado": {"institucion": "ESPOL", "titulo": "Magister", "fechas": "2016-2018"}
    },
    "certificaciones": [
        {"nombre": "Cert 1", "institucion": "Inst 1", "horas": "40", "fecha": "2020"},
        {"nombre": "Cert 2", "institucion": "Inst 2", "horas": "20", "fecha": "2021"},
        {"nombre": "Cert 3", "institucion": "Inst 3", "horas": "10", "fecha": "2022"} # Extra
    ],
    "logros": [
        {"nombre": "Logro 1", "descripcion": "Desc 1", "fecha": "2020", "herramientas": "H1"},
        {"nombre": "Logro 2", "descripcion": "Desc 2", "fecha": "2021", "herramientas": "H2"},
        {"nombre": "Logro 3", "descripcion": "Desc 3", "fecha": "2022", "herramientas": "H3"}, # Extra
        {"nombre": "Logro 4", "descripcion": "Desc 4", "fecha": "2023", "herramientas": "H4"}  # Extra
    ],
    "experiencia": [
        {"empresa": "Emp 1", "fecha_ingreso": "2015", "fecha_salida": "2020", "cargo": "C1", "funciones": "F1"},
        {"empresa": "Emp 2", "fecha_ingreso": "2020", "fecha_salida": "Presente", "cargo": "C2", "funciones": "F2"}
    ],
    "autoevaluacion": {}
}

template_path = r"c:\Users\jcabrera\TalentoWEB\SDE_Project Manager.docx"
output_path = r"c:\Users\jcabrera\TalentoWEB\backend\scratch\test_output.docx"

os.makedirs(os.path.dirname(output_path), exist_ok=True)

try:
    fill_docx_template(template_path, data, output_path)
    print(f"Documento generado exitosamente en: {output_path}")
except Exception as e:
    print(f"Error: {e}")
