# 🚀 GUÍA RÁPIDA - Agente Inteligente del Metro de Santiago

**¡Comienza en 5 minutos!**

## ⚡ Opción 1: Windows (Lo más fácil)

### Paso 1: Abrir terminal

```bash
# Abre PowerShell o CMD en la carpeta del proyecto
cd C:\Users\rena4\Downloads\EVA3_Ing_Sol_IA
```

### Paso 2: Configurar API Key

```bash
# Copia el archivo de ejemplo
copy .env.example .env

# Edita .env y reemplaza:
# OPENAI_API_KEY=sk-xxxx
# con tu clave real desde: https://platform.openai.com/api-keys
```

### Paso 3: Instalar

```bash
setup.bat install
```

### Paso 4: Ejecutar (en 2 terminales)

**Terminal 1 - Agente:**
```bash
setup.bat agent
```

**Terminal 2 - Dashboard:**
```bash
setup.bat dashboard
```

Luego abre: http://localhost:8501

---

## ⚡ Opción 2: macOS/Linux

### Paso 1: Abrir terminal

```bash
cd /ruta/a/EVA3_Ing_Sol_IA
```

### Paso 2: Configurar API Key

```bash
cp .env.example .env
# Edita .env con tu editor favorito (nano, vim, vscode)
# Reemplaza: OPENAI_API_KEY=sk-xxxx
```

### Paso 3: Instalar

```bash
chmod +x setup.sh
./setup.sh install
```

### Paso 4: Ejecutar (en 2 terminales)

**Terminal 1 - Agente:**
```bash
./setup.sh agent
```

**Terminal 2 - Dashboard:**
```bash
./setup.sh dashboard
```

Luego abre: http://localhost:8501

---

## 🐳 Opción 3: Docker (Recomendado para producción)

### Paso 1: Configurar

```bash
cp .env.example .env
# Edita .env con tu OPENAI_API_KEY
```

### Paso 2: Levantar

```bash
docker-compose up --build
```

### Paso 3: Usar

- **Dashboard**: http://localhost:8501
- **Agente**: Escribe en la terminal de Docker

---

## 📝 Ejemplos de Consultas

Una vez que el agente esté ejecutándose, prueba con:

```
¿Cuál es la tarifa a las 8:00?
¿Cómo llego de Los Heroes a Baquedano?
¿Hay impedimentos hoy?
Envía mi viaje a mi.correo@gmail.com
¿Mejor hora para viajar a Tobalaba?
```

---

## 🔑 Obtener tu API Key de OpenAI

1. Ir a: https://platform.openai.com/api-keys
2. Click en "Create new secret key"
3. Copiar la clave
4. Pegarlo en el archivo `.env`

> ⚠️ **IMPORTANTE**: No compartas tu API key. Es confidencial.

---

## 📊 Ver Dashboard

Una vez con datos, abre:
```
http://localhost:8501
```

Verás:
- ✓ Latencia de herramientas
- ✓ Errores detectados
- ✓ Uso de RAM
- ✓ Frecuencia de consultas
- ✓ Exportar datos CSV/JSON

---

## 🧪 Probar Sin Escribir Consultas

```bash
# En una terminal:
python ejemplos.py pruebas

# O para demostración interactiva:
python ejemplos.py demo

# O verificar instalación:
python ejemplos.py verificar
```

---

## ❌ Si No Funciona

### Error: "OPENAI_API_KEY not found"
→ Revisa que .env existe y tiene tu clave

### Error: "ModuleNotFoundError"
→ Ejecuta: `setup.bat install` (Windows) o `./setup.sh install` (Mac/Linux)

### Error: Puerto 8501 en uso
→ Ejecuta: `streamlit run dashboard.py --server.port 8502`

### Dashboard vacío
→ Ejecuta el agente primero en otra terminal

---

## 📂 Archivos Importantes

| Archivo | Función |
|---------|---------|
| `backend/agent.py` | Core del agente (NO modificar para empezar) |
| `dashboard.py` | Dashboard Streamlit (NO modificar) |
| `.env` | Tu configuración (EDITA SOLO ESTO) |
| `logs/agent_logs.jsonl` | Datos que genera el agente (automático) |

---

## 🆘 Soporte Rápido

**¿Necesitas ayuda?**

1. Lee el README.md completo
2. Ejecuta: `python ejemplos.py verificar`
3. Revisa `logs/agent_logs.jsonl` (JSONL) y `logs/agente_metro.log`

---

## ✅ Checklist de Inicio

- [ ] Descargar archivos del proyecto
- [ ] Crear `.env` desde `.env.example`
- [ ] Agregar `OPENAI_API_KEY` en `.env`
- [ ] Ejecutar `setup.bat install` o `./setup.sh install`
- [ ] Abrir Terminal 1 y ejecutar agente
- [ ] Abrir Terminal 2 y ejecutar dashboard
- [ ] Acceder a http://localhost:8501
- [ ] Realizar 3-5 consultas en el agente
- [ ] Ver datos en el dashboard

---

**¡Listo! El agente ya está funcionando.** 🎉

Para documentación completa, lee el `README.md`
