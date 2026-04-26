import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Prode Exincor 2026", page_icon="🏆", layout="centered")

# 2. BASE DE DATOS DEL FIXTURE (Extraída del PDF)
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

# Función para generar los 6 partidos de un grupo (Todos contra Todos)
def generar_partidos(equipos):
    return [
        (equipos[0], equipos[1]), (equipos[2], equipos[3]),
        (equipos[0], equipos[2]), (equipos[1], equipos[3]),
        (equipos[0], equipos[3]), (equipos[1], equipos[2])
    ]

# 3. INTERFAZ VISUAL
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏆 Prode Mundial 2026 - Exincor</h1>", unsafe_allow_html=True)
st.write("Completa tus pronósticos para la fase de grupos. ¡Demuestra quién sabe más de fútbol en la oficina!")
st.markdown("---")

# Iniciamos el Formulario
with st.form("formulario_prode"):
    st.subheader("👤 Tus Datos")
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Apellido y Nombre", placeholder="Ej: Perez, Juan")
    with col2:
        legajo = st.text_input("Legajo", placeholder="Tu número de legajo")
        
    st.markdown("---")
    st.subheader("⚽ Pronósticos de Fase de Grupos")
    
    # Creamos las pestañas dinámicamente según el diccionario de grupos
    nombres_grupos = list(grupos.keys())
    tabs = st.tabs(nombres_grupos)
    
    # Diccionario para guardar las respuestas temporalmente antes de enviar
    respuestas = {}
    
    for i, (nombre_grupo, equipos) in enumerate(grupos.items()):
        with tabs[i]:
            st.markdown(f"### {nombre_grupo}")
            partidos = generar_partidos(equipos)
            
            for j, partido in enumerate(partidos):
                # Usamos columnas para darle formato de "Marcador"
                c_loc, c_res, c_vis = st.columns([2, 3, 2])
                
                with c_loc:
                    st.markdown(f"<p style='text-align:right; font-weight:bold; margin-top:10px;'>{partido[0]}</p>", unsafe_allow_html=True)
                
                with c_res:
                    # Guardamos la elección con un key único por partido
                    clave_partido = f"{nombre_grupo}_Match_{j}"
                    respuestas[clave_partido] = st.radio(
                        "Resultado",
                        options=[partido[0], "Empate", partido[1]],
                        horizontal=True,
                        label_visibility="collapsed",
                        key=clave_partido
                    )
                    
                with c_vis:
                    st.markdown(f"<p style='text-align:left; font-weight:bold; margin-top:10px;'>{partido[1]}</p>", unsafe_allow_html=True)
                
                st.write("") # Pequeño separador visual entre partidos

    st.markdown("---")
    # Botón de envío final
    enviado = st.form_submit_button("🚀 Enviar Mis Pronósticos", use_container_width=True)

# 4. LÓGICA DE ENVÍO (Simulada por ahora)
if enviado:
    if nombre == "" or legajo == "":
        st.error("⚠️ Por favor, completa tu Nombre y Legajo antes de enviar.")
    else:
        st.success(f"🎉 ¡Excelente {nombre}! Tus pronósticos se han guardado temporalmente en la pantalla.")
        st.info("Próximo paso: Conectar Google Cloud para que estos datos viajen al Sheet de RRHH.")
        
        # Opcional: Mostrarle al usuario un resumen de lo que votó en el grupo de Argentina
        st.write("**Tus votos para el Grupo de Argentina (Grupo J):**")
        for key, value in respuestas.items():
            if "Grupo J" in key:
                st.write(f"- {value}")
