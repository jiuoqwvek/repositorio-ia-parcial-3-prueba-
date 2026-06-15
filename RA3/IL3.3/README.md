IL3.3 - Seguridad y Ética

Descripción:
- La sección "Seguridad y Ética" del README.md en la raíz explica los
  guardrails implementados (detección de RUT, tarjetas, contraseñas) y
  las prácticas de privacidad.
- El agente aplica validaciones antes de procesar consultas (RA3/IL3.2/agente_metro.py).

Verificación rápida:
1. Ejecuta el agente y envía un RUT en la conversación; el agente debe
   rechazar o advertir y no incluirlo en logs sensibles.
