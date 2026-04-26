import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Prode Exincor 2026", page_icon="🏆", layout="wide")

# --- FUNCIÓN DE CONEXIÓN A GOOGLE SHEETS ---
def conectar_sheet():
    try:
        # 1. Cargamos el secreto
        creds_json = st.secrets["gcp_service_account"]["json_key"]
        info = json.loads(creds_json, strict=False)
        
        # 2. Configuramos los permisos
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        
        # 3. Abrimos la planilla
        # IMPORTANTE: Asegúrate de que el nombre sea "Prode Mundial Exincor" 
        # (o el que le hayas puesto al archivo de Google Sheets)
        nombre_planilla = "Prode Mundial Exincor"
        sheet = client.open(nombre_planilla).sheet1
        return sheet
    except Exception as e:
        # Solo mostramos el error si realmente no puede conectar
        st.error(f"No se pudo conectar con la base de datos: {e}")
        return None

# 2. DATOS DEL MUNDIAL
grupos = {
    "Grupo A": ["México", "Sudáfrica", "Corea del Sur", "Rep. Checa"],
    "Grupo B": ["Canadá", "Bosnia", "Qatar", "Suiza"],
    "Grupo C": ["Brasil", "Marruecos", "Haití", "Escocia"],
    "Grupo D": ["EE. UU.", "Turquía", "Australia", "Paraguay"],
    "Grupo E": ["Alemania", "Curazao", "C. Marfil", "Ecuador"],
    "Grupo F": ["P. Bajos", "Japón", "Suecia", "Túnez"],
    "Grupo G": ["Bélgica", "Egipto", "Irán", "N. Zelanda"],
    "Grupo H": ["España", "C. Verde", "Arabia S.", "Uruguay"],
    "Grupo I": ["Francia", "Senegal", "Irak", "Noruega"],
    "Grupo J": ["Austria", "Jordania", "Argentina", "Argelia"],
    "Grupo K": ["Portugal", "RD Congo", "Uzbekistán", "Colombia"],
    "Grupo L": ["Inglaterra", "Croacia", "Ghana", "Panamá"]
}

siglas = {
    "México": "MEX", "Sudáfrica": "RSA", "Corea del Sur": "KOR", "Rep. Checa": "CZE",
    "Canadá": "CAN", "Bosnia": "BIH", "Qatar": "QAT", "Suiza": "SUI",
    "Brasil": "BRA", "Marruecos": "MAR", "Haití": "HAI", "Escocia": "SCO",
    "EE. UU.": "USA", "Turquía": "TUR", "Australia": "AUS", "Paraguay": "PAR",
    "Alemania": "GER", "Curazao": "CUW", "C. Marfil": "CIV", "Ecuador": "ECU",
    "P. Bajos": "NED", "Japón": "JPN", "Suecia": "SWE", "Túnez": "TUN",
    "Bélgica": "BEL", "Egipto": "EGY", "Irán": "IRN", "N. Zelanda": "NZL",
    "España": "ESP", "C. Verde": "CPV", "Arabia S.": "KSA", "Uruguay": "URU",
    "Francia": "FRA", "Senegal": "SEN", "Irak": "IRQ", "Noruega": "NOR",
    "Austria": "AUT", "Jordania": "JOR", "Argentina": "ARG", "Argelia": "ALG",
    "Portugal": "POR", "RD Congo": "COD", "Uzbekistán": "UZB", "Colombia": "COL",
    "Inglaterra": "ENG", "Croacia": "CRO", "Ghana": "GHA", "Panamá": "PAN"
}

def generar_partidos(equipos):
    return [(equipos[0], equipos[1]), (equipos[2], equipos[3]),
            (equipos[0], equipos[2]), (equipos[1], equipos[3]),
            (equipos[0], equipos[3]), (equipos[1], equipos[2])]

# 3. INTERFAZ VISUAL
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏆 Prode Mundial 2026 - Exincor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Completa tus pronósticos y sumá puntos. ¡El ganador se lleva el premio mayor!</p>", unsafe_allow_html=True)

espacio_izq, col_central, espacio_der = st.columns([1, 3, 1])

with col_central:
    with st.form("formulario_prode"):
        st.subheader("👤 Tus Datos")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Apellido y Nombre", placeholder="Ej: Perez, Juan")
        with col2:
            legajo = st.text_input("Legajo", placeholder="Tu número de legajo")
            
        st.markdown("---")
        st.subheader("⚽ Pronósticos")
        
        n_grupos = list(grupos.keys())
        tabs = st.tabs(n_grupos)
        respuestas = {} # Diccionario para guardar lo que elije el usuario
        
        for i, (n_grupo, equipos) in enumerate(grupos.items()):
            with tabs[i]:
                st.markdown(f"<h3 style='color:#1E3A8A;'>{n_grupo}</h3>", unsafe_allow_html=True)
                partidos = generar_partidos(equipos)
                
                for j, partido in enumerate(partidos):
                    loc, vis = partido[0], partido[1]
                    s_L, s_V = siglas.get(loc, "---"), siglas.get(vis, "---")
                    
                    with st.container(border=True):
                        st.markdown(f"<p style='text-align:center; color:#64748B; font-size:14px;'>Partido {j+1}</p>", unsafe_allow_html=True)
                        clave = f"{n_grupo}_Match_{j}"
                        opciones = [f"[{s_L}] Gana {loc}", "🤝 Empate", f"[{s_V}] Gana {vis}"]
                        
                        respuestas[clave] = st.radio("Resultado:", options=opciones, horizontal=True, label_visibility="collapsed", key=clave)

        st.markdown("---")
        st.info("💡 Por favor, revisá todas las pestañas de los grupos antes de enviar.")
        enviado = st.form_submit_button("🚀 ENVIAR MIS PRONÓSTICOS", use_container_width=True)

# 4. LÓGICA DE ENVÍO A GOOGLE SHEETS
if enviado:
    if nombre == "" or legajo == "":
        st.warning("⚠️ Falta completar Nombre o Legajo.")
    else:
        with st.spinner("Guardando tus pronósticos..."):
            hoja = conectar_sheet()
            if hoja:
                # Preparamos la fila para el Excel
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                # Armamos la lista de valores: Marca Temporal, Nombre, Legajo + todos los votos
                nueva_fila = [timestamp, nombre, legajo]
                
                # Recorremos los grupos en orden para asegurar que los votos vayan a la columna correcta
                for n_grupo in n_grupos:
                    for j in range(6):
                        clave = f"{n_grupo}_Match_{j}"
                        nueva_fila.append(respuestas[clave])
                
                try:
                    hoja.append_row(nueva_fila)
                    st.balloons()
                    st.success(f"✅ ¡Excelente {nombre}! Tus pronósticos se guardaron correctamente. ¡Mucha suerte!")
                except Exception as e:
                    st.error(f"Error al escribir en el Sheet: {e}")
