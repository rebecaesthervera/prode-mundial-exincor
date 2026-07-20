import json
from datetime import datetime
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

# =========================================================
# ⚙️ CONTROL INTERNO DE FECHAS Y PLATAFORMA
# =========================================================
# TRUE: El partido ya comenzó, la carga queda deshabilitada por completo.
PRONOSTICOS_BLOQUEADOS = True

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Prode Exincor 2026 - Finales",
    page_icon="🏆",
    layout="wide",
)

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
    unsafe_allow_html=True,
)


# --- FUNCIÓN DE CONEXIÓN A GOOGLE SHEETS ---
def conectar_sheet(num_pestana):
    try:
        json_key = st.secrets["gcp_service_account"]["json_key"]
        info = json.loads(json_key, strict=False)
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(info, scopes=scope)
        client = gspread.authorize(creds)
        ID_PLANILLA = "1lrC5SJmWmpN5KIVRAlYbQk7AXVsb7NK0bZwMKQ4rU_E"
        spreadsheet = client.open_by_key(ID_PLANILLA)
        return spreadsheet.get_worksheet(num_pestana)
    except Exception as e:
        return None


# =========================================================
# ⚽ 2. CRONOGRAMA DE PARTIDOS FINALES (3er Puesto y Final)
# =========================================================
partidos_finales = [
    {
        "id": "3puesto",
        "tipo": "🥉 Tercer Puesto",
        "loc": "Francia",
        "sigla_l": "FRA",
        "vis": "Inglaterra",
        "sigla_v": "ENG",
        "detalles": "Sáb 18, Jul - 18:00 hs | Miami Stadium"
    },
    {
        "id": "final",
        "tipo": "👑 Gran Final",
        "loc": "España",
        "sigla_l": "ESP",
        "vis": "Argentina",
        "sigla_v": "ARG",
        "detalles": "Dom 19, Jul - 16:00 hs | New York New Jersey Stadium"
    },
]

# PESTAÑAS PRINCIPALES DEL SISTEMA
tab_voto, tab_ranking, tab_antiguos = st.tabs([
    "⚽ Cargar Pronósticos (Finales)",
    "📊 Tabla de Posiciones Acumulada",
    "🏅 Top 10 Primera Ronda",
])

