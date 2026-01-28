# 📚 Plataforma de Formación Online

Una plataforma educativa moderna con diseño flat design, colores vibrantes y textos completamente editables.

## 🎨 Características del Diseño

- **Colores vibrantes**: Azul (#4A90E2), Amarillo (#FFD93D), Verde (#4CAF50), Rosa (#FF6B9D)
- **Ilustraciones flat design** personalizadas
- **Diseño moderno** con bordes redondeados, sombras suaves y gradientes
- **Responsive** y optimizado para diferentes pantallas
- **Textos editables** desde archivo de configuración

## 📁 Estructura del Proyecto

```
plataforma_formacion/
├── app.py              # Aplicación principal de Streamlit
├── config.json         # Archivo de configuración con todos los textos
├── assets/             # Carpeta de recursos visuales
│   ├── hero_illustration.png
│   ├── module1.png
│   ├── module2.png
│   └── module3.png
└── README.md           # Este archivo
```

## 🚀 Cómo Ejecutar

1. Asegúrate de tener Streamlit instalado:
   ```bash
   pip install streamlit
   ```

2. Ejecuta la aplicación:
   ```bash
   streamlit run app.py
   ```

3. Abre tu navegador en: http://localhost:8501

## ✏️ Cómo Editar los Textos

Todos los textos de la aplicación se pueden editar desde el archivo `config.json`. Este archivo está organizado en secciones:

### Configuración de la Aplicación
```json
"app_config": {
  "page_title": "Plataforma de Formación Online",
  "page_icon": "📚",
  "logo_caption": "Tu Academia Digital"
}
```

### Hero Section (Sección Principal)
```json
"hero": {
  "title": "Aprende a tu ritmo",
  "subtitle": "Descubre el futuro de la educación online",
  "highlight_text": "educación online",
  "description": "Plataforma completa de formación...",
  "cta_primary": "Comenzar ahora",
  "cta_secondary": "Ver cursos"
}
```

### Módulos del Curso
```json
"modules": {
  "module1": {
    "tab_title": "Módulo 1",
    "title": "Introducción",
    "content": "Bienvenido al primer módulo..."
  }
}
```

### Footer
```json
"footer": {
  "contact": {
    "title": "Contacto",
    "email": "📧 contacto@plataforma.com"
  }
}
```

## 🎨 Cómo Cambiar los Colores

Los colores están definidos en el CSS dentro de `app.py`. Busca la sección `:root` y modifica las variables:

```css
:root {
    --primary-blue: #4A90E2;      /* Azul principal */
    --accent-yellow: #FFD93D;     /* Amarillo de acentos */
    --accent-green: #4CAF50;      /* Verde de acentos */
    --accent-pink: #FF6B9D;       /* Rosa de acentos */
}
```

## 🖼️ Cómo Cambiar las Ilustraciones

1. Reemplaza las imágenes en la carpeta `assets/`:
   - `hero_illustration.png` - Ilustración principal
   - `module1.png` - Icono del Módulo 1
   - `module2.png` - Icono del Módulo 2
   - `module3.png` - Icono del Módulo 3

2. Mantén el mismo nombre de archivo o actualiza las referencias en `app.py`

## 📝 Secciones Disponibles

1. **📚 Contenido** - Módulos del curso con tabs
2. **🤖 Tutor AI** - Asistente inteligente con chat, generación de tests y trabajos
3. **📝 Formularios** - Formulario de contacto con validación
4. **📤 Archivos** - Sistema de carga de archivos
5. **🎨 Diseño** - Ejemplos de layouts y componentes

## 🤖 Configuración del Tutor AI

El Tutor AI es un asistente inteligente que puede:
- 💬 Responder preguntas sobre el contenido cargado
- 📚 Procesar documentos grandes (PDF, DOCX, TXT)
- 📝 Generar tests personalizados
- ✍️ Realizar trabajos (ensayos, resúmenes, análisis)

### Paso 1: Obtener API Key de Google Gemini

1. Ve a https://makersuite.google.com/app/apikey
2. Inicia sesión con tu cuenta de Google
3. Haz clic en "Create API Key"
4. Copia la API key generada

### Paso 2: Configurar la API Key

1. Abre el archivo `.env` en la raíz del proyecto
2. Reemplaza `tu_api_key_aqui` con tu API key:
   ```
   GOOGLE_API_KEY=AIzaSy...tu_api_key_real
   ```
3. Guarda el archivo

### Paso 3: Reiniciar la Aplicación

1. Detén la aplicación (Ctrl+C)
2. Vuelve a ejecutar: `streamlit run app.py`
3. Ve a la sección "🤖 Tutor AI"

### Uso del Tutor AI

#### 💬 Chat
- Haz preguntas sobre cualquier tema
- Activa "Usar documentos cargados" para que busque en tus archivos
- El historial se mantiene durante la sesión

#### 📚 Documentos
- Carga archivos PDF, DOCX o TXT
- Soporta archivos grandes (>2GB)
- Los documentos se procesan y almacenan para búsqueda rápida
- Puedes eliminar documentos cuando quieras

#### 📝 Tests
- Especifica el tema del test
- Elige el número de preguntas (5-50)
- Selecciona la dificultad (Fácil, Medio, Difícil)
- Descarga el test generado en formato JSON

#### ✍️ Trabajos
- Describe el trabajo que necesitas
- Elige el tipo: Ensayo, Resumen, Análisis o Ejercicio
- El tutor generará el trabajo completo
- Descarga el resultado en formato TXT

### Costos

Google Gemini ofrece un tier gratuito generoso:
- 60 solicitudes por minuto
- 1,500 solicitudes por día
- Gratis para uso personal y educativo

Para más información: https://ai.google.dev/pricing

## 💡 Consejos

- **Edita solo `config.json`** para cambiar textos - no necesitas tocar el código
- **Guarda los cambios** en `config.json` y recarga la página (presiona `R` en Streamlit)
- **Usa emojis** en los textos para hacerlos más visuales
- **Mantén los textos cortos** para mejor legibilidad

## 🛠️ Personalización Avanzada

Si quieres personalizar más allá de los textos:

1. **Estilos CSS**: Edita la sección `st.markdown("""<style>...</style>""")` en `app.py`
2. **Layout**: Modifica las columnas y secciones en el código principal
3. **Componentes**: Añade nuevos elementos de Streamlit según necesites

## 📞 Soporte

Para más información sobre Streamlit, visita: https://docs.streamlit.io

---

¡Disfruta de tu plataforma de formación! 🎓
