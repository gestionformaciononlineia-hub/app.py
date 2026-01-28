import streamlit as st
import json
from datetime import datetime
import time
from pathlib import Path
import os
from dotenv import load_dotenv
import tempfile

# Cargar variables de entorno
load_dotenv()

import base64

# Función para convertir imagen a base64
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# Cargar configuración
def load_config():
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

def save_config(config):
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def render_admin_panel(config):
    st.title("⚙️ Panel de Configuración")
    
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False
        
    if not st.session_state.admin_logged_in:
        with st.form("login_admin"):
            password = st.text_input("Contraseña de administrador", type="password")
            submit = st.form_submit_button("Acceder")
            if submit:
                if password == config.get("theme", {}).get("admin_password", "admin"):
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta")
        return

    st.success("Acceso concedido")
    if st.button("Cerrar Sesión", key="admin_logout"):
        st.session_state.admin_logged_in = False
        st.rerun()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎨 Apariencia", "📝 Contenido", "🔌 APIs", "🚀 Despliegue", "🖼️ Imágenes"])
    
    with tab1:
        st.subheader("Colores y Estilo")
        col1, col2 = st.columns(2)
        with col1:
            new_p_color = st.color_picker("Color Primario", config["theme"]["primary_color"])
            new_bg_color = st.color_picker("Color de Fondo", config["theme"]["bg_color"])
        with col2:
            new_s_color = st.color_picker("Color Secundario", config["theme"]["secondary_color"])
            new_font = st.selectbox("Fuente Principal", ["Outfit", "Inter", "Roboto", "Open Sans", "Lato"], index=0)
            
        if st.button("Guardar Estilo"):
            config["theme"]["primary_color"] = new_p_color
            config["theme"]["secondary_color"] = new_s_color
            config["theme"]["bg_color"] = new_bg_color
            config["theme"]["font_family"] = new_font
            save_config(config)
            st.success("¡Estilo actualizado! Recarga la página.")
            st.rerun()

    with tab2:
        st.subheader("Ajustes de Texto")
        new_title = st.text_input("Título de la Sesión", config["content_section"]["modules"]["module1"]["title"])
        new_desc = st.text_area("Descripción de la Sesión", config["content_section"]["modules"]["module1"]["content"])
        
        if st.button("Guardar Textos"):
            config["content_section"]["modules"]["module1"]["title"] = new_title
            config["content_section"]["modules"]["module1"]["content"] = new_desc
            save_config(config)
            st.success("Textos actualizados.")

    with tab3:
        st.subheader("Configuración de APIs")
        st.info("Estas claves se guardan en el archivo .env de forma segura.")
        
        with st.form("api_keys_form"):
            new_google_key = st.text_input("Google Gemini API Key", value=os.getenv('GOOGLE_API_KEY', ""), type="password")
            new_openai_key = st.text_input("OpenAI API Key", value=os.getenv('OPENAI_API_KEY', ""), type="password")
            new_mistral_key = st.text_input("Mistral API Key", value=os.getenv('MISTRAL_API_KEY', ""), type="password")
            new_ollama_host = st.text_input("Ollama Host URL", value=os.getenv('OLLAMA_API_HOST', "http://localhost:11434"), help="Por defecto: http://localhost:11434")
            
            if st.form_submit_button("Guardar API Keys"):
                # Actualizar archivo .env
                env_path = Path(__file__).parent / ".env"
                env_lines = []
                if env_path.exists():
                    with open(env_path, "r") as f:
                        env_lines = f.readlines()
                
                # Función para actualizar o añadir línea en .env
                def update_env(lines, key, value):
                    found = False
                    new_lines = []
                    for line in lines:
                        if line.startswith(f"{key}="):
                            new_lines.append(f"{key}={value}\n")
                            found = True
                        else:
                            new_lines.append(line)
                    if not found:
                        new_lines.append(f"{key}={value}\n")
                    return new_lines

                updated_lines = update_env(env_lines, "GOOGLE_API_KEY", new_google_key)
                updated_lines = update_env(updated_lines, "OPENAI_API_KEY", new_openai_key)
                updated_lines = update_env(updated_lines, "MISTRAL_API_KEY", new_mistral_key)
                updated_lines = update_env(updated_lines, "OLLAMA_API_HOST", new_ollama_host)
                
                with open(env_path, "w") as f:
                    f.writelines(updated_lines)
                
                st.success("API Keys guardadas correctamente. Reinicia la app si es necesario.")
                load_dotenv(override=True)
                # Forzar recarga del tutor para que coja las nuevas keys inmediatamente
                st.session_state.tutor = None
                st.rerun()

    with tab4:
        st.subheader("Despliegue y Móvil")
        st.subheader("📱 Acceso Móvil (Red Local)")
        st.info("Escanea este código con tu móvil para acceder a la app (debes estar en la misma WiFi).")
        
        # Obtener IP local
        import socket
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            mobile_url = f"http://{local_ip}:8501"
            
            # Generar QR
            import qrcode
            from io import BytesIO
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(mobile_url)
            qr.make(fit=True)
            img_qr = qr.make_image(fill_color="black", back_color="white")
            
            buf = BytesIO()
            img_qr.save(buf)
            img_base64 = base64.b64encode(buf.getvalue()).decode()
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(f"""
                <div style='background: white; padding: 10px; border-radius: 10px; display: inline-block;'>
                    <img src='data:image/png;base64,{img_base64}' width='150'>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"### URL de Acceso:")
                st.code(mobile_url, language="text")
                st.warning("⚠️ Asegúrate de que el Firewall de Windows permita conexiones a Python/Streamlit.")

        except Exception as e:
            st.error(f"No se pudo generar el QR: {e}")

        st.markdown("---")
        st.subheader("☁️ Despliegue en la Nube")
        st.markdown("""
        **Pasos para el móvil (Internet):**
        1. Sube tu código a un repositorio privado de GitHub.
        2. Conecta tu cuenta en [share.streamlit.io](https://share.streamlit.io).
        3. En el móvil, abre la URL de tu app en Chrome y selecciona **'Añadir a pantalla de inicio'**.
        """)
        
        st.markdown("---")
        st.subheader("💻 Instalador PC")
        if st.button("Generar Instalador PC"):
            # Generar acceso directo en el escritorio con Powershell
            import subprocess
            import sys
            desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            icon_path = os.path.join(os.getcwd(), config["theme"]["app_icon"]) 
            app_path = os.path.join(os.getcwd(), "app.py")
            python_path = sys.executable
            
            ps_script = f"""
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{desktop}\\Academia AI.lnk")
            $Shortcut.TargetPath = "{python_path}"
            $Shortcut.Arguments = "-m streamlit run '{app_path}'"
            $Shortcut.IconLocation = "{icon_path}"
            $Shortcut.WorkingDirectory = "{os.getcwd()}"
            $Shortcut.WindowStyle = 7
            $Shortcut.Save()
            """
            try:
                subprocess.run(["powershell", "-Command", ps_script], check=True)
                st.success(f"¡Acceso directo creado en el escritorio!")
            except Exception as e:
                st.error(f"Error al crear acceso directo: {e}")

    with tab5:
        st.subheader("Gestión de Imágenes")
        st.write("Sube nuevas imágenes para personalizar tu plataforma.")
        
        # Hero Image
        st.markdown("### 🖼️ Imagen Principal (Hero)")
        hero_file = st.file_uploader("Subir imagen Hero", type=["png", "jpg", "jpeg"], key="hero_upload")
        if hero_file:
            with open(config["theme"]["hero_image"], "wb") as f:
                f.write(hero_file.getbuffer())
            st.success("Imagen Hero actualizada!")

        # Module 1
        st.markdown("### 📦 Imagen Módulo 1")
        m1_file = st.file_uploader("Subir imagen Módulo 1", type=["png", "jpg", "jpeg"], key="m1_upload")
        if m1_file:
            with open(config["theme"]["module1_image"], "wb") as f:
                f.write(m1_file.getbuffer())
            st.success("Imagen Módulo 1 actualizada!")

        # Module 2
        st.markdown("### 📦 Imagen Módulo 2")
        m2_file = st.file_uploader("Subir imagen Módulo 2", type=["png", "jpg", "jpeg"], key="m2_upload")
        if m2_file:
            with open(config["theme"]["module2_image"], "wb") as f:
                f.write(m2_file.getbuffer())
            st.success("Imagen Módulo 2 actualizada!")

        # App Icon
        st.markdown("### 🌟 Icono de la Aplicación")
        icon_file = st.file_uploader("Subir nuevo icono", type=["png", "jpg", "jpeg"], key="icon_upload")
        if icon_file:
            with open(config["theme"]["app_icon"], "wb") as f:
                f.write(icon_file.getbuffer())
            st.success("Icono de la aplicación actualizado!")

# Configuración de la página
st.set_page_config(
    page_title=config['app_config']['page_title'],
    page_icon=config['app_config']['page_icon'],
    layout="centered",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
theme = config.get("theme", {})
p_color = theme.get("primary_color", "#8b5cf6")
s_color = theme.get("secondary_color", "#3b82f6")
bg_main = theme.get("bg_color", "#0f172a")
sidebar_bg = theme.get("sidebar_color", "#1e293b")
card_bg = theme.get("card_bg", "#1e293b")
text_main = theme.get("text_main", "#f8fafc")
text_muted = theme.get("text_muted", "#94a3b8")
font = theme.get("font_family", "Inter")


css_styles = """
<style>
@import url('https://fonts.googleapis.com/css2?family=CUSTOM_FONT:wght@300;400;500;600;700&display=swap');

/* GLOBAL RESET & FONT */
html, body, [class*="css"] {
    font-family: 'CUSTOM_FONT', sans-serif !important;
    background-color: var(--bg-main);
    color: var(--text-main);
}

:root {
    --primary: PRIMARY_COLOR;
    --secondary: SECONDARY_COLOR;
    --bg-main: BG_COLOR;
    --bg-sidebar: SIDEBAR_BG;
    --card-bg: CARD_BG;
    --text-main: TEXT_MAIN;
    --text-muted: TEXT_MUTED;
    --border: rgba(255, 255, 255, 0.1);
    --glass: rgba(255, 255, 255, 0.05);
    --glass-hover: rgba(255, 255, 255, 0.1);
}

/* HIDE STREAMLIT DEFAULT ELEMENTS */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
/*header {visibility: hidden;}  <-- Comentado para no ocultar el botón del sidebar */

/* Ajustar header para que no moleste visualmente pero permita abrir el sidebar */
header[data-testid="stHeader"] {
    background: transparent !important;
    z-index: 1000;
}

/* CONTAINER SPACING */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 5rem !important;
    max-width: 1200px !important;
}

/* SIDEBAR STYLING */
[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar);
    border-right: 1px solid var(--border);
}

