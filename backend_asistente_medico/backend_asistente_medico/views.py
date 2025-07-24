from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime
from agentes.agentes import crear_agentes, crear_tareas
from crewai import Crew, Process

def serializar_resultado_crew(resultado):
    """
    Función helper para convertir el resultado de CrewAI a formato serializable
    Extrae información específica de los agentes médicos
    """
    try:
        resultado_final = {}
        
        # Si es un objeto CrewOutput, extraer la información relevante
        if hasattr(resultado, 'raw'):
            resultado_final['respuesta_completa'] = resultado.raw
            
        # Extraer outputs de las tareas individuales
        if hasattr(resultado, 'tasks_output') and resultado.tasks_output:
            resultado_final['tareas'] = []
            
            for i, task in enumerate(resultado.tasks_output):
                tarea_info = {
                    'numero_tarea': i + 1,
                    'descripcion': getattr(task, 'description', 'Sin descripción'),
                    'agente': getattr(task, 'agent', 'Agente desconocido'),
                    'output_completo': str(getattr(task, 'output', task))
                }
                
                # Extraer información específica del output del agente
                output_str = str(getattr(task, 'output', ''))
                
                # Buscar respuesta final del agente
                if 'Final Answer:' in output_str:
                    partes = output_str.split('Final Answer:')
                    if len(partes) > 1:
                        tarea_info['respuesta_final'] = partes[1].strip()
                
                # Extraer estadísticas si están presentes
                if 'ESTADÍSTICAS DEL SISTEMA' in output_str:
                    tarea_info['contiene_estadisticas'] = True
                    # Puedes agregar más parsing específico aquí si necesitas los números
                
                # Identificar si es respuesta de triaje o gestión de BD
                if 'triaje' in str(getattr(task, 'agent', '')).lower():
                    tarea_info['tipo_agente'] = 'triaje'
                elif 'base de datos' in str(getattr(task, 'agent', '')).lower() or 'bd' in str(getattr(task, 'agent', '')).lower():
                    tarea_info['tipo_agente'] = 'base_datos'
                else:
                    tarea_info['tipo_agente'] = 'desconocido'
                    
                resultado_final['tareas'].append(tarea_info)
        
        # Agregar información de uso de tokens si está disponible
        if hasattr(resultado, 'token_usage') and resultado.token_usage:
            resultado_final['token_usage'] = resultado.token_usage
            
        # Si no hay información estructurada, usar la representación completa
        if not resultado_final:
            resultado_final = {'respuesta': str(resultado)}
            
        # Agregar metadata
        resultado_final['timestamp'] = str(datetime.now())
        resultado_final['total_tareas'] = len(getattr(resultado, 'tasks_output', []))
    except Exception as e:
        print(f"Error al serializar el resultado de CrewAI: {str(e)}")
        resultado_final = {'error': str(e)}
    return resultado_final
        
def limpiar_dict_para_json(obj):
    """
    Limpia recursivamente un diccionario/objeto para que sea serializable en JSON
    """
    import json
    
    if obj is None:
        return None
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, list):
        return [limpiar_dict_para_json(item) for item in obj]
    elif isinstance(obj, dict):
        resultado = {}
        for key, value in obj.items():
            try:
                # Probar si el valor es serializable
                json.dumps(value)
                resultado[key] = value
            except (TypeError, ValueError):
                # Si no es serializable, limpiar recursivamente
                resultado[key] = limpiar_dict_para_json(value)
        return resultado
    else:
        # Para objetos complejos, intentar convertir a dict
        try:
            # Probar si es serializable tal como está
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            # Si no es serializable, intentar diferentes métodos
            if hasattr(obj, 'model_dump'):
                try:
                    return limpiar_dict_para_json(obj.model_dump())
                except:
                    pass
            elif hasattr(obj, 'to_dict'):
                try:
                    return limpiar_dict_para_json(obj.to_dict())
                except:
                    pass
            elif hasattr(obj, '__dict__'):
                try:
                    return limpiar_dict_para_json(dict(obj.__dict__))
                except:
                    pass
            # Como último recurso, convertir a string
            return str(obj)

