import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime
import plotly.express as px

# =========================================================
# ⚙️ CONTROL INTERNO DE FECHAS Y PLATAFORMA
# =========================================================
# False para abrir la carga de los 16avos / True para cerrar
PRONOSTICOS_BLOQUEADOS = False 

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Prode Exincor 2026 - 16avos", page_icon="🏆", layout="wide")

# --- CONFIGURACIÓN DE BANNER SUPERIOR DESDE GITHUB ---
usuario_github = "rebecaesthervera"
repositorio = "prode-mundial-exincor"
nombre_imagen = "fondo_exincor.jpeg.jpeg"

url_raw_github = f"https://raw.githubusercontent.com/{usuario_github}/{repositorio}/main/{nombre_imagen}"

st.markdown(
    f"""
    <style>
    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }}
    .banner-exincor {{
        background-image: url("{url_raw_github}");
        background-size: cover;
        background-position: center;
        width: 100%;
        height: 280px;
        margin-bottom: 25px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }}
    .stApp {{
        background-color: #EBF4FA;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: #FFFFFF !important;
        border-radius: 12px;
        padding: 22px;
        box-shadow: 0px 3px 8px rgba(0,0,0,0.06);
    }}
    .stTabs [data-baseweb="tab-list"] {{
        background-color: #FFFFFF;
        padding: 6px;
        border-radius: 8px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    }}
    </style>
    <div class="banner-exincor"></div>
    """,
    unsafe_allow_html=True
)

# --- FUNCIÓN DE CONEXIÓN A GOOGLE SHEETS ---
def conectar_sheet():
    try:
        json_key = st.secrets["gcp_service_account"]["json_key"]
        info = json.loads(json_key, strict=False)
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        ID_PLANILLA = "1lrC5SJmWmpN5KIVRAlYbQk7AXVsb7NK0bZwMKQ4rU_E"
        spreadsheet = client.open_by_key(ID_PLANILLA)
        # Apunta a la segunda pestaña (índice 1), llamada "16avos"
        return spreadsheet.get_worksheet(1)
    except Exception as e:
        return None

# =========================================================
# ⚽ 2. CONFIGURACIÓN DE LOS PARTIDOS DE 16AVOS (REALES)
# =========================================================
partidos_16avos = [
    {"id": "P1", "loc": "Sudáfrica", "sigla_l": "RSA", "vis": "Canadá", "sigla_v": "CAN"},
    {"id": "P2", "loc": "Brasil", "sigla_l": "BRA", "vis": "Japón", "sigla_v": "JPN"},
    {"id": "P3", "loc": "Alemania", "sigla_l": "GER", "vis": "Paraguay", "sigla_v": "PAR"},
    {"id": "P4", "loc": "Países Bajos", "sigla_l": "NED", "vis": "Marruecos", "sigla_v": "MAR"},
    {"id": "P5", "loc": "Costa de Marfil", "sigla_l": "CIV", "vis": "Noruega", "sigla_v": "NOR"},
    {"id": "P6", "loc": "Francia", "sigla_l": "FRA", "vis": "Suecia", "sigla_v": "SWE"},
    {"id": "P7", "loc": "México", "sigla_l": "MEX", "vis": "Ecuador", "sigla_v": "ECU"},
    {"id": "P8", "loc": "Argentina", "sigla_l": "ARG", "vis": "Cabo Verde", "sigla_v": "CPV"},
]

# PESTAÑAS PRINCIPALES DEL SISTEMA
tab_voto, tab_ranking, tab_stats, tab_politicas = st.tabs([
    "⚽ Cargar Pronósticos (16avos)", 
    "📊 Tabla de Posiciones", 
    "📈 Tendencias", 
    "📋 Reglamento y Cuadro de Honor"
])

