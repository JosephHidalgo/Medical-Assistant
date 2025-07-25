from crewai import Agent, Task
from crewai import Process
from langchain_openai import ChatOpenAI
from agentes.herramientas import (
    ConsultarDoctoresTool,
    CrearCitaTool,
    ObtenerEstadisticasTool,
    ConsultarDisponibilidadTool
)
import re
import sqlite3
from agentes.bd import db


# Configurar el modelo GPT-4o mini
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)

consultar_doctores_tool = ConsultarDoctoresTool()
crear_cita_tool = CrearCitaTool()
obtener_estadisticas_tool = ObtenerEstadisticasTool()
consultar_disponibilidad_tool = ConsultarDisponibilidadTool()

def crear_agentes():
    # Agente de Triaje (sin herramientas, usará delegation)
    agente_triaje = Agent(
        role='Especialista en Triaje Médico',
        goal='Evaluar síntomas de pacientes, determinar nivel de urgencia y recomendar especialidad médica apropiada. Sugerir doctor disponible y preguntar si desea agendar cita.',
        backstory="""Eres un enfermero especializado en triaje médico con 10 años de experiencia. \
        Tu trabajo es evaluar los síntomas que presentan los pacientes, determinar el nivel de urgencia \
        (ALTA, MEDIA, BAJA) y recomendar qué tipo de especialista médico necesitan.\n\n        CRITERIOS DE URGENCIA:\n        - ALTA: Síntomas que ponen en riesgo la vida (dolor en pecho, dificultad respiratoria severa, pérdida de conciencia)\n        - MEDIA: Síntomas que requieren atención pronta (fiebre alta, dolor intenso, síntomas neurológicos)\n        - BAJA: Síntomas que pueden esperar consulta regular (síntomas leves, consultas preventivas)\n\n        ESPECIALIDADES DISPONIBLES:\n        - Cardiología: problemas cardíacos, dolor en pecho, arritmias, hipertensión\n        - Neurología: problemas neurológicos, dolores de cabeza severos, mareos, convulsiones\n        - Pediatría: todos los pacientes menores de 18 años\n        - Medicina General: síntomas generales, primera consulta, síntomas no específicos\n\n        Cuando termines tu análisis, consulta al agente de base de datos para obtener el doctor disponible en la especialidad recomendada y pregunta al usuario si desea agendar una cita con ese doctor.""",
        verbose=True,
        allow_delegation=True,
        llm=llm
    )
    
    # Agente de Base de Datos con herramientas reales
    agente_bd = Agent(
        role='Administrador de Base de Datos Médica',
        goal='Gestionar información de doctores, consultar disponibilidad y crear citas médicas usando herramientas de base de datos real. Sugerir alternativas si no hay disponibilidad.',
        backstory="""Eres un administrador de sistemas médicos experto en gestión de bases de datos SQLite. \
        Tu trabajo es manejar toda la información usando herramientas reales de base de datos.\n\n        HERRAMIENTAS DISPONIBLES:\n        - consultar_doctores: Para buscar doctores disponibles por especialidad\n        - consultar_disponibilidad: Para verificar si un doctor está disponible en una fecha/hora\n        - crear_cita: Para crear citas médicas reales\n        - obtener_estadisticas: Para consultar estadísticas del sistema\n\n        PROCESO RECOMENDADO:\n        1. Usa consultar_doctores para obtener el doctor disponible en la especialidad recomendada\n        2. Usa consultar_disponibilidad para sugerir la fecha/hora más próxima según urgencia\n        3. Si el usuario acepta, usa crear_cita\n        4. Si el usuario pide otra fecha, verifica disponibilidad y responde si es posible o sugiere alternativas.\n        5. Confirma la cita y muestra detalles.\n        """,
        verbose=True,
        allow_delegation=False,
        tools=[consultar_doctores_tool, consultar_disponibilidad_tool, crear_cita_tool, obtener_estadisticas_tool],
        llm=llm
    )
    
    return agente_triaje, agente_bd

