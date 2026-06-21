import streamlit as st
import google.generativeai as genai
import json
from pathlib import Path

st.set_page_config(
    page_title="Generador de Propuestas",
    page_icon="📝",
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

# ─── Sidebar: API key + perfil profesional ───────────────────────────────────
with st.sidebar:
    st.title("⚙️ Configuración")

    api_key = st.text_input(
        "🔑 Google AI API Key",
        value=cfg.get("api_key", ""),
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

    system_prompt = f"""Eres un experto en redacción de propuestas profesionales ganadoras para freelancers y consultores.

Tu tarea: generar una propuesta convincente y personalizada para que el profesional la envíe al cliente.

PERFIL DEL PROFESIONAL:
{perfil_texto}

LINEAMIENTOS OBLIGATORIOS:
1. PERSONALIZACIÓN: Menciona detalles específicos del proyecto del cliente para demostrar que lo leíste. Si aparece el nombre del cliente, úsalo.
2. SÍNTESIS ESTRATÉGICA: Destaca solo las habilidades directamente relevantes para ESE proyecto; no enumeres todo el CV.
3. ADAPTACIÓN TOTAL: Cada párrafo debe responder a lo que el cliente pide. Cero plantillas genéricas.
4. PROPUESTA DE VALOR CLARA: Explica concretamente qué aportarás y por qué eres la persona idónea.
5. PASIÓN Y DISPONIBILIDAD: Demuestra interés genuino. Indica disponibilidad para comenzar o para hablar.
6. RESPONDE LAS PREGUNTAS: Si el cliente hizo preguntas o mencionó requisitos concretos, respóndelos directamente.
7. SIN ERRORES: Ortografía, gramática y puntuación perfectas. Sin repeticiones, sin clichés, sin promesas imposibles.

TONO: {tono_map[tono]}

FORMATO DE SALIDA:
- Escribe la propuesta directamente, sin títulos, sin "Aquí tienes tu propuesta:", sin meta-comentarios.
- Máximo 3-4 párrafos concisos. Evita listas con viñetas salvo que sea imprescindible.
- Debe leerse como un mensaje personal y directo al cliente, listo para copiar y pegar.
- Si el perfil está incompleto, genera igualmente la mejor propuesta posible con la información disponible."""

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
