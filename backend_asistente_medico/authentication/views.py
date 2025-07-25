from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.sessions.models import Session
from django.utils import timezone
import json
import hashlib
import sqlite3
from datetime import datetime
import uuid

# Importar la base de datos médica
from agentes.bd import db

def hash_password(password):
    """Función para hashear contraseñas"""
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_credenciales(correo_electronico, contraseña):
    """Verificar las credenciales del paciente"""
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    contraseña_hash = hash_password(contraseña)
    
    cursor.execute('''
        SELECT id, nombres, apellidos, correo_electronico, numero_telefono, edad 
        FROM pacientes 
        WHERE correo_electronico = ? AND contraseña = ?
    ''', (correo_electronico, contraseña_hash))
    
    paciente = cursor.fetchone()
    conn.close()
    
    if paciente:
        return {
            'id': paciente[0],
            'nombres': paciente[1],
            'apellidos': paciente[2],
            'correo_electronico': paciente[3],
            'numero_telefono': paciente[4],
            'edad': paciente[5]
        }
    return None

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    try:
        data = json.loads(request.body)
        correo_electronico = data.get('correo_electronico') or data.get('email')
        contraseña = data.get('contraseña') or data.get('password')
        
        if not correo_electronico or not contraseña:
            return JsonResponse({
                'success': False, 
                'message': 'Correo electrónico y contraseña son requeridos'
            }, status=400)
        
        # Verificar credenciales con la base de datos personalizada
        paciente = verificar_credenciales(correo_electronico, contraseña)
        
        if paciente:
            # Guardar información del paciente en la sesión
            request.session['paciente_id'] = paciente['id']
            request.session['paciente_nombres'] = paciente['nombres']
            request.session['paciente_apellidos'] = paciente['apellidos']
            request.session['paciente_email'] = paciente['correo_electronico']
            request.session['is_authenticated'] = True
            
            # print(paciente['edad'])
            # print(paciente['numero_telefono'])
            
            return JsonResponse({
                'success': True,
                'message': 'Inicio de sesión exitoso',
                'paciente': {
                    'id': paciente['id'],
                    'nombres': paciente['nombres'],
                    'apellidos': paciente['apellidos'],
                    'correo_electronico': paciente['correo_electronico'],
                    'numero_telefono': paciente['numero_telefono'],
                    'edad': paciente['edad']
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Credenciales inválidas'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    try:
        # Limpiar la sesión
        request.session.flush()
        
        return JsonResponse({
            'success': True,
            'message': 'Sesión cerrada exitosamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al cerrar sesión: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    try:
        data = json.loads(request.body)
        print(data)
        nombres = data.get('nombres')
        apellidos = data.get('apellidos')
        correo_electronico = data.get('correo_electronico') or data.get('email')
        numero_telefono = data.get('numero_telefono')
        edad = data.get('edad')
        contraseña = data.get('contraseña') or data.get('password')

        # Validaciones
        if not all([nombres, apellidos, correo_electronico, edad, contraseña]):
            return JsonResponse({
                'success': False,
                'message': 'Nombres, apellidos, correo electrónico, edad y contraseña son requeridos.'
            }, status=400)
        
        try:
            edad = int(edad)
            if edad <= 0 or edad > 120:
                return JsonResponse({
                    'success': False,
                    'message': 'La edad debe ser un número válido entre 1 y 120.'
                }, status=400)
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'La edad debe ser un número válido.'
            }, status=400)

        # Registrar paciente usando la función de la base de datos
        paciente_id = db.registrar_paciente(
            nombres=nombres,
            apellidos=apellidos,
            correo_electronico=correo_electronico,
            numero_telefono=numero_telefono,
            edad=edad,
            contraseña=contraseña
        )

        if paciente_id:
            # Auto-login después del registro
            request.session['paciente_id'] = paciente_id
            request.session['paciente_nombres'] = nombres
            request.session['paciente_apellidos'] = apellidos
            request.session['paciente_email'] = correo_electronico
            request.session['is_authenticated'] = True
            
            return JsonResponse({
                'success': True,
                'message': 'Registro e inicio de sesión exitosos.',
                'paciente': {
                    'id': paciente_id,
                    'nombres': nombres,
                    'apellidos': apellidos,
                    'correo_electronico': correo_electronico,
                    'numero_telefono': numero_telefono,
                    'edad': edad
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'El correo electrónico ya está registrado.'
            }, status=400)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def check_auth(request):
    if request.session.get('is_authenticated'):
        return JsonResponse({
            'authenticated': True,
            'paciente': {
                'id': request.session.get('paciente_id'),
                'nombres': request.session.get('paciente_nombres'),
                'apellidos': request.session.get('paciente_apellidos'),
                'correo_electronico': request.session.get('paciente_email')
            }
        })
    else:
        return JsonResponse({
            'authenticated': False
        })

def login_required_paciente(view_func):
    """Decorador personalizado para requerir autenticación de paciente"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_authenticated'):
            return JsonResponse({
                'success': False,
                'message': 'Autenticación requerida'
            }, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required_paciente
@require_http_methods(["GET"])
def perfil_paciente(request):
    """Obtener información completa del perfil del paciente"""
    try:
        paciente_id = request.session.get('paciente_id')
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nombres, apellidos, correo_electronico, numero_telefono, edad, fecha_registro
            FROM pacientes 
            WHERE id = ?
        ''', (paciente_id,))
        
        paciente = cursor.fetchone()
        conn.close()
        
        if paciente:
            return JsonResponse({
                'success': True,
                'paciente': {
                    'id': paciente[0],
                    'nombres': paciente[1],
                    'apellidos': paciente[2],
                    'correo_electronico': paciente[3],
                    'numero_telefono': paciente[4],
                    'edad': paciente[5],
                    'fecha_registro': paciente[6]
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Paciente no encontrado'
            }, status=404)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def obtener_especialidades(request):
    """Obtener todas las especialidades médicas disponibles"""
    try:
        especialidades = db.obtener_especialidades()
        return JsonResponse({
            'success': True,
            'especialidades': especialidades
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def obtener_doctores(request):
    """Obtener doctores, opcionalmente filtrados por especialidad"""
    try:
        especialidad = request.GET.get('especialidad')
        doctores = db.obtener_doctores_por_especialidad(especialidad)
        
        doctores_data = []
        for doctor in doctores:
            doctores_data.append({
                'id': doctor[0],
                'nombre': doctor[1],
                'especialidad': doctor[2],
                'disponible': doctor[3],
                'telefono': doctor[4],
                'email': doctor[5]
            })
        
        return JsonResponse({
            'success': True,
            'doctores': doctores_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }, status=500)

@login_required_paciente
@csrf_exempt
@require_http_methods(["POST"])
def crear_cita(request):
    """Crear una nueva cita médica"""
    try:
        data = json.loads(request.body)
        doctor_id = data.get('doctor_id')
        fecha = data.get('fecha')
        hora = data.get('hora')
        motivo = data.get('motivo')
        urgencia = data.get('urgencia', 'Normal')
        
        if not all([doctor_id, fecha, hora, motivo]):
            return JsonResponse({
                'success': False,
                'message': 'Doctor, fecha, hora y motivo son requeridos'
            }, status=400)
        
        paciente_id = request.session.get('paciente_id')
        
        # Crear la cita usando la función de la base de datos
        cita_id = db.crear_cita(
            paciente_id=paciente_id,
            doctor_id=doctor_id,
            fecha=fecha,
            hora=hora,
            motivo=motivo,
            urgencia=urgencia
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Cita creada exitosamente',
            'cita_id': cita_id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }, status=500)

@login_required_paciente
@require_http_methods(["GET"])
def mis_citas(request):
    """Obtener todas las citas del paciente autenticado"""
    try:
        paciente_id = request.session.get('paciente_id')
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.fecha, c.hora, c.motivo, c.urgencia, c.estado, 
                   d.nombre, d.especialidad, c.fecha_creacion
            FROM citas c
            JOIN doctores d ON c.doctor_id = d.id
            WHERE c.paciente_id = ?
            ORDER BY c.fecha DESC, c.hora DESC
        ''', (paciente_id,))
        
        citas = cursor.fetchall()
        conn.close()
        
        citas_data = []
        for cita in citas:
            citas_data.append({
                'id': cita[0],
                'fecha': cita[1],
                'hora': cita[2],
                'motivo': cita[3],
                'urgencia': cita[4],
                'estado': cita[5],
                'doctor_nombre': cita[6],
                'doctor_especialidad': cita[7],
                'fecha_creacion': cita[8]
            })
        
        return JsonResponse({
            'success': True,
            'citas': citas_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }, status=500)