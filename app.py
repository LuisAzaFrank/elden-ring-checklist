import streamlit as st
import pandas as pd

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Elden Ring Checklist", layout="centered")

# DISEÑO MÓVIL (DARK GOLD)
st.markdown("""
    <style>
    .main { background-color: #0f0f0f; color: #d4af37; }
    .stCheckbox { 
        background-color: #1a1a1a; 
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #333; 
        margin-bottom: 8px; 
    }
    .stProgress > div > div > div > div { background-color: #d4af37; }
    h1, h2, h3 { color: #c19a6b !important; }
    </style>
    """, unsafe_allow_html=True)

# CARGA DE DATOS
@st.cache_data
def load_data():
    # Asegúrate de que este nombre coincida con tu archivo en GitHub
    return pd.read_csv('guia_rapida.csv')

df = load_data()

# INICIALIZAR ESTADO DE CHECKS
if 'checks' not in st.session_state:
    st.session_state.checks = {}

# --- TÍTULO Y BARRA DE PROGRESO ---
st.title("⚔️ Elden Ring Checklist")

# Calcular progreso
total_items = len(df)
items_completados = sum(st.session_state.checks.values())
porcentaje = items_completados / total_items if total_items > 0 else 0

st.write(f"**Progreso Total:** {int(porcentaje*100)}% ({items_completados}/{total_items})")
st.progress(porcentaje)

# --- FILTROS ---
regiones = sorted(df['Región'].unique())
region_sel = st.selectbox("🌍 Selecciona Región", ["-- Elige una --"] + regiones)

if region_sel != "-- Elige una --":
    df_reg = df[df['Región'] == region_sel]
    
    # CONTADORES EN CATEGORÍAS
    # Contamos cuántos elementos hay de cada categoría en la región elegida
    counts = df_reg['Categoría'].value_counts()
    opciones_cat = [f"{cat} ({counts[cat]})" for cat in counts.index]
    
    cat_sel_raw = st.selectbox("🏷️ Categoría", ["-- Elige una --"] + opciones_cat)
    
    if cat_sel_raw != "-- Elige una --":
        # Extraer el nombre de la categoría ignorando el número entre paréntesis
        cat_sel = cat_sel_raw.split(" (")[0]
        df_final = df_reg[df_reg['Categoría'] == cat_sel]
        
        st.markdown(f"### {cat_sel}")
        
        # MOSTRAR ELEMENTOS
        for idx, row in df_final.iterrows():
            # Crear clave única para el checkbox
            key = f"item_{idx}"
            
            # Dibujar checkbox y actualizar estado
            st.session_state.checks[idx] = st.checkbox(
                row['Nombre'], 
                value=st.session_state.checks.get(idx, False),
                key=key
            )
            
            with st.expander("📍 Ver ubicación/nota"):
                st.write(row['Ubicación / Detalle / Acción'])
else:
    st.info("Selecciona una región para ver tu progreso.")
            # Aquí puedes agregar más columnas si decides robustecer el CSV
            st.markdown("---")
