#!/usr/bin/env python
# coding: utf-8

# In[1]:

import streamlit as st
import json
import random
import re
from collections import defaultdict

# Selección de tema y archivos correspondientes
temas = {
    "Todas": "preguntas.json",
    "Protección Radiológica": "preguntas_proteccion_radiologica.json",
    "Dosimetría Física": "preguntas_dosimetria_fisica.json",
    "Radiobiología": "preguntas_radiobiologia.json",
    "Radioterapia": "preguntas_radioterapia.json",
    "Medicina Nuclear": "preguntas_medicina_nuclear.json",
    "Protones": "preguntas_protones.json",
    "Temario Comun": "preguntas_comunes.json",
    "Resto": "preguntas_resto.json",
    "Problemas numéricos": "preguntas_numericas.json",
}

tema_elegido = st.selectbox("Selecciona un tema:", list(temas.keys()))

# Cargar las preguntas desde el archivo correspondiente al tema
with open(temas[tema_elegido], 'r', encoding='utf-8') as f:
    preguntas_dict = json.load(f)
    todas_las_claves = list(preguntas_dict.keys())

# Inicializar el estado de la sesión
if 'preguntas_mostradas' not in st.session_state:
    st.session_state.preguntas_mostradas = []

if 'estadisticas' not in st.session_state:
    st.session_state.estadisticas = defaultdict(int)

if 'current_question' not in st.session_state:
    st.session_state.current_question = None
    st.session_state.show_answer = False
    st.session_state.selected_option = None

# Función para obtener nombre del examen desde el ID de pregunta
def extraer_nombre_examen(id_pregunta):
    index = id_pregunta.find("_pregunta")
    if index != -1:
        return id_pregunta[:index]
    return id_pregunta

# Función para obtener una pregunta aleatoria que no se haya mostrado todavía
def get_random_question():
    preguntas_restantes = list(set(todas_las_claves) - set(st.session_state.preguntas_mostradas))
    if not preguntas_restantes:
        return None, None
    key = random.choice(preguntas_restantes)
    pregunta = preguntas_dict[key]
    st.session_state.preguntas_mostradas.append(key)
    examen = extraer_nombre_examen(key)
    st.session_state.estadisticas[examen] += 1
    return key, pregunta

# Botón para reiniciar preguntas
if st.button("🔄 Reiniciar preguntas"):
    st.session_state.preguntas_mostradas = []
    st.session_state.estadisticas = defaultdict(int)
    st.session_state.current_question = None
    st.session_state.selected_option = None
    st.session_state.show_answer = False
    st.rerun()

# Botón para mostrar estadísticas
if st.button("📊 Estadísticas"):
    st.subheader("Preguntas mostradas por examen")
    if st.session_state.estadisticas:
        for examen, cuenta in sorted(st.session_state.estadisticas.items()):
            st.write(f"- **{examen}**: {cuenta} pregunta(s)")
    else:
        st.info("Aún no se ha mostrado ninguna pregunta.")

# Obtener nueva pregunta si no hay ninguna activa
if st.session_state.current_question is None:
    key, pregunta = get_random_question()
    if pregunta is None:
        st.warning("Ya se han mostrado todas las preguntas.")
    else:
        st.session_state.current_question = (key, pregunta)
else:
    key, pregunta = st.session_state.current_question

st.title("Aplicación de Preguntas Tipo Test")

# Mostrar progreso
total = len(todas_las_claves)
respondidas = len(st.session_state.preguntas_mostradas)
st.markdown(f"**Progreso:** {respondidas} de {total} preguntas respondidas")

# Si quedan preguntas, mostrar contenido
if pregunta:
    st.markdown(f"<div style='font-size: 20px'>{pregunta['pregunta']}</div>", unsafe_allow_html=True)

    opciones = [f"{opcion}) {texto}" for opcion, texto in pregunta['opciones'].items()]
    st.session_state.selected_option = st.radio(
        "Selecciona una opción:",
        opciones,
        index=opciones.index(st.session_state.selected_option) if st.session_state.selected_option else 0
    )

    if st.button("Comprobar respuesta"):
        respuesta_correcta = pregunta['respuesta_correcta']
        texto_correcto = f"{respuesta_correcta}) {pregunta['opciones'][respuesta_correcta]}"
        if st.session_state.selected_option == texto_correcto:
            st.success("¡Correcto!")
        else:
            st.error(f"Incorrecto. La respuesta correcta es: {texto_correcto}")
        st.session_state.show_answer = True

    if st.button("Siguiente pregunta"):
        key, pregunta = get_random_question()
        if pregunta is None:
            st.warning("Ya se han mostrado todas las preguntas.")
            st.session_state.current_question = None
        else:
            st.session_state.current_question = (key, pregunta)
            st.session_state.show_answer = False
            st.session_state.selected_option = None
        st.rerun()

    if st.button("Mostrar información"):
        st.info(f"ID de la pregunta: {key}")

    st.write("Respuesta mostrada" if st.session_state.show_answer else "Responda la pregunta")
else:
    st.info("Haz clic en 'Reiniciar preguntas' para empezar de nuevo.")