# --- 1. PESTAÑA DE CARGA ---
with tab_voto:
    espacio_izq, col_central, espacio_der = st.columns([1, 2.8, 1])
    with col_central:
        if PRONOSTICOS_BLOQUEADOS:
            st.warning("⚠️ **La carga de pronósticos para 16avos se encuentra CERRADA.**")

        st.markdown("<div style='background-color: #1E3A8A; padding: 10px; border-radius: 5px; margin-bottom: 15px;'><h3 style='color: white; margin: 0; font-size: 18px;'>👤 1. Tus Datos Personales</h3></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: nombre = st.text_input("Apellido y Nombre", placeholder="Ej: Perez, Juan", disabled=PRONOSTICOS_BLOQUEADOS)
        with c2: legajo = st.text_input("Legajo", placeholder="Tu número de legajo", disabled=PRONOSTICOS_BLOQUEADOS)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='background-color: #1E3A8A; padding: 10px; border-radius: 5px; margin-bottom: 5px;'><h3 style='color: white; margin: 0; font-size: 18px;'>🔮 2. Pronósticos para la Fase Eliminatoria</h3></div>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748B; font-size: 14px; margin-bottom: 15px;'>Seleccioná tus predicciones. Los puntos comienzan desde cero para esta nueva etapa.</p>", unsafe_allow_html=True)
        
        if "votos" not in st.session_state:
            st.session_state.votos = {}

        for idx, partido in enumerate(partidos_16avos):
            loc, vis = partido["loc"], partido["vis"]
            s_L, s_V = partido["sigla_l"], partido["sigla_v"]
            clave = f"16avos_{partido['id']}"
            
            with st.container(border=True):
                st.markdown(f"<p style='margin:0; color:#1E3A8A; font-weight: bold;'>Partido {idx+1}: {loc} vs. {vis}</p>", unsafe_allow_html=True)
                opciones = ["Sin seleccionar", f"[{s_L}] Gana {loc}", "🤝 Empate (90 min + Alargue)", f"[{s_V}] Gana {vis}"]
                
                default_idx = opciones.index(st.session_state.votos[clave]) if clave in st.session_state.votos else 0
                
                seleccion = st.radio(
                    label=f"Opciones_{clave}",
                    options=opciones,
                    index=default_idx,
                    horizontal=True,
                    label_visibility="collapsed",
                    key=f"radio_{clave}",
                    disabled=PRONOSTICOS_BLOQUEADOS
                )
                st.session_state.votos[clave] = seleccion

        st.markdown("---")
        
        if not PRONOSTICOS_BLOQUEADOS:
            enviado = st.button("🚀 ENVIAR PRONÓSTICOS DE 16AVOS", use_container_width=True, type="primary")

            if enviado:
                if nombre.strip() == "" or legajo.strip() == "":
                    st.error("🚫 Error: Por favor, ingresá tu Nombre y tu Legajo.")
                else:
                    incompletos = False
                    for partido in partidos_16avos:
                        if st.session_state.votos.get(f"16avos_{partido['id']}", "Sin seleccionar") == "Sin seleccionar":
                            incompletos = True
                            break
                    
                    if incompletos:
                        st.error("⚠️ ¡Faltan completar partidos! Revisá que todos los cruces tengan una opción seleccionada.")
                    else:
                        with st.spinner("Guardando en el servidor Exincor..."):
                            hoja = conectar_sheet()
                            if hoja:
                                nueva_fila = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nombre.strip(), legajo.strip()]
                                for partido in partidos_16avos:
                                    nueva_fila.append(st.session_state.votos[f"16avos_{partido['id']}"])
                                
                                try:
                                    hoja.append_row(nueva_fila)
                                    st.balloons()
                                    st.success("✅ ¡Pronósticos de 16avos guardados con éxito! ¡Comenzamos la carrera de cero!")
                                    st.session_state.votos = {}
                                except Exception as e:
                                    st.error(f"Error al escribir en la planilla: {e}")
        else:
            st.info("🔒 El envío de formularios está deshabilitado temporalmente.")

# --- DESCARGA DE DATOS PARA RANKING (DESDE LA NUEVA PESTAÑA) ---
try:
    hoja = conectar_sheet()
    datos = hoja.get_all_records()
    df_prode = pd.DataFrame(datos)
    
    # SOLUCIÓN AL KEYERROR: Limpia automáticamente espacios fantasmas al inicio o final de los encabezados del Sheet
    if not df_prode.empty:
        df_prode.columns = df_prode.columns.str.strip()
except:
    df_prode = pd.DataFrame()

# --- 2. PESTAÑA DE RANKING (DESDE CERO) ---
with tab_ranking:
    if not df_prode.empty:
        mascara_oficial = df_prode['Apellido y Nombre'].str.contains("RESULTADOS OFICIALES", na=False)
        if mascara_oficial.any():
            resultados_reales = df_prode[mascara_oficial].iloc[0]
            df_jugadores = df_prode[~mascara_oficial]
            ranking = []
            
            for _, fila in df_jugadores.iterrows():
                puntos = 0
                for col in df_prode.columns[3:]:
                    if col in resultados_reales and fila[col] == resultados_reales[col] and fila[col] != "":
                        puntos += 3
                ranking.append({"Colaborador": fila["Apellido y Nombre"], "Legajo": fila["Legajo"], "Puntos": puntos})
            
            if ranking:
                df_rank = pd.DataFrame(ranking).sort_values(by="Puntos", ascending=False)
                df_rank.index = range(1, len(df_rank) + 1)
                df_rank.index.name = "Puesto"
                df_rank = df_rank.reset_index()

                st.markdown("<h3 style='color: #1E3A8A; text-align: center;'>🏆 Tabla de Posiciones - Fase Eliminatoria</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #64748B; text-align: center; font-size: 14px; margin-bottom: 25px;'>Destacados en color los 3 puestos líderes que compiten por los Grandes Premios Finales.</p>", unsafe_allow_html=True)
                
                # Función para sombrear a los 3 primeros líderes
                def destacar_top3(row):
                    if row['Puesto'] <= 3:
                        return ['background-color: #D0E1F9; color: #1E3A8A; font-weight: bold;'] * len(row)
                    return [''] * len(row)
                
                df_estilizado = df_rank.style.apply(destacar_top3, axis=1)
                st.dataframe(df_estilizado, use_container_width=True, hide_index=True)
        else:
            st.info("💡 El ranking de esta fase se activará cuando se cargue la fila de 'RESULTADOS OFICIALES' en la pestaña '16avos'.")
    else:
        st.info("Aún no hay predicciones cargadas para esta fase.")

