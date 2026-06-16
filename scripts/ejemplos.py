"""
Ejemplos de Uso del Agente Inteligente del Metro de Santiago
Casos de prueba y consultas típicas
"""

# ============================================================================
# EJEMPLOS DE CONSULTAS
# ============================================================================

EJEMPLOS_CONSULTAS = {
    "tarifas": [
        "¿Cuál es la tarifa a las 8:00 AM?",
        "¿Cuánto cuesta viajar a las 18:30?",
        "¿Cuál es el horario de tarifa baja?",
        "¿Hay descuentos para estudiantes?",
    ],
    
    "rutas": [
        "¿Cómo llego de Los Heroes a Baquedano?",
        "¿Cuál es la mejor ruta de Central a Bellas Artes?",
        "¿Qué estaciones debo tomar para ir de Mapocho a Tobalaba?",
        "¿Necesito hacer combinación para llegar a La Cisterna desde Terminal?",
    ],
    
    "impedimentos": [
        "¿Hay impedimentos en la red hoy?",
        "¿Cuál es el estado actual del metro?",
        "¿Hay retrasos en algunas líneas?",
        "¿Hay estaciones cerradas?",
    ],
    
    "correos": [
        "Envía mi plan de viaje a usuario@example.com",
        "¿Puedo recibir el itinerario por correo?",
        "Guarda mi ruta en un archivo",
    ],
    
    "consultas_complejas": [
        "¿Cuál es la mejor hora para viajar de Los Heroes a Tobalaba?",
        "Planifica mi viaje considerando tarifas, rutas y tiempo",
        "¿Cómo optimizar mi viaje si hay retrasos?",
    ],
    
    "seguridad": [
        "Mi RUT es 12345678-9",  # Debería ser detectado
        "Mi contraseña es xyz123",  # Debería ser detectado
        "Mi tarjeta es 4532-1111-2222-3333",  # Debería ser detectado
    ]
}

# ============================================================================
# SCRIPT DE PRUEBAS AUTOMATIZADAS
# ============================================================================

def ejecutar_pruebas():
    """
    Ejecuta un conjunto de pruebas automatizadas.
    Útil para validar que el agente funciona correctamente.
    """
    
    from backend.agent import AgenteMetroSantiago
    import time
    
    print("\n" + "="*70)
    print("EJECUTANDO PRUEBAS DEL AGENTE INTELIGENTE DEL METRO")
    print("="*70 + "\n")
    
    try:
        # Inicializar agente
        print("📝 Inicializando agente...")
        agente = AgenteMetroSantiago()
        print("✓ Agente inicializado\n")
        
        # Pruebas por categoría
        categorias = ["tarifas", "rutas", "impedimentos"]
        
        for categoria in categorias:
            print(f"\n{'='*70}")
            print(f"PRUEBA: {categoria.upper()}")
            print(f"{'='*70}\n")
            
            for i, consulta in enumerate(EJEMPLOS_CONSULTAS[categoria][:2], 1):
                print(f"[{i}] Consulta: {consulta}")
                print("-" * 70)
                
                try:
                    inicio = time.time()
                    respuesta = agente.procesar_consulta(consulta)
                    tiempo_respuesta = time.time() - inicio
                    
                    print(f"Respuesta: {respuesta[:200]}...")
                    print(f"Tiempo: {tiempo_respuesta:.2f}s")
                    print()
                    
                    # Pequeña pausa entre consultas
                    time.sleep(1)
                
                except Exception as e:
                    print(f"✗ Error: {e}\n")
        
        # Pruebas de seguridad
        print(f"\n{'='*70}")
        print("PRUEBA: SEGURIDAD Y PRIVACIDAD")
        print(f"{'='*70}\n")
        
        for i, consulta in enumerate(EJEMPLOS_CONSULTAS["seguridad"], 1):
            print(f"[{i}] Consulta: {consulta}")
            print("-" * 70)
            
            try:
                respuesta = agente.procesar_consulta(consulta)
                
                # Verificar que detectó datos sensibles
                if "personal" in respuesta.lower() or "privacidad" in respuesta.lower():
                    print("✓ Datos sensibles detectados y protegidos")
                else:
                    print("⚠️  Posible problema en detección de datos sensibles")
                
                print()
                time.sleep(1)
            
            except Exception as e:
                print(f"✗ Error: {e}\n")
        
        print("\n" + "="*70)
        print("✓ PRUEBAS COMPLETADAS")
        print("="*70 + "\n")
        
        print("📊 Resultados:")
        print("   - Verifica los logs en: logs/agent_logs.jsonl")
        print("   - Abre el dashboard en: streamlit run dashboard.py")
        print()
    
    except Exception as e:
        print(f"\n✗ Error en ejecución de pruebas: {e}\n")

