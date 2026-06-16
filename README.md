# Agente Inteligente del Metro de Santiago - EP3

**Sistema Completo de IA para Consultas de Transporte con Observabilidad, Trazabilidad y Seguridad**

Evaluación Parcial 3 (EP3) de la asignatura "Ingeniería de Soluciones con IA"

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Características](#características)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Requisitos Previos](#requisitos-previos)
5. [Instalación](#instalación)
6. [Uso](#uso)
7. [Dashboard de Monitoreo](#dashboard-de-monitoreo)
8. [Estructura del Proyecto](#estructura-del-proyecto)
9. [Seguridad y Ética](#seguridad-y-ética)
10. [Solución de Problemas](#solución-de-problemas)
11. [Contribuciones](#contribuciones)

---

## 🎯 Descripción General

El **Agente Inteligente del Metro de Santiago** es un sistema conversacional de IA construido con LangChain y OpenAI (GPT-4o) que ayuda a los usuarios a:

- Consultar tarifas del metro según la hora
- Encontrar rutas óptimas entre estaciones
- Conocer impedimentos y retrasos en la red
- Enviar planes de viaje por correo
- Responder consultas complejas con razonamiento multi-paso

### Requisitos Especiales (EP3)

El sistema incluye:

✅ **Herramientas Especializadas**: 5 herramientas de consulta

✅ **Memoria Compuesta**: Memoria a corto plazo (conversación) + Memoria a largo plazo (vectorial)

✅ **Monitoreo y Trazabilidad**: Callback personalizado que registra latencia, RAM y errores

✅ **Dashboard Interactivo**: Visualización en Streamlit de todas las métricas

✅ **Guardrails de Seguridad**: Protección contra solicitud de datos personales

---

## ⚙️ Características

### Herramientas del Agente

| Herramienta | Descripción | Ejemplo de Uso |
|-------------|-------------|-----------------|
| `consultar_tarifa` | Retorna tarifa según hora (Punta/Valle/Bajo) | "¿Cuál es la tarifa a las 8:00 AM?" |
| `consultar_ruta` | Encuentra ruta entre dos estaciones | "¿Cómo llego de Los Heroes a Baquedano?" |
| `consultar_impedimentos` | ⭐ NUEVA: Estado actual de la red | "¿Hay retrasos hoy?" |
| `enviar_correo` | Envía plan de viaje por email o lo guarda | "Envía mi ruta por correo" |
| `razonar_viaje` | Razonamiento multi-paso para consultas complejas | "¿Cuál es la mejor hora para viajar?" |

### Monitoreo (IE1-IE4)

Cada ejecución registra:

- ⏱️ **Timestamp**: Hora exacta de ejecución
- 🔧 **Herramienta**: Nombre de la herramienta utilizada
- ⚡ **Latencia**: Tiempo de respuesta en segundos
- 💾 **Memoria RAM**: Uso de recursos en MB
- ⚠️ **Errores**: Excepciones capturadas

Todos los datos se guardan en `logs/agent_logs.jsonl`

### Dashboard (IE5)

Visualizaciones en tiempo real:

- 📊 Latencia promedio y máxima
- 📈 Gráficos de línea y distribuciones
- 🔴 Frecuencia y timeline de errores
- 💾 Uso de RAM por herramienta
- 🔧 Frecuencia de uso de herramientas
- 📤 Exportar datos en CSV/JSON

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────┐
│        USUARIO (Interfaz CLI)              │
└────────────────┬────────────────────────────┘
                 │
┌─────────────────────────────────────────────┐
│    AGENTE INTELIGENTE (backend/agent.py)    │
├─────────────────────────────────────────────┤
│ - Herramientas (consultar_*, enviar_*, etc) │
│ - Memoria Compuesta (corto/largo plazo)     │
│ - System Prompt con Guardrails (IE6)        │
│ - MonitoreoAgenteCallback (IE1-IE4)         │
└────────┬──────────────────────────┬─────────┘
         │                          │
    ┌────▼─────┐           ┌───────▼─────┐
    │  Logs    │           │  Vector DB  │
    │ JSONL    │           │ (Embeddings)│
    └────┬─────┘           └─────────────┘
         │
    ┌────▼─────────────────────────────┐
    │  DASHBOARD (dashboard.py)        │
    │  Streamlit @ localhost:8501      │
    │  - Gráficos Plotly               │
    │  - Filtros de datos              │
    │  - Exportar CSV/JSON             │
    └────────────────────────────────────┘
```

---

## 📦 Requisitos Previos

### Opción 1: Sin Docker

- Python 3.10+
- OpenAI API Key (https://platform.openai.com/api-keys)

### Opción 2: Con Docker

- Docker 20.10+
- Docker Compose 2.0+

---

## 🚀 Instalación

### OPCIÓN 1: Instalación Local (Recomendado para desarrollo)

#### Paso 1: Clonar o descargar el proyecto

```bash
cd /ruta/a/EVA3_Ing_Sol_IA
```

#### Paso 2: Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

#### Paso 4: Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tu API key de OpenAI
# .env
# OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

Abre el archivo `.env` y reemplaza `OPENAI_API_KEY` con tu clave real.

#### Paso 5: Verificar instalación

```bash
python -c "import langchain, openai, streamlit; print('✓ Dependencias instaladas correctamente')"
```

---

### OPCIÓN 2: Instalación con Docker (Recomendado para producción)

#### Paso 1: Preparar archivo .env

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

#### Paso 2: Compilar imágenes y levantar servicios

```bash
# Levantar todos los servicios
docker-compose up --build

# O en background
docker-compose up -d --build
```

#### Paso 3: Verificar que los servicios estén activos

```bash
docker-compose ps
```

Deberías ver dos contenedores:
- `agente-metro-santiago` (Agente)
- `dashboard-metro-santiago` (Dashboard)

---

## 💻 Uso

### Uso Local - Ejecutar el Agente

#### Terminal 1: Agente Inteligente

```bash
python backend/agent.py
```

El agente inicia en modo interactivo. Ejemplos de consultas:

```
Tú: ¿Cuál es la tarifa a las 8:00 AM?
Agente: [Respuesta con tarifa Punta]

Tú: ¿Cómo llego de Los Heroes a Baquedano?
Agente: [Ruta completa con paradas]

Tú: ¿Hay impedimentos en la red?
Agente: [Estado actual de la red]

Tú: Envía mi plan de viaje a usuario@correo.com
Agente: [Confirmación de envío o guardado de archivo .eml]

Tú: salir
```

#### Terminal 2: Dashboard de Monitoreo

En otra terminal:

```bash
streamlit run dashboard.py
```

Accede a: http://localhost:8501

---

### Uso con Docker - Ejecución

#### Ejecutar todo junto

```bash
docker-compose up
```

Accede a:
- **Agente**: Interactúa por terminal en el contenedor
- **Dashboard**: http://localhost:8501

#### Ejecutar en background

```bash
docker-compose up -d

# Ver logs del agente
docker-compose logs -f agente-metro

# Ver logs del dashboard
docker-compose logs -f dashboard

# Acceder a la terminal del agente
docker-compose exec agente-metro bash
```

#### Detener servicios

```bash
docker-compose down
```

---

## 📊 Dashboard de Monitoreo

### Cómo Acceder

1. **Local**: http://localhost:8501
2. **Docker**: http://localhost:8501

### Secciones del Dashboard

#### 1️⃣ Métricas Principales
- Total de operaciones
- Latencia promedio y máxima
- Uso de RAM
- Total de errores y tasa de error

#### 2️⃣ Análisis de Latencia
- Gráfico de línea en tiempo real
- Distribución de latencias (histograma)
- Promedio móvil

#### 3️⃣ Análisis de Errores
- Errores por herramienta (gráfico de barras)
- Timeline de errores
- Detalles de excepciones

#### 4️⃣ Uso de Recursos
- Gráfico de RAM en el tiempo
- Distribución de RAM por herramienta
- Picos de consumo

#### 5️⃣ Análisis de Herramientas
- Frecuencia de uso (gráfico de pastel)
- Estadísticas por herramienta
- Rendimiento comparativo

#### 6️⃣ Datos Detallados
- Tabla filtrable de todos los logs
- Buscar por herramienta
- Mostrar solo errores

#### 7️⃣ Exportar Datos
- Descargar como CSV
- Descargar como JSON
- Análisis posterior en Excel/Python

---

## 📁 Estructura del Proyecto

```
EVA3_Ing_Sol_IA/
├── backend/agent.py              # Core del agente (herramientas, memoria, callbacks)
├── dashboard.py                 # Dashboard en Streamlit
├── requirements.txt             # Dependencias Python
├── docker-compose.yml           # Orquestación de servicios
├── Dockerfile                   # Configuración del contenedor
├── .env.example                 # Plantilla de variables de entorno
├── .env                         # Variables de entorno (crear a partir de .env.example)
├── README.md                    # Este archivo
├── logs/
│   └── agent_logs.jsonl        # Registros de monitoreo (se crea automáticamente)
├── vector_db/                  # Base de datos vectorial (se crea automáticamente)
└── data/                       # Datos adicionales (opcional)
```

---

## 🔒 Seguridad y Ética

### Guardrails Implementados (IE6)

El agente está configurado con reglas estrictas:

#### 1. Protección de Datos Personales

```python
# El agente detecta y rechaza:
- RUT o números de identificación
- Contraseñas o claves de acceso
- Números de tarjeta de crédito
- Datos bancarios
```

Si un usuario intenta compartir datos sensibles:

```
Usuario: Mi RUT es 12345678-9
Agente: He detectado que compartiste información personal.
        Por tu privacidad y seguridad, no almaceno ni proceso datos
        como RUT, contraseñas o tarjetas de crédito.
        Tu información está protegida.
```

#### 2. Respuestas Respetuosas e Inclusivas

- Lenguaje inclusivo
- Sin discriminación
- Atención a todos los usuarios

#### 3. Transparencia en Monitoreo

- Los usuarios pueden solicitar ver sus datos
- Derecho a solicitar eliminación
- Registro transparente en `agent_logs.jsonl`

### Mejores Prácticas de Seguridad

1. **Variables de Entorno**: Nunca guardes API keys en código
2. **HTTPS**: En producción, usa HTTPS para todas las conexiones
3. **Rate Limiting**: Implementa límites de uso por usuario
4. **Auditoría**: Revisa regularmente los logs

---

## 🐛 Solución de Problemas

### Problema: "OPENAI_API_KEY not found"

**Solución:**
```bash
# Verificar que el archivo .env existe
ls -la .env

# Si no existe, crear:
cp .env.example .env

# Editar .env y agregar tu clave
# OPENAI_API_KEY=sk-xxxxxxxxxxxx
```

### Problema: "ModuleNotFoundError: No module named 'langchain'"

**Solución:**
```bash
# Asegúrate de estar en el entorno virtual
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows

# Reinstalar dependencias
pip install -r requirements.txt
```

### Problema: Puerto 8501 ya está en uso

**Solución:**
```bash
# Cambiar puerto en Streamlit
streamlit run dashboard.py --server.port 8502

# O matar el proceso en el puerto
# macOS/Linux:
lsof -i :8501
kill -9 <PID>

# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

### Problema: Docker no encuentra .env

**Solución:**
```bash
# Verificar que el archivo .env existe en la raíz del proyecto
ls -la .env

# Asegúrate de que docker-compose está en la misma carpeta
docker-compose up --build
```

### Problema: "FAISS database could not be found"

**Solución:**
```bash
# Es normal en primera ejecución. Se crea automáticamente:
    python backend/agent.py

# Verifica que se cree:
ls -la vector_db/
```

### Problema: Dashboard muestra "En espera de datos"

**Solución:**
1. Asegúrate de que `backend/agent.py` está ejecutándose
2. Ejecuta al menos una consulta en el agente
3. Verifica que `logs/agent_logs.jsonl` existe y tiene contenido
4. Recarga el dashboard (F5)

---

## 📋 Ejemplos de Uso

### Ejemplo 1: Consulta de Tarifa

```
Tú: ¿Cuál es el precio del metro a las 18:30?
Agente: La tarifa a las 18:30 es Valle: $1,080
        Este es un horario intermedio, entre pico y fuera de pico.
```

### Ejemplo 2: Búsqueda de Ruta

```
Tú: Quiero ir desde Central a Bellas Artes
Agente: Mejor Ruta Disponible:
        - Ruta: Línea 1 (Roja)
        - Tiempo Estimado: 8 minutos
        - Paradas: Central -> Santa Ana -> Bellas Artes
```

### Ejemplo 3: Consulta de Impedimentos

```
Tú: ¿Cómo está la red hoy?
Agente: Estado de la Red del Metro:
        - Estado General: Retrasos Menores
        - Tiempo Extra Estimado: 5-10 minutos
        - Estaciones Afectadas: Plaza Italia, Manuel Montt
```

### Ejemplo 4: Envío de Correo

```
Tú: Envía mi plan de viaje a mi.email@gmail.com
Agente: Correo guardado como archivo .eml en:
        logs/viaje_20240315_143022.eml
        
        (Si tienes SMTP configurado, se envía directamente)
```

### Ejemplo 5: Razonamiento Complejo

```
Tú: ¿Cuál es la mejor hora para viajar desde Los Heroes a Tobalaba?
Agente: Analizando tu pregunta...
        
        Pasos de razonamiento:
        1. Identifiqué los puntos clave
        2. Consideré las tarifas, rutas y impedimentos
        3. Generé una recomendación
        
        Recomendación: Viaja entre 9-17 (Valle) o después de 22 (Bajo)
```

---

## 📈 Métricas y Reportes

### Generar Reporte de Monitoreo

```python
import pandas as pd
import json

# Leer logs
logs = []
with open("logs/agent_logs.jsonl") as f:
    for line in f:
        logs.append(json.loads(line))

df = pd.DataFrame(logs)

# Estadísticas
print(f"Total de operaciones: {len(df)}")
print(f"Latencia promedio: {df['latency_seconds'].mean():.4f}s")
print(f"Tasa de error: {(df['error'].notna().sum() / len(df) * 100):.1f}%")
print(f"Uso promedio de RAM: {df['memory_usage_mb'].mean():.2f}MB")

# Guardar reporte
df.to_csv("reporte_monitoreo.csv", index=False)
```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para sugerir mejoras:

1. Abre un issue describiendo el problema
2. Fork el proyecto
3. Crea una rama para tu feature
4. Envía un PR con tus cambios

---

## 📝 Licencia

Este proyecto es parte de la evaluación EP3 de la asignatura
"Ingeniería de Soluciones con IA".

Uso académico permitido.

---

## 👨‍💻 Autor

**Agente Inteligente del Metro de Santiago**
- Desarrollado para: EP3 - Ingeniería de Soluciones con IA
- Tecnología: LangChain + OpenAI + Streamlit
- Año: 2024

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa la sección **Solución de Problemas**
2. Verifica que las dependencias estén instaladas correctamente
3. Comprueba que tu `OPENAI_API_KEY` es válida
4. Revisa los logs en `logs/agent_logs.jsonl`

---

## 🎓 Requisitos de la EP3 Completados

✅ **Herramientas (5 requeridas)**
- ✓ consultar_tarifa
- ✓ consultar_ruta
- ✓ consultar_impedimentos (NUEVA)
- ✓ enviar_correo
- ✓ razonar_viaje

✅ **Memoria Compuesta**
- ✓ Corto Plazo: ConversationBufferMemory
- ✓ Largo Plazo: Vector DB con Embeddings

✅ **Observabilidad y Trazabilidad (IE1-IE4)**
- ✓ BaseCallbackHandler personalizado (MonitoreoAgenteCallback)
- ✓ Registro de timestamp
- ✓ Nombre de herramienta
- ✓ Latencia
- ✓ Uso de RAM (psutil)
- ✓ Errores

✅ **Dashboard de Monitoreo (IE5)**
- ✓ Streamlit
- ✓ Gráficos de latencia (línea)
- ✓ Frecuencia de errores (barras, timeline)
- ✓ Uso de recursos RAM

✅ **Seguridad y Ética (IE6)**
- ✓ System Prompt con Guardrails
- ✓ No solicitar/almacenar RUT, contraseñas, tarjetas
- ✓ Respuestas respetuosas e inclusivas
- ✓ Advertencia de privacidad automática

---

**¡Gracias por usar el Agente Inteligente del Metro de Santiago!** 🚇

Para soporte o sugerencias, contacta a tu profesor de la asignatura.
