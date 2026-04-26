import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime
import plotly.express as px

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Prode Exincor 2026", page_icon="🏆", layout="wide")

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
        return spreadsheet.get_worksheet(0)
    except Exception as e:
        if "200" in str(e):
            try:
                creds = Credentials.from_service_account_info(info, scopes=scope)
                client = gspread.authorize(creds)
                return client.open_by_key("1lrC5SJmWmpN5KIVRAlYbQk7AXVsb7NK0bZwMKQ4rU_E").get_worksheet(0)
            except:
                st.error("Error crítico de comunicación con Google.")
        else:
            st.error(f"No se pudo conectar: {e}")
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

# 3. CABECERA
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏆 Prode Mundial 2026 - Exincor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Cargá tus pronósticos y seguí el ranking de la oficina en vivo.</p>", unsafe_allow_html=True)

# CREACIÓN DE PESTAÑAS PRINCIPALES
tab_voto, tab_ranking, tab_stats = st.tabs(["⚽ Cargar Pronósticos", "📊 Tabla de Posiciones", "📈 Tendencias"])

with tab_voto:
    espacio_izq, col_central, espacio_der = st.columns([1, 3, 1])
    with col_central:
        with st.form("formulario_prode"):
            st.subheader("👤 Tus Datos")
            c1, c2 = st.columns(2)
            with c1: nombre = st.text_input("Apellido y Nombre", placeholder="Ej: Perez, Juan")
            with c2: legajo = st.text_input("Legajo", placeholder="Tu número de legajo")
            
            st.markdown("---")
            n_grupos = list(grupos.keys())
            tabs_grupos = st.tabs(n_grupos)
            respuestas = {}
            
            for i, (n_grupo, equipos) in enumerate(grupos.items()):
                with tabs_grupos[i]:
                    st.markdown(f"### {n_grupo}")
                    partidos = generar_partidos(equipos)
                    for j, partido in enumerate(partidos):
                        loc, vis = partido[0], partido[1]
                        s_L, s_V = siglas.get(loc, "---"), siglas.get(vis, "---")
                        with st.container(border=True):
                            st.markdown(f"<p style='text-align:center; color:#64748B; font-size:12px;'>Partido {j+1}</p>", unsafe_allow_html=True)
                            clave = f"{n_grupo}_Match_{j}"
                            opciones = [f"[{s_L}] Gana {loc}", "🤝 Empate", f"[{s_V}] Gana {vis}"]
                            respuestas[clave] = st.radio("Resultado:", options=opciones, horizontal=True, label_visibility="collapsed", key=clave)

            enviado = st.form_submit_button("🚀 ENVIAR MIS PRONÓSTICOS", use_container_width=True)

    if enviado:
        if nombre == "" or legajo == "":
            st.warning("⚠️ Completá tu nombre y legajo.")
        else:
            with st.spinner("Guardando..."):
                hoja = conectar_sheet()
                if hoja:
                    nueva_fila = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nombre, legajo]
                    for n_g in n_grupos:
                        for j in range(6):
                            nueva_fila.append(respuestas[f"{n_g}_Match_{j}"])
                    try:
                        hoja.append_row(nueva_fila)
                        st.balloons()
                        st.success("✅ Guardado correctamente. ¡Mucha suerte!")
                    except Exception as e:
                        st.error(f"Error al escribir: {e}")

# DESCARGA DE DATOS PARA RANKING Y ESTADÍSTICAS
try:
    hoja = conectar_sheet()
    datos = hoja.get_all_records()
    df_prode = pd.DataFrame(datos)
except:
    df_prode = pd.DataFrame()

with tab_ranking:
    if not df_prode.empty:
        # Buscamos la fila de RESULTADOS OFICIALES
        mascara_oficial = df_prode['Apellido y Nombre'].str.contains("RESULTADOS OFICIALES", na=False)
        
        if mascara_oficial.any():
            resultados_reales = df_prode[mascara_oficial].iloc[0]
            df_jugadores = df_prode[~mascara_oficial]
            
            ranking = []
            for _, fila in df_jugadores.iterrows():
                puntos = 0
                for col in df_prode.columns[3:]:
                    # Verificamos que tanto el resultado oficial como el del usuario existan
                    if col in resultados_reales and fila[col] == resultados_reales[col] and fila[col] != "":
                        puntos += 3
                
                ranking.append({
                    "Colaborador": fila["Apellido y Nombre"], 
                    "Legajo": fila["Legajo"], 
                    "Puntos": puntos
                })
            
            # --- CORRECCIÓN DEL ERROR ---
            if ranking: # Solo intentamos crear y ordenar si hay gente en la lista
                df_rank = pd.DataFrame(ranking)
                if "Puntos" in df_rank.columns:
                    df_rank = df_rank.sort_values(by="Puntos", ascending=False)
                    st.dataframe(df_rank, use_container_width=True, hide_index=True)
                    
                    st.divider()
                    st.metric("🏆 Líder Actual", df_rank.iloc[0]["Colaborador"], f"{df_rank.iloc[0]['Puntos']} pts")
            else:
                st.info("Aún no hay participantes registrados para calcular el ranking.")
        else:
            st.info("💡 El ranking se activará cuando cargues la fila 'RESULTADOS OFICIALES' en el Sheet.")
    else:
        st.info("Aún no hay datos para mostrar.")

with tab_stats:
    if not df_prode.empty:
        df_solo_votos = df_prode[~df_prode['Apellido y Nombre'].str.contains("RESULTADOS", na=False)]
        if not df_solo_votos.empty:
            st.subheader("¿En quién confía Exincor?")
            
            # Gráfico de Favoritos
            todos_votos = df_solo_votos.melt(id_vars=['Apellido y Nombre'], value_vars=df_prode.columns[3:])
            votos_ganadores = todos_votos[~todos_votos['value'].str.contains("Empate")].copy()
            votos_ganadores['Equipo'] = votos_ganadores['value'].str.split(" Gana ").str[-1]
            
            favs = votos_ganadores['Equipo'].value_counts().head(10).reset_index()
            fig = px.bar(favs, x='count', y='Equipo', orientation='h', title="Top 10 Favoritos", color_discrete_sequence=['#1E3A8A'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Analizador por partido
            st.divider()
            partido_sel = st.selectbox("Analizá un partido específico:", df_prode.columns[3:])
            tendencia = df_solo_votos[partido_sel].value_counts(normalize=True).reset_index()
            tendencia.columns = ['Opción', 'Porcentaje']
            tendencia['Porcentaje'] = tendencia['Porcentaje'] * 100
            
            fig_t = px.bar(tendencia, x='Opción', y='Porcentaje', text_auto='.1f', color='Opción')
            st.plotly_chart(fig_t, use_container_width=True)
    else:
        st.info("Las tendencias aparecerán cuando haya pronósticos cargados.")
