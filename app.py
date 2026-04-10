import streamlit as st
from openai import OpenAI
import PyPDF2
from PIL import Image
import base64
import io
import pandas as pd
import json

HISTORY_FOLDER = "histories"

import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🎨 ESTILOS (FONDO NUDE + CHAT BONITO)
st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        120deg,
        #0b0b0b 0%,
        #1a1410 40%,
        #2a1f17 70%,
        #0a0a0a 100%
    );
}
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;

    background: radial-gradient(
        circle at 70% 30%,
        rgba(255, 200, 150, 0.06),
        transparent 40%
    );

    pointer-events: none;
}

/* Uploaders */
section[data-testid="stFileUploader"] {
    background-color: #F5EDE4;
    border: 1px solid #D6C1B1;
    border-radius: 12px;
}

/* Botón upload */
section[data-testid="stFileUploader"] button {
    background-color: #B08974;
    color: white;
    border-radius: 8px;
}

/* Texto dentro */
section[data-testid="stFileUploader"] {
    color: #333;
}
h1 {
    color: #3a2e2a;
}
.chat-placeholder {
    color: gray;
    font-style: italic;
}
.logo {
    font-family: 'Playfair Display', serif;
    font-size: 42px;
    font-weight: 500;
    letter-spacing: 4px;

    color: #f5f5f5;

    text-align: center;
    margin-bottom: 5px;

    text-shadow: 0 0 20px rgba(255, 210, 160, 0.15);

    /* 👇 AGREGA ESTO */
    opacity: 0;
    animation: fadeUp 1s ease forwards;
}
.subtitle {
    text-align: center;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    letter-spacing: 1px;
    color: rgba(255,255,255,0.6);
    margin-bottom: 30px;

    opacity: 0;
    animation: fadeUp 1.4s ease forwards;
}
/* 👇 animación */
[data-testid="stChatMessage"] {
    animation: fadeUp 0.5s ease;
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(15px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
/* CONTENEDOR GENERAL DEL CHAT */
[data-testid="stChatMessage"] {
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}

/* BURBUJA GENERAL */
[data-testid="stChatMessage"] > div {
    padding: 14px 18px;
    border-radius: 14px;
    margin-bottom: 10px;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    line-height: 1.5;
}

/* USUARIO (derecha) */
[data-testid="stChatMessage"][data-testid*="user"] > div {
    background: #d6c2a8;
    color: #1a1a1a;
    margin-left: auto;
    max-width: 70%;
}

/* ASISTENTE (izquierda) */
[data-testid="stChatMessage"][data-testid*="assistant"] > div {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255,255,255,0.08);
    color: #f1f1f1;
    margin-right: auto;
    max-width: 70%;
}

/* INPUT BOX */
[data-testid="stChatInput"] {
    border-radius: 12px;
}

/* TEXTO INPUT */
[data-testid="stChatInput"] textarea {
    background: rgba(255,255,255,0.05);
    color: #fff;
    border-radius: 10px;
}
/* SIDEBAR FONDO */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #0f0f0f 0%,
        #1a1410 100%
    );
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* TEXTO SIDEBAR */
section[data-testid="stSidebar"] * {
    color: #eaeaea;
    font-family: 'Inter', sans-serif;
}

/* SELECTBOX */
section[data-testid="stSidebar"] .stSelectbox {
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
}

/* INPUT */
section[data-testid="stSidebar"] input {
    background: rgba(255,255,255,0.05);
    color: white;
    border-radius: 8px;
}
/* ARREGLAR CAPAS */
* {
    position: relative;
    z-index: 1;
}

.stApp {
    position: relative;
    z-index: 0;
}
/* UPLOADER COMPACTO */
section[data-testid="stFileUploader"] {
    background: transparent;
    border: none;
}

/* BOTÓN */
section[data-testid="stFileUploader"] button {
    background: rgba(255,255,255,0.08);
    border-radius: 8px;
    height: 40px;
}

/* INPUT ALINEADO */
[data-testid="stChatInput"] {
    margin-top: -10px;
}
/* BOTONES PROYECTOS */
section[data-testid="stSidebar"] button {
    width: 100%;
    text-align: left;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 10px;
    margin-bottom: 6px;
    padding: 10px;

    transition: all 0.3s ease;
}

/* HOVER */
section[data-testid="stSidebar"] button:hover {
    background: rgba(255,255,255,0.08);
    transform: translateX(4px);
}

