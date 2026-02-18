import streamlit as st
import pandas as pd

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Elden Ring Checklist", layout="centered")

# ESTILO OSCURO Y DORADO (Muy Elden Ring)
st.markdown("""
    <style>
    .main { background-color: #0f0f0f; color: #d4af37; }
    .stCheckbox { background-color: #1a1a1a; padding: 12px; border-radius: 10px; border: 1px solid #333; margin-bottom: 5px; }
    .stProgress > div > div > div > div { background-color: #c19a6b; }
    h1, h2, h3 { color: #c19a6b !important; }
    </style>
    """, unsafe_allow_html=True)

# CARGA DE DATOS
@st.cache_data
def load_data():
    return pd.read_csv('guia_rapida.csv')

df = load_data()

# INICIALIZAR EL PROGRESO EN LA SESIÓN
if 'completados' not in st.session_state:
    st.session_state.completados = set()

# --- TÍTULO Y BARRA DE PROGRESO ---
st.title("⚔️ Elden Ring Checklist")

total_puntos = len(df)
hechos = len(st.session_state.completados)
porcentaje = hechos / total_puntos if total_puntos > 0 else 0

st.write(f"**Tu Progreso:** {int(porcentaje*100)}% ({hechos}/{total_puntos})")
st.progress(porcentaje)

# --- FILTROS ---
regiones = sorted(df['Región'].unique())
reg_sel = st.selectbox("🌍 Región", ["-- Elige una --"] + regiones)

if reg_sel != "-- Elige una --":
    df_reg = df[df['Región'] == reg_sel]
    
    # CONTADORES DINÁMICOS
    # Esto cuenta cuántas cosas hay de cada categoría SOLO en la región elegida
    conteos = df_reg['Categoría'].value_counts()
    cat_opciones = [f"{cat} ({conteos[cat]})" for cat in conteos.index]
    
    cat_sel_raw = st.selectbox("🏷️ Categoría", ["-- Elige una --"] + cat_opciones)
    
    if cat_sel_raw != "-- Elige una --":
        # Extraemos el nombre real de la categoría (quitando el número)
        cat_real = cat_sel_raw.split(" (")[0]
        df_final = df_reg[df_reg['Categoría'] == cat_real]
        
        st.write(f"### {cat_real}")
        
        # LISTADO DE ITEMS
        for idx, row in df_final.iterrows():
            key = f"check_{idx}"
            # Al marcar, se guarda en la memoria de la sesión
            is_checked = st.checkbox(row['Nombre'], key=key, value=(idx in st.session_state.completados))
            
            if is_checked:
                st.session_state.completados.add(idx)
            else:
                st.session_state.completados.discard(idx)
            
            with st.expander("📍 Ubicación y Detalles"):
                st.write(row['Ubicación / Detalle / Acción'])
else:
    st.info("Explora las tierras intermedias seleccionando una región.")