# --- 3. PESTAÑA DE TENDENCIAS ---
with tab_stats:
    if not df_prode.empty:
        df_solo_votos = df_prode[~df_prode['Apellido y Nombre'].str.contains("RESULTADOS", na=False)]
        if not df_solo_votos.empty and len(df_prode.columns) > 3:
            st.subheader("¿Cómo están distribuidas las apuestas en Exincor?")
            todos_votos = df_solo_votos.melt(id_vars=['Apellido y Nombre'], value_vars=df_prode.columns[3:])
            votos_ganadores = todos_votos[~todos_votos['value'].str.contains("Empate")].copy()
            if not votos_ganadores.empty:
                votos_ganadores['Equipo'] = votos_ganadores['value'].str.split(" Gana ").str[-1]
                favs = votos_ganadores['Equipo'].value_counts().head(10).reset_index()
                fig = px.bar(favs, x='count', y='Equipo', orientation='h', title="Top Favoritos de la Fase", color_discrete_sequence=['#1E3A8A'])
                st.plotly_chart(fig, use_container_width=True)

# --- 4. PESTAÑA DE REGLAMENTO Y CUADRO DE HONOR ---
with tab_politicas:
    # CUADRO DE HONOR EXCLUSIVO DE LA 1RA RONDA
    st.markdown("""
    <div style='background-color: #1E3A8A; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 25px;'>
        <h2 style='color: white; margin: 0;'>🎖️ CUADRO DE HONOR - GANADORES 1RA RONDA 🎖️</h2>
        <p style='color: #D0E1F9; margin: 5px 0 0 0; font-size: 16px;'>Felicitaciones al Top 5 que conquistó la Fase de Grupos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Nombres extraídos fielmente de la tabla general previa
    col_ganadores = pd.DataFrame([
        {"Puesto": "🥇 1° Lugar", "Ganador": "Goyochea Axel Samuel", "Legajo": "637", "Puntos": "141 pts"},
        {"Puesto": "🥈 2° Lugar", "Ganador": "Guerrero Lautaro", "Legajo": "664", "Puntos": "138 pts"},
        {"Puesto": "🥉 3° Lugar", "Ganador": "Agustín rojas", "Legajo": "600", "Puntos": "138 pts"},
        {"Puesto": "🏅 4° Lugar", "Ganador": "Federico Lyons", "Legajo": "632", "Puntos": "132 pts"},
        {"Puesto": "🏅 5° Lugar", "Ganador": "JUAN CAZON", "Legajo": "9050", "Puntos": "132 pts"},
    ])
    st.table(col_ganadores)
    
    st.markdown("---")
    st.markdown("""
    ### 🔄 ¡Borrón y Cuenta Nueva!
    Para mantener la emoción en toda la planta y garantizar que **todos los colaboradores sigan participando con chances reales**, el puntaje se ha reiniciado completamente a **0 puntos** para esta fase eliminatoria. 
    
    ### 📋 Reglamento y Políticas de la Fase Eliminatoria
    * **Límite de registro:** Estrictamente **una (1) sola carga por Legajo** para toda la fase de 16avos.
    * **Regla de Oro (90 Minutos):** Cuenta el resultado al finalizar el tiempo reglamentario o prórroga de alargue. Si el partido va a definición por penales, el resultado válido para el Prode es **🤝 Empate**.
    
    ### 🎁 Nueva Estructura de Premios Finales
    Al finalizar el certamen, el podio definitivo se consagrará únicamente con los **3 primeros puestos generales** de la fase acumulativa eliminatoria:
    * 🥇 **1° Puesto General:** Importante Orden de Compra Corporativa.
    * 🥈 **2° Puesto General:** Importante Orden de Compra Corporativa.
    * 🥉 **3° Puesto General:** Importante Orden de Compra Corporativa.
    """)