/* BOTÓN NUEVO */
section[data-testid="stSidebar"] button:first-child {
    background: #d6c2a8;
    color: #1a1a1a;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

# 🎄 TÍTULO PERSONALIZADO
st.markdown('<h1 class="logo">NIVARA</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Dirección creativa para experiencias navideñas en retail</p>',
    unsafe_allow_html=True
)

import os

# Crear carpeta si no existe
if not os.path.exists(HISTORY_FOLDER):
    os.makedirs(HISTORY_FOLDER)

# Lista de chats existentes
chat_files = [f.replace(".json","") for f in os.listdir(HISTORY_FOLDER)]

# ---------- SIDEBAR CORREGIDO ----------
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "nuevo"

with st.sidebar:

    st.markdown('<h2 class="logo">NIVARA</h2>', unsafe_allow_html=True)
    st.markdown("### Proyectos")

    # BOTÓN NUEVO
    if st.button("＋ Nuevo proyecto"):
        st.session_state.current_chat = "nuevo"
        st.session_state.messages = []

    # LISTA DE PROYECTOS
    for chat in chat_files:
        if st.button(chat, key=f"chat_{chat}"):
            st.session_state.current_chat = chat
            st.session_state.messages = []

    # NOMBRE DEL PROYECTO
    if st.session_state.current_chat == "nuevo":
        chat_name = st.text_input("Nombre del proyecto")
    else:
        chat_name = st.session_state.current_chat

# ---------- HISTORIAL ----------
if chat_name:
    HISTORY_FILE = f"{HISTORY_FOLDER}/{chat_name}.json"
else:
    HISTORY_FILE = None

# 🧠 SYSTEM (TU ADN)
system_prompt = """
Eres un director creativo senior especializado en diseño navideño para centros comerciales en Latinoamérica.

Trabajas bajo estándares reales de diseño para licitaciones comerciales, donde el objetivo es desarrollar propuestas visuales atractivas, coherentes y vendibles.

---

ENFOQUE PRINCIPAL:

No existe una única forma de diseñar Navidad.

Cada propuesta debe adaptarse al tipo de cliente, su público, su ubicación y su intención comercial.

Eres capaz de diseñar diferentes tipos de Navidad, como por ejemplo:

- Navidad elegante / premium (lujo, sobriedad, materiales refinados)
- Navidad tradicional (Santa, renos, rojo, verde, familiar)
- Navidad popular (colores vivos, elementos grandes, impacto visual)
- Navidad temática (hielo, fantasía, países del mundo, etc.)
- Navidad no tradicional (conceptual, abstracta o experiencial)

Siempre interpretas el brief antes de diseñar.

---

CRITERIOS CLAVE (SIEMPRE SE MANTIENEN):

1. TODO parte de un concepto.
Nada se diseña sin intención. Cada elemento tiene justificación.

2. COHERENCIA:
- No saturación sin sentido
- No mezcla de estilos sin control
- Todo responde a una narrativa

3. CALIDAD VISUAL:
- Debe verse como render profesional (Rhino + Keyshot + Photoshop)
- Pensado para presentación comercial
- Detalles cuidados

4. INSTAGRAMEABLE:
- Espacios pensados como photo opportunities
- Uso de composición (alturas, capas, elementos)
- Interacción real de personas
- Integración de marca

5. ERRORES A EVITAR:
- Muñecos mal diseñados
- Elementos sin concepto
- Mala escala
- Saturación visual sin intención

---

ILUMINACIÓN (REGLAS TÉCNICAS):

CORTINAS DE LUZ:
- Simulan caída vertical desde cable principal
- En render:
  - 40 cm separación estándar
  - 60–80 cm en fachadas grandes
  - 60 cm en vacíos
- No se representan cada 10–20 cm

ICICLE:
- Tiras verticales de 40 cm a 1 m (40-60-80 y 1 mt)
- Uso:
  - bordes superiores
  - barandas con vidrio
- NO se usan colgando en vacíos sin estructura
- Uso elegante y controlado

LUZ:
- Generalmente cálida (2700K–3000K)
- Puede variar según concepto (ej: hielo = luz fría)
- Siempre con intención

---

FORMA DE RESPONDER:

- Piensas como diseñador real
- No das respuestas genéricas
- Propones ideas aplicables
- Todo debe poder convertirse en diapositiva de presentación

---
CRITERIOS DE PRODUCCIÓN REAL (OBLIGATORIO):

Siempre propones materiales utilizados en producción escenográfica real, evitando soluciones básicas o escolares.

MATERIALES ESCENOGRÁFICOS PROFESIONALES:

Estructuras:
- acero estructural
- aluminio
- perfilería metálica

Volúmenes:
- fibra de vidrio
- icopor densificado con resina
- espuma rígida tallada (CNC)

Superficies:
- MDF lacado
- acrílico
- policarbonato
- PVC espumado

Acabados:
- pintura automotriz
- acabados metalizados
- escarchados profesionales
- vinilos de alta calidad

Textiles:
- telas tensadas
- lycra
- mallas translúcidas

Iluminación:
- LED programable
- neón flexible
- fibra óptica

Técnicas:
- corte CNC
- termoformado
- impresión gran formato
- pintura especializada

Siempre priorizar materiales durables, resistentes y aptos para instalación comercial.


Nunca propones:
- cartón simple
- papel común
- materiales frágiles o poco durables

Además:

- Consideras viabilidad constructiva
- Piensas en instalación real (anclajes, pesos, alturas)
- Sugieres rangos de costo (bajo, medio, alto)
- Diferencias entre propuesta económica vs premium

Cuando propongas elementos, incluye:

- material recomendado
- técnica de fabricación
- percepción de costo (bajo / medio / alto)

Tu enfoque es siempre comercial, vendible y ejecutable en un centro comercial real.


OBJETIVO:

Desarrollar propuestas creativas adaptadas a cada cliente, manteniendo criterio profesional, coherencia conceptual y calidad visual.
"""
# 🧠 MEMORIA
if "messages" not in st.session_state or not st.session_state.messages:

    if HISTORY_FILE and os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            st.session_state.messages = json.load(f)
    else:
        st.session_state.messages = [
            {"role": "system", "content": system_prompt}
        ]

    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Referencia cargada", use_column_width=True)

# 💬 MOSTRAR CHAT
for msg in st.session_state.messages[1:]:

    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])

    elif msg["role"] == "assistant":

        st.chat_message("assistant").write(msg["content"])

        # 🔥 mostrar imagen si existe
        if "image" in msg and msg["image"]:

            import base64

            try:
                img_bytes = base64.b64decode(msg["image"])
                st.image(img_bytes, use_container_width=True)
            except:
                st.warning("⚠️ Error cargando imagen guardada")
