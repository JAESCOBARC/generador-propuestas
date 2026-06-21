import streamlit as st
import google.generativeai as genai
import json
import os
import base64
from pathlib import Path

LOGO_FILE = Path(__file__).parent / "logo.svg"
logo_svg = LOGO_FILE.read_text(encoding="utf-8") if LOGO_FILE.exists() else ""
logo_b64 = base64.b64encode(logo_svg.encode()).decode() if logo_svg else ""

st.set_page_config(
    page_title="Generador de Propuestas",
    page_icon=f"data:image/svg+xml;base64,{logo_b64}" if logo_b64 else "📝",
    layout="wide"
)

CONFIG_FILE = Path(__file__).parent / "config.json"

def cargar_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def guardar_config(data: dict):
    CONFIG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

cfg = cargar_config()

# API key: config.json (local) → variable de entorno (Render) → vacío
api_key_default = cfg.get("api_key") or os.environ.get("GOOGLE_API_KEY", "")

# ─── Sidebar: API key + perfil profesional ───────────────────────────────────
with st.sidebar:
    if logo_svg:
        st.markdown(
            f'<div style="text-align:center;margin-bottom:8px">'
            f'<img src="data:image/svg+xml;base64,{logo_b64}" width="64"/>'
            f'</div>',
            unsafe_allow_html=True
        )
    st.title("⚙️ Configuración")

    api_key = st.text_input(
        "🔑 Google AI API Key",
        value=api_key_default,
        type="password",
        placeholder="AIza...",
        help="Obtén tu clave GRATIS en aistudio.google.com → Get API key"
    )

    st.divider()

    st.subheader("👤 Tu Perfil Profesional")
    st.caption("Esta información personaliza cada propuesta.")

    nombre      = st.text_input("Nombre completo", value=cfg.get("nombre", ""), placeholder="Ej: María García")
    profesion   = st.text_input("Profesión / Rol", value=cfg.get("profesion", ""), placeholder="Ej: Data Analyst, Diseñador Web...")
    experiencia = st.slider("Años de experiencia", 0, 30, cfg.get("experiencia", 1))
    habilidades = st.text_area(
        "Habilidades principales",
        value=cfg.get("habilidades", ""),
        placeholder="Ej: Python, Power BI, SQL, Machine Learning, Excel...",
        height=100
    )
    descripcion = st.text_area(
        "Tu propuesta de valor",
        value=cfg.get("descripcion", ""),
        placeholder="¿Qué te diferencia? Logros relevantes, tipo de proyectos en los que destacas...",
        height=120
    )
    idiomas   = st.text_input("Idiomas", value=cfg.get("idiomas", ""), placeholder="Ej: Español (nativo), Inglés (B2)")
    portfolio = st.text_input("Portfolio / LinkedIn (opcional)", value=cfg.get("portfolio", ""), placeholder="https://...")

    if st.button("💾 Guardar configuración", use_container_width=True):
        guardar_config({
            "api_key":     api_key,
            "nombre":      nombre,
            "profesion":   profesion,
            "experiencia": experiencia,
            "habilidades": habilidades,
            "descripcion": descripcion,
            "idiomas":     idiomas,
            "portfolio":   portfolio,
        })
        st.success("✅ ¡Guardado!")

# ─── Main: solicitud del cliente ─────────────────────────────────────────────
st.title("📝 Generador de Propuestas Profesionales")
st.markdown("Pega la solicitud del cliente y obtén una propuesta personalizada lista para enviar.")

if not (nombre and profesion and habilidades and descripcion):
    st.info("💡 Completa tu perfil en el panel izquierdo para obtener propuestas más personalizadas.")

st.subheader("📋 Solicitud del cliente")
solicitud = st.text_area(
    "solicitud",
    height=250,
    placeholder="Pega aquí el texto de la oferta, solicitud de trabajo o descripción del proyecto del cliente...",
    label_visibility="collapsed"
)

col1, _ = st.columns([1, 4])
with col1:
    tono = st.selectbox(
        "Tono",
        ["Profesional y cercano", "Formal y ejecutivo", "Dinámico y creativo"],
    )

generar = st.button("✨ Generar propuesta", type="primary")

