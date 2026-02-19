import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN
st.set_page_config(page_title="Elden Ring Checklist Pro", layout="centered")

# ESTILO MEJORADO
st.markdown("""
    <style>
    .stCheckbox { background-color: #1a1a1a; padding: 12px; border-radius: 10px; margin-bottom: 5px; border: 1px solid #333; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a1a; border-radius: 5px 5px 0 0; padding: 10px 20px; color: #c19a6b; }
    .stTabs [aria-selected="true"] { background-color: #c19a6b !important; color: #000 !important; }
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

if not user_name:
    st.info("⚠️ Ingresa tu nombre en la barra lateral para cargar tu progreso.")
else:
    # 2. LEER PROGRESO DE LA NUBE
    df_progreso = conn.read(ttl=0)
    
    if not df_progreso.empty and 'Usuario' in df_progreso.columns:
        user_progress = df_progreso[df_progreso['Usuario'] == user_name]
        hechos_ids = set(user_progress['ID'].astype(str))
    else:
        hechos_ids = set()

    # 3. MÉTRICAS
    total = len(df_fijo)
    completados = len(hechos_ids)
    st.write(f"### Guerrero: {user_name}")
    st.progress(completados / total if total > 0 else 0)
    st.write(f"Misiones completadas: {completados} de {total}")

    # 4. PESTAÑAS
    tab_pendientes, tab_completadas = st.tabs(["⚔️ Senda del Guerrero", "🏆 Salón de los Héroes"])

    with tab_pendientes:
        # Filtros de Región y Categoría
        col1, col2 = st.columns(2)
        with col1:
            reg_sel = st.selectbox("🌍 Región", sorted(df_fijo['Región'].unique()), key="reg_pend")
        with col2:
            cats = sorted(df_fijo[df_fijo['Región'] == reg_sel]['Categoría'].unique())
            cat_sel = st.selectbox("🏷️ Categoría", cats, key="cat_pend")

        df_view = df_fijo[(df_fijo['Región'] == reg_sel) & (df_fijo['Categoría'] == cat_sel)]

        with st.form("form_pendientes"):
            check_status = {}
            for idx, row in df_view.iterrows():
                id_str = str(idx)
                ya_hecho = id_str in hechos_ids
                
                # Solo mostramos lo que NO está hecho en esta pestaña
                if not ya_hecho:
                    check_status[idx] = st.checkbox(row['Nombre'], key=f"p_{idx}")
                    with st.expander("📍 Ubicación"):
                        st.write(row['Ubicación / Detalle / Acción'])

            if st.form_submit_button("💾 MARCAR COMO COMPLETADAS"):
                # Mantener datos de otros usuarios
                df_otros = df_progreso[df_progreso['Usuario'] != user_name] if not df_progreso.empty else pd.DataFrame()
                
                # Nuevos datos: Lo que ya estaba hecho + lo nuevo que se marcó
                nuevos_datos = []
                # Re-agregamos lo que ya estaba hecho
                for idx_base, row_base in df_fijo.iterrows():
                    if str(idx_base) in hechos_ids:
                        nuevos_datos.append({"Usuario": user_name, "ID": str(idx_base), "Nombre": row_base['Nombre'], "Completado": True})
                
                # Agregamos lo nuevo marcado en el formulario
                for id_form, valor in check_status.items():
                    if valor:
                        nuevos_datos.append({"Usuario": user_name, "ID": str(id_form), "Nombre": df_fijo.loc[id_form, 'Nombre'], "Completado": True})
                
                df_final = pd.concat([df_otros, pd.DataFrame(nuevos_datos)], ignore_index=True)
                conn.update(data=df_final)
                st.success("¡Misiones añadidas a tu leyenda!")
                st.rerun()

    with tab_completadas:
        st.write("### Tus Victorias")
        # Mostrar lo que ya está en hechos_ids
        if not hechos_ids:
            st.write("Aún no has registrado victorias.")
        else:
            df_done = df_fijo[df_fijo.index.map(str).isin(hechos_ids)]
            for _, row in df_done.iterrows():
                st.markdown(f"✅ **{row['Nombre']}** ({row['Región']})")
            
            if st.button("🗑️ Reiniciar mi progreso (Cuidado)"):
                df_otros = df_progreso[df_progreso['Usuario'] != user_name]
                conn.update(data=df_otros)
                st.warning("Progreso borrado.")
                st.rerun()
