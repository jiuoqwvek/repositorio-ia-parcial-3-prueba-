import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Agente Metro - UI", layout="wide")

st.title("Agente Metro - Interfaz")

with st.form("query_form"):
    q = st.text_input("Consulta", "¿Cuál es la tarifa a las 8:00?")
    submitted = st.form_submit_button("Enviar")

if submitted and q:
    with st.spinner("Consultando agente..."):
        try:
            r = requests.post(f"{BACKEND_URL}/api/query", json={"query": q}, timeout=30)
            if r.status_code == 200:
                st.markdown("**Respuesta:**")
                st.write(r.json().get("response"))
            else:
                st.error(f"Error del backend: {r.status_code} - {r.text}")
        except Exception as e:
            st.error(f"Error al conectar con backend: {e}")

if st.button("Actualizar métricas"):
    try:
        r = requests.get(f"{BACKEND_URL}/api/metrics", timeout=10)
        if r.status_code == 200:
            st.json(r.json())
        else:
            st.error("No se pudieron obtener métricas")
    except Exception as e:
        st.error(f"Error: {e}")