# Función adicional para extraer información médica específica
def extraer_info_medica(output_str):
    """
    Extrae información médica específica del output de los agentes
    """
    info_medica = {}
    
    # Extraer estadísticas del sistema
    if 'Total de pacientes:' in output_str:
        try:
            import re
            # Extraer números de las estadísticas
            total_pacientes = re.search(r'Total de pacientes:\s*(\d+)', output_str)
            total_citas = re.search(r'Total de citas:\s*(\d+)', output_str)
            doctores_disponibles = re.search(r'Doctores disponibles:\s*(\d+)', output_str)
            urgencia_alta = re.search(r'ALTA:\s*(\d+)', output_str)
            
            info_medica['estadisticas'] = {
                'total_pacientes': int(total_pacientes.group(1)) if total_pacientes else 0,
                'total_citas': int(total_citas.group(1)) if total_citas else 0,
                'doctores_disponibles': int(doctores_disponibles.group(1)) if doctores_disponibles else 0,
                'pacientes_urgencia_alta': int(urgencia_alta.group(1)) if urgencia_alta else 0
            }
        except:
            info_medica['estadisticas'] = 'Error al extraer estadísticas'
    
    # Extraer información de citas
    if 'cita con' in output_str.lower():
        try:
            import re
            cita_match = re.search(r'cita con (?:la |el |Dr\.|Dra\.)([^,]+)', output_str, re.IGNORECASE)
            fecha_match = re.search(r'(\d{1,2} de \w+ de \d{4})', output_str)
            hora_match = re.search(r'(\d{1,2}:\d{2} [AP]M)', output_str)
            
            info_medica['cita'] = {
                'doctor': cita_match.group(1).strip() if cita_match else 'No especificado',
                'fecha': fecha_match.group(1) if fecha_match else 'No especificada',
                'hora': hora_match.group(1) if hora_match else 'No especificada'
            }
        except:
            info_medica['cita'] = 'Error al extraer información de cita'
    
    # Extraer nivel de urgencia o diagnóstico
    if 'urgencia' in output_str.lower() or 'prioridad' in output_str.lower():
        if 'ALTA' in output_str:
            info_medica['nivel_urgencia'] = 'ALTA'
        elif 'MEDIA' in output_str:
            info_medica['nivel_urgencia'] = 'MEDIA'
        elif 'BAJA' in output_str:
            info_medica['nivel_urgencia'] = 'BAJA'
    
    return info_medica

# Vista usando la función helper
@csrf_exempt
@require_http_methods(["POST"])
def atender_paciente(request):
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre')
        edad = data.get('edad')
        sintomas = data.get('sintomas')
        telefono = data.get('telefono', None)
        
        if not nombre or not edad or not sintomas:
            return JsonResponse({
                'success': False,
                'message': 'Faltan datos obligatorios: nombre, edad o síntomas.'
            }, status=400)
        
        datos_paciente = {
            'nombre': nombre,
            'edad': edad,
            'sintomas': sintomas,
            'telefono': telefono
        }
        
        agente_triaje, agente_bd = crear_agentes()
        tarea_triaje, tarea_gestion = crear_tareas(agente_triaje, agente_bd, datos_paciente)
        
        crew = Crew(
            agents=[agente_triaje, agente_bd],
            tasks=[tarea_triaje, tarea_gestion],
            process=Process.sequential,
            verbose=False
        )
        
        resultado = crew.kickoff()
        
        # DEPURACIÓN TEMPORAL - puedes quitar esto después
        print(f"Tipo de resultado: {type(resultado)}")
        print(f"Raw attribute: {hasattr(resultado, 'raw')}")
        print(f"Tasks output: {hasattr(resultado, 'tasks_output')}")
        if hasattr(resultado, 'raw'):
            print(f"Raw content: {resultado.raw}")
        if hasattr(resultado, 'tasks_output'):
            print(f"Tasks output length: {len(resultado.tasks_output) if resultado.tasks_output else 0}")
        
        resultado_serializable = serializar_resultado_crew(resultado)
        
        # Verificar que el resultado sea serializable antes de enviarlo
        try:
            json.dumps(resultado_serializable)
        except (TypeError, ValueError) as e:
            print(f"Error de serialización JSON: {e}")
            # Fallback: usar solo strings
            resultado_serializable = {
                'respuesta_completa': str(resultado.raw) if hasattr(resultado, 'raw') else str(resultado),
                'timestamp': str(datetime.now()),
                'error_serializacion': f"Fallback aplicado: {str(e)}"
            }
        
        return JsonResponse({
            'success': True,
            'resultado': resultado_serializable
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error: El cuerpo de la petición no es un JSON válido.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error en el asistente médico: {str(e)}'
        }, status=500)