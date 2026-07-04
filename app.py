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
# Carga ABIERTA exclusivamente para la segunda tanda de partidos
PRONOSTICOS_BLOQUEADOS = False 

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Prode Exincor 2026 - 16avos (Parte 2)", page_icon="🏆", layout="wide")

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
def conectar_sheet(num_pestana):
    try:
        json_key = st.secrets["gcp_service_account"]["json_key"]
        info = json.loads(json_key, strict=False)
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        ID_PLANILLA = "1lrC5SJmWmpN5KIVRAlYbQk7AXVsb7NK0bZwMKQ4rU_E"
        spreadsheet = client.open_by_key(ID_PLANILLA)
        return spreadsheet.get_worksheet(num_pestana)
    except Exception as e:
        return None

# =========================================================
# ⚽ 2. CONFIGURACIÓN EXCLUSIVA DE LOS 8 PARTIDOS FALTANTES
# =========================================================
# Reordenados EXACTAMENTE según la estructura de tus columnas P, Q, R y S del Sheets
partidos_16avos = [
    {"id": "P9", "loc": "Canadá", "sigla_l": "CAN", "vis": "Marruecos", "sigla_v": "MAR"},
    {"id": "P10", "loc": "Paraguay", "sigla_l": "PAR", "vis": "Francia", "sigla_v": "FRA"},
    {"id": "P11", "loc": "Brasil", "sigla_l": "BRA", "vis": "Noruega", "sigla_v": "NOR"},
    {"id": "P12", "loc": "México", "sigla_l": "MEX", "vis": "Inglaterra", "sigla_v": "ENG"},
    {"id": "P13", "loc": "Portugal", "sigla_l": "POR", "vis": "España", "sigla_v": "ESP"},            # Columna P
    {"id": "P14", "loc": "Suiza", "sigla_l": "SUI", "vis": "Colombia", "sigla_v": "COL"},           # Columna Q
    {"id": "P15", "loc": "Argentina", "sigla_l": "ARG", "vis": "Egipto", "sigla_v": "EGY"},         # Columna R
    {"id": "P16", "loc": "Estados Unidos", "sigla_l": "USA", "vis": "Bélgica", "sigla_v": "BEL"},   # Columna S
]

# PESTAÑAS PRINCIPALES DEL SISTEMA
tab_voto, tab_ranking, tab_antiguos, tab_stats, tab_politicas = st.tabs([
    "⚽ Cargar Pronósticos (Parte 2)", 
    "📊 Tabla de Posiciones", 
    "🏅 Top 10 Primera Ronda",
    "📈 Tendencias", 
    "📋 Reglamento y Cuadro de Honor"
])

# --- 1. PESTAÑA DE CARGA ---
with tab_voto:
    espacio_izq, col_central, espacio_der = st.columns([1, 2.8, 1])
    with col_central:
        if PRONOSTICOS_BLOQUEADOS:
            st.warning("⚠️ **La carga de pronósticos se encuentra CERRADA.**")

        st.markdown("<div style='background-color: #1E3A8A; padding: 10px; border-radius: 5px; margin-bottom: 15px;'><h3 style='color: white; margin: 0; font-size: 18px;'>👤 1. Tus Datos Personales</h3></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: nombre = st.text_input("Apellido y Nombre", placeholder="Ej: Perez, Juan", disabled=PRONOSTICOS_BLOQUEADOS)
        with c2: legajo = st.text_input("Legajo", placeholder="Tu número de legajo", disabled=PRONOSTICOS_BLOQUEADOS)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='background-color: #1E3A8A; padding: 10px; border-radius: 5px; margin-bottom: 5px;'><h3 style='color: white; margin: 0; font-size: 18px;'>🔮 2. Pronósticos Restantes</h3></div>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748B; font-size: 14px; margin-bottom: 15px;'>Completá los 8 partidos que faltaban actualizar.</p>", unsafe_allow_html=True)
        
        if "votos" not in st.session_state:
            st.session_state.votos = {}

        for idx, partido in enumerate(partidos_16avos):
            loc, vis = partido["loc"], partido["vis"]
            s_L, s_V = partido["sigla_l"], partido["sigla_v"]
            clave = f"16avos_{partido['id']}"
            
            with st.container(border=True):
                # Muestra el número correlativo real del fixture (Partido 9 al 16)
                st.markdown(f"<p style='margin:0; color:#1E3A8A; font-weight: bold;'>Partido {idx+9}: {loc} vs. {vis}</p>", unsafe_allow_html=True)
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
            enviado = st.button("🚀 ENVIAR PRONÓSTICOS RESTANTES", use_container_width=True, type="primary")

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
                            hoja = conectar_sheet(1) # Escribe en la pestaña de 16avos (índice 1)
                            if hoja:
                                nueva_fila = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nombre.strip(), legajo.strip()]
                                
                                # Rellena con celdas vacías las primeras 8 columnas de partidos para no pisar el orden del Sheets
                                for _ in range(8):
                                    nueva_fila.append("")
                                    
                                # Agrega las 8 nuevas respuestas seleccionadas
                                for partido in partidos_16avos:
                                    nueva_fila.append(st.session_state.votos[f"16avos_{partido['id']}"])
                                
                                try:
                                    hoja.append_row(nueva_fila)
                                    st.balloons()
                                    st.success("✅ ¡Tus pronósticos restantes fueron guardados con éxito!")
                                    st.session_state.votos = {}
                                except Exception as e:
                                    st.error(f"Error al escribir en la planilla: {e}")
        else:
            st.info("🔒 El envío de formularios está deshabilitado temporalmente.")

