import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
from datetime import datetime
import plotly.express as px

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Prode Exincor 2026", page_icon="🏆", layout="wide")

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
        return spreadsheet.get_worksheet(0)
    except Exception as e:
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

# PESTAÑAS PRINCIPALES
tab_voto, tab_ranking, tab_stats, tab_politicas = st.tabs([
    "⚽ Cargar Pronósticos", 
    "📊 Tabla de Posiciones", 
    "📈 Tendencias", 
    "📋 Reglamento y Políticas"
])

with tab_voto:
    espacio_izq, col_central, espacio_der = st.columns([1, 2.8, 1])
    with col_central:
        st.markdown("<div style='background-color: #1E3A8A; padding: 10px; border-radius: 5px; margin-bottom: 15px;'><h3 style='color: white; margin: 0; font-size: 18px;'>👤 1. Tus Datos Personales</h3></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: nombre = st.text_input("Apellido y Nombre", placeholder="Ej: Perez, Juan")
        with c2: legajo = st.text_input("Legajo", placeholder="Tu número de legajo")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='background-color: #1E3A8A; padding: 10px; border-radius: 5px; margin-bottom: 5px;'><h3 style='color: white; margin: 0; font-size: 18px;'>🔮 2. Completá los Partidos</h3></div>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748B; font-size: 14px; margin-bottom: 15px;'>Hacé clic en cada pestaña (Grupo A al L) y elegí tu opción. No olvides ninguna.</p>", unsafe_allow_html=True)
        
        n_grupos = list(grupos.keys())
        tabs_grupos = st.tabs(n_grupos)
        
        if "votos" not in st.session_state:
            st.session_state.votos = {}

        for i, (n_grupo, equipos) in enumerate(grupos.items()):
            with tabs_grupos[i]:
                st.markdown(f"<h3 style='color: #1E3A8A; margin-top: 10px;'>🏆 {n_grupo}</h3>", unsafe_allow_html=True)
                partidos = generar_partidos(equipos)
                
                for j, partido in enumerate(partidos):
                    loc, vis = partido[0], partido[1]
                    s_L, s_V = siglas.get(loc, "---"), siglas.get(vis, "---")
                    
                    with st.container(border=True):
                        st.markdown(f"<p style='margin:0; color:#1E3A8A; font-weight: bold;'>Partido {j+1}: {loc} vs. {vis}</p>", unsafe_allow_html=True)
                        clave = f"{n_grupo}_Match_{j}"
                        opciones = ["Sin seleccionar", f"[{s_L}] Gana {loc}", "🤝 Empate", f"[{s_V}] Gana {vis}"]
                        
                        default_idx = opciones.index(st.session_state.votos[clave]) if clave in st.session_state.votos else 0
                        
                        seleccion = st.radio(
                            label=f"Opciones_{clave}",
                            options=opciones,
                            index=default_idx,
                            horizontal=True,
                            label_visibility="collapsed",
                            key=f"radio_{clave}"
                        )
                        st.session_state.votos[clave] = seleccion

        st.markdown("---")
        enviado = st.button("🚀 ENVIAR MI PRODE COMPLETO", use_container_width=True, type="primary")

        if enviado:
            if nombre.strip() == "" or legajo.strip() == "":
                st.error("🚫 Error: Por favor, ingresá tu Nombre y tu Legajo en la parte superior.")
            else:
                incompletos = []
                for n_g in n_grupos:
                    for j in range(6):
                        c_key = f"{n_g}_Match_{j}"
                        if c_key not in st.session_state.votos or st.session_state.votos[c_key] == "Sin seleccionar":
                            incompletos.append(n_g)
                            break
                
                if incompletos:
                    incompletos_unicos = list(set(incompletos))
                    incompletos_unicos.sort()
                    grupos_texto = ", ".join(incompletos_unicos)
                    st.error(f"⚠️ ¡No podés enviar el Prode todavía! Te faltan completar partidos en: **{grupos_texto}**.")
                else:
                    with st.spinner("Conectando con el servidor Exincor..."):
                        hoja = conectar_sheet()
                        if hoja:
                            datos_completos = hoja.get_all_records()
                            df_check = pd.DataFrame(datos_completos)
                            ya_existe = False
                            if not df_check.empty and 'Legajo' in df_check.columns:
                                if str(legajo).strip() in df_check['Legajo'].astype(str).values:
                                    ya_existe = True
                            
                            if ya_existe:
                                st.error(f"🚫 Acceso denegado: El legajo {legajo} ya registró sus pronósticos.")
                            else:
                                nueva_fila = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nombre.strip(), legajo.strip()]
                                for n_g in n_grupos:
                                    for j in range(6):
                                        nueva_fila.append(st.session_state.votos[f"{n_g}_Match_{j}"])
                                try:
                                    hoja.append_row(nueva_fila)
                                    st.balloons()
                                    st.success("✅ ¡Excelente! Tus pronósticos se guardaron de forma segura en Exincor. ¡Mucha suerte!")
                                    st.session_state.votos = {}
                                except Exception as e:
                                    st.error(f"Error técnico al escribir en la planilla: {e}")

# DESCARGA DE DATOS PARA VISUALIZACIÓN
try:
    hoja = conectar_sheet()
    datos = hoja.get_all_records()
    df_prode = pd.DataFrame(datos)
