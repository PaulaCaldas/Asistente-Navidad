import streamlit as st
from openai import OpenAI
import PyPDF2
from PIL import Image
import base64
import io

import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# 🎨 ESTILOS (FONDO NUDE + CHAT BONITO)
st.markdown("""
<style>
.stApp {
    background-color: #A48374;
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
</style>
""", unsafe_allow_html=True)

# 🎄 TÍTULO PERSONALIZADO
st.title("✨ Tu mano derecha para crear Navidad")
st.write("Tu asistente creativo para conceptos, storytelling y diseño navideño en centros comerciales.")

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

OBJETIVO:

Desarrollar propuestas creativas adaptadas a cada cliente, manteniendo criterio profesional, coherencia conceptual y calidad visual.
"""
# 🧠 MEMORIA
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

# 📎 EXPANDER PARA ARCHIVOS
with st.expander("📎 Adjuntar archivos del proyecto"):

    # 📄 PDF
    uploaded_pdf = st.file_uploader("📄 Sube tu brief en PDF", type="pdf")

    pdf_text = ""
    if uploaded_pdf:
        reader = PyPDF2.PdfReader(uploaded_pdf)
        for page in reader.pages:
            pdf_text += page.extract_text()

    # 🖼 IMAGEN
    uploaded_image = st.file_uploader("🖼 Sube una imagen (fachada, vacío, referencia)", type=["png","jpg","jpeg"])

    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Referencia cargada", use_column_width=True)

# 💬 MOSTRAR CHAT
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])

# ✍️ INPUT USUARIO
user_input = st.chat_input("💬 Hola… ¿cómo vamos a comenzar esta nueva Navidad?")

if user_input:

    # Mostrar input
    st.chat_message("user").write(user_input)

    # Construir prompt completo
    image_note = ""

    if uploaded_image:
        image_note = """
El usuario subió una imagen del espacio.

Analiza como diseñador:
- identifica si es fachada, vacío o interior
- propone intervención con iluminación, icicle, composición
- sé específico (no genérico)
"""

    full_prompt = f"""
Usuario dice:
{user_input}

--- CONTEXTO DEL PROYECTO ---

Contenido del PDF:
{pdf_text}

{image_note}

--- INSTRUCCIONES ---

Actúa como director creativo experto en diseño navideño.

Si hay PDF:
- analiza el brief
- define dirección creativa

Si hay imagen:
- propone intervención clara en el espacio

Responde con propuesta clara, aplicable y profesional.
"""

    st.session_state.messages.append({"role": "user", "content": user_input})

 # --- PROCESAR IMAGEN ---
    image_content = None

    if uploaded_image:
        uploaded_image.seek(0)
        image_bytes = uploaded_image.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        image_content = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{image_base64}"
            }
        }

    # --- CONSTRUIR MENSAJE ---
    user_message = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": full_prompt
            }
        ]
    }

    if image_content:
        user_message["content"].append(image_content)

    # --- LLAMADO ---
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            user_message
        ]
    )

    reply = response.choices[0].message.content

    st.chat_message("assistant").write(reply)
st.session_state.messages.append({"role": "assistant", "content": reply})
try:
    image_prompt = f"""
Render arquitectónico navideño profesional para centro comercial.

Basado en esta propuesta:
{reply}

Debe incluir:
- iluminación navideña realista
- uso de icicle y cortinas de luz si aplica
- composición atractiva
- estilo render tipo Keyshot
- ambiente comercial

Alta calidad, sin texto.
"""

    img = client.images.generate(
        model="gpt-image-1",
        prompt=image_prompt,
        size="1024x1024"
    )

    image_base64 = img.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    st.image(image_bytes, caption="Propuesta visual generada", use_container_width=True)

except Exception as e:
    st.write("")  # no muestra nada
