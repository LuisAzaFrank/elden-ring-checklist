import streamlit as st
import pandas as pd
import os

# CONFIGURACIÓN DE PÁGINA "ESTILO GAMER"
st.set_page_config(
    page_title="Elden Ring Ultimate Tracker",
    page_icon="⚔️",
    layout="wide"
)

# CSS PERSONALIZADO (Diseño Dark Gold)
st.markdown("""
    <style>
    .main { background-color: #0b0b0b; color: #d4af37; }
    .stCheckbox { background-color: #1a1a1a; padding: 20px; border-radius: 15px; border: 1px solid #333; margin-bottom: 10px; transition: 0.3s; }
    .stCheckbox:hover { border: 1px solid #d4af37; background-color: #252525; }
    h1, h2, h3 { color: #c19a6b !important; font-family: 'Georgia', serif; }
    .stProgress > div > div > div > div { background-color: #d4af37; }
    </style>
    """, unsafe_allow_html=True)

# CARGA DE DATOS
@st.cache_data
def load_data():
    return pd.read_csv('guia_rapida.csv')

df = load_data()

# HEADER PROFESIONAL
st.title("⚔️ ELDEN RING CHECKLIST")
st.markdown("---")

# BARRA DE PROGRESO CON ESTILO
col_prog, col_stats = st.columns([2, 1])
with col_prog:
    total = len(df)
    # Aquí el progreso se guardará en la sesión del navegador
    if 'checks' not in st.session_state: st.session_state.checks = {}
    hechos = sum(st.session_state.checks.values())
    st.write(f"### Tu Senda hacia el Trono: {int((hechos/total)*100)}%")
    st.progress(hechos/total)

# FILTROS LATERALES
st.sidebar.header("🗺️ MAPA DE GRACIA")
region = st.sidebar.selectbox("Región", sorted(df['Región'].unique()))
categoria = st.sidebar.radio("Categoría", sorted(df['Categoría'].unique()))

# VISTA DE CONTENIDO ROBUSTO
df_view = df[(df['Región'] == region) & (df['Categoría'] == categoria)]

st.subheader(f"📍 {region} - {categoria}")

for idx, row in df_view.iterrows():
    with st.container():
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            st.session_state.checks[idx] = st.checkbox("", key=f"check_{idx}")
        with col2:
            st.markdown(f"### {row['Nombre']}")
            st.write(f"**Descripción/Ubicación:** {row['Ubicación / Detalle / Acción']}")
            # Aquí puedes agregar más columnas si decides robustecer el CSV
            st.markdown("---")
