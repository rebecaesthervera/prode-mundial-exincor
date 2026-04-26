import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA (Layout 'wide' para tener más espacio, pero centraremos el contenido)
st.set_page_config(page_title="Prode Exincor 2026", page_icon="🏆", layout="wide")

# 2. DICCIONARIOS DE DATOS
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

# Diccionario de banderas para darle color a la app
banderas = {
    "México": "🇲🇽", "Sudáfrica": "🇿🇦", "Corea del Sur": "🇰🇷", "Rep. Checa": "🇨🇿",
    "Canadá": "🇨🇦", "Bosnia": "🇧🇦", "Qatar": "🇶🇦", "Suiza": "🇨🇭",
    "Brasil": "🇧🇷", "Marruecos": "🇲🇦", "Haití": "🇭🇹", "Escocia": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "EE. UU.": "🇺🇸", "Turquía": "🇹🇷", "Australia": "🇦🇺", "Paraguay": "🇵🇾",
    "Alemania": "🇩🇪", "Curazao": "🇨🇼", "C. Marfil": "🇨🇮", "Ecuador": "🇪🇨",
    "P. Bajos": "🇳🇱", "Japón": "🇯🇵", "Suecia": "🇸🇪", "Túnez": "🇹🇳",
    "Bélgica": "🇧🇪", "Egipto": "🇪🇬", "Irán": "🇮🇷", "N. Zelanda": "🇳🇿",
    "España": "🇪🇸", "C. Verde": "🇨🇻", "Arabia S.": "🇸🇦", "Uruguay": "🇺🇾",
    "Francia": "🇫🇷", "Senegal": "🇸🇳", "Irak": "🇮🇶", "Noruega": "🇳🇴",
    "Austria": "🇦🇹", "Jordania": "🇯🇴", "Argentina": "🇦🇷", "Argelia": "🇩🇿",
    "Portugal": "🇵🇹", "RD Congo": "🇨🇩", "Uzbekistán": "🇺🇿", "Colombia": "🇨🇴",
    "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Croacia": "🇭🇷", "Ghana": "🇬🇭", "Panamá": "🇵🇦"
}

def generar_partidos(equipos):
    return [
        (equipos[0], equipos[1]), (equipos[2], equipos[3]),
        (equipos[0], equipos[2]), (equipos[1], equipos[3]),
        (equipos[0], equipos[3]), (equipos[1], equipos[2])
    ]

# 3. INTERFAZ VISUAL
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏆 Prode Mundial 2026 - Exincor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Completa tus pronósticos para la fase de grupos. ¡Demuestra quién sabe más de fútbol en la oficina!</p>", unsafe_allow_html=True)
st.markdown("---")

# Usamos columnas para que el formulario no ocupe el 100% del monitor ancho, dejándolo centrado y legible.
espacio_izq, col_central, espacio_der = st.columns([1, 2, 1])

with col_central:
    with st.form("formulario_prode"):
        st.subheader("👤 Tus Datos")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Apellido y Nombre", placeholder="Ej: Perez, Juan")
        with col2:
            legajo = st.text_input("Legajo", placeholder="Tu número de legajo")
            
        st.markdown("---")
        st.subheader("⚽ Pronósticos de Fase de Grupos")
        
        nombres_grupos = list(grupos.keys())
        tabs = st.tabs(nombres_grupos)
        respuestas = {}
        
        for i, (nombre_grupo, equipos) in enumerate(grupos.items()):
            with tabs[i]:
                st.markdown(f"<h3 style='color:#1E3A8A;'>{nombre_grupo}</h3>", unsafe_allow_html=True)
                partidos = generar_partidos(equipos)
                
                for j, partido in enumerate(partidos):
                    local = partido[0]
                    visita = partido[1]
                    bandera_L = banderas.get(local, "🏳️")
                    bandera_V = banderas.get(visita, "🏳️")
                    
                    # AQUÍ ESTÁ LA MAGIA: El diseño de "Tarjeta"
                    with st.container(border=True):
                        st.markdown(f"<p style='text-align:center; color:#64748B; margin-bottom:5px; font-size:14px;'>Partido {j+1}</p>", unsafe_allow_html=True)
                        
                        clave_partido = f"{nombre_grupo}_Match_{j}"
                        # Las banderas van directo adentro de las opciones
                        opciones_voto = [f"{bandera_L} Gana {local}", "🤝 Empate", f"{bandera_V} Gana {visita}"]
                        
                        respuestas[clave_partido] = st.radio(
                            "Selecciona un resultado:",
                            options=opciones_voto,
                            horizontal=True,
                            label_visibility="collapsed",
                            key=clave_partido
                        )

        st.markdown("---")
        st.info("💡 Revisa todas las pestañas antes de enviar. ¡Mucha suerte!")
        enviado = st.form_submit_button("🚀 Enviar Mis Pronósticos", use_container_width=True)

# 4. LÓGICA DE ENVÍO
if enviado:
    if nombre == "" or legajo == "":
        st.error("⚠️ Por favor, completa tu Nombre y Legajo antes de enviar.")
    else:
        st.success(f"🎉 ¡Excelente {nombre}! Tus pronósticos están listos.")
        
        # Muestra de prueba: qué votó en el Grupo J
        st.write(f"**Tus predicciones para el Grupo de Argentina:**")
        for key, value in respuestas.items():
            if "Grupo J" in key:
                st.write(f"- {value}")