# 📄 PDF
uploaded_pdf = st.file_uploader("📄 Sube tu brief en PDF", type="pdf")

pdf_text = ""
if uploaded_pdf:
    reader = PyPDF2.PdfReader(uploaded_pdf)
    for page in reader.pages:
        pdf_text += page.extract_text()

# 🖼 IMÁGENES (MULTIPLE)
uploaded_files = st.file_uploader(
    "",
    type=["png","jpg","jpeg"],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

# 👀 PREVIEW
if uploaded_files:
    for file in uploaded_files:
        image = Image.open(file)
        st.image(image, width=120)
col1, col2 = st.columns([1, 8])

user_input = st.chat_input("Escribe aquí tu idea…")  
# ✍️ INPUT USUARIO

if user_input:

    # Mostrar mensaje usuario
    st.chat_message("user").write(user_input)

    # Guardar historial
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # -------- PROMPT --------
    image_note = ""

    # 🔹 CASO 1: DOS IMÁGENES
    if uploaded_files and len(uploaded_files) > 1:
        image_note = (
            "El usuario subió dos imágenes:\n"
            "1. Imagen del espacio\n"
            "2. Imagen de elementos decorativos\n\n"

            "OBLIGATORIO:\n\n"

            "1. Describe el espacio con precisión:\n"
            "- tipo (fachada, vacío, interior, escena)\n"
            "- cantidad de niveles o altura\n"
            "- elementos arquitectónicos visibles\n"
            "- proporciones del espacio\n\n"

            "2. Analiza cómo se comporta visualmente:\n"
            "- puntos focales\n"
            "- ejes visuales\n"
            "- zonas de mayor impacto\n\n"

            "3. Analiza los elementos decorativos:\n"
            "- tipo de elemento\n"
            "- material aparente\n"
            "- escala y proporción\n"
            "- estilo\n\n"

            "4. Propón la integración:\n"
            "- ubicación exacta\n"
            "- alturas específicas\n"
            "- densidad y distribución\n"
            "- relación con la arquitectura\n\n"

            "5. Justifica decisiones\n"
            "6. Usa lenguaje comercial\n"
            "7. Evita propuestas genéricas\n\n"

            "Responde como un pitch profesional."
        )

    # 🔹 CASO 2: SOLO ESPACIO
    elif uploaded_files:
        image_note = (
            "El usuario subió una imagen del espacio.\n\n"

            "OBLIGATORIO:\n\n"

            "1. Describe el espacio:\n"
            "- tipo\n"
            "- niveles\n"
            "- arquitectura\n"
            "- proporciones\n\n"

            "2. Analiza comportamiento visual:\n"
            "- puntos focales\n"
            "- ejes\n"
            "- impacto\n\n"

            "3. Propón intervención:\n"
            "- ubicación\n"
            "- alturas\n"
            "- distribución\n\n"

            "4. Justifica decisiones\n"
            "5. Lenguaje comercial\n"
            "6. Evita lo genérico\n\n"

            "Responde como diseñador profesional."
        )

    # 🔹 CASO 3: SIN IMÁGENES
    else:
        image_note = (
            "El usuario no subió imágenes.\n\n"

            "OBLIGATORIO:\n\n"

            "1. Pregunta que proyecto quiere revisar:\n"
            "- narrativa\n"
            "- estilo (tradicional, elegante, mágico, etc.)\n"
            "- intención del espacio\n\n"

            "Evita propuestas genéricas. Responde como diseñador experto."
        )

    # -------- FULL PROMPT --------
    full_prompt = (
        f"Usuario dice:\n{str(user_input)}\n\n"
        f"Contenido del PDF:\n{str(pdf_text)}\n\n"
        f"{image_note}\n\n"
        "Actúa como director creativo senior especializado en diseño navideño.\n"
        "No des ideas genéricas.\n"
        "Usa materiales reales.\n"
        "Justifica decisiones.\n"
    )

    # -------- IMÁGENES --------
    image_content = []

    if uploaded_files:
    for file in uploaded_files:
        file.seek(0)
        image_bytes = file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        image_content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{image_base64}"
            }
        })

    # -------- MENSAJE --------
    user_message = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": full_prompt
            }
        ]
    }

    for img in image_content:
        user_message["content"].append(img)

    # -------- CONTROL USO --------
    import time

    if "last_request" not in st.session_state:
        st.session_state.last_request = 0

    current_time = time.time()

    if current_time - st.session_state.last_request < 3:
        st.warning("⏳ Espera un momento antes de enviar otra solicitud")
        st.stop()

    st.session_state.last_request = current_time

    # -------- OPENAI --------
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                user_message
            ]
        )

        reply = ""
        if response and response.choices:
            reply = response.choices[0].message.content
        else:
            reply = "No se pudo generar respuesta"
            
        st.chat_message("assistant").write(reply)
        
        if HISTORY_FILE:
            with open(HISTORY_FILE, "w") as f:
                json.dump(st.session_state.messages, f)
                
    except Exception as e:
        st.error(f"Error: {e}")

    # -------- TABLAS --------
    if reply and "|" in reply:
        try:
            lines = reply.split("\n")
            table_lines = [line for line in lines if "|" in line]

            if len(table_lines) > 2:
                headers = table_lines[0].split("|")
                headers = [h.strip() for h in headers if h.strip()]

                data = []
                for row in table_lines[2:]:
                    cols = row.split("|")
                    cols = [c.strip() for c in cols if c.strip()]
                    if len(cols) == len(headers):
                        data.append(cols)

                df = pd.DataFrame(data, columns=headers)
                st.dataframe(df)

        except:
            pass


    # -------- GENERAR IMAGEN CON OPENAI --------
        # -------- GENERAR IMAGEN CON OPENAI --------
    try:
        image_prompt = f"""
Render hiperrealista de un centro comercial intervenido con decoración navideña.

Basado en este concepto:
{reply}

Incluir:
- iluminación cálida elegante (2700K–3000K)
- icicle en barandas con caída natural (40cm a 1m)
- cortinas de luz suspendidas en vacíos
- materiales premium (metal, vidrio, acrílico)
- integración arquitectónica realista
- proporciones correctas

Estilo:
render tipo fotografía profesional, iluminación cinematográfica, ultra realista.
"""

        image = client.images.generate(
            model="gpt-image-1",
            prompt=image_prompt,
            size="1024x1024"
        )

        # 🔥 VALIDACIÓN CLAVE
        if image and image.data and len(image.data) > 0:

            import base64

            img_base64 = image.data[0].b64_json
            img_bytes = base64.b64decode(img_base64)

            st.image(img_bytes, caption="Propuesta generada", use_container_width=True)

            # 🔥 GUARDAR MENSAJE + IMAGEN
            st.session_state.messages.append({
                "role": "assistant",
                "content": reply,
                "image": img_base64
            })

            # 🔥 GUARDAR EN ARCHIVO (AQUÍ, NO ANTES)
            if HISTORY_FILE:
                with open(HISTORY_FILE, "w") as f:
                    json.dump(st.session_state.messages, f)
            
        else:
            st.warning("⚠️ No se generó imagen")

    except Exception as e:
        st.error(f"Error generando imagen: {e}")
