"""
Agente Inteligente del Metro de Santiago - EP3
Ingeniero de Software Experto en IA y Python
Sistema completo con herramientas, memoria compuesta, monitoreo y seguridad
"""

import os
import json
import time
import psutil
import logging
from datetime import datetime
from typing import Any, List, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

import openai

# 1. IMPORTACIONES PARA LANGCHAIN 1.2.15
# create_agent reemplaza a AgentExecutor + create_openai_tools_agent
from langchain_core.tools import Tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.callbacks import BaseCallbackHandler
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langgraph.checkpoint.memory import MemorySaver  # Reemplaza a ConversationBufferMemory

# ============================================================================
# CONFIGURACIÓN INICIAL Y LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Normalizar API key: soporta OPENAI_API_KEY o GITHUB_TOKEN (GitHub Models)
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("GITHUB_TOKEN") or ""
BASE_URL = os.getenv("OPENAI_BASE_URL")  # "https://models.inference.ai.azure.com"
EMBEDDINGS_URL = os.getenv("OPENAI_EMBEDDINGS_URL") or BASE_URL

if not API_KEY:
    logger.warning("OPENAI_API_KEY / GITHUB_TOKEN no está configurada. Revisa tu .env")

LOGS_DIR = Path("./logs")
LOGS_DIR.mkdir(exist_ok=True)
LOGS_FILE = LOGS_DIR / "agent_logs.jsonl"
VECTOR_DB_DIR = Path("./vector_db")
VECTOR_DB_DIR.mkdir(exist_ok=True)

# ============================================================================
# CALLBACK DE MONITOREO (IE1, IE2, IE3, IE4)
# ============================================================================

class MonitoreoAgenteCallback(BaseCallbackHandler):
    """
    Callback personalizado para monitorear la ejecución del agente.
    Registra: timestamp, herramienta usada, latencia, uso de RAM y errores.
    Requisito: IE1, IE2, IE3, IE4
    """
    
    def __init__(self):
        self.tool_start_time = None
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        """Llamado cuando comienza la ejecución de una herramienta."""
        self.tool_start_time = time.time()
        self.tool_name = serialized.get("name", "unknown")
        logger.info(f"Iniciando herramienta: {self.tool_name}")
    
    def on_tool_end(self, output: str, **kwargs):
        """Llamado cuando termina la ejecución de una herramienta."""
        if self.tool_start_time:
            latency = time.time() - self.tool_start_time
            current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            memory_usage = current_memory - self.initial_memory
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "tool_name": self.tool_name,
                "latency_seconds": round(latency, 4),
                "memory_usage_mb": round(memory_usage, 2),
                "current_memory_mb": round(current_memory, 2),
                "error": None,
                "output_length": len(str(output))
            }
            
            # Registrar en archivo JSONL
            try:
                with open(LOGS_FILE, "a") as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                logger.info(f"Herramienta {self.tool_name} completada en {latency:.4f}s, RAM: {memory_usage:.2f}MB")
            except Exception as e:
                logger.error(f"Error al registrar log: {e}")
    
    def on_tool_error(self, error: Exception, **kwargs):
        """Llamado cuando ocurre un error en una herramienta."""
        latency = time.time() - self.tool_start_time if self.tool_start_time else 0
        current_memory = self.process.memory_info().rss / 1024 / 1024
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": self.tool_name,
            "latency_seconds": round(latency, 4),
            "memory_usage_mb": round(current_memory - self.initial_memory, 2),
            "current_memory_mb": round(current_memory, 2),
            "error": str(error),
            "error_type": type(error).__name__
        }
        
        try:
            with open(LOGS_FILE, "a") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            logger.error(f"Error en herramienta {self.tool_name}: {error}")
        except Exception as e:
            logger.error(f"Error al registrar log de error: {e}")

# ============================================================================
# DEFINICIÓN DE HERRAMIENTAS
# ============================================================================

def consultar_tarifa(hora: str) -> str:
    """
    Consulta la tarifa según la hora del día.
    Retorna: Punta, Valle o Bajo
    
    Args:
        hora: Formato "HH:MM" en rango 24 horas
    
    Returns:
        Tipo de tarifa disponible
    """
    try:
        horas = int(hora.split(":")[0])
        
        # Tarifas según horario de Santiago
        if 7 <= horas < 9 or 17 <= horas < 19:
            return "Tarifa Punta: $1,300 (Hora pico de congestión)"
        elif 9 <= horas < 17 or 19 <= horas < 22:
            return "Tarifa Valle: $1,080 (Horario intermedio)"
        else:
            return "Tarifa Bajo: $800 (Horario fuera de pico)"
    except Exception as e:
        logger.error(f"Error en consultar_tarifa: {e}")
        return f"Error al consultar tarifa: {e}"

