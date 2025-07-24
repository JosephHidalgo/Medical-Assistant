import sqlite3
import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type
from agentes.bd import db

# Modelos Pydantic para las herramientas
class ConsultarDoctoresInput(BaseModel):
    especialidad: Optional[str] = Field(default=None, description="Especialidad médica a buscar")

class RegistrarPacienteInput(BaseModel):
    id_paciente: str = Field(description="ID único del paciente")
    nombre: str = Field(description="Nombre completo del paciente")
    edad: int = Field(description="Edad del paciente")
    sintomas: str = Field(description="Síntomas reportados")
    urgencia: str = Field(description="Nivel de urgencia (ALTA, MEDIA, BAJA)")
    telefono: Optional[str] = Field(default=None, description="Teléfono del paciente")
    email: Optional[str] = Field(default=None, description="Email del paciente")

class CrearCitaInput(BaseModel):
    id_cita: str = Field(description="ID único de la cita")
    paciente_id: str = Field(description="ID del paciente")
    doctor_id: int = Field(description="ID del doctor")
    fecha: str = Field(description="Fecha de la cita (YYYY-MM-DD)")
    hora: str = Field(description="Hora de la cita")
    motivo: str = Field(description="Motivo de la consulta")

# Herramientas personalizadas usando CrewAI BaseTool
class ConsultarDoctoresTool(BaseTool):
    name: str = "consultar_doctores"
    description: str = "Consulta doctores disponibles por especialidad. Puede filtrar por especialidad específica o mostrar todos los doctores disponibles."
    args_schema: Type[BaseModel] = ConsultarDoctoresInput

    def _run(self, especialidad: Optional[str] = None) -> str:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        if especialidad:
            cursor.execute(
                "SELECT id, nombre, especialidad, telefono FROM doctores WHERE especialidad LIKE ? AND disponible = 1",
                (f"%{especialidad}%",)
            )
        else:
            cursor.execute(
                "SELECT id, nombre, especialidad, telefono FROM doctores WHERE disponible = 1"
            )
        
        doctores = cursor.fetchall()
        conn.close()
        
        if not doctores:
            return f"No se encontraron doctores disponibles" + (f" para la especialidad {especialidad}" if especialidad else "")
        
        doctores_dict = [
            {
                "id": doc[0],
                "nombre": doc[1],
                "especialidad": doc[2],
                "telefono": doc[3]
            }
            for doc in doctores
        ]
        
        return json.dumps(doctores_dict, indent=2, ensure_ascii=False)

class RegistrarPacienteTool(BaseTool):
    name: str = "registrar_paciente"
    description: str = "Registra un nuevo paciente en la base de datos con toda su información médica y personal."
    args_schema: Type[BaseModel] = RegistrarPacienteInput

    def _run(self, id_paciente: str, nombre: str, edad: int, sintomas: str, 
             urgencia: str, telefono: str = None, email: str = None) -> str:
        try:
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """INSERT INTO pacientes (id, nombre, edad, telefono, email, sintomas, urgencia)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (id_paciente, nombre, edad, telefono, email, sintomas, urgencia)
            )
            
            conn.commit()
            conn.close()
            
            return f"✅ Paciente {nombre} registrado exitosamente con ID: {id_paciente}"
        except sqlite3.IntegrityError:
            return f"❌ Error: Ya existe un paciente con ID {id_paciente}"
        except Exception as e:
            return f"❌ Error al registrar paciente: {str(e)}"

class CrearCitaTool(BaseTool):
    name: str = "crear_cita"
    description: str = "Crea una nueva cita médica entre un paciente registrado y un doctor disponible."
    args_schema: Type[BaseModel] = CrearCitaInput

    def _run(self, id_cita: str, paciente_id: str, doctor_id: int, 
             fecha: str, hora: str, motivo: str) -> str:
        try:
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            
            # Verificar que el paciente existe
            cursor.execute("SELECT nombre FROM pacientes WHERE id = ?", (paciente_id,))
            paciente = cursor.fetchone()
            if not paciente:
                return f"❌ Error: No existe paciente con ID {paciente_id}"
            
            # Verificar que el doctor existe y está disponible
            cursor.execute("SELECT nombre, especialidad FROM doctores WHERE id = ? AND disponible = 1", (doctor_id,))
            doctor = cursor.fetchone()
            if not doctor:
                return f"❌ Error: Doctor con ID {doctor_id} no existe o no está disponible"
            
            # Crear la cita
            cursor.execute(
                """INSERT INTO citas (id, paciente_id, doctor_id, fecha, hora, motivo)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (id_cita, paciente_id, doctor_id, fecha, hora, motivo)
            )
            
            conn.commit()
            conn.close()
            
            return f"""✅ Cita creada exitosamente:
- ID Cita: {id_cita}
- Paciente: {paciente[0]}
- Doctor: {doctor[0]} ({doctor[1]})
- Fecha: {fecha} a las {hora}
- Motivo: {motivo}"""
        
        except sqlite3.IntegrityError:
            return f"❌ Error: Ya existe una cita with ID {id_cita}"
        except Exception as e:
            return f"❌ Error al crear cita: {str(e)}"

class ObtenerEstadisticasTool(BaseTool):
    name: str = "obtener_estadisticas"
    description: str = "Obtiene estadísticas actuales del sistema médico incluyendo totales y clasificaciones."

    def _run(self) -> str:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Contar pacientes
        cursor.execute("SELECT COUNT(*) FROM pacientes")
        total_pacientes = cursor.fetchone()[0]
        
        # Contar citas
        cursor.execute("SELECT COUNT(*) FROM citas")
        total_citas = cursor.fetchone()[0]
        
        # Contar doctores disponibles
        cursor.execute("SELECT COUNT(*) FROM doctores WHERE disponible = 1")
        doctores_disponibles = cursor.fetchone()[0]
        
        # Pacientes por urgencia
        cursor.execute("SELECT urgencia, COUNT(*) FROM pacientes GROUP BY urgencia")
        urgencias = cursor.fetchall()
        
        conn.close()
        
        estadisticas = f"""📊 ESTADÍSTICAS DEL SISTEMA:
- Total de pacientes: {total_pacientes}
- Total de citas: {total_citas}
- Doctores disponibles: {doctores_disponibles}

Pacientes por urgencia:"""
        
        for urgencia, cantidad in urgencias:
            estadisticas += f"\n- {urgencia}: {cantidad}"
        
        return estadisticas 