def crear_tareas(agente_triaje, agente_bd, datos_paciente, etapa, contexto=None):
    """
    Crea las tareas para los agentes según la etapa conversacional.
    etapa: 'triaje', 'sugerir_cita', 'confirmar_cita', 'negociar_fecha', etc.
    contexto: información relevante de etapas previas (ej: especialidad, doctor, urgencia)
    """
    tareas = []
    if etapa == 'triaje':
        tarea_triaje = Task(
            description=(
                f"""
                Analiza los síntomas del paciente y determina:
                - Nivel de urgencia (ALTA, MEDIA, BAJA)
                - Especialidad médica recomendada
                - Justificación médica
                Luego, consulta al agente de base de datos para obtener el doctor disponible en la especialidad recomendada.
                Finalmente, responde al usuario de forma conversacional:
                Ejemplo de respuesta:
                Según los síntomas que describes, tu nivel de urgencia es {{urgencia}} y te recomiendo acudir a la especialidad de {{especialidad}}. El doctor disponible es {{doctor}}. ¿Te gustaría agendar una cita con él?"
                DATOS DEL PACIENTE:
                - Nombre: {datos_paciente['nombre']}
                - Edad: {datos_paciente['edad']} años
                - Síntomas: {datos_paciente['sintomas']}
                """
            ),
            expected_output="Recomendación médica conversacional con especialidad, doctor y pregunta de agendar cita.",
            agent=agente_triaje
        )
        tareas.append(tarea_triaje)
    elif etapa == 'sugerir_cita':
        # contexto debe incluir: especialidad, doctor_id, doctor_nombre, urgencia
        print(contexto)
        tarea_sugerir = Task(
            description=f"""
            Usando las herramientas de base de datos, consulta la disponibilidad del doctor {contexto['doctor_nombre']} (ID: {contexto['doctor_id']}) para la fecha y hora más próxima posible según la urgencia ({contexto['urgencia']}).
            Sugiere al usuario la fecha/hora disponible y pregunta si desea agendar la cita.
            Ejemplo de respuesta:
            "La cita más próxima disponible con el Dr. {contexto['doctor_nombre']} es el {{fecha}} a las {{hora}}. ¿Te gustaría agendarla?"
            """,
            expected_output="Sugerencia de fecha/hora disponible y pregunta de confirmación de cita.",
            agent=agente_bd
        )
        tareas.append(tarea_sugerir)
    elif etapa == 'confirmar_cita':
        # contexto debe incluir: doctor_id, doctor_nombre, paciente_id, fecha, hora, motivo
        tarea_confirmar = Task(
            description=f"""
            Registra la cita médica entre el paciente (ID: {contexto.get('paciente_id', datos_paciente.get('id_paciente', 'NO_ID'))}) y el doctor {contexto['doctor_nombre']} (ID: {contexto['doctor_id']}) para el {contexto['fecha']} a las {contexto['hora']}.
            Confirma al usuario que la cita ha sido agendada exitosamente y muestra los detalles.
            """,
            expected_output="Confirmación de cita agendada con detalles.",
            agent=agente_bd
        )
        tareas.append(tarea_confirmar)
    elif etapa == 'negociar_fecha':
        # contexto debe incluir: doctor_id, doctor_nombre, fecha_deseada, hora_deseada
        tarea_negociar = Task(
            description=f"""
            Verifica si el doctor {contexto['doctor_nombre']} (ID: {contexto['doctor_id']}) está disponible el {contexto['fecha_deseada']} a las {contexto['hora_deseada']}.
            Si está disponible, sugiere agendar la cita y pregunta al usuario si desea confirmarla.
            Si no está disponible, sugiere la siguiente fecha/hora disponible y pregunta si desea agendarla.
            """,
            expected_output="Respuesta sobre disponibilidad y sugerencia alternativa si es necesario.",
            agent=agente_bd
        )
        tareas.append(tarea_negociar)
    return tareas 

def extraer_contexto_triaje(output):
    import re
    especialidad = None
    doctor_nombre = None
    urgencia = None
    doctor_id = None
    fecha = None
    hora = None

    # Buscar especialidad
    match_especialidad = re.search(r'especialidad de ([^.]+)', output, re.IGNORECASE)
    if match_especialidad:
        especialidad = match_especialidad.group(1).strip()

    # Buscar doctor (Dr. o Dra., con o sin 'el/la')
    match_doctor = re.search(r'(?:el|la)?\s*Dr\.\s*([A-Za-zÁÉÍÓÚáéíóúñÑ ]+?)(?:\.| es|,|\?|$)|(?:el|la)?\s*Dra\.\s*([A-Za-zÁÉÍÓÚáéíóúñÑ ]+?)(?:\.| es|,|\?|$)', output, re.IGNORECASE)
    if match_doctor:
        doctor_nombre = match_doctor.group(1) or match_doctor.group(2)
        doctor_nombre = doctor_nombre.strip()
    else:
        print("no match_doctor")

    # Buscar urgencia
    match_urgencia = re.search(r'nivel de urgencia es ([A-ZÁÉÍÓÚ]+)', output, re.IGNORECASE)
    if match_urgencia:
        urgencia = match_urgencia.group(1).strip()

    # Buscar fecha (YYYY-MM-DD o '10 de junio de 2024')
    match_fecha = re.search(r'el (\d{4}-\d{2}-\d{2})', output)
    if not match_fecha:
        match_fecha = re.search(r'el (\d{1,2} de \w+ de \d{4})', output)
    if match_fecha:
        fecha = match_fecha.group(1).strip()

    # Buscar hora
    match_hora = re.search(r'a las (\d{2}:\d{2})', output)
    if match_hora:
        hora = match_hora.group(1).strip()

    # Buscar doctor_id en la base de datos si tenemos nombre
    if doctor_nombre:
        import sqlite3
        from agentes.bd import db
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        if especialidad:
            cursor.execute(
                """SELECT id FROM doctores WHERE nombre LIKE ? AND especialidad LIKE ? AND disponible = 1 LIMIT 1""",
                (f'%{doctor_nombre}%', f'%{especialidad}%')
            )
        else:
            cursor.execute(
                """SELECT id FROM doctores WHERE nombre LIKE ? AND disponible = 1 LIMIT 1""",
                (f'%{doctor_nombre}%',)
            )
        row = cursor.fetchone()
        if row:
            doctor_id = row[0]
        conn.close()

    return {
        'especialidad': especialidad,
        'doctor_nombre': doctor_nombre,
        'doctor_id': doctor_id,
        'urgencia': urgencia,
        'fecha': fecha,
        'hora': hora
    } 