def consultar_ruta(origen: str, destino: str) -> str:
    """
    Consulta la mejor ruta entre dos estaciones.
    
    Args:
        origen: Estación de origen
        destino: Estación de destino
    
    Returns:
        Ruta recomendada con combinaciones
    """
    try:
        # Base de datos simulada de rutas comunes en Santiago
        rutas = {
            ("Los Heroes", "Baquedano"): {
                "ruta": "Línea 2 (Rojo)",
                "tiempo_estimado": "12 minutos",
                "paradas": ["Los Heroes", "Santa Lucia", "Moneda", "Teatinos", "Baquedano"]
            },
            ("Mapocho", "Tobalaba"): {
                "ruta": "Línea 1 (Roja) -> Línea 6 (Café)",
                "tiempo_estimado": "25 minutos",
                "paradas": ["Mapocho", "Cal y Canto", "Puente Cal y Canto", "Baquedano", "Ñuble", "Plaza Italia", "Tobalaba"],
                "combinacion": True
            },
            ("Central", "Bellas Artes"): {
                "ruta": "Línea 1 (Roja)",
                "tiempo_estimado": "8 minutos",
                "paradas": ["Central", "Santa Ana", "Bellas Artes"]
            },
            ("Terminal", "La Cisterna"): {
                "ruta": "Línea 4 y 5 (Azul)",
                "tiempo_estimado": "35 minutos",
                "paradas": ["Terminal", "Estación Central", "La Moneda", "Manuel Montt", "La Cisterna"]
            }
        }
        
        key = (origen.title(), destino.title())
        if key in rutas:
            ruta_info = rutas[key]
            return f"""
            Mejor Ruta Disponible:
            - Ruta: {ruta_info['ruta']}
            - Tiempo Estimado: {ruta_info['tiempo_estimado']}
            - Paradas: {' -> '.join(ruta_info['paradas'])}
            - Combinación: {'Sí' if ruta_info.get('combinacion') else 'No'}
            """
        else:
            return f"Ruta no disponible en base de datos. Intenta con estaciones comunes como: Los Heroes, Baquedano, Mapocho, Tobalaba, Central, Bellas Artes."
    except Exception as e:
        logger.error(f"Error en consultar_ruta: {e}")
        return f"Error al consultar ruta: {e}"

def consultar_impedimentos() -> str:
    """
    NUEVA HERRAMIENTA: Simula consultar el estado de la red.
    Retorna información sobre retrasos, estaciones cerradas o impedimentos.
    
    Returns:
        Estado actual de la red con posibles impedimentos
    """
    try:
        import random
        
        estado_general = random.choice(["Normal", "Retrasos Menores", "Congestión Moderada"])
        
        impedimentos = {
            "Normal": {
                "estado": "La red funciona con normalidad",
                "tiempo_extra": "0 minutos",
                "estaciones_afectadas": []
            },
            "Retrasos Menores": {
                "estado": "Hay retrasos de 5 a 10 minutos",
                "tiempo_extra": "5-10 minutos",
                "estaciones_afectadas": ["Plaza Italia", "Manuel Montt"]
            },
            "Congestión Moderada": {
                "estado": "Congestión moderada en línea principal",
                "tiempo_extra": "10-15 minutos",
                "estaciones_afectadas": ["Baquedano", "La Moneda", "Terminal"]
            }
        }
        
        info = impedimentos.get(estado_general, impedimentos["Normal"])
        resultado = f"""
        Estado de la Red del Metro:
        - Estado General: {info['estado']}
        - Tiempo Extra Estimado: {info['tiempo_extra']}
        - Estaciones Afectadas: {', '.join(info['estaciones_afectadas']) if info['estaciones_afectadas'] else 'Ninguna'}
        """
        return resultado
    except Exception as e:
        logger.error(f"Error en consultar_impedimentos: {e}")
        return f"Error al consultar impedimentos: {e}"