# ─── Generación ──────────────────────────────────────────────────────────────
if generar:
    if not api_key:
        st.error("❌ Ingresa tu API Key de Google AI en el panel izquierdo.")
        st.stop()
    if not solicitud.strip():
        st.error("❌ Pega la solicitud del cliente antes de generar.")
        st.stop()

    # Construir bloque de perfil
    lineas = []
    if nombre:        lineas.append(f"- Nombre: {nombre}")
    if profesion:     lineas.append(f"- Profesión / Rol: {profesion}")
    if experiencia:   lineas.append(f"- Años de experiencia: {experiencia}")
    if habilidades:   lineas.append(f"- Habilidades: {habilidades}")
    if descripcion:   lineas.append(f"- Propuesta de valor: {descripcion}")
    if idiomas:       lineas.append(f"- Idiomas: {idiomas}")
    if portfolio:     lineas.append(f"- Portfolio / LinkedIn: {portfolio}")

    perfil_texto = (
        "\n".join(lineas) if lineas
        else "El profesional no ha completado su perfil aún."
    )

    tono_map = {
        "Profesional y cercano": "Usa un tono profesional pero humano y cercano. Evita ser frío o demasiado formal.",
        "Formal y ejecutivo":    "Usa un tono formal, corporativo y orientado a resultados. Directo y ejecutivo.",
        "Dinámico y creativo":   "Usa un tono energético y entusiasta. Muestra pasión y dinamismo genuinos.",
    }

    system_prompt = f"""Eres un experto en redacción de propuestas profesionales para freelancers y consultores independientes.

Tu tarea es redactar la propuesta que el profesional enviará al cliente. Debe sentirse como si el profesional se tomó unos minutos reales para escribirla — no como una propuesta genérica copiada y pegada.

PERFIL DEL PROFESIONAL:
{perfil_texto}

INSTRUCCIONES PARA REDACTAR LA PROPUESTA:

1. PERSONALIZACIÓN REAL
   El cliente debe sentir que esta propuesta fue escrita específicamente para él y su proyecto, no que es una plantilla enviada a cien personas. Menciona detalles concretos de su solicitud que demuestren que la leíste con atención.

2. SÍNTESIS DE CAPACIDADES Y EXPERIENCIA
   Haz un breve resumen de las capacidades y experiencia del profesional, destacando únicamente aquellas que resulten clave para este proyecto específico. No enumeres todo el perfil — selecciona lo que es realmente relevante.

3. ADAPTA LA PROPUESTA A ESTA BÚSQUEDA EN PARTICULAR
   Aunque el profesional pueda tener una propuesta tipo, esta debe estar completamente adaptada a lo que el cliente está pidiendo. Cada propuesta es única.

4. CLARIDAD Y DIFERENCIACIÓN
   Expresa claramente cuál sería el aporte del profesional ante la necesidad del cliente. De modo concreto y profesional: qué lo diferencia del resto y por qué es la persona correcta para este proyecto.

5. DISPONIBILIDAD E INTERÉS GENUINO
   El cliente quiere colaboradores con pasión y compromiso. La propuesta debe transmitir:
   - Por qué el profesional quiere llevar adelante este proyecto en particular
   - Por qué es clave que el cliente lo elija a él y no a otro
   - Que está disponible para responder todas las consultas que el cliente tenga

6. RESPONDE LAS PREGUNTAS Y REQUERIMIENTOS DEL CLIENTE
   Si el cliente hizo preguntas específicas o mencionó requerimientos de información, respóndelos directamente en la propuesta. Muchos clientes descartan propuestas que no responden sus preguntas. No hace falta extenderse, solo responder de forma concreta.

7. REVISIÓN FINAL IMPLÍCITA
   La propuesta debe estar libre de errores ortográficos, gramaticales y de puntuación. Sin repeticiones. Sin comprometerse con algo que no se pueda cumplir. Sin prometer algo que luego no se pueda cotizar o ejecutar.

TONO: {tono_map[tono]}

FORMATO DE SALIDA:
- Escribe la propuesta directamente. Sin títulos, sin "Aquí tienes tu propuesta:", sin ningún meta-comentario tuyo.
- 3 a 4 párrafos fluidos y concisos. Evita listas con viñetas salvo que sea estrictamente necesario.
- Que se lea como un mensaje personal y directo al cliente, listo para copiar y pegar tal cual.
- Si el perfil del profesional está incompleto, genera igualmente la mejor propuesta posible con la información disponible."""

    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=2048,
                temperature=0.75,
            ),
        )

        st.divider()
        st.subheader("📄 Tu propuesta")
        placeholder = st.empty()
        propuesta = ""

        with st.spinner("Generando tu propuesta..."):
            response = model.generate_content(
                f"Solicitud del cliente:\n\n{solicitud}",
                stream=True,
            )
            for chunk in response:
                if chunk.text:
                    propuesta += chunk.text
                    placeholder.markdown(propuesta + "▌")

        placeholder.markdown(propuesta)

        st.text_area(
            "📋 Copia tu propuesta desde aquí:",
            value=propuesta,
            height=300,
            help="Selecciona todo (Ctrl+A) y copia (Ctrl+C)"
        )
        st.success("✅ ¡Propuesta lista! Revísala y envíala.")

    except Exception as e:
        st.error(f"❌ Error: {e}")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.caption("💡 Revisa siempre la propuesta antes de enviarla al cliente.")