/* CUSTOM BUTTONS IN SIDEBAR */
.stButton > button {
    background: transparent;
    color: var(--text-muted);
    border: 1px solid transparent;
    border-radius: 12px;
    text-align: left;
    padding: 1rem 1.2rem; /* Aumentado padding */
    transition: all 0.2s ease;
    width: 100%;
    margin-bottom: 8px; /* Separación extra */
    font-size: 1.15rem !important; /* Letra más grande */
    font-weight: 600 !important; /* Más negrita */
    text-transform: uppercase; /* Mayúsculas */
    letter-spacing: 0.5px;
}

.stButton > button:hover {
    background: var(--glass-hover);
    color: white;
}

.stButton > button:focus:not(:active) {
    border-color: transparent;
    color: white;
}

/* CARDS & CONTAINERS */
.session-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.session-card-header {
    height: 200px;
    position: relative;
    overflow: hidden;
}

.session-card-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s;
}

.session-card:hover .session-card-img {
    transform: scale(1.05);
}

.session-badge {
    position: absolute;
    top: 15px;
    right: 15px;
    background: rgba(0,0,0,0.6);
    backdrop-filter: blur(4px);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.2);
}

/* TEXT STYLES */
h1, h2, h3 {
    font-weight: 700 !important;
    color: var(--text-main) !important;
    letter-spacing: -0.5px;
}

p, span, div {
    color: var(--text-main);
}

.text-muted {
    color: var(--text-muted) !important;
}
</style>
<script>
    const meta = document.createElement('meta');
    meta.name = "viewport";
    meta.content = "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no";
    window.parent.document.getElementsByTagName('head')[0].appendChild(meta);
</script>
"""

# Inyectar variables manualmente
css_styles = css_styles.replace('CUSTOM_FONT', font)
css_styles = css_styles.replace('PRIMARY_COLOR', p_color)
css_styles = css_styles.replace('SECONDARY_COLOR', s_color)
css_styles = css_styles.replace('BG_COLOR', bg_main)
css_styles = css_styles.replace('SIDEBAR_BG', sidebar_bg)
css_styles = css_styles.replace('CARD_BG', card_bg)
css_styles = css_styles.replace('TEXT_MAIN', text_main)
css_styles = css_styles.replace('TEXT_MUTED', text_muted)

st.markdown(css_styles, unsafe_allow_html=True)

# Inicializar estado de sesión para el tutor AI
if 'tutor' not in st.session_state:
    st.session_state.tutor = None
if 'tutor_provider' not in st.session_state:
    st.session_state.tutor_provider = config.get('ai_models', {}).get('default_provider', 'gemini')
if 'tutor_model' not in st.session_state:
    st.session_state.tutor_model = config.get('ai_models', {}).get('default_model', 'gemini-1.5-flash')
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'generated_test' not in st.session_state:
    st.session_state.generated_test = None
if 'generated_work' not in st.session_state:
    st.session_state.generated_work = None

# Intentar inicializar el tutor AI
try:
    if st.session_state.tutor is None:
        from ai_tutor import AITutor
        api_key_to_use = os.getenv('GOOGLE_API_KEY')
        if not api_key_to_use:
             api_key_to_use = "dummy_key_for_local_models"
             
        st.session_state.tutor = AITutor(
            api_key_to_use, 
            provider=st.session_state.tutor_provider,
            model_name=st.session_state.tutor_model
        )
except Exception as e:
    st.session_state.tutor_error = str(e)

def render_tutor_chat():
    st.markdown(f"# {config['tutor_section']['title']}")
    with st.expander("🧠 Configuración del Modelo de IA", expanded=False):
        col_p, col_m = st.columns(2)
        providers = config.get('ai_models', {}).get('providers', {})
        provider_names = {k: f"{v['icon']} {v['name']}" for k, v in providers.items()}
        
        selected_provider_key = st.selectbox(
            "Proveedor de IA",
            options=list(provider_names.keys()),
            format_func=lambda x: provider_names[x],
            index=list(provider_names.keys()).index(st.session_state.tutor_provider)
        )
        
        models = providers[selected_provider_key]['models']
        selected_model = st.selectbox(
            "Modelo",
            options=models,
            index=models.index(st.session_state.tutor_model) if st.session_state.tutor_model in models else 0
        )
        
        if st.button("Aplicar Cambios de Modelo", use_container_width=True):
            st.session_state.tutor_provider = selected_provider_key
            st.session_state.tutor_model = selected_model
            if st.session_state.tutor:
                st.session_state.tutor.set_model(selected_provider_key, selected_model)
            st.success(f"Cambiado a {selected_model}")
            st.rerun()

    st.markdown(f"*{config['tutor_section']['subtitle']}*")
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if st.session_state.tutor_provider == "gemini" and (not google_api_key or google_api_key == 'tu_api_key_aqui'):
        st.markdown(f"""