def enviar_correo(destinatario: str, asunto: str, cuerpo: str) -> str:
    """
    Envía el plan de viaje usando SMTP o lo guarda como archivo .eml localmente.
    
    Args:
        destinatario: Email del destinatario
        asunto: Asunto del correo
        cuerpo: Cuerpo del mensaje
    
    Returns:
        Confirmación de envío o guardado
    """
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        
        if not sender_email or not sender_password:
            # Si no hay credenciales, guardar como archivo .eml
            eml_path = LOGS_DIR / f"viaje_{datetime.now().strftime('%Y%m%d_%H%M%S')}.eml"
            
            mensaje = f"""From: Sistema Metro Santiago <no-reply@metro.cl>
To: {destinatario}
Subject: {asunto}
Content-Type: text/plain; charset=utf-8

{cuerpo}
"""
            with open(eml_path, "w", encoding="utf-8") as f:
                f.write(mensaje)
            
            logger.info(f"Correo guardado localmente en: {eml_path}")
            return f"Correo guardado localmente en: {eml_path}"
        
        # Intenta enviar por SMTP
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, sender_password)
            
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = destinatario
            msg["Subject"] = asunto
            msg.attach(MIMEText(cuerpo, "plain", "utf-8"))
            
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Correo enviado exitosamente a: {destinatario}")
            return f"Correo enviado exitosamente a: {destinatario}"
        except Exception as e:
            logger.warning(f"Error al enviar por SMTP: {e}. Guardando como archivo .eml")
            # Si falla SMTP, guardar como .eml
            eml_path = LOGS_DIR / f"viaje_{datetime.now().strftime('%Y%m%d_%H%M%S')}.eml"
            mensaje = f"""From: Sistema Metro Santiago <no-reply@metro.cl>
To: {destinatario}
Subject: {asunto}
Content-Type: text/plain; charset=utf-8

{cuerpo}
"""
            with open(eml_path, "w", encoding="utf-8") as f:
                f.write(mensaje)
            return f"Correo guardado como archivo .eml en: {eml_path}"
    
    except Exception as e:
        logger.error(f"Error en enviar_correo: {e}")
        return f"Error al enviar correo: {e}"

def razonar_viaje(pregunta: str) -> str:
    """
    Realiza razonamiento multi-paso para consultas complejas sobre viajes.
    
    Args:
        pregunta: La pregunta del usuario
    
    Returns:
        Respuesta razonada del agente
    """
    try:
        # Aquí se podría llamar a un LLM para razonamiento complejo
        # Por ahora, retorna un patrón de respuesta estructurado
        respuesta = f"""
        Analizando tu pregunta: "{pregunta}"
        
        Pasos de razonamiento:
        1. Identifiqué los puntos clave de tu consulta
        2. Consideré las tarifas, rutas y posibles impedimentos
        3. Generé una recomendación basada en datos actuales
        
        Para una respuesta más precisa, proporciona:
        - Punto de origen
        - Punto de destino
        - Hora aproximada de viaje
        """
        logger.info(f"Razonamiento realizado para: {pregunta}")
        return respuesta
    except Exception as e:
        logger.error(f"Error en razonar_viaje: {e}")
        return f"Error en razonamiento: {e}"

# ============================================================================
# INICIALIZACIÓN DE MEMORIA COMPUESTA
# ============================================================================