# --- 1. PESTAÑA DE CARGA ---
with tab_voto:
    espacio_izq, col_central, espacio_der = st.columns([1, 2.8, 1])
    with col_central:
        if PRONOSTICOS_BLOQUEADOS:
            st.error("🚫 **¡LAS APUESTAS ESTÁN CERRADAS!**")
            st.info("El partido ya comenzó y el tiempo límite de carga ha expirado.")
        else:
            st.markdown(
                "<div style='background-color: #1E3A8A; padding: 10px; border-radius: 5px; margin-bottom: 15px;'><h3 style='color: white; margin: 0; font-size: 18px;'>👤 1. Tus Datos Personales</h3></div>",
                unsafe_allow_html=True,
            )
            c1, c2 = st.columns(2)
            with c1:
                nombre = st.text_input(
                    "Apellido y Name",
                    placeholder="Ej: Perez, Juan",
                    disabled=PRONOSTICOS_BLOQUEADOS,
                )
            with c2:
                legajo = st.text_input(
                    "Legajo",
                    placeholder="Tu número de legajo",
                    disabled=PRONOSTICOS_BLOQUEADOS,
                )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                "<div style='background-color: #1E3A8A; padding: 10px; border-radius: 5px; margin-bottom: 5px;'><h3 style='color: white; margin: 0; font-size: 18px;'>🔮 2. Pronósticos de la Etapa Final</h3></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<p style='color: #64748B; font-size: 14px; margin-bottom: 15px;'>Completá los últimos 2 partidos correspondientes al podio del torneo.</p>",
                unsafe_allow_html=True,
            )

            if "votos_finales" not in st.session_state:
                st.session_state.votos_finales = {}

            for idx, partido in enumerate(partidos_finales):
                loc, vis = partido["loc"], partido["vis"]
                s_L, s_V = partido["sigla_l"], partido["sigla_v"]
                detalles = partido["detalles"]
                tipo_partido = partido["tipo"]
                clave = f"finales_{partido['id']}"

                with st.container(border=True):
                    st.markdown(
                        f"<p style='margin:0; color:#1E3A8A; font-weight: bold;'>{tipo_partido}: {loc} vs. {vis}</p>"
                        f"<p style='margin:0; color:#64748B; font-size: 12px; font-style: italic;'>{detalles}</p>",
                        unsafe_allow_html=True,
                    )
                    opciones = [
                        "Sin seleccionar",
                        f"[{s_L}] Gana {loc}",
                        "🤝 Empate (90 min + Alargue)",
                        f"[{s_V}] Gana {vis}",
                    ]

                    default_idx = (
                        opciones.index(st.session_state.votos_finales[clave])
                        if clave in st.session_state.votos_finales
                        else 0
                    )

                    seleccion = st.radio(
                        label=f"Opciones_{clave}",
                        options=opciones,
                        index=default_idx,
                        horizontal=True,
                        label_visibility="collapsed",
                        key=f"radio_{clave}",
                        disabled=PRONOSTICOS_BLOQUEADOS,
                    )
                    st.session_state.votos_finales[clave] = seleccion

            st.markdown("---")

            if not PRONOSTICOS_BLOQUEADOS:
                enviado = st.button(
                    "🚀 ENVIAR PRONÓSTICOS FINALES",
                    use_container_width=True,
                    type="primary",
                )

                if enviado:
                    if nombre.strip() == "" or legajo.strip() == "":
                        st.error(
                            "🚫 Error: Por favor, ingresá tu Nombre y tu Legajo."
                        )
                    else:
                        incompletos = False
                        for partido in partidos_finales:
                            if (
                                st.session_state.votos_finales.get(
                                    f"finales_{partido['id']}", "Sin seleccionar"
                                )
                                == "Sin seleccionar"
                            ):
                                incompletos = True
                                break

                        if incompletos:
                            st.error(
                                "⚠️ ¡Faltan completar partidos! Revisá que todos los cruces tengan una opción seleccionada."
                            )
                        else:
                            with st.spinner(
                                "Guardando en la pestaña de Finales..."
                            ):
                                hoja = conectar_sheet(5)  
                                if hoja:
                                    nueva_fila = [
                                        datetime.now().strftime(
                                            "%d/%m/%Y %H:%M:%S"
                                        ),
                                        nombre.strip(),
                                        legajo.strip(),
                                    ]

                                    for partido in partidos_finales:
                                        nueva_fila.append(
                                            st.session_state.votos_finales[
                                                f"finales_{partido['id']}"
                                            ]
                                        )

                                    try:
                                        hoja.append_row(nueva_fila)
                                        st.balloons()
                                        st.success(
                                            "✅ ¡Tus pronósticos finales fueron guardados con éxito!"
                                        )
                                        st.session_state.votos_finales = {}
                                    except Exception as e:
                                        st.error(
                                            f"Error al escribir en la planilla: {e}"
                                        )
                                else:
                                    st.error("No se pudo conectar a la pestaña 'FINALES'. Verificá que el orden de las pestañas sea correcto.")

# --- PROCESAMIENTO UNIFICADO DE RANKING POR LEGAJO ---
dict_acumulado = {}
fases = [
    {"num": 1, "nombre_fase": "16avos"},
    {"num": 2, "nombre_fase": "8vos"},
    {"num": 3, "nombre_fase": "4tos"},
    {"num": 4, "nombre_fase": "semis"},
    {"num": 5, "nombre_fase": "FINALES"},
]

for fase in fases:
    try:
        hoja = conectar_sheet(fase["num"])
        if hoja:
            # Usamos get_all_values() para evitar fallos por títulos vacíos o duplicados en las hojas
            datos_crudos = hoja.get_all_values()
            if len(datos_crudos) > 1:
                columnas = [c.strip() for c in datos_crudos[0]]
                df_fase = pd.DataFrame(datos_crudos[1:], columns=columnas)

                # Buscar la fila de resultados oficiales sin importar mayúsculas
                mascara_oficial = df_fase["Apellido y Nombre"].str.upper().str.contains("RESULTADOS OFICIALES", na=False)
                df_jugadores = df_fase[~mascara_oficial]

                if mascara_oficial.any():
                    res_oficial = df_fase[mascara_oficial].iloc[0]
                    columnas_pred = columnas[3:]

                    for _, fila in df_jugadores.iterrows():
                        # Extraer y limpiar el legajo como identificador clave
                        leg = str(fila.get("Legajo", "")).strip().split(".")[0]
                        if not leg or leg == "nan" or leg == "0" or leg == "":
                            continue

                        puntos_fase = 0
                        for col in columnas_pred:
                            # Ignorar columnas vacías generadas al final de la hoja por celdas fantasmas
                            if col == "" or "Unnamed" in col or col.startswith("//"):
                                continue

                            val_oficial = str(res_oficial.get(col, "")).strip().lower()
                            val_jugador = str(fila.get(col, "")).strip().lower()

                            if val_oficial != "" and val_oficial == val_jugador:
                                puntos_fase += 3

                        nombre_limpio = fila["Apellido y Nombre"].strip().title()
                        if leg in dict_acumulado:
                            dict_acumulado[leg]["Puntos"] += puntos_fase
                            # Si un nombre viene más completo en otra pestaña, lo actualiza
                            if len(nombre_limpio) > len(dict_acumulado[leg]["Nombre"]):
                                dict_acumulado[leg]["Nombre"] = nombre_limpio
                        else:
                            dict_acumulado[leg] = {
                                "Nombre": nombre_limpio,
                                "Puntos": puntos_fase,
                            }
    except Exception as e:
        pass