<div class='warning-box'>
<h3>{config['tutor_section']['api_key_required']}</h3>
<p style='white-space: pre-line;'>{config['tutor_section']['api_key_instructions']}</p>
</div>
""", unsafe_allow_html=True)

    if st.session_state.tutor is None:
        try:
             from ai_tutor import AITutor
             st.session_state.tutor = AITutor(
                "dummy_key", 
                provider=st.session_state.tutor_provider,
                model_name=st.session_state.tutor_model
            )
        except:
            pass

    if st.session_state.tutor is None:
        error_msg = st.session_state.get('tutor_error', 'Error desconocido')
        st.error(f"Error al inicializar el tutor AI: {error_msg}")
        st.info("Intenta seleccionar 'Ollama' en la configuración si no tienes claves API.")
    else:
        tab1, tab2, tab3, tab4 = st.tabs([
            config['tutor_section']['tabs']['chat'],
            config['tutor_section']['tabs']['documents'],
            config['tutor_section']['tabs']['tests'],
            config['tutor_section']['tabs']['assignments']
        ])
        with tab1:
            st.markdown(f"### {config['tutor_section']['chat']['title']}")
            chat_container = st.container()
            with chat_container:
                if len(st.session_state.chat_messages) == 0:
                    st.info(config['tutor_section']['chat']['empty_message'])
                else:
                    for message in st.session_state.chat_messages:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])
            
            if prompt := st.chat_input(config['tutor_section']['chat']['placeholder']):
                st.session_state.chat_messages.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner(config['tutor_section']['chat']['loading_message']):
                        response_obj = st.session_state.tutor.answer_question(prompt)
                        if isinstance(response_obj, dict):
                            answer_text = response_obj.get('answer', str(response_obj))
                            if response_obj.get('status') == 'error':
                                st.error(answer_text)
                            else:
                                st.markdown(answer_text)
                        else:
                            answer_text = str(response_obj)
                            st.markdown(answer_text)
                        
                        st.session_state.chat_messages.append({"role": "assistant", "content": answer_text})

        with tab2:
            st.markdown(f"### {config['tutor_section']['documents']['title']}")
            uploaded_files = st.file_uploader(
                config['tutor_section']['documents']['upload_label'],
                type=['pdf', 'docx', 'txt'],
                accept_multiple_files=True
            )
            
            if st.button(config['tutor_section']['documents']['upload_button']):
                if uploaded_files:
                    with st.spinner(config['tutor_section']['documents']['processing_message']):
                        success_count = 0
                        errors = []
                        for file in uploaded_files:
                            # Crear archivo temporal para procesar
                            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.name).suffix) as tmp:
                                tmp.write(file.getvalue())
                                tmp_path = tmp.name
                            try:
                                result = st.session_state.tutor.ingest_file(tmp_path, file_name=file.name)
                                if result.get("status") == "success":
                                    success_count += 1
                                else:
                                    errors.append(f"{file.name}: {result.get('error')}")
                            except Exception as e:
                                errors.append(f"{file.name}: {str(e)}")
                            finally:
                                if os.path.exists(tmp_path):
                                    os.unlink(tmp_path)
                        
                        if success_count > 0:
                            st.success(f"✅ {success_count} documentos procesados correctamente.")
                        
                        if errors:
                            for err in errors:
                                st.error(f"❌ Error: {err}")
                else:
                    st.warning(config['tutor_section']['documents']['no_files_message'])

        with tab3:
            st.markdown(f"### {config['tutor_section']['tests']['title']}")
            test_topic = st.text_input(
                config['tutor_section']['tests']['topic_label'],
                placeholder=config['tutor_section']['tests']['topic_placeholder']
            )
            num_q = st.slider(config['tutor_section']['tests']['num_questions_label'], 1, 10, 5)
            difficulty = st.select_slider(
                config['tutor_section']['tests']['difficulty_label'],
                options=['Básico', 'Intermedio', 'Avanzado']
            )
            
            if st.button(config['tutor_section']['tests']['generate_button'], use_container_width=True):
                if test_topic:
                    with st.spinner(config['tutor_section']['tests']['generating_message']):
                        test = st.session_state.tutor.generate_test(test_topic, num_q, difficulty)
                        st.session_state.generated_test = test
                else:
                    st.warning("Por favor introduce un tema para el test.")
            
            if st.session_state.generated_test:
                st.markdown("---")
                st.json(st.session_state.generated_test)
                test_text = json.dumps(st.session_state.generated_test, indent=2, ensure_ascii=False)
                st.download_button(
                    config['tutor_section']['tests']['download_button'],
                    data=test_text,
                    file_name=f"test_{test_topic}.json",
                    mime="application/json"
                )

        with tab4:
            st.markdown(f"### {config['tutor_section']['assignments']['title']}")
            
            assignment_desc = st.text_area(
                config['tutor_section']['assignments']['description_label'],
                placeholder=config['tutor_section']['assignments']['description_placeholder'],
                height=100
            )
            
            assignment_type = st.selectbox(
                config['tutor_section']['assignments']['type_label'],
                options=list(config['tutor_section']['assignments']['type_options'].keys()),
                format_func=lambda x: config['tutor_section']['assignments']['type_options'][x]
            )
            
            if st.button(config['tutor_section']['assignments']['generate_button'], use_container_width=True):
                if assignment_desc:
                    with st.spinner(config['tutor_section']['assignments']['generating_message']):
                        result = st.session_state.tutor.complete_assignment(assignment_desc, assignment_type)
                        if result['status'] == 'success':
                            st.session_state.generated_work = result
                            st.success("✅ Trabajo generado correctamente")
            
            if st.session_state.generated_work:
                st.markdown("---")
                st.markdown(st.session_state.generated_work['work'])
                st.download_button(
                    config['tutor_section']['assignments']['download_button'],
                    data=st.session_state.generated_work['work'],
                    file_name=f"trabajo_{assignment_type}.txt",
                    mime="text/plain"
                )

# -----------------------------------------------------------------------------
# GESTIÓN DE SESIÓN Y LOGIN
# -----------------------------------------------------------------------------
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = None # None, 'admin', 'student'
if 'user_info' not in st.session_state:
    st.session_state.user_info = None

def login_form():
    st.markdown("## 🔐 Iniciar Sesión")
    
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Entrar", use_container_width=True)
        
        if submitted:
            from data_manager import authenticate
            user = authenticate(username, password)
            
            if user:
                st.session_state.auth_status = user['role']
                st.session_state.user_info = user
                
                if user['role'] == 'admin':
                    st.toast(f"👋 ¡Hola {user['name']}!", icon="👨‍🏫")
                else:
                    st.toast(f"👋 ¡Hola {user['name']}!", icon="🎓")
                
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")

if not st.session_state.auth_status:
    # Diseño de la página de Login
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        # Logo o Imagen Hero en Login
        if os.path.exists(config["theme"]["app_icon"]):
             st.image(config["theme"]["app_icon"], width=100)
        
        st.markdown(f"<h1 style='text-align: center;'>{config['app_config']['page_title']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: var(--text-muted);'>{config['app_config']['logo_caption']}</p>", unsafe_allow_html=True)
        
        st.markdown("---")
        login_form()
        
        with st.expander("ℹ️ Credenciales de Prueba"):
            st.info("""
            **Profesor:** admin / 1234  
            **Alumno:** alumno / 1234
            """)
    
    # Detener ejecución si no está logueado
    st.stop()

# -----------------------------------------------------------------------------
# SIDEBAR Y NAVEGACIÓN
# -----------------------------------------------------------------------------


# Inicializar user_info si no existe o es None para evitar errores
if 'user_info' not in st.session_state or st.session_state.user_info is None:
    st.session_state.user_info = {
        'id': 'anon',
        'name': 'Usuario',
        'email': 'usuario@academia.ai'
    }


if 'menu_choice' not in st.session_state:
    if st.session_state.auth_status == 'admin':
        st.session_state.menu_choice = "Editor Programa"
    elif st.session_state.auth_status == 'student':
        st.session_state.menu_choice = "Mi Perfil"
    else:
        st.session_state.menu_choice = "Alumnos"


with st.sidebar:
    st.markdown("### Academia AI - Tu Tutor Digital")
    
    if st.session_state.auth_status == 'admin':
        menu_options = {
            "Inicio": "🏠",
            "Secuencias e-learning": "⛓️",
            "Seguimiento pedagógico": "📊",
            "Editor Programa": "�️",
            "Alumnos": "👥",
            "Firmas": "✍️",
            "Evaluaciones": "⭐",
            "Tutor IA": "🤖",
            "Configuración": "⚙️"
        }
        user_badge = "👨‍🏫 Profesor"
    else:
        menu_options = {
            "Mi Perfil": "👤",
            "Mi Curso": "⛓️",
            "Tutor IA": "🤖",
            "Mis Evaluaciones": "⭐"
        }
        user_badge = "🎓 Estudiante"


    user_email = st.session_state.user_info.get('email', 'usuario@academia.ai')


    st.markdown(f"""
    <div style='
        background: var(--glass); 
        padding: 15px; 
        border-radius: 16px; 
        margin-bottom: 30px; 
        border: 1px solid var(--border);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    '>
        <div style='display: flex; align-items: center; gap: 15px; margin-bottom: 10px;'>
            <div style='
                background: linear-gradient(135deg, var(--primary), var(--secondary)); 
                width: 50px; 
                height: 50px; 
                border-radius: 50%; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                font-weight: bold; 
                font-size: 1.2rem;
                color: white;
                box-shadow: 0 4px 10px rgba(139, 92, 246, 0.3);
            '>
                {st.session_state.user_info['name'][0]}
            </div>
            <div>
                <div style='font-weight: 700; font-size: 1.1rem; color: white;'>{st.session_state.user_info['name']}</div>
                <div style='font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;'>{user_badge}</div>
            </div>
        </div>
        <div style='background: rgba(0,0,0,0.2); padding: 8px 12px; border-radius: 8px; font-size: 0.8rem; color: var(--text-muted);'>
            <div style='display:flex; justify-content:space-between; margin-bottom:4px;'>
                <span>🆔 ID:</span> <span style='color: white;'>{st.session_state.user_info.get('id', 'N/A')}</span>
            </div>
            <div style='display:flex; justify-content:space-between;'>
                <span>📧 Email:</span> <span style='color: white; overflow: hidden; text-overflow: ellipsis; max-width: 140px;'>{user_email}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


    role_prefix = st.session_state.auth_status or 'anon'
    for i, (option, emoji) in enumerate(menu_options.items()):
        btn_key = f"sidebar_{role_prefix}_{i}"
        if st.button(f"{emoji} {option}", key=btn_key, use_container_width=True):
            st.session_state.menu_choice = option
            st.rerun()
    
    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", key=f"sidebar_logout_{st.session_state.user_info.get('id','anon')}", use_container_width=True):
        st.session_state.auth_status = None
        st.session_state.user_info = None
        st.rerun()
            
    menu = st.session_state.menu_choice