class MemoriaCompuesta:
    """
    Sistema de memoria compuesta con:
    - Memoria a Corto Plazo: MemorySaver (LangGraph checkpointer)
    - Memoria a Largo Plazo: Base de vectores con embeddings
    """
    
    def __init__(self):
        self.checkpointer = MemorySaver()  # Reemplaza a ConversationBufferMemory
        self.thread_id = "default"
        self.long_term = None
        self._inicializar_vector_db()
    
    def _inicializar_vector_db(self):
        """Inicializa la base de datos vectorial."""
        try:
            embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                api_key=API_KEY,
                base_url=EMBEDDINGS_URL
            )
            
            # Crear documentos iniciales con resúmenes de interacciones típicas
            docs_iniciales = [
                Document(page_content="Consulta de tarifa: El usuario preguntó sobre precios del metro según horario"),
                Document(page_content="Consulta de ruta: El usuario consultó sobre rutas entre estaciones"),
                Document(page_content="Impedimentos: El usuario quería saber sobre estado de la red"),
                Document(page_content="Envío de correo: El usuario solicitó enviar plan de viaje por email"),
            ]
            
            if len(docs_iniciales) > 0:
                self.long_term = FAISS.from_documents(docs_iniciales, embeddings)
                self.long_term.save_local(str(VECTOR_DB_DIR))
                logger.info("Base de datos vectorial inicializada")
            else:
                logger.warning("No hay documentos para inicializar vector DB")
        except Exception as e:
            logger.warning(f"No se pudo inicializar vector DB: {e}")
    
    def agregar_a_largo_plazo(self, contenido: str):
        """Agrega un nuevo documento a la memoria a largo plazo."""
        try:
            if self.long_term is not None:
                embeddings = OpenAIEmbeddings(
                    model="text-embedding-3-small",
                    api_key=API_KEY,
                    base_url=EMBEDDINGS_URL
                )
                doc = Document(page_content=contenido)
                self.long_term.add_documents([doc])
                self.long_term.save_local(str(VECTOR_DB_DIR))
        except Exception as e:
            logger.warning(f"Error al agregar a memoria a largo plazo: {e}")

# ============================================================================
# INICIALIZACIÓN DEL AGENTE
# ============================================================================

