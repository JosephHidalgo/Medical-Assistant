from crewai import Agent, Task
from crewai import Process
from langchain_openai import ChatOpenAI
from agentes.herramientas import (
    ConsultarDoctoresTool,
    RegistrarPacienteTool,
    CrearCitaTool,
    ObtenerEstadisticasTool
)

# Configurar el modelo GPT-4o mini
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)

consultar_doctores_tool = ConsultarDoctoresTool()
registrar_paciente_tool = RegistrarPacienteTool()
crear_cita_tool = CrearCitaTool()
obtener_estadisticas_tool = ObtenerEstadisticasTool()

def crear_agentes():
    # Agente de Triaje (sin herramientas, usará delegation)
    agente_triaje = Agent(
        role='Especialista en Triaje Médico',
        goal='Evaluar síntomas de pacientes, determinar nivel de urgencia y recomendar especialidad médica apropiada',
        backstory="""Eres un enfermero especializado en triaje médico con 10 años de experiencia. \
        Tu trabajo es evaluar los síntomas que presentan los pacientes, determinar el nivel de urgencia \
        (ALTA, MEDIA, BAJA) y recomendar qué tipo de especialista médico necesitan.\n\n        CRITERIOS DE URGENCIA:\n        - ALTA: Síntomas que ponen en riesgo la vida (dolor en pecho, dificultad respiratoria severa, pérdida de conciencia)\n        - MEDIA: Síntomas que requieren atención pronta (fiebre alta, dolor intenso, síntomas neurológicos)\n        - BAJA: Síntomas que pueden esperar consulta regular (síntomas leves, consultas preventivas)\n\n        ESPECIALIDADES DISPONIBLES:\n        - Cardiología: problemas cardíacos, dolor en pecho, arritmias, hipertensión\n        - Neurología: problemas neurológicos, dolores de cabeza severos, mareos, convulsiones\n        - Pediatría: todos los pacientes menores de 18 años\n        - Medicina General: síntomas generales, primera consulta, síntomas no específicos""",
        verbose=True,
        allow_delegation=True,
        llm=llm
    )
    
    # Agente de Base de Datos con herramientas reales
    agente_bd = Agent(
        role='Administrador de Base de Datos Médica',
        goal='Gestionar información de doctores, registrar pacientes, crear citas médicas usando herramientas de base de datos real',
        backstory="""Eres un administrador de sistemas médicos experto en gestión de bases de datos SQLite. \
        Tu trabajo es manejar toda la información usando herramientas reales de base de datos.\n\n        HERRAMIENTAS DISPONIBLES:\n        - consultar_doctores: Para buscar doctores disponibles por especialidad\n        - registrar_paciente: Para registrar nuevos pacientes en la BD\n        - crear_cita: Para crear citas médicas reales\n        - obtener_estadisticas: Para consultar estadísticas del sistema\n\n        PROCESO OBLIGATORIO QUE DEBES SEGUIR:\n        1. Primero usa consultar_doctores para verificar doctores disponibles de la especialidad recomendada\n        2. Luego usa registrar_paciente con todos los datos del triaje\n        3. Después usa crear_cita para programar la consulta con el primer doctor disponible\n        4. Finalmente usa obtener_estadisticas para confirmar que todo se registró correctamente\n\n        SIEMPRE usa las herramientas en este orden específico y confirma cada operación antes de continuar.""",
        verbose=True,
        allow_delegation=False,
        tools=[consultar_doctores_tool, registrar_paciente_tool, crear_cita_tool, obtener_estadisticas_tool],
        llm=llm
    )
    
    return agente_triaje, agente_bd

def crear_tareas(agente_triaje, agente_bd, datos_paciente):
    # Tarea 1: Triaje del paciente
    tarea_triaje = Task(
        description=f"""
        Realiza el triaje médico completo del siguiente paciente:
        
        DATOS DEL PACIENTE:
        - Nombre: {datos_paciente['nombre']}
        - Edad: {datos_paciente['edad']} años
        - Síntomas reportados: {datos_paciente['sintomas']}
        
        INSTRUCCIONES DE EVALUACIÓN:
        1. Analiza cuidadosamente los síntomas presentados
        2. Evalúa la gravedad y determina el nivel de urgencia:
           - ALTA: Síntomas que requieren atención inmediata (riesgo de vida)
           - MEDIA: Síntomas que requieren atención en las próximas horas
           - BAJA: Síntomas que pueden esperar consulta regular
        3. Recomienda la especialidad médica más apropiada:
           - Cardiología: problemas cardíacos, dolor en pecho, arritmias
           - Neurología: problemas neurológicos, dolores de cabeza severos
           - Pediatría: pacientes menores de 18 años
           - Medicina General: síntomas generales, primera consulta
        
        FORMATO DE RESPUESTA REQUERIDO:
        - Nivel de urgencia: [ALTA/MEDIA/BAJA]
        - Especialidad recomendada: [Especialidad]
        - Justificación médica: [Explicación detallada de por qué esta clasificación]
        - ID del paciente sugerido: paciente_{datos_paciente['nombre'].replace(' ', '_').lower()}
        """,
        expected_output="Evaluación médica completa con nivel de urgencia, especialidad recomendada, justificación médica detallada y ID del paciente",
        agent=agente_triaje
    )
    
    # Tarea 2: Gestión real de base de datos
    tarea_gestion = Task(
        description=f"""
        USANDO LAS HERRAMIENTAS DE BASE DE DATOS REALES, realiza las siguientes operaciones basándote en la evaluación de triaje:
        
        PASO 1 - CONSULTAR DOCTORES DISPONIBLES:
        Usa la herramienta consultar_doctores con la especialidad recomendada en el triaje.
        
        PASO 2 - REGISTRAR PACIENTE:
        Usa la herramienta registrar_paciente con estos datos:
        - ID: El sugerido en el triaje
        - Nombre: {datos_paciente['nombre']}
        - Edad: {datos_paciente['edad']}
        - Síntomas: {datos_paciente['sintomas']}
        - Urgencia: La determinada en el triaje
        - Teléfono: {datos_paciente.get('telefono', 'No proporcionado')}
        
        PASO 3 - CREAR CITA:
        Usa la herramienta crear_cita con:
        - ID de cita: cita_{{nombre_paciente}}_{{fecha}}
        - Paciente ID: El registrado en el paso anterior
        - Doctor ID: El primer doctor disponible de la especialidad
        - Fecha: 2025-07-24
        - Hora: 10:00 AM
        - Motivo: Los síntomas del paciente
        
        PASO 4 - VERIFICAR ESTADÍSTICAS:
        Usa la herramienta obtener_estadisticas para confirmar que todo se registró correctamente.
        
        IMPORTANTE: DEBES usar todas las herramientas en el orden indicado. Cada herramienta realizará operaciones reales en la base de datos SQLite.
        """,
        expected_output="Confirmación detallada de todas las operaciones realizadas en la base de datos real con herramientas específicas",
        agent=agente_bd,
        context=[tarea_triaje]
    )
    
    return tarea_triaje, tarea_gestion 