# -----------------------------------------------------------------------------
# VISTAS PRINCIPALES
# -----------------------------------------------------------------------------

if menu == "Mi Perfil":
    from data_manager import load_users, save_users
    
    # Cargar datos actualizados para asegurar persistencia
    all_users_data = load_users()
    current_user_idx = next((i for i, u in enumerate(all_users_data['users']) if u['id'] == st.session_state.user_info['id']), None)
    
    if current_user_idx is not None:
        user_data = all_users_data['users'][current_user_idx]
    else:
        user_data = st.session_state.user_info

    u_name = user_data.get('name', 'Estudiante')
    u_initial = u_name[0] if u_name else 'E'
    u_avatar = user_data.get('avatar', None)
    
    # --- DISEÑO DE PERFIL ---
    if u_avatar:
        avatar_inner = f'<img src="data:image/png;base64,{u_avatar}" style="width:100%; height:100%; object-fit:cover;">'
    else:
        avatar_inner = u_initial

    avatar_html = f"""
    <div style='width: 100px; height: 100px; border-radius: 50%; background: #ccc; border: 4px solid white; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; font-weight: bold; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;'>
        {avatar_inner}
    </div>
    """
    
    st.markdown(f"""
    <div style='background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); padding: 40px; border-radius: 20px 20px 0 0; position: relative; margin-bottom: 50px;'>
        <div style='position: absolute; bottom: -40px; left: 40px;'>
            {avatar_html}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([3, 1])
    with c1:
        new_name = st.text_input("Nombre Completo", value=u_name)
        if new_name != u_name:
            user_data['name'] = new_name
            all_users_data['users'][current_user_idx] = user_data
            save_users(all_users_data)
            st.session_state.user_info = user_data
            st.rerun()
            
        st.markdown("<p style='margin:0; padding-left: 10px; color: var(--text-muted);'>Estado: <span style='color: #10b981; font-weight: 600;'>Activo</span></p>", unsafe_allow_html=True)
    with c2:
        with st.expander("📸 Cambiar Foto"):
            uploaded_file = st.file_uploader("Sube tu imagen", type=['png', 'jpg', 'jpeg'])
            if uploaded_file:
                bytes_data = uploaded_file.getvalue()
                base64_str = base64.b64encode(bytes_data).decode()
                user_data['avatar'] = base64_str
                all_users_data['users'][current_user_idx] = user_data
                save_users(all_users_data)
                st.session_state.user_info = user_data
                st.success("¡Foto actualizada!")
                st.rerun()

    st.write("") # Spacer

    tab_perfil, tab_pub, tab_cursos, tab_grupos = st.tabs(["Perfil", "Publicaciones", "Cursos", "Grupos"])
    
    with tab_perfil:
        with st.container():
            st.markdown("#### Descripción general ✏️")
            bio = user_data.get('bio', '')
            new_bio = st.text_area("Sobre mí", value=bio, placeholder="Cuéntanos algo sobre ti...")
            if st.button("Guardar Biografía"):
                user_data['bio'] = new_bio
                all_users_data['users'][current_user_idx] = user_data
                save_users(all_users_data)
                st.success("Biografía guardada")
            
            st.divider()
            
            st.markdown("#### Mi experiencia")
            experiences = user_data.get('experience', [])
            for i, exp in enumerate(experiences):
                col_exp, col_del = st.columns([5, 1])
                col_exp.text(f"• {exp}")
                if col_del.button("🗑️", key=f"del_exp_{i}"):
                    experiences.pop(i)
                    user_data['experience'] = experiences
                    all_users_data['users'][current_user_idx] = user_data
                    save_users(all_users_data)
                    st.rerun()
            
            new_exp = st.text_input("Añadir nueva experiencia")
            if st.button("➕ Añadir Experiencia"):
                if new_exp:
                    if 'experience' not in user_data: user_data['experience'] = []
                    user_data['experience'].append(new_exp)
                    all_users_data['users'][current_user_idx] = user_data
                    save_users(all_users_data)
                    st.rerun()

# Vista: Secuencias e-Learning (Ruta de Aprendizaje - Diseño captura usuario)
elif menu == "Secuencias e-learning" or menu == "Mi Curso":
    # VERIFICACIÓN DE MATRÍCULA
    # Cargar nombre del curso actual
    current_course_name = "Curso General"
    if os.path.exists("course_metadata.json"):
        with open("course_metadata.json", 'r', encoding='utf-8') as f:
            meta = json.load(f)
            current_course_name = meta.get('name', "Curso General")
            
    # Verificar si el alumno tiene acceso (Admin y Tutor siempre tienen acceso)
    user_courses = st.session_state.user_info.get('enrolled_courses', [])
    has_access = (current_course_name in user_courses) or (st.session_state.auth_status in ['admin', 'tutor'])
    
    if not has_access:
        st.warning(f"🔒 No estás matriculado en el curso: **{current_course_name}**")
        st.info("Por favor, contacta con tu tutor o administrador para que active tu acceso.")
        st.stop() # Detener la carga del resto de la página

    # SI TIENE ACCESO, MOSTRAR CONTENIDO:
    st.caption(f"Curso: {current_course_name}")
    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>⛓️ Secuencias e-Learning</h1>", unsafe_allow_html=True)
    
    st.markdown("### Ruta de aprendizaje actual")
    
    # Cargar contenido dinámico del curso
    COURSE_FILE = "course_content.json"
    course_content = []
    if os.path.exists(COURSE_FILE):
        try:
            with open(COURSE_FILE, 'r', encoding='utf-8') as f:
                course_content = json.load(f)
        except:
            course_content = []

    if not course_content:
        st.info("🚧 Este curso aún no tiene contenido estructurado. El profesor está trabajando en ello.")
    else:
        for idx, block in enumerate(course_content):
            # Contenedor visual para cada bloque
            with st.container():
                if block['type'] == 'editor':
                    if block.get('title'):
                        st.markdown(f"### {block['title']}")
                    st.markdown(block.get('content', ''))
                
                elif block['type'] == 'accordion':
                    with st.expander(block.get('title', 'Sección Desplegable')):
                        for item in block.get('items', []):
                            st.markdown(f"• {item}")
                            
                elif block['type'] == 'video':
                    if block.get('title'):
                        st.markdown(f"#### 📺 {block['title']}")
                    if block.get('url'):
                        st.video(block['url'])
                        
                elif block['type'] == 'image':
                    if block.get('title'):
                        st.markdown(f"#### 🖼️ {block['title']}")
                    if block.get('url'):
                        st.image(block['url'])
                        
                elif block['type'] == 'quiz':
                    st.markdown(f"#### ❓ {block.get('title', 'Pregunta')}")
                    st.write(block.get('question', ''))
                    # Usar key única para evitar conflictos
                    ans = st.radio("Tu respuesta:", block.get('options', []), key=f"q_view_{idx}")
                    if st.button("Verificar", key=f"check_{idx}"):
                        if ans == block.get('correct'):
                            st.success("¡Correcto! ✅")
                        else:
                            st.error("Incorrecto ❌")
    
    # SOLO ADMIN: Botón de edición rápida
    if st.session_state.auth_status == 'admin':
        if st.button("✏️ Editar Secuencia", use_container_width=True):
            st.session_state.menu_choice = "Gestión Cursos"
            st.rerun()
    else:
        st.info("💡 Selecciona un módulo en progreso para continuar tu formación.")

# -----------------------------------------------------------------------------
# VISTA: Interfaz Moderna (réplica aproximada del prototipo)
# -----------------------------------------------------------------------------
elif menu == "Interfaz Moderna":
    st.markdown("<h1 style='text-align:center; margin-bottom:0.5rem;'>Interfaz Moderna — Panel Interactivo</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#64748b;'>Versión adaptada del prototipo. Usa los controles para ver acciones.</p>", unsafe_allow_html=True)

    # Top controls (filtros / botones principales)
    with st.container():
        c1, c2, c3 = st.columns([3, 2, 2])
        with c1:
            q = st.text_input("Buscar cursos / temas", value="", placeholder="Escribe y presiona Enter")
        with c2:
            cat = st.selectbox("Categoría", options=["Todas","Tecnología","Gestión","Idiomas","Comercio"], index=0)
        with c3:
            if st.button("Aplicar filtros"):
                st.info(f"Buscando '{q}' en '{cat}'...")

    st.markdown("---")

    # Left: lista de items / Right: detalle (estilo prototipo)
    left, right = st.columns([1, 2])
    with left:
        st.markdown("### Cursos Disponibles")
        items = [f"Curso {i} - {cat}" for i in range(1,8)]
        sel = st.radio("Selecciona un curso", items, index=0)
        if st.button("Inscribirme / Acceder"):
            st.success(f"Inscrito en {sel}")

    with right:
        st.markdown(f"## {sel}")
        st.markdown("<div style='color:#64748b;'>Descripción breve del curso y acciones disponibles.</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top:12px; display:flex; gap:10px;'>", unsafe_allow_html=True)
        if st.button("💬 Abrir Tutor IA", key='open_tutor'):
            st.session_state.menu_choice = 'Tutor IA'
            st.rerun()
        if st.button("📄 Materiales", key='materials'):
            st.info("Abriendo materiales...")
        if st.button("📝 Generar Test", key='gen_test'):
            st.info("Generando test con la IA...")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Lecciones")
        for i in range(1,5):
            with st.expander(f"Lección {i}: Título de la lección", expanded=False):
                st.write("Contenido de ejemplo para la lección. Aquí irían videos, textos y recursos interactivos.")

    # MOSTRAR MATERIALES PUBLICADOS (Para que el alumno vea el test)
    st.markdown("---")
    st.markdown("### 📂 Materiales y Recursos del Curso")
    mat_dir = "course_materials"
    if os.path.exists(mat_dir) and os.listdir(mat_dir):
        for f_name in os.listdir(mat_dir):
            c_icon, c_name, c_dl = st.columns([1, 6, 2])
            c_icon.markdown("📄")
            c_name.markdown(f"**{f_name}**")
            file_path = os.path.join(mat_dir, f_name)
            with open(file_path, "rb") as f:
                c_dl.download_button("⬇️ Descargar", f, file_name=f_name, key=f"dl_{f_name}")
    else:
        st.info("No hay materiales adicionales disponibles por el momento.")

# Vista: Gestión de Cursos (Admin/Tutor)
elif (menu == "Gestión Cursos" or menu == "Editor Programa") and st.session_state.auth_status in ['admin', 'tutor']:
    st.markdown("## 📚 Gestión Integral del Curso")
    
    # Pestañas de gestión
    tab_ficha, tab_temario, tab_editor, tab_asignar = st.tabs(["📋 Ficha Técnica", "📂 Repositorio de Temarios", "✏️ Editor de Contenidos", "👥 Asignar Alumnos"])
    
    # --- TAB 1: FICHA TÉCNICA ---
    with tab_ficha:
        st.markdown("### Especificaciones del Curso")
        
        # Cargar metadatos
        META_FILE = "course_metadata.json"
        default_meta = {"name": "", "code": "", "hours": 0, "modality": "Online", "description": "", "objectives": ""}
        
        if os.path.exists(META_FILE):
            with open(META_FILE, 'r', encoding='utf-8') as f:
                course_meta = json.load(f)
        else:
            course_meta = default_meta
            
        with st.form("course_meta_form"):
            c1, c2 = st.columns(2)
            course_meta['name'] = c1.text_input("Nombre del Curso", value=course_meta.get('name', ''))
            course_meta['code'] = c2.text_input("Código de Referencia", value=course_meta.get('code', ''))
            
            c3, c4 = st.columns(2)
            course_meta['hours'] = c3.number_input("Horas Totales", value=course_meta.get('hours', 0))
            course_meta['modality'] = c4.selectbox("Modalidad", ["Online", "Presencial", "Mixta"], index=["Online", "Presencial", "Mixta"].index(course_meta.get('modality', 'Online')))
            
            course_meta['description'] = st.text_area("Descripción General", value=course_meta.get('description', ''))
            course_meta['objectives'] = st.text_area("Objetivos Pedagógicos", value=course_meta.get('objectives', ''))
            
            if st.form_submit_button("💾 Guardar Ficha Técnica"):
                with open(META_FILE, 'w', encoding='utf-8') as f:
                    json.dump(course_meta, f, indent=4, ensure_ascii=False)
                st.success("Ficha técnica actualizada correctamente")

    # --- TAB 2: REPOSITORIO DE TEMARIOS ---
    with tab_temario:
        st.markdown("### 📂 Subida de Temarios y Materiales")
        st.info("Sube aquí los archivos PDF, ZIP o documentos grandes que componen el temario oficial del curso.")
        
        # Directorio de materiales
        MATERIALS_DIR = "course_materials"
        os.makedirs(MATERIALS_DIR, exist_ok=True)
        
        # Uploader
        uploaded_materials = st.file_uploader("Arrastra tus archivos aquí", accept_multiple_files=True)
        if uploaded_materials:
            for u_file in uploaded_materials:
                file_path = os.path.join(MATERIALS_DIR, u_file.name)
                with open(file_path, "wb") as f:
                    f.write(u_file.getbuffer())
            st.success(f"✅ {len(uploaded_materials)} archivos subidos correctamente.")
        
        st.divider()
        st.markdown("#### 📑 Archivos Disponibles")
        
        files = os.listdir(MATERIALS_DIR)
        if not files:
            st.caption("No hay archivos subidos aún.")
        else:
            for f_name in files:
                col_f1, col_f2, col_f3 = st.columns([1, 4, 1])
                col_f1.markdown("📄")
                col_f2.markdown(f"**{f_name}**")
                
                f_path = os.path.join(MATERIALS_DIR, f_name)
                if col_f3.button("🗑️", key=f"del_mat_{f_name}"):
                    os.remove(f_path)
                    st.rerun()

    # --- TAB 3: EDITOR DE CONTENIDOS (Lo que ya tenías) ---
    with tab_editor:
        st.markdown("### 🛠️ Constructor de Secuencias Didácticas")
    
    # Archivo de persistencia
    COURSE_FILE = "course_content.json"
    
    # Cargar contenido existente o iniciar vacío
    if 'editor_course_content' not in st.session_state:
        if os.path.exists(COURSE_FILE):
            try:
                with open(COURSE_FILE, 'r', encoding='utf-8') as f:
                    st.session_state.editor_course_content = json.load(f)
            except:
                st.session_state.editor_course_content = []
        else:
            st.session_state.editor_course_content = [
                {"type": "editor", "title": "Bienvenida", "content": "Bienvenido al curso. Edita este texto."}
            ]

    # Barra de Acciones Superior
    col_info, col_actions = st.columns([2, 2])
    with col_info:
        st.caption(f"Editando: {len(st.session_state.editor_course_content)} bloques")
    with col_actions:
        c_save, c_export, c_clear = st.columns([2, 2, 1])
        if c_save.button("💾 Guardar Cambios", type="primary", use_container_width=True):
            with open(COURSE_FILE, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.editor_course_content, f, indent=4, ensure_ascii=False)
            st.success("✅ Curso guardado correctamente")

        # Funcionalidad de Exportar a Markdown (Nueva)
        if c_export.button("📥 Exportar MD", use_container_width=True, help="Descargar curso en formato Markdown"):
            md_content = f"# {course_meta.get('name', 'Curso Sin Título')}\n\n"
            md_content += f"_{course_meta.get('description', '')}_\n\n---\n\n"

            for block in st.session_state.editor_course_content:
                if block['type'] == 'editor':
                    md_content += f"## {block.get('title', 'Sección')}\n\n{block.get('content', '')}\n\n"
                elif block['type'] == 'accordion':
                    md_content += f"### 📂 {block.get('title', 'Desplegable')}\n"
                    for item in block.get('items', []):
                        md_content += f"- {item}\n"
                    md_content += "\n"
                elif block['type'] == 'quiz':
                    md_content += f"### ❓ Pregunta: {block.get('question', '')}\n"
                    for opt in block.get('options', []):
                        md_content += f"- [ ] {opt}\n"
                    md_content += f"\n**Respuesta correcta:** {block.get('correct', '')}\n\n"

            st.download_button("⬇️ Bajar Archivo", data=md_content, file_name="curso_exportado.md", mime="text/markdown")

        if c_clear.button("🗑️ Borrar Todo", use_container_width=True):
            st.session_state.editor_course_content = []
            st.rerun()

    st.markdown("---")

    # ÁREA DE EDICIÓN PRINCIPAL
    indices_to_remove = []
    
    for idx, block in enumerate(st.session_state.editor_course_content):
        with st.container():
            # Cabecera del bloque
            c_head, c_del = st.columns([6, 1])
            with c_head:
                # Icono según tipo
                icons = {"editor": "📝", "accordion": "📂", "video": "🎥", "image": "🖼️", "quiz": "❓"}
                icon = icons.get(block['type'], "📄")
                
                new_title = st.text_input(f"Título (Bloque {idx+1})", value=block.get('title', ''), key=f"title_{idx}", label_visibility="collapsed")
                block['title'] = new_title
            with c_del:
                if st.button("❌", key=f"del_{idx}", help="Eliminar bloque"):
                    indices_to_remove.append(idx)
            
            # Contenido Editable según tipo
            if block['type'] == "editor":
                st.caption(f"{icon} Editor de Texto")
                block['content'] = st.text_area("Contenido", block.get('content', ''), key=f"content_{idx}", height=150)
                
                # Botón IA
                if st.button("✨ Mejorar con IA", key=f"ai_{idx}"):
                    if st.session_state.tutor:
                        with st.spinner("Mejorando texto..."):
                            try:
                                improved = st.session_state.tutor._generate_response(f"Mejora este texto educativo para que sea más claro y profesional:\n\n{block['content']}")
                                block['content'] = improved
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error IA: {e}")
                
            elif block['type'] == "accordion":
                st.caption(f"{icon} Lista Desplegable")
                items_text = "\n".join(block.get('items', []))
                new_items = st.text_area("Items (uno por línea)", items_text, key=f"acc_{idx}")
                block['items'] = new_items.split('\n')
            
            elif block['type'] == "video":
                st.caption(f"{icon} Reproductor de Video")
                block['url'] = st.text_input("URL del Video (YouTube)", block.get('url', ''), key=f"vid_{idx}")
                if block['url']:
                    st.video(block['url'])
            
            elif block['type'] == "image":
                st.caption(f"{icon} Visor de Imagen")
                block['url'] = st.text_input("URL de la Imagen", block.get('url', ''), key=f"img_{idx}")
                if block['url']:
                    st.image(block['url'], width=300)
            
            elif block['type'] == "quiz":
                st.caption(f"{icon} Pregunta de Test")
                block['question'] = st.text_input("Pregunta", block.get('question', ''), key=f"q_{idx}")
                opts_text = "\n".join(block.get('options', []))
                new_opts = st.text_area("Opciones (una por línea)", opts_text, key=f"qo_{idx}")
                block['options'] = new_opts.split('\n')
                if block['options']:
                    block['correct'] = st.selectbox("Respuesta Correcta", block['options'], key=f"qc_{idx}")

    # Eliminar bloques marcados
    if indices_to_remove:
        for i in sorted(indices_to_remove, reverse=True):
            st.session_state.editor_course_content.pop(i)
        st.rerun()

    # BARRA DE HERRAMIENTAS FUNCIONAL
    st.markdown("### ➕ Añadir Contenido")
    
    b1, b2, b3, b4, b5 = st.columns(5)
    
    if b1.button(" Texto", use_container_width=True):
        st.session_state.editor_course_content.append({"type": "editor", "title": "Nuevo Texto", "content": ""})
        st.rerun()
        
    if b2.button("📂 Acordeón", use_container_width=True):
        st.session_state.editor_course_content.append({"type": "accordion", "title": "Desplegable", "items": ["Elemento 1", "Elemento 2"]})
        st.rerun()
        
    if b3.button("🎥 Video", use_container_width=True):
        st.session_state.editor_course_content.append({"type": "video", "title": "Video", "url": ""})
        st.rerun()
        
    if b4.button("🖼️ Imagen", use_container_width=True):
        st.session_state.editor_course_content.append({"type": "image", "title": "Imagen", "url": ""})
        st.rerun()
        
    if b5.button("❓ Test", use_container_width=True):
        st.session_state.editor_course_content.append({"type": "quiz", "title": "Evaluación", "question": "¿...?", "options": ["Sí", "No"], "correct": "Sí"})
        st.rerun()

    # --- TAB 4: ASIGNAR ALUMNOS (NUEVO) ---
    with tab_asignar:
        st.markdown("### 👥 Matriculación de Alumnos")
        
        # Obtener nombre del curso actual
        curr_course_name = "Curso Sin Nombre"
        if os.path.exists("course_metadata.json"):
            with open("course_metadata.json", 'r', encoding='utf-8') as f:
                curr_course_name = json.load(f).get('name', "Curso Sin Nombre")
        
        st.info(f"Gestionando acceso para: **{curr_course_name}**")
        
        from data_manager import load_users, toggle_course_enrollment
        users_db = load_users()['users']
        students = [u for u in users_db if u['role'] == 'student']
        
        if not students:
            st.warning("No hay alumnos registrados en la plataforma.")
        else:
            # Crear tabla de asignación
            st.markdown(f"**Selecciona los alumnos que pueden acceder a este curso:**")
            
            for stu in students:
                col_check, col_name, col_email = st.columns([1, 3, 3])
                
                is_enrolled = curr_course_name in stu.get('enrolled_courses', [])
                
                with col_check:
                    if st.checkbox("", value=is_enrolled, key=f"enroll_{stu['id']}"):
                        if not is_enrolled:
                            toggle_course_enrollment(stu['id'], curr_course_name)
                            st.rerun()
                    else:
                        if is_enrolled:
                            toggle_course_enrollment(stu['id'], curr_course_name)
                            st.rerun()
                
                with col_name:
                    st.write(f"**{stu['name']}**")
                with col_email:
                    st.caption(stu['email'])
            
            st.divider()
            st.caption("Nota: Los cambios se guardan automáticamente al marcar/desmarcar.")

# Vista: Inicio (Dashboard Admin / General)
elif menu == "Inicio":

    # 1. HERO SEARCH (Estilo Femxa)
    hero_title = config['hero'].get('title', '¿Qué quieres aprender hoy?')
    hero_subtitle = config['hero'].get('subtitle', 'Descubre cursos online gratuitos y subvencionados para impulsar tu carrera.')
    search_ph = config['hero'].get('search_placeholder', 'Busca cursos, temáticas (ej: Administración, Informática...)')
    
    st.markdown(f"""
    <div class="search-hero">
        <h1 style="color: white; margin-bottom: 1rem; font-size: 2.5rem;">{hero_title}</h1>
        <p style="color: rgba(255,255,255,0.9); margin-bottom: 2rem; font-size: 1.1rem;">{hero_subtitle}</p>
        <div style="background: white; padding: 8px; border-radius: 50px; max-width: 600px; margin: 0 auto; display: flex; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <span style="font-size: 1.2rem; padding-left: 15px; padding-right: 10px;">🔍</span>
            <input type="text" placeholder="{search_ph}" style="border: none; outline: none; padding: 10px; width: 100%; font-size: 1rem; border-radius: 50px; color: #333;">
            <button style="background: var(--primary); color: white; border: none; padding: 12px 30px; border-radius: 40px; font-weight: 600; cursor: pointer; white-space: nowrap;">Buscar</button>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. CATEGORÍAS (Áreas Formativas)
    st.markdown("### 🏢 Áreas Formativas")
    st.markdown("""
    <div class="cat-grid">
        <div class="cat-card"><div style="font-size: 2rem; margin-bottom: 10px;">💻</div><div style="font-weight:600;">Tecnología</div></div>
        <div class="cat-card"><div style="font-size: 2rem; margin-bottom: 10px;">📊</div><div style="font-weight:600;">Gestión</div></div>
        <div class="cat-card"><div style="font-size: 2rem; margin-bottom: 10px;">🗣️</div><div style="font-weight:600;">Idiomas</div></div>
        <div class="cat-card"><div style="font-size: 2rem; margin-bottom: 10px;">🛒</div><div style="font-weight:600;">Comercio</div></div>
        <div class="cat-card"><div style="font-size: 2rem; margin-bottom: 10px;">🏥</div><div style="font-weight:600;">Sanidad</div></div>
        <div class="cat-card"><div style="font-size: 2rem; margin-bottom: 10px;">🎓</div><div style="font-weight:600;">Docencia</div></div>
    </div>
    """, unsafe_allow_html=True)

    # 3. CURSOS DESTACADOS (Grid de Tarjetas)
    st.markdown("### 🎓 Cursos Destacados")
    
    # Cargar datos del curso real
    course_name = "Curso General"
    course_hours = 0
    course_modality = "Online"
    if os.path.exists("course_metadata.json"):
        try:
            with open("course_metadata.json", 'r', encoding='utf-8') as f:
                meta = json.load(f)
                course_name = meta.get('name', course_name)
                course_hours = meta.get('hours', 0)
                course_modality = meta.get('modality', "Online")
        except:
            pass
            
    # Grid de 3 columnas
    col1, col2, col3 = st.columns(3)
    
    # Tarjeta 1 (Tu Curso Real)
    with col1:
        st.markdown(f"""
        <div class="course-card">
            <div class="course-img-container">
                <span class="course-badge">SUBVENCIONADO</span>
                <img src="https://img.freepik.com/free-photo/online-learning-study-concept_53876-124236.jpg" class="course-img">
            </div>
            <div class="course-body">
                <div class="course-title">{course_name}</div>
                <div class="course-meta">
                    <span>⏱️ {course_hours}h</span>
                    <span>📍 {course_modality}</span>
                </div>
                <div class="course-btn">Ver Ficha</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Botón invisible de Streamlit para funcionalidad
        if st.button("Ir al Curso", key="btn_real", use_container_width=True):
             st.session_state.menu_choice = "Secuencias e-learning"
             st.rerun()

    # Tarjeta 2 (Ejemplo Visual)
    with col2:
        st.markdown(f"""
        <div class="course-card">
            <div class="course-img-container">
                <span class="course-badge" style="background:#3b82f6;">PREMIUM</span>
                <img src="https://img.freepik.com/free-photo/programming-background-with-person-working-with-codes-computer_23-2150010125.jpg" class="course-img">
            </div>
            <div class="course-body">
                <div class="course-title">Máster en Inteligencia Artificial Generativa</div>
                <div class="course-meta">
                    <span>⏱️ 350h</span>
                    <span>📍 Online</span>
                </div>
                <div class="course-btn">Más Información</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Tarjeta 3 (Ejemplo Visual)
    with col3:
        st.markdown(f"""
        <div class="course-card">
            <div class="course-img-container">
                <span class="course-badge" style="background:#f59e0b;">NUEVO</span>
                <img src="https://img.freepik.com/free-photo/group-people-working-out-business-plan-office_1303-15861.jpg" class="course-img">
            </div>
            <div class="course-body">
                <div class="course-title">Gestión de Equipos y Liderazgo Digital</div>
                <div class="course-meta">
                    <span>⏱️ 60h</span>
                    <span>📍 Mixta</span>
                </div>
                <div class="course-btn">Más Información</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # 4. VENTAJAS (Iconos estilo Femxa)
    st.markdown("### ¿Por qué elegirnos?")
    
    adv = config.get('advantages', {
        "a1": {"icon": "🎓", "title": "Títulos Oficiales", "text": "Certificados válidos"},
        "a2": {"icon": "💻", "title": "100% Online", "text": "A tu propio ritmo"},
        "a3": {"icon": "👩‍🏫", "title": "Tutores Expertos", "text": "Seguimiento real"},
        "a4": {"icon": "💼", "title": "Bolsa de Empleo", "text": "Prácticas en empresas"}
    })
    
    w1, w2, w3, w4 = st.columns(4)
    with w1:
        st.markdown(f"<div style='text-align:center;'><div style='font-size:2.5rem; color:var(--primary);'>{adv['a1']['icon']}</div><b>{adv['a1']['title']}</b><br><span style='font-size:0.8rem; color:#666;'>{adv['a1']['text']}</span></div>", unsafe_allow_html=True)
    with w2:
        st.markdown(f"<div style='text-align:center;'><div style='font-size:2.5rem; color:var(--primary);'>{adv['a2']['icon']}</div><b>{adv['a2']['title']}</b><br><span style='font-size:0.8rem; color:#666;'>{adv['a2']['text']}</span></div>", unsafe_allow_html=True)
    with w3:
        st.markdown(f"<div style='text-align:center;'><div style='font-size:2.5rem; color:var(--primary);'>{adv['a3']['icon']}</div><b>{adv['a3']['title']}</b><br><span style='font-size:0.8rem; color:#666;'>{adv['a3']['text']}</span></div>", unsafe_allow_html=True)
    with w4:
        st.markdown(f"<div style='text-align:center;'><div style='font-size:2.5rem; color:var(--primary);'>{adv['a4']['icon']}</div><b>{adv['a4']['title']}</b><br><span style='font-size:0.8rem; color:#666;'>{adv['a4']['text']}</span></div>", unsafe_allow_html=True)

elif menu == "Tutor IA" or menu == config['navigation']['sections']['tutor']:
    render_tutor_chat()

elif menu == config['navigation']['sections']['forms']:
    st.markdown(f"## {config['forms_section']['title']}")
    
    with st.form(key="contact_form"):
        st.markdown(f"### {config['forms_section']['contact_form']['title']}")
        
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input(
                config['forms_section']['contact_form']['fields']['name'],
                key="name"
            )
            email = st.text_input(
                config['forms_section']['contact_form']['fields']['email'],
                key="email"
            )
        
        with col2:
            fecha = st.date_input(
                config['forms_section']['contact_form']['fields']['date'],
                min_value=datetime.now()
            )
            nivel = st.select_slider(
                config['forms_section']['contact_form']['fields']['experience_level'],
                options=config['forms_section']['contact_form']['experience_options']
            )
        
        mensaje = st.text_area(config['forms_section']['contact_form']['fields']['message'])
        submitted = st.form_submit_button(config['forms_section']['contact_form']['submit_button'])
        
        if submitted:
            if not nombre or not email:
                st.error(config['forms_section']['contact_form']['error_message'])
            else:
                st.success(config['forms_section']['contact_form']['success_message'])
                st.balloons()

elif menu == config['navigation']['sections']['files']:
    st.markdown(f"## {config['files_section']['title']}")
    
    st.markdown(f"### {config['files_section']['upload']['subtitle']}")
    
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader(
            config['files_section']['upload']['label'],
            type=config['files_section']['upload']['accepted_types'],
            help=config['files_section']['upload']['help_text']
        )
    
    with col2:
        if uploaded_file:
            st.info(f"{config['files_section']['upload']['file_loaded']} {uploaded_file.name}")
            st.metric(
                label=config['files_section']['upload']['file_size_label'],
                value=f"{uploaded_file.size/1024:.1f} KB"
            )
            
            with st.spinner(config['files_section']['upload']['processing_message']):
                time.sleep(1)
                st.success(config['files_section']['upload']['success_message'])

elif menu == config['navigation']['sections']['design']:
    st.markdown(f"## {config['design_section']['title']}")
    
    tab1, tab2 = st.tabs([
        config['design_section']['tabs']['columns'],
        config['design_section']['tabs']['expanders']
    ])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-icon icon-blue'>📚</div>", unsafe_allow_html=True)
            st.markdown(f"### {config['design_section']['columns_demo']['col1_title']}")
            st.write("Contenido de ejemplo para la primera columna")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-icon icon-yellow'>📊</div>", unsafe_allow_html=True)
            st.markdown(f"### {config['design_section']['columns_demo']['col2_title']}")
            st.metric(
                label=config['design_section']['columns_demo']['col2_metric_label'],
                value=config['design_section']['columns_demo']['col2_metric_value'],
                delta=config['design_section']['columns_demo']['col2_metric_delta']
            )
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-icon icon-green'>🎯</div>", unsafe_allow_html=True)
            st.markdown(f"### {config['design_section']['columns_demo']['col3_title']}")
            st.button(config['design_section']['columns_demo']['col3_button'], use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        with st.expander(config['design_section']['expanders_demo']['section1_title']):
            st.write(config['design_section']['expanders_demo']['section1_content'])
            st.slider(
                config['design_section']['expanders_demo']['section1_slider_label'],
                0, 100, 50
            )
        
        with st.expander(config['design_section']['expanders_demo']['section2_title']):
            st.write(config['design_section']['expanders_demo']['section2_content'])
            st.checkbox(config['design_section']['expanders_demo']['section2_checkbox'])

elif menu == "Alumnos":
    st.markdown(f"## 👥 Gestión de Estudiantes")
    
    # Cargar datos reales
    from data_manager import load_users, add_user, delete_user
    all_users = load_users()['users']
    students_data = [u for u in all_users if u['role'] == 'student']
    
    st.session_state.students_data = students_data # Sync for display

    # KPIs Superiores
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.markdown(f"""
        <div class='progress-widget'>
            <div style='color:var(--primary); font-size:2rem; font-weight:700;'>{len(students_data)}</div>
            <div style='font-size:0.9rem; color:var(--text-muted);'>Total Alumnos</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        active_count = sum(1 for s in students_data if s['status'] == 'Activo')
        st.markdown(f"""
        <div class='progress-widget'>
            <div style='color:#10b981; font-size:2rem; font-weight:700;'>{active_count}</div>
            <div style='font-size:0.9rem; color:var(--text-muted);'>Activos Hoy</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        avg_progress = 0
        if len(students_data) > 0:
            avg_progress = sum(s['progress'] for s in students_data) / len(students_data)
        
        st.markdown(f"""
        <div class='progress-widget'>
            <div style='color:#f59e0b; font-size:2rem; font-weight:700;'>{int(avg_progress)}%</div>
            <div style='font-size:0.9rem; color:var(--text-muted);'>Progreso Promedio</div>
        </div>
        """, unsafe_allow_html=True)

    # Barra de Herramientas + Añadir
    st.markdown("### Listado de Clase")
    
    # Formulario para agregar alumno (Toggleable)
    with st.expander("➕ Añadir Nuevo Alumno", expanded=False):
        with st.form("add_student_form"):
            c_add1, c_add2 = st.columns(2)
            new_name = c_add1.text_input("Nombre completo")
            new_user = c_add1.text_input("Nombre de usuario (Login)")
            new_email = c_add2.text_input("Email")
            new_pass = c_add2.text_input("Contraseña", value="1234", type="password")
            
            if st.form_submit_button("Guardar Alumno"):
                if new_name and new_user and new_email:
                    add_user(new_user, new_pass, new_name, new_email, role='student')
                    st.success("Alumno creado correctamente")
                    st.rerun()
                else:
                    st.error("Rellena todos los campos")

    tb_col1, tb_col2 = st.columns([3, 1])
    with tb_col1:
        search = st.text_input("🔍 Buscar...", key="student_search", label_visibility="collapsed", placeholder="Buscar estudiante...")
    
    # Tabla de Alumnos
    st.divider()
    h_c1, h_c2, h_c3, h_c4 = st.columns([3, 2, 2, 1])
    h_c1.markdown("**Estudiante**")
    h_c2.markdown("**Progreso**")
    h_c3.markdown("**Estado**")
    h_c4.markdown("**Acciones**")
    st.divider()

    for student in students_data:
        if not search or search.lower() in student['name'].lower() or student['email'] and search.lower() in student['email'].lower():
            r_c1, r_c2, r_c3, r_c4 = st.columns([3, 2, 2, 1])
            
            with r_c1:
                st.markdown(f"""
                <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                    <div class='student-avatar'>{student['name'][0]}</div>
                    <div style='margin-left: 10px;'>
                        <div style='font-weight: 600; color: var(--text-main);'>{student['name']}</div>
                        <div style='font-size: 0.8rem; color: var(--text-muted);'>{student.get('email', '')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with r_c2:
                prog = student.get('progress', 0)
                st.progress(prog / 100)
                st.caption(f"{prog}% Completado")
            
            with r_c3:
                status = student.get('status', 'Inactivo')
                status_color = "#10b981" if status == "Activo" else "#ef4444"
                last_acc = student.get('last_access', 'Nunca')
                
                st.markdown(f"""
                <div>
                    <span class='status-badge' style='background: {status_color}20; color: {status_color}; border: 1px solid {status_color}40;'>● {status}</span>
                    <div style='font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;'>{last_acc}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with r_c4:
                # Delete functionality
                if st.button("🗑️", key=f"del_{student['id']}", help="Eliminar Alumno"):
                    delete_user(student['id'])
                    st.rerun()
            
            st.markdown("<div style='height: 1px; background: var(--border); margin: 5px 0 15px 0;'></div>", unsafe_allow_html=True)

# Lógica de ruteo para Configuración (Admin Panel)
elif menu == "Configuración":
    render_admin_panel(config)
# Footer
st.markdown("---")
st.markdown("<div class='footer'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"### {config['footer']['contact']['title']}")
    st.write(config['footer']['contact']['email'])
with col2:
    st.markdown(f"### {config['footer']['social']['title']}")
    st.write(config['footer']['social']['text'])
with col3:
    st.markdown(f"### {config['footer']['support']['title']}")
    st.write(config['footer']['support']['text'])
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div style='text-align: center; margin-top: 2rem; color: #888; padding: 2rem;'>&copy; 2026 TUTOR IA. Todos los derechos reservados.</div>", unsafe_allow_html=True)
