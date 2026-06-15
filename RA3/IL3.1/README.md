IL3.1 - Herramientas de Observabilidad

Arquitectura y archivos relevantes:
- RA3/IL3.1/dashboard.py        # Streamlit + Plotly para visualizaciones
- RA3/IL3.1/config_logging.py   # Configuración de logging central

Cómo verificar:
1. Ejecuta el agente para generar logs: python agente_metro.py
2. Abre el dashboard: streamlit run dashboard.py
3. Verifica que los gráficos muestren latencia, errores y uso de RAM.
