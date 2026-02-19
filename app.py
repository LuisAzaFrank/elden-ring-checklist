import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN
st.set_page_config(page_title="Elden Ring Pro Tracker", layout="centered")

# ESTILO
st.markdown("""
    <style>
    .stCheckbox { background-color: #1a1a1a; padding: 10px; border-radius: 8px; margin-bottom: 5px; }
    .done-text { color: #888; text-decoration: line-through; }
    </style>
    """, unsafe_allow_html=True)

# 1. CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data
def load_base_data():
    return pd.read_csv('guia_rapida.csv')

df_fijo = load_base_data()

st.title("⚔️ Elden Ring Checklist Pro")

# --- BARRA LATERAL ---
st.sidebar.title("👤 Sesión")
user_name = st.sidebar.text_input("Ingresa tu Gamer Tag:", placeholder="Ej: Luis_Elden")

# NUEVA FUNCIÓN: Filtro para ocultar completados
hide_completed = st.sidebar.toggle("Ocultar misiones completadas")

if not user_name:
    st.info("⚠️ Ingresa tu nombre en la barra lateral para empezar.")
else:
    # 2. LEER PROGRESO
    df_progreso = conn.read(ttl=0)
    
    if not df_progreso.empty and 'Usuario' in df_progreso.columns:
        user_progress = df_progreso[df_progreso['Usuario'] == user_name]
        hechos_ids = set(user_progress['ID'].astype(str))
    else:
        hechos_ids = set()

    # 3. PROGRESO
    total = len(df_fijo)
    completados = len(hechos_ids)
    st.write(f"### Guerrero: {user_name}")
    st.progress(completados / total if total > 0 else 0)
    st.write(f"Misiones completadas: {completados} de {total}")

    # 4. FILTROS DE REGIÓN
    reg_sel = st.selectbox("🌍 Región", sorted(df_fijo['Región'].unique()))
    df_view = df_fijo[df_fijo['Región'] == reg_sel]

    # --- LISTADO DINÁMICO ---
    with st.form("planilla_progreso"):
        st.write(f"📌 {reg_sel}")
        check_status = {}
        
        for idx, row in df_view.iterrows():
            id_str = str(idx)
            ya_hecho = id_str in hechos_ids
            
            # Lógica de Filtrado: Si el usuario quiere ocultar hechos, nos saltamos esta misión
            if hide_completed and ya_hecho:
                continue
            
            # Indicativo visual: Añadimos una medalla si ya está hecho
            label = f"🎖️ {row['Nombre']} (Hecho)" if ya_hecho else row['Nombre']
            
            check_status[idx] = st.checkbox(label, value=ya_hecho, key=f"c_{idx}_{user_name}")
            
            with st.expander("📍 Detalles"):
                st.write(row['Ubicación / Detalle / Acción'])
        
        if st.form_submit_button("💾 GUARDAR MI PROGRESO"):
            # Lógica para no borrar a otros usuarios
            if not df_progreso.empty:
                df_otros = df_progreso[df_progreso['Usuario'] != user_name]
            else:
                df_otros = pd.DataFrame(columns=['Usuario', 'ID', 'Nombre', 'Completado'])

            nuevos_datos = []
            for id_obj, valor in check_status.items():
                if valor:
                    nuevos_datos.append({
                        "Usuario": user_name,
                        "ID": str(id_obj),
                        "Nombre": df_fijo.loc[id_obj, 'Nombre'],
                        "Completado": True
                    })
            
            # Unimos los datos nuevos con los de los demás usuarios
            df_actualizado = pd.concat([df_otros, pd.DataFrame(nuevos_datos)], ignore_index=True)
            conn.update(data=df_actualizado)
            st.success("¡Progreso actualizado!")
            st.rerun()
