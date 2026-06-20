import streamlit as st
import requests
import base64

# ==============================================================================
# ⚙️ CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
# ==============================================================================
st.set_page_config(page_title="ISPC | Repositorio de Emergencia", page_icon="🎓", layout="centered")

# CSS Personalizado para embellecer la interfaz
st.markdown("""
    <style>
        /* Estilos para títulos y textos */
        h1 { color: #009FE3; font-weight: 800; padding-bottom: 0; margin-bottom: 0;}
        .subtitulo { color: #555555; font-size: 1.1rem; margin-top: -10px; margin-bottom: 30px; }
        
        /* Estilos de botones */
        .stButton>button {
            background-color: #009FE3;
            color: white;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: bold;
            border: none;
            transition: all 0.3s ease 0s;
            width: 100%;
        }
        .stButton>button:hover { background-color: #007bb5; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2); color: white;}
        
        /* Separadores y tarjetas */
        hr { margin-top: 2rem; margin-bottom: 2rem; border-color: #e0e0e0; }
        
        /* Pie de página */
        .footer { text-align: center; margin-top: 50px; padding-top: 20px; font-size: 14px; color: #888; border-top: 1px solid #eaeaea; font-family: monospace;}
        .footer b { color: #009FE3; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 🛠️ CONFIGURACIÓN DE GITHUB (PEGÁ TUS DATOS ACÁ)
# ==============================================================================

# Si usaste secrets.toml, descomentá la línea de abajo y borrá la otra.
# GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"] 

# Si preferís pegarlo directo (Acordate de usar .gitignore si subís el código):
# Ahora el token se lee de forma segura desde los secretos de Streamlit
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

REPO_NAME = "Gdicampli22/materialispc"  # Ej: "gaston/material-ispc"
BRANCH = "main"

# ==============================================================================
# 🎨 INTERFAZ GRÁFICA: ENCABEZADO
# ==============================================================================

col1, col2 = st.columns([1, 3])
with col1:
    try:
        # Intenta cargar el logo local
        st.image("logo_ispc.png", width=160)
    except:
        # Si no encuentra el archivo, muestra un aviso sin romper la app
        st.info("📌 Guardá el logo como 'logo_ispc.png' en esta carpeta para que se muestre aquí.")

with col2:
    st.markdown("<h1>Repositorio de Emergencia</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitulo'>Tecnicatura en Ciencia de Datos e Inteligencia Artificial</p>", unsafe_allow_html=True)

st.write("Seleccioná la materia para acceder al material de estudio o colaborar subiendo apuntes, resúmenes y trabajos para los coloquios.")

# ==============================================================================
# 📚 LÓGICA DE MATERIAS Y ARCHIVOS
# ==============================================================================

MATERIAS = [
    "Seleccione una materia...",
    "(A84310.CDIA) Modelos de IA",
    "(A84306.CDIA) Procesamiento de Imágenes",
    "(A84307.CDIA) Minería de Datos",
    "(A84309.CDIA) Técnicas de Procesamiento de Habla",
    "(A80206.CDIA) Práctica Profesionalizante II"
]

materia_seleccionada = st.selectbox("📌 Materia", MATERIAS, label_visibility="collapsed")

if materia_seleccionada != "Seleccione una materia...":
    carpeta_materia = materia_seleccionada.replace(" ", "_").replace("(", "").replace(")", "")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- SECCIÓN: SUBIR MATERIAL ---
    st.subheader(f"📤 Compartir material")
    st.caption(f"Subiendo a la carpeta: **{materia_seleccionada}**")
    
    archivos_subidos = st.file_uploader(
        "Arrastrá acá tus archivos (PDF, Word, Excel, Powerpoint):", 
        type=['pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt'],
        accept_multiple_files=True 
    )

    if archivos_subidos: 
        if st.button("🚀 Confirmar y subir archivos"):
            with st.spinner("Sincronizando con la nube..."):
                todos_exitosos = True
                
                for archivo_subido in archivos_subidos:
                    nombre_archivo = archivo_subido.name
                    ruta_github = f"{carpeta_materia}/{nombre_archivo}"
                    url_api = f"https://api.github.com/repos/{REPO_NAME}/contents/{ruta_github}"

                    headers = {
                        "Authorization": f"token {GITHUB_TOKEN}",
                        "Accept": "application/vnd.github.v3+json"
                    }

                    contenido_base64 = base64.b64encode(archivo_subido.getvalue()).decode("utf-8")

                    datos = {
                        "message": f"Aporte de material: {nombre_archivo}",
                        "content": contenido_base64,
                        "branch": BRANCH
                    }

                    res_check = requests.get(url_api, headers=headers)
                    if res_check.status_code == 200:
                        datos["sha"] = res_check.json()["sha"]

                    res_put = requests.put(url_api, headers=headers, json=datos)

                    if res_put.status_code in [200, 201]:
                        st.success(f"✅ **{nombre_archivo}** subido correctamente.")
                    else:
                        st.error(f"❌ Error con '{nombre_archivo}': {res_put.json().get('message', 'Error desconocido')}")
                        todos_exitosos = False
                
                if todos_exitosos:
                    st.balloons()

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- SECCIÓN: DESCARGAR MATERIAL ---
    st.subheader(f"📥 Material disponible para descargar")
    
    with st.spinner("Buscando archivos disponibles..."):
        url_listar = f"https://api.github.com/repos/{REPO_NAME}/contents/{carpeta_materia}?ref={BRANCH}"
        headers_listar = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
        
        res_list = requests.get(url_listar, headers=headers_listar)

    if res_list.status_code == 200:
        archivos = res_list.json()
        archivos_validos = [f for f in archivos if f["type"] == "file"]

        if not archivos_validos:
            st.info("📭 Aún no hay archivos para esta materia. ¡Sé el primero en colaborar!")
        else:
            # Usamos un expander para que la lista no se haga eterna si hay muchos apuntes
            with st.expander("📚 Ver apuntes disponibles", expanded=True):
                for arc in archivos_validos:
                    col_file, col_btn = st.columns([4, 1])
                    with col_file:
                        st.write(f"📄 **{arc['name']}**")
                    with col_btn:
                        st.markdown(f"<a href='{arc['download_url']}' target='_blank' style='text-decoration: none;'><button style='padding: 5px 10px; border-radius: 5px; background-color: #f0f2f6; border: 1px solid #ccc; cursor: pointer; width: 100%; text-align: center; color: #333;'>Descargar</button></a>", unsafe_allow_html=True)
    elif res_list.status_code == 404:
        st.info("📭 Aún no hay archivos subidos para esta materia. ¡Colaborá subiendo el primero!")
    else:
        st.error("⚠️ No se pudo conectar con el repositorio. Verificá tu Token y el nombre del Repositorio.")

# ==============================================================================
# ✒️ FOOTER / CRÉDITOS
# ==============================================================================
st.markdown("<div class='footer'>Desarrollado para la comunidad de alumnos del ISPC <b>by Gdicampli</b></div>", unsafe_allow_html=True)