# --- 2. PESTAÑA DE RANKING ACUMULADO ---
with tab_ranking:
    if dict_acumulado:
        lista_ranking = [
            {
                "Colaborador": v["Nombre"],
                "Legajo": k,
                "Puntos Totales": v["Puntos"],
            }
            for k, v in dict_acumulado.items()
        ]
        
        df_rank_total = pd.DataFrame(lista_ranking).sort_values(
            by="Puntos Totales", ascending=False
        )
        
        # Asignación estética y matemática de los puestos en orden consecutivo
        df_rank_total.index = range(1, len(df_rank_total) + 1)
        df_rank_total.index.name = "Puesto"
        df_rank_total = df_rank_total.reset_index()

        st.markdown(
            "<h3 style='color: #1E3A8A; text-align: center;'>🏆 Tabla de Posiciones Acumulada (Fase Eliminatoria)</h3>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='color: #64748B; text-align: center; font-size: 14px; margin-bottom: 25px;'>Suma total acumulada de los puntos obtenidos en las fases eliminatorias.</p>",
            unsafe_allow_html=True,
        )

        def destacar_top3(row):
            if row["Puesto"] <= 3:
                return [
                    "background-color: #D0E1F9; color: #1E3A8A; font-weight: bold;"
                ] * len(row)
            return [""] * len(row)

        st.dataframe(
            df_rank_total.style.apply(destacar_top3, axis=1),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("💡 Aún no se registraron jugadas en esta etapa acumulativa.")

# --- 3. HISTORIAL TOP 10 (Fase de grupos original - Índice 0) ---
with tab_antiguos:
    st.markdown(
        "<h3 style='color: #1E3A8A; text-align: center;'>📊 Top 10 Definitivo - Fase de Grupos</h3>",
        unsafe_allow_html=True,
    )
    try:
        hoja_vieja = conectar_sheet(0)
        df_viejo = pd.DataFrame(hoja_vieja.get_all_records())
        if not df_viejo.empty:
            df_viejo.columns = df_viejo.columns.str.strip()
            mascara_oficial_viejos = df_viejo['Apellido y Nombre'].str.contains(
                "RESULTADOS OFICIALES", na=False
            )

            if mascara_oficial_viejos.any():
                resultados_reales_viejos = df_viejo[
                    mascara_oficial_viejos
                ].iloc[0]
                df_jugadores_viejos = df_viejo[~mascara_oficial_viejos]
                ranking_viejo = []

                for _, fila in df_jugadores_viejos.iterrows():
                    puntos = 0
                    for col in df_viejo.columns[3:]:
                        if (
                            col in resultados_reales_viejos
                            and fila[col] == resultados_reales_viejos[col]
                            and fila[col] != ""
                        ):
                            puntos += 3
                    ranking_viejo.append({
                        "Colaborador": fila["Apellido y Nombre"],
                        "Legajo": fila["Legajo"],
                        "Puntos": puntos,
                    })

                if ranking_viejo:
                    df_rank_viejo = pd.DataFrame(ranking_viejo).sort_values(
                        by="Puntos", ascending=False
                    )
                    df_rank_viejo.index = range(1, len(df_rank_viejo) + 1)
                    df_rank_viejo.index.name = "Puesto"
                    st.dataframe(
                        df_rank_viejo.head(10).reset_index(),
                        use_container_width=True,
                        hide_index=True,
                    )
    except Exception as e:
        st.error(f"No se pudo cargar el historial: {e}")