# --- DESCARGA DE DATOS DESDE LA NUEVA PESTAÑA (16AVOS) ---
try:
    hoja_actual = conectar_sheet(1)
    datos_actual = hoja_actual.get_all_records()
    df_prode = pd.DataFrame(datos_actual)
    if not df_prode.empty:
        df_prode.columns = df_prode.columns.str.strip()
except:
    df_prode = pd.DataFrame()

# --- 2. PESTAÑA DE RANKING DE LA FASE ACTUAL ---
with tab_ranking:
    if not df_prode.empty:
        mascara_oficial = df_prode['Apellido y Nombre'].str.contains("RESULTADOS OFICIALES", na=False)
        df_jugadores = df_prode[~mascara_oficial]
        
        if mascara_oficial.any():
            resultados_reales = df_prode[mascara_oficial].iloc[0]
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
                
                def destacar_top3(row):
                    if row['Puesto'] <= 3:
                        return ['background-color: #D0E1F9; color: #1E3A8A; font-weight: bold;'] * len(row)
                    return [''] * len(row)
                
                df_estilizado = df_rank.style.apply(destacar_top3, axis=1)
                st.dataframe(df_estilizado, use_container_width=True, hide_index=True)
        else:
            st.markdown("<h3 style='color: #1E3A8A; text-align: center;'>📝 Colaboradores Registrados - 16avos</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #64748B; text-align: center; font-size: 14px; margin-bottom: 25px;'>A continuación se muestran los empleados que ya guardaron con éxito sus apuestas de la fase.</p>", unsafe_allow_html=True)
            
            if not df_jugadores.empty:
                df_registrados = df_jugadores[["Apellido y Nombre", "Legajo"]].copy()
                df_registrados.columns = ["Colaborador", "Legajo"]
                df_registrados.insert(0, "Estado", "✅ Guardado")
                df_registrados.index = range(1, len(df_registrados) + 1)
                df_registrados.index.name = "N°"
                df_registrados = df_registrados.reset_index()
                
                def estilo_registro(row):
                    return ['background-color: #FFFFFF; color: #1E3A8A;'] * len(row)
                
                st.dataframe(df_registrados.style.apply(estilo_registro, axis=1), use_container_width=True, hide_index=True)
            else:
                st.info("💡 Aún no se registraron jugadas. ¡Sé el primero en enviar tus pronósticos!")
    else:
        st.info("Aún no hay predicciones cargadas para esta fase.")

# --- 3. NUEVA PESTAÑA: RECUPERACIÓN EN VIVO DEL TOP 10 ANTERIOR ---
with tab_antiguos:
    st.markdown("<h3 style='color: #1E3A8A; text-align: center;'>📊 Top 10 Definitivo - Fase de Grupos</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; text-align: center; font-size: 14px; margin-bottom: 25px;'>Historial completo de los mejores puntajes acumulados durante la Primera Ronda del Prode.</p>", unsafe_allow_html=True)
    
    with st.spinner("Calculando tabla histórica desde la base de datos..."):
        try:
            hoja_vieja = conectar_sheet(0)
            datos_viejos = hoja_vieja.get_all_records()
            df_viejo = pd.DataFrame(datos_viejos)
            
            if not df_viejo.empty:
                df_viejo.columns = df_viejo.columns.str.strip()
                mascara_oficial_viejos = df_viejo['Apellido y Nombre'].str.contains("RESULTADOS OFICIALES", na=False)
                
                if mascara_oficial_viejos.any():
                    resultados_reales_viejos = df_viejo[mascara_oficial_viejos].iloc[0]
                    df_jugadores_viejos = df_viejo[~mascara_oficial_viejos]
                    ranking_viejo = []
                    
                    for _, fila in df_jugadores_viejos.iterrows():
                        puntos = 0
                        for col in df_viejo.columns[3:]:
                            if col in resultados_reales_viejos and fila[col] == resultados_reales_viejos[col] and fila[col] != "":
                                puntos += 3
                        ranking_viejo.append({"Colaborador": fila["Apellido y Nombre"], "Legajo": fila["Legajo"], "Puntos": puntos})
                    
                    if ranking_viejo:
                        df_rank_viejo = pd.DataFrame(ranking_viejo).sort_values(by="Puntos", ascending=False)
                        df_rank_viejo.index = range(1, len(df_rank_viejo) + 1)
                        df_rank_viejo.index.name = "Puesto"
                        df_rank_viejo = df_rank_viejo.reset_index()
                        
                        df_top10 = df_rank_viejo.head(10)
                        
                        def destacar_top5_viejo(row):
                            if row['Puesto'] <= 5:
                                return ['background-color: #D0E1F9; color: #1E3A8A; font-weight: bold;'] * len(row)
                            return [''] * len(row)
                        
                        st.dataframe(df_top10.style.apply(destacar_top5_viejo, axis=1), use_container_width=True, hide_index=True)
                else:
                    st.warning("No se encontró la fila 'RESULTADOS OFICIALES' en la pestaña original de grupos.")
            else:
                st.info("No se encontraron registros en la pestaña original.")
        except Exception as e:
            st.error(f"No se pudo cargar el historial: {e}")

# --- 4. PESTAÑA DE TENDENCIAS ---
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

# --- 5. PESTAÑA DE REGLAMENTO Y CUADRO DE HONOR ---
with tab_politicas:
    st.markdown("""
    <div style='background-color: #1E3A8A; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 25px;'>
        <h2 style='color: white; margin: 0;'>🎖️ CUADRO DE HONOR - GANADORES 1RA RONDA 🎖️</h2>
        <p style='color: #D0E1F9; margin: 5px 0 0 0; font-size: 16px;'>Felicitaciones al Top 5 que conquistó la Fase de Grupos</p>
    </div>
    """, unsafe_allow_html=True)
    
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
