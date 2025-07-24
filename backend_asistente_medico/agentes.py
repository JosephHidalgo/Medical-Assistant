import os
import sqlite3
from datetime import datetime, timedelta
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Optional, Type
import json

# # Configurar API Key de OpenAI

# Configurar el modelo GPT-4o mini
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)

# Instancia global de la base de datos
from agentes.bd import db

# Modelos Pydantic para las herramientas
# Quitar los modelos Pydantic y las clases BaseTool de aquí

# Herramientas personalizadas usando CrewAI BaseTool
# Quitar los modelos Pydantic y las clases BaseTool de aquí

# Crear instancias de las herramientas
# Quitar los modelos Pydantic y las clases BaseTool de aquí

# Crear agentes
from agentes.agentes import crear_agentes, crear_tareas

# Función para mostrar estado de la base de datos
def mostrar_estado_bd():
    """Muestra el estado actual de la base de datos"""
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("📊 ESTADO ACTUAL DE LA BASE DE DATOS")
    print("="*60)
    
    # Mostrar pacientes
    cursor.execute("SELECT id, nombre, edad, urgencia, fecha_registro FROM pacientes ORDER BY fecha_registro DESC LIMIT 5")
    pacientes = cursor.fetchall()
    
    if pacientes:
        print("\n👥 ÚLTIMOS PACIENTES REGISTRADOS:")
        for p in pacientes:
            print(f"  • {p[1]} (ID: {p[0]}) - Edad: {p[2]} - Urgencia: {p[3]} - Registro: {p[4]}")
    else:
        print("\n👥 No hay pacientes registrados aún")
    
    # Mostrar citas
    cursor.execute("""
        SELECT c.id, p.nombre, d.nombre, d.especialidad, c.fecha, c.hora, c.estado
        FROM citas c
        JOIN pacientes p ON c.paciente_id = p.id
        JOIN doctores d ON c.doctor_id = d.id
        ORDER BY c.fecha_creacion DESC LIMIT 5
    """)
    citas = cursor.fetchall()
    
    if citas:
        print("\n📅 ÚLTIMAS CITAS CREADAS:")
        for c in citas:
            print(f"  • {c[1]} → {c[2]} ({c[3]}) - {c[4]} {c[5]} - Estado: {c[6]}")
    else:
        print("\n📅 No hay citas registradas aún")
    
    # Mostrar doctores
    cursor.execute("SELECT nombre, especialidad, disponible FROM doctores")
    doctores = cursor.fetchall()
    
    print("\n👨‍⚕️ DOCTORES EN EL SISTEMA:")
    for d in doctores:
        estado = "✅ Disponible" if d[2] else "❌ No disponible"
        print(f"  • {d[0]} - {d[1]} - {estado}")
    
    conn.close()

# Función principal para ejecutar el sistema
def ejecutar_sistema_medico(datos_paciente):
    print("=== INICIANDO SISTEMA DE ASISTENTE MÉDICO CON BD REAL ===\n")
    
    # Mostrar estado inicial
    mostrar_estado_bd()
    
    # Crear agentes
    agente_triaje, agente_bd = crear_agentes()
    
    # Crear tareas
    tarea_triaje, tarea_gestion = crear_tareas(agente_triaje, agente_bd, datos_paciente)
    
    # Crear crew (equipo de agentes)
    crew = Crew(
        agents=[agente_triaje, agente_bd],
        tasks=[tarea_triaje, tarea_gestion],
        process=Process.sequential,
        verbose=True
    )
    
    print("\n=== EJECUTANDO COMUNICACIÓN ENTRE AGENTES ===\n")
    
    # Ejecutar el crew
    resultado = crew.kickoff()
    
    print("\n=== RESULTADO DE LA COMUNICACIÓN ENTRE AGENTES ===")
    print(resultado)
    
    # Mostrar estado final
    print("\n=== ESTADO FINAL DESPUÉS DE OPERACIONES ===")
    mostrar_estado_bd()
    
    return resultado

# Ejemplo de uso
if __name__ == "__main__":
    # Datos del paciente de ejemplo
    paciente_ejemplo = {
        "nombre": "Joseph Hidalgo",
        "edad": 20,
        "sintomas": "Colitis, dolor abdominal, fiebre leve",
        "telefono": "999-0126"
    }
    
    print("INSTRUCCIONES DE INSTALACIÓN:")
    print("pip install crewai langchain-openai")
    print("\nCONFIGURACIÓN:")
    print("- Reemplaza 'tu_api_key_aqui' con tu API key real de OpenAI") 
    print("- Se creará automáticamente una base de datos SQLite llamada 'sistema_medico.db'")
    print("- Los agentes usarán herramientas reales para interactuar con la BD")
    print("\n" + "="*50)
    
    try:
        resultado = ejecutar_sistema_medico(paciente_ejemplo)
        print("\n🎉 SISTEMA EJECUTADO EXITOSAMENTE")
        print("✅ Agentes comunicándose correctamente usando delegation")
        print("✅ Herramientas de base de datos funcionando")
        print("✅ Base de datos SQLite operando correctamente")
        print("\n📁 Revisa el archivo 'sistema_medico.db' para ver los datos almacenados")
        print("🔍 Puedes abrir la BD con cualquier cliente SQLite para inspeccionar las tablas")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Verifica que tu API key esté correctamente configurada")