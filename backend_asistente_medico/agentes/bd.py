import sqlite3

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
        
        # Tabla de pacientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                edad INTEGER NOT NULL,
                telefono TEXT,
                email TEXT,
                sintomas TEXT,
                urgencia TEXT,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de citas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS citas (
                id TEXT PRIMARY KEY,
                paciente_id TEXT NOT NULL,
                doctor_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                motivo TEXT,
                estado TEXT DEFAULT 'Programada',
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
                FOREIGN KEY (doctor_id) REFERENCES doctores (id)
            )
        ''')
        
        # Insertar doctores de ejemplo si no existen
        cursor.execute("SELECT COUNT(*) FROM doctores")
        if cursor.fetchone()[0] == 0:
            doctores_ejemplo = [
                (1, "Dr. García", "Medicina General", True, "123-456-7890", "garcia@hospital.com"),
                (2, "Dra. López", "Cardiología", True, "123-456-7891", "lopez@hospital.com"),
                (3, "Dr. Martínez", "Neurología", True, "123-456-7892", "martinez@hospital.com"),
                (4, "Dra. Rodríguez", "Pediatría", True, "123-456-7893", "rodriguez@hospital.com")
            ]
            cursor.executemany(
                "INSERT INTO doctores (id, nombre, especialidad, disponible, telefono, email) VALUES (?, ?, ?, ?, ?, ?)",
                doctores_ejemplo
            )
        
        conn.commit()
        conn.close()

# Instancia global de la base de datos

db = BaseDatosMedica() 