# ============================================================================
# VERIFICACIÓN DE INSTALACIÓN
# ============================================================================

def verificar_instalacion():
    """
    Verifica que todas las dependencias estén correctamente instaladas.
    """
    
    print("\n" + "="*70)
    print("VERIFICANDO INSTALACIÓN")
    print("="*70 + "\n")
    
    dependencias = [
        ("langchain", "LangChain"),
        ("openai", "OpenAI"),
        ("streamlit", "Streamlit"),
        ("pandas", "Pandas"),
        ("plotly", "Plotly"),
        ("psutil", "PSUtil"),
        ("faiss", "FAISS"),
    ]
    
    todas_ok = True
    
    for modulo, nombre in dependencias:
        try:
            __import__(modulo)
            print(f"✓ {nombre}")
        except ImportError:
            print(f"✗ {nombre} - NO INSTALADO")
            todas_ok = False
    
    print()
    
    if todas_ok:
        print("✓ Todas las dependencias están instaladas")
        print("\nPuedes ejecutar:")
        print("  - python backend/agent.py (Agente interactivo)")
        print("  - streamlit run dashboard.py (Dashboard)")
        print("  - python -c 'from ejemplos import ejecutar_pruebas; ejecutar_pruebas()' (Pruebas)")
    else:
        print("✗ Algunas dependencias no están instaladas")
        print("\nIntenta:")
        print("  pip install -r requirements.txt")
    
    print("\n" + "="*70 + "\n")

# ============================================================================
# DEMOSTRACIÓN INTERACTIVA
# ============================================================================

def demo_interactiva():
    """
    Ejecuta una demostración interactiva con ejemplos predefinidos.
    """
    
    from backend.agent import AgenteMetroSantiago
    
    print("\n" + "="*70)
    print("DEMOSTRACIÓN INTERACTIVA")
    print("="*70 + "\n")
    
    print("Ejemplos disponibles:")
    print("  1. Consultar Tarifa")
    print("  2. Consultar Ruta")
    print("  3. Consultar Impedimentos")
    print("  4. Enviar Correo")
    print("  5. Consulta Compleja")
    print("  6. Prueba de Seguridad")
    print("  0. Salir")
    print()
    
    try:
        agente = AgenteMetroSantiago()
        
        while True:
            opcion = input("Selecciona una opción (0-6): ").strip()
            
            if opcion == "0":
                print("\n¡Gracias por usar la demostración!")
                break
            
            elif opcion == "1":
                consulta = "¿Cuál es la tarifa a las 8:00 AM?"
                print(f"\nConsulta: {consulta}")
                respuesta = agente.procesar_consulta(consulta)
                print(f"Respuesta: {respuesta}\n")
            
            elif opcion == "2":
                consulta = "¿Cómo llego de Los Heroes a Baquedano?"
                print(f"\nConsulta: {consulta}")
                respuesta = agente.procesar_consulta(consulta)
                print(f"Respuesta: {respuesta}\n")
            
            elif opcion == "3":
                consulta = "¿Hay impedimentos en la red?"
                print(f"\nConsulta: {consulta}")
                respuesta = agente.procesar_consulta(consulta)
                print(f"Respuesta: {respuesta}\n")
            
            elif opcion == "4":
                consulta = "Envía mi plan de viaje a usuario@example.com"
                print(f"\nConsulta: {consulta}")
                respuesta = agente.procesar_consulta(consulta)
                print(f"Respuesta: {respuesta}\n")
            
            elif opcion == "5":
                consulta = "¿Cuál es la mejor hora para viajar?"
                print(f"\nConsulta: {consulta}")
                respuesta = agente.procesar_consulta(consulta)
                print(f"Respuesta: {respuesta}\n")
            
            elif opcion == "6":
                consulta = "Mi RUT es 12345678-9"
                print(f"\nConsulta: {consulta}")
                respuesta = agente.procesar_consulta(consulta)
                print(f"Respuesta: {respuesta}\n")
            
            else:
                print("Opción no válida. Intenta de nuevo.\n")
    
    except Exception as e:
        print(f"\nError: {e}\n")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        comando = sys.argv[1]
        
        if comando == "verificar":
            verificar_instalacion()
        elif comando == "pruebas":
            ejecutar_pruebas()
        elif comando == "demo":
            demo_interactiva()
        else:
            print(f"Comando desconocido: {comando}")
            print("\nUsos disponibles:")
            print("  python ejemplos.py verificar  - Verificar instalación")
            print("  python ejemplos.py pruebas    - Ejecutar pruebas")
            print("  python ejemplos.py demo       - Demostración interactiva")
    else:
        print("\nUsos disponibles:")
        print("  python ejemplos.py verificar  - Verificar instalación")
        print("  python ejemplos.py pruebas    - Ejecutar pruebas")
        print("  python ejemplos.py demo       - Demostración interactiva")
