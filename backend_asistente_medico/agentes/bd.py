import sqlite3
import hashlib
from datetime import datetime

class BaseDatosMedica:
    def __init__(self, db_path="sistema_medico.db"):
        self.db_path = db_path
        self.inicializar_bd()
    
    def inicializar_bd(self):
        """Crear las tablas si no existen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de doctores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctores (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                especialidad TEXT NOT NULL,
                disponible BOOLEAN DEFAULT 1,
                telefono TEXT,
                email TEXT
            )
        ''')
        
        # Tabla de pacientes reformulada
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                id TEXT PRIMARY KEY,
                nombres TEXT NOT NULL,
                apellidos TEXT NOT NULL,
                correo_electronico TEXT UNIQUE NOT NULL,
                numero_telefono TEXT,
                edad INTEGER NOT NULL,
                contraseña TEXT NOT NULL,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de citas con campo urgencia añadido
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS citas (
                id TEXT PRIMARY KEY,
                paciente_id TEXT NOT NULL,
                doctor_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                motivo TEXT,
                urgencia TEXT DEFAULT 'Normal',
                estado TEXT DEFAULT 'Programada',
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
                FOREIGN KEY (doctor_id) REFERENCES doctores (id)
            )
        ''')
        
        # Insertar doctores con más especialidades si no existen
        cursor.execute("SELECT COUNT(*) FROM doctores")
        if cursor.fetchone()[0] == 0:
            doctores_ejemplo = [
                # Medicina General y Familia
                (1, "Dr. Carlos García", "Medicina General", True, "123-456-7890", "garcia@hospital.com"),
                (2, "Dra. Ana López", "Medicina Familiar", True, "123-456-7891", "lopez@hospital.com"),
                
                # Especialidades Cardiovasculares
                (3, "Dr. Miguel Martínez", "Cardiología", True, "123-456-7892", "martinez@hospital.com"),
                (4, "Dra. Elena Rodríguez", "Cardiología Intervencionista", True, "123-456-7893", "rodriguez@hospital.com"),
                
                # Neurología y Psiquiatría
                (5, "Dr. Jorge Hernández", "Neurología", True, "123-456-7894", "hernandez@hospital.com"),
                (6, "Dra. María Fernández", "Psiquiatría", True, "123-456-7895", "fernandez@hospital.com"),
                (7, "Dr. Luis Gómez", "Neurología Pediátrica", True, "123-456-7896", "gomez@hospital.com"),
                
                # Especialidades Pediátricas
                (8, "Dra. Carmen Jiménez", "Pediatría", True, "123-456-7897", "jimenez@hospital.com"),
                (9, "Dr. Roberto Morales", "Neonatología", True, "123-456-7898", "morales@hospital.com"),
                
                # Ginecología y Obstetricia
                (10, "Dra. Isabel Torres", "Ginecología", True, "123-456-7899", "torres@hospital.com"),
                (11, "Dr. Antonio Ruiz", "Obstetricia", True, "123-456-7800", "ruiz@hospital.com"),
                
                # Especialidades Quirúrgicas
                (12, "Dr. Fernando Castro", "Cirugía General", True, "123-456-7801", "castro@hospital.com"),
                (13, "Dra. Patricia Vargas", "Cirugía Plástica", True, "123-456-7802", "vargas@hospital.com"),
                (14, "Dr. Andrés Mendoza", "Traumatología", True, "123-456-7803", "mendoza@hospital.com"),
                (15, "Dra. Sofía Ortega", "Neurocirugía", True, "123-456-7804", "ortega@hospital.com"),
                
                # Especialidades de Diagnóstico
                (16, "Dr. Ricardo Peña", "Radiología", True, "123-456-7805", "pena@hospital.com"),
                (17, "Dra. Lucía Ramírez", "Patología", True, "123-456-7806", "ramirez@hospital.com"),
                
                # Especialidades Internas
                (18, "Dr. Eduardo Silva", "Gastroenterología", True, "123-456-7807", "silva@hospital.com"),
                (19, "Dra. Gabriela Vega", "Endocrinología", True, "123-456-7808", "vega@hospital.com"),
                (20, "Dr. Marcos Delgado", "Neumología", True, "123-456-7809", "delgado@hospital.com"),
                (21, "Dra. Valeria Campos", "Nefrología", True, "123-456-7810", "campos@hospital.com"),
                (22, "Dr. Héctor Ramos", "Hematología", True, "123-456-7811", "ramos@hospital.com"),
                
                # Especialidades Sensoriales
                (23, "Dra. Andrea Soto", "Oftalmología", True, "123-456-7812", "soto@hospital.com"),
                (24, "Dr. Daniel Cruz", "Otorrinolaringología", True, "123-456-7813", "cruz@hospital.com"),
                
                # Dermatología y Urología
                (25, "Dra. Mónica Aguilar", "Dermatología", True, "123-456-7814", "aguilar@hospital.com"),
                (26, "Dr. Pablo Guerrero", "Urología", True, "123-456-7815", "guerrero@hospital.com"),
                
                # Especialidades de Emergencia
                (27, "Dr. Javier Medina", "Medicina de Emergencia", True, "123-456-7816", "medina@hospital.com"),
                (28, "Dra. Natalia Herrera", "Medicina Intensiva", True, "123-456-7817", "herrera@hospital.com"),
                
                # Especialidades Complementarias
                (29, "Dr. Oscar Moreno", "Anestesiología", True, "123-456-7818", "moreno@hospital.com"),
                (30, "Dra. Carolina Núñez", "Medicina del Trabajo", True, "123-456-7819", "nunez@hospital.com")
            ]
            cursor.executemany(
                "INSERT INTO doctores (id, nombre, especialidad, disponible, telefono, email) VALUES (?, ?, ?, ?, ?, ?)",
                doctores_ejemplo
            )
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Función para hashear contraseñas"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def registrar_paciente(self, nombres, apellidos, correo_electronico, numero_telefono, edad, contraseña):
        """Registrar un nuevo paciente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generar ID único para el paciente
        paciente_id = f"PAC{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Hashear la contraseña
        contraseña_hash = self.hash_password(contraseña)
        
        try:
            cursor.execute('''
                INSERT INTO pacientes (id, nombres, apellidos, correo_electronico, numero_telefono, edad, contraseña)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (paciente_id, nombres, apellidos, correo_electronico, numero_telefono, edad, contraseña_hash))
            
            conn.commit()
            return paciente_id
        except sqlite3.IntegrityError:
            return None  # El correo ya existe
        finally:
            conn.close()
    
    def obtener_doctores_por_especialidad(self, especialidad=None):
        """Obtener doctores filtrados por especialidad"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if especialidad:
            cursor.execute(
                "SELECT * FROM doctores WHERE especialidad = ? AND disponible = 1",
                (especialidad,)
            )
        else:
            cursor.execute("SELECT * FROM doctores WHERE disponible = 1")
        
        doctores = cursor.fetchall()
        conn.close()
        return doctores
    
    def obtener_especialidades(self):
        """Obtener todas las especialidades disponibles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT especialidad FROM doctores WHERE disponible = 1 ORDER BY especialidad")
        especialidades = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return especialidades
    
    def crear_cita(self, paciente_id, doctor_id, fecha, hora, motivo, urgencia="Normal"):
        """Crear una nueva cita médica"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Generar ID único para la cita
        cita_id = f"CITA{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute('''
            INSERT INTO citas (id, paciente_id, doctor_id, fecha, hora, motivo, urgencia)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (cita_id, paciente_id, doctor_id, fecha, hora, motivo, urgencia))
        
        conn.commit()
        conn.close()
        return cita_id

# Instancia global de la base de datos
db = BaseDatosMedica()