import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN PRO
st.set_page_config(page_title="Elden Ring Pro Checklist", layout="centered")

# ESTILO
st.markdown("<style>.stCheckbox { background-color: #1a1a1a; padding: 10px; border-radius: 8px; }</style>", unsafe_allow_html=True)

# 1. CONEXIÓN A LA NUBE
conn = st.connection("gsheets", type=GSheetsConnection)

# Cargar base de datos local y progreso de la nube
@st.cache_data
def load_base_data():
    return pd.read_csv('guia_rapida.csv')

df_fijo = load_base_data()
df_progreso = conn.read(ttl=0) # ttl=0 para que siempre lea lo más nuevo

st.title("⚔️ Elden Ring Checklist")

# 2. CÁLCULO DE PROGRESO REAL
total = len(df_fijo)
# Si la hoja está vacía, creamos un set vacío
hechos_ids = set(df_progreso['ID'].astype(str)) if not df_progreso.empty else set()
porcentaje = len(hechos_ids) / total

st.metric("Progreso Guardado", f"{int(porcentaje*100)}%", f"{len(hechos_ids)} de {total}")
st.progress(porcentaje)

# 3. FILTROS
reg_sel = st.selectbox("🌍 Región", sorted(df_fijo['Región'].unique()))
df_view = df_fijo[df_fijo['Región'] == reg_sel]

# 4. LISTADO CON GUARDADO
with st.form("planilla_progreso"):
    st.write(f"### {reg_sel}")
    check_status = {}
    
    for idx, row in df_view.iterrows():
        # Verificamos si ya está marcado en la nube
        ya_hecho = str(idx) in hechos_ids
        check_status[idx] = st.checkbox(row['Nombre'], value=ya_hecho, key=f"c_{idx}")
        
    if st.form_submit_button("💾 GUARDAR CAMBIOS EN LA NUBE"):
        # Creamos el nuevo DataFrame de progreso
        nuevos_datos = []
        for id_obj, valor in check_status.items():
            if valor:
                # Solo guardamos los que están marcados para ahorrar espacio
                nuevos_datos.append({"ID": str(id_obj), "Nombre": df_fijo.loc[id_obj, 'Nombre'], "Completado": True})
        
        # Actualizamos Google Sheets
        df_update = pd.DataFrame(nuevos_datos)
        conn.update(data=df_update)
        st.success("¡Progreso tatuado en la nube con éxito!")
        st.rerun()