class AgenteMetroSantiago:
    """
    Agente Inteligente del Metro de Santiago con:
    - Herramientas especializadas
    - Memoria compuesta (corto y largo plazo)
    - Monitoreo y trazabilidad
    - Guardrails de seguridad y ética
    """
    
    def __init__(self):
        self.callback = MonitoreoAgenteCallback()
        self.memoria = MemoriaCompuesta()
        self._inicializar_agente()
    
    def _inicializar_agente(self):
        """Inicializa el agente LangChain 1.x con create_agent."""
        
        # PASO 1: Definir el LLM (gpt-4o como requiere la EP3)
        try:
            llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0,
                max_tokens=2048,
                api_key=API_KEY,
                base_url=BASE_URL
            )
            logger.info("✓ LLM (ChatOpenAI - gpt-4o) inicializado exitosamente")
        except Exception as e:
            logger.warning(f"No se pudo inicializar GPT-4o: {e}. Usando gpt-3.5-turbo como fallback")
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0,
                max_tokens=2048,
                api_key=API_KEY,
                base_url=BASE_URL
            )
        
        # Definir herramientas
        tools = [
            Tool(
                name="consultar_tarifa",
                func=consultar_tarifa,
                description="Consulta la tarifa del metro según la hora (Punta, Valle, Bajo). Input: hora en formato HH:MM"
            ),
            Tool(
                name="consultar_ruta",
                func=consultar_ruta,
                description="Consulta la mejor ruta entre dos estaciones del metro. Input: origen, destino"
            ),
            Tool(
                name="consultar_impedimentos",
                func=consultar_impedimentos,
                description="Consulta el estado actual de la red y posibles impedimentos, retrasos o estaciones cerradas"
            ),
            Tool(
                name="enviar_correo",
                func=enviar_correo,
                description="Envía el plan de viaje por correo o lo guarda como archivo .eml. Input: destinatario, asunto, cuerpo"
            ),
            Tool(
                name="razonar_viaje",
                func=razonar_viaje,
                description="Realiza razonamiento multi-paso para consultas complejas. Input: pregunta"
            ),
        ]
        
        # System Prompt con Guardrails (IE6)
        system_prompt = """
        Eres un Agente Inteligente del Metro de Santiago altamente capacitado y ético.
        
        REGLAS ESTRICTAS (GUARDRAILS):
        1. NUNCA solicites ni almacenes: RUT, contraseñas, tarjetas de crédito o datos bancarios
        2. NUNCA guardes información personal identificable del usuario
        3. Si el usuario proporciona datos sensibles, IGNÓRALOS e INFORMA de privacidad
        4. Siempre mantén respuestas RESPETUOSAS e INCLUSIVAS
        5. Prioriza la seguridad y privacidad del usuario
        
        INSTRUCCIONES OPERACIONALES:
        - Proporciona información de rutas, tarifas y estado del metro
        - Ayuda a planificar viajes eficientemente
        - Simula envío de planes de viaje por correo
        - Responde consultas sobre impedimentos en la red
        - Realiza razonamiento multi-paso para consultas complejas
        
        ADVERTENCIA DE PRIVACIDAD AUTOMÁTICA:
        Si detectas que el usuario está compartiendo información personal, responde:
        "He detectado que compartiste información personal. Por tu privacidad y seguridad, 
        no almaceno ni proceso datos como RUT, contraseñas o tarjetas de crédito. 
        Tu información está protegida."
        """
        
        # PASO 2: Crear el agente con create_agent (LangChain 1.x)
        # Reemplaza a: AgentExecutor + create_openai_tools_agent + hub.pull()
        try:
            self.agent = create_agent(
                model=llm,
                tools=tools,
                system_prompt=system_prompt,
                checkpointer=self.memoria.checkpointer,  # MemorySaver para memoria conversacional
                debug=True,
                name="agente_metro"
            )
            logger.info("✓ Agente creado exitosamente con create_agent (LangChain 1.x)")
        except Exception as e:
            logger.error(f"Error al crear agente: {e}")
            raise
        
        logger.info("✅ Agente moderno inicializado exitosamente (LangChain 1.2.15)")
    
    def procesar_consulta(self, consulta: str) -> str:
        """
        Procesa una consulta del usuario con la nueva API de LangChain 1.x.
        
        Args:
            consulta: Pregunta o solicitud del usuario
        
        Returns:
            Respuesta del agente
        """
        try:
            # Detectar información personal (guardrail)
            palabras_sensibles = ["rut", "contraseña", "tarjeta", "crédito", "banco", "cvv", "clave"]
            if any(palabra in consulta.lower() for palabra in palabras_sensibles):
                aviso = """
                He detectado que compartiste información personal o sensible.
                Por tu privacidad y seguridad, no almaceno ni proceso datos como:
                - RUT o números de identificación
                - Contraseñas o claves de acceso
                - Números de tarjeta de crédito o datos bancarios
                
                Tu información está protegida y asegurada.
                ¿En qué más puedo ayudarte respecto al metro?
                """
                logger.warning(f"Datos sensibles detectados en consulta")
                return aviso
            
            # Procesar consulta con create_agent (LangChain 1.x)
            # thread_id mantiene la conversación para la memoria a corto plazo
            config = {"configurable": {"thread_id": self.memoria.thread_id}}
            resultado = self.agent.invoke(
                {"messages": [("user", consulta)]},
                config=config
            )
            
            # Extraer la respuesta del AI del historial de mensajes
            output = resultado["messages"][-1].content
            
            # Agregar a memoria a largo plazo
            self.memoria.agregar_a_largo_plazo(f"Consulta: {consulta} | Respuesta: {output}")
            
            return output
        
        except Exception as e:
            logger.error(f"Error al procesar consulta: {e}")
            return f"Error al procesar tu consulta: {str(e)}"

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal para ejecutar el agente de forma interactiva."""
    print("\n" + "="*80)
    print("AGENTE INTELIGENTE DEL METRO DE SANTIAGO - EP3")
    print("="*80)
    print("\nBienvenido. Soy tu asistente personal para viajes en el metro.")
    print("Puedo ayudarte con:")
    print("  - Consultar tarifas según la hora")
    print("  - Encontrar rutas entre estaciones")
    print("  - Informarte sobre impedimentos en la red")
    print("  - Enviar planes de viaje por correo")
    print("  - Responder consultas complejas\n")
    print("Escribe 'salir' para terminar.\n")
    print("="*80 + "\n")
    
    # Inicializar agente
    try:
        agente = AgenteMetroSantiago()
        print("✓ Agente inicializado correctamente\n")
    except Exception as e:
        print(f"✗ Error al inicializar agente: {e}")
        return
    
    # Loop interactivo
    while True:
        try:
            consulta = input("Tú: ").strip()
            
            if consulta.lower() == "salir":
                print("\n¡Gracias por usar el Agente del Metro de Santiago! Hasta pronto.")
                break
            
            if not consulta:
                print("Por favor, ingresa una consulta válida.\n")
                continue
            
            print("\nAgente procesando...\n")
            respuesta = agente.procesar_consulta(consulta)
            print(f"Agente: {respuesta}\n")
            
        except KeyboardInterrupt:
            print("\n\n¡Hasta pronto!")
            break
        except Exception as e:
            logger.error(f"Error inesperado: {e}")
            print(f"Error inesperado: {e}\n")

if __name__ == "__main__":
    main()
