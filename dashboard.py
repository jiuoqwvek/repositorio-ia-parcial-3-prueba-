"""
Dashboard de Monitoreo - Agente Inteligente del Metro de Santiago
Visualiza métricas de latencia, errores y uso de recursos
Requisito: IE5 - Dashboard de Monitoreo
"""

import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime, timedelta
import os

# ============================================================================
# CONFIGURACIÓN DE STREAMLIT
# ============================================================================

st.set_page_config(
    page_title="Dashboard Metro Santiago",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    h1 {
        color: #1f77b4;
        text-align: center;
    }
    h2 {
        color: #ff7f0e;
        border-bottom: 2px solid #ff7f0e;
        padding-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# FUNCIONES DE CARGA DE DATOS
# ============================================================================

@st.cache_data
def cargar_logs():
    """Carga el archivo agent_logs.jsonl y lo convierte a DataFrame."""
    logs_path = Path("./logs/agent_logs.jsonl")
    
    if not logs_path.exists():
        st.warning("No se encontró el archivo de logs. Ejecuta primero agente_metro.py")
        return pd.DataFrame()
    
    try:
        logs = []
        with open(logs_path, "r", encoding="utf-8") as f:
            for linea in f:
                if linea.strip():
                    logs.append(json.loads(linea))
        
        df = pd.DataFrame(logs)
        
        # Convertir timestamp a datetime
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        return df
    except Exception as e:
        st.error(f"Error al cargar logs: {e}")
        return pd.DataFrame()

def obtener_estadisticas(df):
    """Calcula estadísticas generales de los logs."""
    if df.empty:
        return {
            "total_herramientas": 0,
            "latencia_promedio": 0,
            "latencia_max": 0,
            "uso_ram_promedio": 0,
            "total_errores": 0,
            "tasa_error": 0
        }
    
    stats = {
        "total_herramientas": len(df),
        "latencia_promedio": df["latency_seconds"].mean() if "latency_seconds" in df.columns else 0,
        "latencia_max": df["latency_seconds"].max() if "latency_seconds" in df.columns else 0,
        "uso_ram_promedio": df["memory_usage_mb"].mean() if "memory_usage_mb" in df.columns else 0,
        "total_errores": df["error"].notna().sum(),
        "tasa_error": (df["error"].notna().sum() / len(df) * 100) if len(df) > 0 else 0
    }
    
    return stats

# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

st.title("🚇 Dashboard de Monitoreo - Agente Metro Santiago")
st.markdown("Análisis de Métricas, Trazabilidad y Rendimiento del Agente")

# Cargar datos
df = cargar_logs()

if df.empty:
    st.info("📊 En espera de datos. Ejecuta el agente con: `python agente_metro.py`")
else:
    # Obtener estadísticas
    stats = obtener_estadisticas(df)
    
    # ====================================================================
    # SECCIÓN 1: MÉTRICAS PRINCIPALES
    # ====================================================================
    
    st.markdown("## 📊 Métricas Principales")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric(
            label="Total de Operaciones",
            value=stats["total_herramientas"],
            delta=None
        )
    
    with col2:
        st.metric(
            label="Latencia Promedio (s)",
            value=f"{stats['latencia_promedio']:.4f}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Latencia Máxima (s)",
            value=f"{stats['latencia_max']:.4f}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="RAM Promedio (MB)",
            value=f"{stats['uso_ram_promedio']:.2f}",
            delta=None
        )
    
    with col5:
        st.metric(
            label="Total de Errores",
            value=int(stats["total_errores"]),
            delta=None
        )
    
    with col6:
        st.metric(
            label="Tasa de Error",
            value=f"{stats['tasa_error']:.1f}%",
            delta=None,
            delta_color="inverse"
        )
    
    # ====================================================================
    # SECCIÓN 2: GRÁFICOS DE LATENCIA
    # ====================================================================
    
    st.markdown("## ⚡ Análisis de Latencia")
    
    tab1, tab2 = st.tabs(["Latencia en Tiempo Real", "Distribución de Latencias"])
    
    with tab1:
        # Gráfico de línea de latencia en el tiempo
        if "timestamp" in df.columns and "latency_seconds" in df.columns:
            df_sorted = df.sort_values("timestamp")
            
            fig_latency = go.Figure()
            
            fig_latency.add_trace(go.Scatter(
                x=df_sorted["timestamp"],
                y=df_sorted["latency_seconds"],
                mode="lines+markers",
                name="Latencia (segundos)",
                line=dict(color="#1f77b4", width=2),
                marker=dict(size=5, color="#1f77b4", opacity=0.7)
            ))
            
            # Agregar promedio
            promedio = df_sorted["latency_seconds"].mean()
            fig_latency.add_hline(
                y=promedio,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Promedio: {promedio:.4f}s",
                annotation_position="right"
            )
            
            fig_latency.update_layout(
                title="Latencia de Herramientas en el Tiempo",
                xaxis_title="Timestamp",
                yaxis_title="Latencia (segundos)",
                hovermode="x unified",
                height=400
            )
            
            st.plotly_chart(fig_latency, use_container_width=True)
    
    with tab2:
        # Histograma de distribución de latencias
        if "latency_seconds" in df.columns:
            fig_dist = px.histogram(
                df,
                x="latency_seconds",
                nbins=20,
                title="Distribución de Latencias",
                labels={"latency_seconds": "Latencia (segundos)", "count": "Frecuencia"},
                color_discrete_sequence=["#1f77b4"]
            )
            
            fig_dist.update_layout(height=400)
            st.plotly_chart(fig_dist, use_container_width=True)
    
    # ====================================================================
    # SECCIÓN 3: ANÁLISIS DE ERRORES
    # ====================================================================
    
    st.markdown("## ⚠️ Análisis de Errores")
    
    col_err1, col_err2 = st.columns([1, 1])
    
    with col_err1:
        # Gráfico de barras: Errores por herramienta
        if "tool_name" in df.columns and "error" in df.columns:
            df_errores = df[df["error"].notna()].groupby("tool_name").size().reset_index(name="cantidad")
            
            if not df_errores.empty:
                fig_errors_by_tool = px.bar(
                    df_errores,
                    x="tool_name",
                    y="cantidad",
                    title="Errores por Herramienta",
                    labels={"tool_name": "Herramienta", "cantidad": "Cantidad de Errores"},
                    color="cantidad",
                    color_continuous_scale="Reds"
                )
                
                fig_errors_by_tool.update_layout(height=400)
                st.plotly_chart(fig_errors_by_tool, use_container_width=True)
            else:
                st.success("✓ No se han detectado errores")
    
    with col_err2:
        # Timeline de errores
        if "timestamp" in df.columns and "error" in df.columns:
            df_errores_timeline = df[df["error"].notna()].sort_values("timestamp")
            
            if not df_errores_timeline.empty:
                fig_errors_timeline = go.Figure()
                
                fig_errors_timeline.add_trace(go.Scatter(
                    x=df_errores_timeline["timestamp"],
                    y=[1] * len(df_errores_timeline),
                    mode="markers",
                    name="Errores",
                    marker=dict(size=10, color="red", symbol="x"),
                    text=df_errores_timeline["error"],
                    hovertemplate="<b>Error:</b><br>%{text}<br><b>Timestamp:</b> %{x}<extra></extra>"
                ))
                
                fig_errors_timeline.update_layout(
                    title="Timeline de Errores",
                    xaxis_title="Timestamp",
                    yaxis_title="",
                    height=400,
                    showlegend=False,
                    yaxis=dict(showticklabels=False)
                )
                
                st.plotly_chart(fig_errors_timeline, use_container_width=True)
            else:
                st.success("✓ No se han detectado errores en la timeline")
    
    # ====================================================================
    # SECCIÓN 4: USO DE RECURSOS
    # ====================================================================
    
    st.markdown("## 💾 Uso de Recursos (RAM)")
    
    col_ram1, col_ram2 = st.columns([1, 1])
    
    with col_ram1:
        # Gráfico de línea: RAM en el tiempo
        if "timestamp" in df.columns and "memory_usage_mb" in df.columns:
            df_sorted = df.sort_values("timestamp")
            
            fig_ram = go.Figure()
            
            fig_ram.add_trace(go.Scatter(
                x=df_sorted["timestamp"],
                y=df_ram["memory_usage_mb"],
                mode="lines+markers",
                name="Uso de RAM (MB)",
                line=dict(color="#2ca02c", width=2),
                fill="tozeroy",
                fillcolor="rgba(44, 160, 44, 0.2)"
            ))
            
            fig_ram.update_layout(
                title="Uso de RAM en el Tiempo",
                xaxis_title="Timestamp",
                yaxis_title="Uso de RAM (MB)",
                hovermode="x unified",
                height=400
            )
            
            st.plotly_chart(fig_ram, use_container_width=True)
    
    with col_ram2:
        # Box plot: Distribución de RAM por herramienta
        if "tool_name" in df.columns and "memory_usage_mb" in df.columns:
            fig_ram_box = px.box(
                df,
                x="tool_name",
                y="memory_usage_mb",
                title="Distribución de Uso de RAM por Herramienta",
                labels={"tool_name": "Herramienta", "memory_usage_mb": "Uso de RAM (MB)"}
            )
            
            fig_ram_box.update_layout(height=400)
            st.plotly_chart(fig_ram_box, use_container_width=True)
    
    # ====================================================================
    # SECCIÓN 5: FRECUENCIA DE HERRAMIENTAS
    # ====================================================================
    
    st.markdown("## 🔧 Análisis de Herramientas")
    
    col_tools1, col_tools2 = st.columns([1, 1])
    
    with col_tools1:
        # Gráfico de pastel: Frecuencia de uso de herramientas
        if "tool_name" in df.columns:
            tool_counts = df["tool_name"].value_counts()
            
            fig_tools_pie = px.pie(
                values=tool_counts.values,
                names=tool_counts.index,
                title="Frecuencia de Uso de Herramientas",
                hole=0.3
            )
            
            st.plotly_chart(fig_tools_pie, use_container_width=True)
    
    with col_tools2:
        # Tabla: Estadísticas por herramienta
        if "tool_name" in df.columns:
            tool_stats = df.groupby("tool_name").agg({
                "latency_seconds": ["mean", "max"],
                "memory_usage_mb": "mean",
                "error": "count"
            }).round(4)
            
            tool_stats.columns = ["Latencia Promedio (s)", "Latencia Máxima (s)", "RAM Promedio (MB)", "Ejecuciones"]
            
            st.dataframe(tool_stats, use_container_width=True, height=300)
    
    # ====================================================================
    # SECCIÓN 6: DATOS DETALLADOS
    # ====================================================================
    
    st.markdown("## 📋 Datos Detallados de Logs")
    
    # Opciones de filtrado
    col_filter1, col_filter2 = st.columns([1, 1])
    
    with col_filter1:
        if "tool_name" in df.columns:
            selected_tool = st.multiselect(
                "Filtrar por Herramienta:",
                options=df["tool_name"].unique(),
                default=df["tool_name"].unique()
            )
        else:
            selected_tool = []
    
    with col_filter2:
        show_errors_only = st.checkbox("Mostrar solo registros con error", value=False)
    
    # Aplicar filtros
    df_filtered = df.copy()
    
    if selected_tool:
        df_filtered = df_filtered[df_filtered["tool_name"].isin(selected_tool)]
    
    if show_errors_only:
        df_filtered = df_filtered[df_filtered["error"].notna()]
    
    # Mostrar tabla
    if not df_filtered.empty:
        st.dataframe(df_filtered.sort_values("timestamp", ascending=False), use_container_width=True, height=400)
    else:
        st.info("No hay datos que mostrar con los filtros aplicados")
    
    # ====================================================================
    # SECCIÓN 7: EXPORTAR DATOS
    # ====================================================================
    
    st.markdown("## 📤 Exportar Datos")
    
    col_export1, col_export2 = st.columns([1, 1])
    
    with col_export1:
        # Descargar como CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="Descargar como CSV",
            data=csv,
            file_name=f"metro_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col_export2:
        # Descargar como JSON
        json_data = df.to_json(orient="records", indent=2)
        st.download_button(
            label="Descargar como JSON",
            data=json_data,
            file_name=f"metro_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # ====================================================================
    # PIE DE PÁGINA
    # ====================================================================
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px;'>
    <p>Dashboard de Monitoreo - Agente Inteligente del Metro de Santiago (EP3)</p>
    <p>Última actualización: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