except:
    df_prode = pd.DataFrame()

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
                
                st.markdown("<h3 style='color: #1E3A8A; text-align: center; margin-bottom: 20px;'>🎖️ Podio Provisional Exincor</h3>", unsafe_allow_html=True)
                podio_cols = st.columns(3)
                
                with podio_cols[0]:
                    if len(df_rank) >= 1:
                        st.metric("🥇 1° Puesto", df_rank.iloc[0]["Colaborador"], f"{df_rank.iloc[0]['Puntos']} pts")
                    else:
                        st.metric("🥇 1° Puesto", "---", "0 pts")
                
                with podio_cols[1]:
                    if len(df_rank) >= 2:
                        st.metric("🥈 2° Puesto", df_rank.iloc[1]["Colaborador"], f"{df_rank.iloc[1]['Puntos']} pts")
                    else:
                        st.metric("🥈 2° Puesto", "---", "0 pts")
                
                with podio_cols[2]:
                    if len(df_rank) >= 3:
                        st.metric("🥉 3° Puesto", df_rank.iloc[2]["Colaborador"], f"{df_rank.iloc[2]['Puntos']} pts")
                    else:
                        st.metric("🥉 3° Puesto", "---", "0 pts")
                
                st.markdown("---")
                st.dataframe(df_rank, use_container_width=True, hide_index=True)
        else:
            st.info("💡 El ranking se activará cuando cargues la fila 'RESULTADOS OFICIALES' en la planilla.")
    else:
        st.info("Aún no hay datos cargados.")

with tab_stats:
    if not df_prode.empty:
        df_solo_votos = df_prode[~df_prode['Apellido y Nombre'].str.contains("RESULTADOS", na=False)]
        if not df_solo_votos.empty:
            st.subheader("¿En quién confía Exincor?")
            todos_votos = df_solo_votos.melt(id_vars=['Apellido y Nombre'], value_vars=df_prode.columns[3:])
            votos_ganadores = todos_votos[~todos_votos['value'].str.contains("Empate")].copy()
            votos_ganadores['Equipo'] = votos_ganadores['value'].str.split(" Gana ").str[-1]
            favs = votos_ganadores['Equipo'].value_counts().head(10).reset_index()
            fig = px.bar(favs, x='count', y='Equipo', orientation='h', title="Top 10 Favoritos", color_discrete_sequence=['#1E3A8A'])
            st.plotly_chart(fig, use_container_width=True)

# 📋 REGLAMENTO OFICIAL TOTALMENTE ADAPTADO A TU NUEVA NEGOCIACIÓN
with tab_politicas:
    st.markdown("<h2 style='color: #1E3A8A;'>📜 Reglamento Oficial y Políticas del Prode Exincor 2026</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    ### 👤 1. Políticas de Participación
    * **Límite de registro:** Se permite estrictamente **una (1) sola carga por empleado (Legajo)**. El sistema bloqueará de forma automática cualquier intento de duplicación.
    * **Modificaciones:** Una vez enviado el formulario, las predicciones son de carácter **irrevocable**. Cualquier error deberá notificarse internamente a Recursos Humanos antes del inicio del torneo.
    * **Cierre de carga:** La plataforma cerrará la recepción de pronósticos exactamente **5 minutos antes** del pitazo inicial del primer partido del Mundial.
    
    ### 🔢 2. Sistema de Puntuación y Fases
    * **Acierto completo (+3 Puntos):** Sumás 3 puntos si acertás al ganador exacto del partido o si pronosticás un empate y el partido termina igualado.
    * **Puntos Acumulativos:** Los puntos obtenidos durante la Fase de Grupos **se mantendrán y se seguirán acumulando** en la tabla general durante las fases eliminatorias (Octavos, Cuartos, Semifinal y Final). Cada acierto en las rondas finales seguirá valiendo 3 puntos.
    
    ### ⚽ 3. Regla de Oro para Fases Eliminatorias (Octavos en adelante)
    * **Resultado Válido:** Para el cálculo de puntos del Prode, el resultado que se toma como oficial es el obtenido **al finalizar los 90 minutos de juego reglamentarios (o prórroga de alargue si la hubiese)**.
    * **¿Qué pasa con los penales?:** La tanda de penales **no se contabiliza** para el Prode. Si un partido se define en penales, significa que el partido terminó empatado, por lo tanto, el resultado oficial para el sistema será **🤝 Empate**.
    
    ### 🎁 4. Estructura Oficial de Grandes Premios
    * **Premios de Primera Ronda (Fase de Grupos):** Al congelarse la tabla provisional al término de la primera fase, se entregarán **5 Premios Sorpresa Especiales (Camisetas Oficiales de la Selección Argentina)** a los colaboradores que ocupen los primeros 5 puestos del ranking general.
    * **Grandes Premios Finales (Podio Definitivo):** Los puntos acumulados continuarán sumándose en las fases eliminatorias. Al concluir la final del Mundial, el podio definitivo se llevará los siguientes premios económicos:
        * 🥇 **1° Puesto General:** Orden de compra por **$300.000**.
        * 🥈 **2° Puesto General:** Orden de compra por **$100.000**.
        * 🥉 **3° Puesto General:** Orden de compra por **$100.000**.
    """)
