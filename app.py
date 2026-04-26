import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Función para conectar a Google Sheets usando los Secrets
def conectar_sheet():
    # Cargamos las credenciales desde el secreto que pegaste recién
    creds_dict = st.secrets["gcp_service_account"]["json_key"]
    
    # Esto convierte el texto de nuevo a un formato que Google entiende
    import json
    info = json.loads(creds_dict)
    
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(info, scopes=scope)
    client = gspread.authorize(creds)
    
    # CAMBIA ESTO por el nombre exacto de tu archivo de Google Sheets
    sheet = client.open("NOMBRE_DE_TU_PLANILLA").sheet1 
    return sheet

# Prueba la conexión
try:
    hoja_datos = conectar_sheet()
    # st.success("Conexión exitosa con Google Sheets") # Descomenta para probar
except Exception as e:
    st.error(f"Error de conexión: {e}")
