import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN
st.set_page_config(page_title="Elden Ring Multi-User Checklist", layout="centered")

# ESTILO
st.markdown("<style>.stCheckbox { background-color: #1a1a1a; padding: 10px; border-radius: 8px; }</style>", unsafe_allow_html=True)

# 1. CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data
def load_base_data():
    return pd.read_csv('guia_rapida.csv')

df_fijo = load_base_data()

st.title("⚔️ Elden Ring Checklist Pro")

# --- SISTEMA DE LOGIN SIMPLE ---
st.sidebar.title("👤 Sesión")
user_name = st.sidebar.text_input("Ingresa tu Gamer Tag:", placeholder="Ej: Luis_Elden")

if not user_name:
    st.info("⚠️ Por favor, ingresa tu nombre en la barra lateral para ver tu progreso individual.")
else:
    # 2. LEER PROGRESO DE LA NUBE
    df_progreso = conn.read(ttl=0)
    
    # Filtrar el progreso solo para el usuario actual
    if not df_progreso.empty and 'Usuario' in df_progreso.columns:
        user_progress = df_progreso[df_progreso['Usuario'] == user_name]
        hechos_ids = set(user_progress['ID'].astype(str))
    else:
        hechos_ids = set()

    # 3. CÁLCULO DE PROGRESO INDIVIDUAL
    total = len(df_fijo)
    completados = len(hechos_ids)
    porcentaje = completados / total if total > 0 else 0

    st.write(f"### Guerrero: {user_name}")
    st.metric("Tu Progreso Individual", f"{int(porcentaje*100)}%", f"{completados} de {total}")
    st.progress(porcentaje)

    # 4. FILTROS Y LISTA
    reg_sel = st.selectbox("🌍 Región", sorted(df_fijo['Región'].unique()))
    df_view = df_fijo[df_fijo['Región'] == reg_sel]

    with st.form("planilla_progreso"):
        st.write(f"📌 {reg_sel}")
        check_status = {}
        
        for idx, row in df_view.iterrows():
            ya_hecho = str(idx) in hechos_ids
            check_status[idx] = st.checkbox(row['Nombre'], value=ya_hecho, key=f"c_{idx}_{user_name}")
            
        if st.form_submit_button("💾 GUARDAR MI PROGRESO"):
            # Mantener el progreso de OTROS usuarios
            if not df_progreso.empty:
                df_otros = df_progreso[df_progreso['Usuario'] != user_name]
            else:
                df_otros = pd.DataFrame(columns=['Usuario', 'ID', 'Nombre', 'Completado'])

            # Crear el progreso del usuario ACTUAL
            nuevos_datos_usuario = []
            for id_obj, valor in check_status.items():
                if valor:
                    nuevos_datos_usuario.append({
                        "Usuario": user_name,
                        "ID": str(id_obj),
                        "Nombre": df_fijo.loc[id_obj, 'Nombre'],
                        "Completado": True
                    })
            
            df_actualizado = pd.concat([df_otros, pd.DataFrame(nuevos_datos_usuario)], ignore_index=True)
            
            # Subir todo a la nube
            conn.update(data=df_actualizado)
            st.success(f"¡Progreso de {user_name} guardado con éxito!")
            st.rerun()
