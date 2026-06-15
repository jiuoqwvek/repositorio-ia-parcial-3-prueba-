import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("Monitoring - Agente Metro")

if st.button("Cargar métricas"):
    try:
        r = requests.get(f"{BACKEND_URL}/api/metrics", timeout=10)
        if r.status_code == 200:
            st.json(r.json())
        else:
            st.error("No se pudieron obtener métricas")
    except Exception as e:
        st.error(f"Error: {e}")

if st.button("Cargar logs (últimos 10)"):
    try:
        r = requests.get(f"{BACKEND_URL}/api/logs?limit=10", timeout=10)
        if r.status_code == 200:
            st.write(r.json().get("logs", []))
        else:
            st.error("No se pudieron obtener logs")
    except Exception as e:
        st.error(f"Error: {e}")
