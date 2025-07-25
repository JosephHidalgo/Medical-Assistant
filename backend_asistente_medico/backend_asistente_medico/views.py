from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
import json
from datetime import datetime
from agentes.agentes import crear_agentes, crear_tareas, extraer_contexto_triaje
from crewai import Crew, Process
from openai import OpenAI
import os
import tempfile

# Configuración de OpenAI
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)


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
            try:
                # Intenta serializar directamente
                json.dumps(resultado.token_usage)
                resultado_final['token_usage'] = resultado.token_usage
            except TypeError:
                # Si falla, convierte a string
                resultado_final['token_usage'] = str(resultado.token_usage)
            
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

def merge_contextos(contexto, nuevo_contexto):
    combinado = contexto.copy()
    for k, v in nuevo_contexto.items():
        if v is not None:
            combinado[k] = v
    return combinado

# Vista usando la función helper
@csrf_exempt
@require_http_methods(["POST"])
def atender_paciente(request):
    try:
        data = json.loads(request.body)
        print(data)
        stage = data.get('stage', 'triaje')
        nombre = data.get('nombre')
        edad = data.get('edad')
        sintomas = data.get('sintomas')
        telefono = data.get('telefono', None)
        respuesta_usuario = data.get('respuesta_usuario')
        contexto = data.get('contexto', {})
        fecha_deseada = data.get('fecha_deseada')
        hora_deseada = data.get('hora_deseada')

        if not nombre or not edad:
            return JsonResponse({
                'success': False,
                'message': 'Faltan datos obligatorios: nombre o edad.'
            }, status=400)

        datos_paciente = {
            'nombre': nombre,
            'edad': edad,
            'sintomas': sintomas,
            'telefono': telefono
        }

        agente_triaje, agente_bd = crear_agentes()
        tareas = []
        next_stage = stage
        next_contexto = contexto.copy() if contexto else {}
        # Flujo por etapas
        if stage == 'triaje':
            tareas = crear_tareas(agente_triaje, agente_bd, datos_paciente, 'triaje')
            crew = Crew(
                agents=[agente_triaje, agente_bd],
                tasks=tareas,
                process=Process.sequential,
                verbose=False
            )
            resultado = crew.kickoff()
            resultado_serializable = limpiar_dict_para_json(serializar_resultado_crew(resultado))
            # Extraer contexto del output del agente de triaje
            output = None
            if resultado_serializable.get('tareas') and len(resultado_serializable['tareas']) > 0:
                output = resultado_serializable['tareas'][0].get('output_completo')
            elif resultado_serializable.get('respuesta_completa'):
                output = resultado_serializable['respuesta_completa']
            else:
                output = ''
            nuevo_contexto = extraer_contexto_triaje(output)
            next_contexto = merge_contextos(contexto, nuevo_contexto)
            return JsonResponse({
                'success': True,
                'stage': 'sugerir_cita',
                'contexto': next_contexto,
                'resultado': resultado_serializable
            })
        elif stage == 'sugerir_cita':
            # Se espera que contexto tenga especialidad, doctor_id, doctor_nombre, urgencia
            if respuesta_usuario and respuesta_usuario.lower() in ['si', 'sí', 'ok', 'acepto', 'quiero', 'confirmo']:
                tareas = crear_tareas(agente_triaje, agente_bd, datos_paciente, 'sugerir_cita', contexto)
                next_stage = 'confirmar_cita'  # Espera confirmación de la fecha sugerida

                crew = Crew(
                    agents=[agente_triaje, agente_bd],
                    tasks=tareas,
                    process=Process.sequential,
                    verbose=False
                )
                resultado = crew.kickoff()
                resultado_serializable = limpiar_dict_para_json(serializar_resultado_crew(resultado))

                # Extraer output del agente de BD (última tarea)
                output = None
                if resultado_serializable.get('tareas') and len(resultado_serializable['tareas']) > 0:
                    output = resultado_serializable['tareas'][-1].get('output_completo')
                elif resultado_serializable.get('respuesta_completa'):
                    output = resultado_serializable['respuesta_completa']
                else:
                    output = ''

                # ACTUALIZA el contexto combinando el anterior y el nuevo
                nuevo_contexto = extraer_contexto_triaje(output)
                next_contexto = merge_contextos(contexto, nuevo_contexto)
                return JsonResponse({
                    'success': True,
                    'stage': next_stage,
                    'contexto': next_contexto,
                    'resultado': resultado_serializable
                })
            else:
                return JsonResponse({
                    'success': True,
                    'stage': 'finalizado',
                    'message': 'No se agenda cita. Si necesitas otra recomendación, vuelve a describir tus síntomas.'
                })
        elif stage == 'confirmar_cita':
            # Validar que el contexto tenga doctor_id, doctor_nombre, fecha, hora
            required_fields = ['doctor_id', 'doctor_nombre', 'fecha', 'hora']
            missing = [f for f in required_fields if not contexto.get(f)]
            if missing:
                return JsonResponse({
                    'success': False,
                    'message': f'Faltan datos en el contexto para confirmar la cita: {", ".join(missing)}. Por favor, vuelve a la etapa anterior.'
                }, status=400)
            if respuesta_usuario and respuesta_usuario.lower() in ['si', 'sí', 'ok', 'acepto', 'confirmo']:
                tareas = crear_tareas(agente_triaje, agente_bd, datos_paciente, 'confirmar_cita', contexto)
                next_stage = 'finalizado'
            elif respuesta_usuario and (fecha_deseada or hora_deseada):
                # Usuario pide otra fecha
                next_contexto['fecha_deseada'] = fecha_deseada
                next_contexto['hora_deseada'] = hora_deseada
                tareas = crear_tareas(agente_triaje, agente_bd, datos_paciente, 'negociar_fecha', next_contexto)
                next_stage = 'confirmar_cita'
            else:
                return JsonResponse({
                    'success': True,
                    'stage': 'finalizado',
                    'message': 'No se agenda cita. Si necesitas otra recomendación, vuelve a describir tus síntomas.'
                })
        elif stage == 'negociar_fecha':
            # Se espera que contexto tenga doctor_id, doctor_nombre, fecha_deseada, hora_deseada
            tareas = crear_tareas(agente_triaje, agente_bd, datos_paciente, 'negociar_fecha', contexto)
            next_stage = 'confirmar_cita'
        else:
            return JsonResponse({
                'success': False,
                'message': f'Etapa desconocida: {stage}'
            }, status=400)

        crew = Crew(
            agents=[agente_triaje, agente_bd],
            tasks=tareas,
            process=Process.sequential,
            verbose=False
        )
        resultado = crew.kickoff()
        resultado_serializable = limpiar_dict_para_json(serializar_resultado_crew(resultado))
        return JsonResponse({
            'success': True,
            'stage': next_stage,
            'contexto': next_contexto,
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
        
@csrf_exempt
@require_http_methods(["POST"])
def transcribir_audio(request):
    """
    Vista para transcribir audio usando Whisper de OpenAI
    """
    try:
        # Verificar que se envió un archivo de audio
        if 'audio' not in request.FILES:
            return JsonResponse({
                'success': False,
                'message': 'No se encontró archivo de audio'
            }, status=400)
        
        audio_file = request.FILES['audio']
        
        # Validar tipo de archivo
        allowed_types = ['audio/wav', 'audio/mpeg', 'audio/mp4', 'audio/webm']
        if audio_file.content_type not in allowed_types:
            return JsonResponse({
                'success': False,
                'message': f'Tipo de archivo no soportado: {audio_file.content_type}'
            }, status=400)
        
        # Crear archivo temporal para Whisper
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name
        
        # Transcribir con Whisper
        with open(temp_file_path, 'rb') as audio:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                language="es"  # Español
            )
        
        # Limpiar archivo temporal
        import os
        os.unlink(temp_file_path)
        
        return JsonResponse({
            'success': True,
            'transcription': transcription.text
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error en transcripción: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def procesar_consulta_voz(request):
    """
    Vista integrada que recibe audio, lo transcribe y procesa la consulta médica
    """
    try:
        # Verificar que se envió un archivo de audio
        if 'audio' not in request.FILES:
            return JsonResponse({
                'success': False,
                'message': 'No se encontró archivo de audio'
            }, status=400)
        
        audio_file = request.FILES['audio']
        
        # Obtener datos adicionales del formulario
        nombre = request.POST.get('nombre')
        edad = request.POST.get('edad')
        telefono = request.POST.get('telefono')
        stage = request.POST.get('stage', 'triaje')
        contexto_str = request.POST.get('contexto', '{}')
        respuesta_usuario = request.POST.get('respuesta_usuario')
        
        try:
            contexto = json.loads(contexto_str)
        except Exception:
            contexto = {}

        if not nombre or not edad:
            return JsonResponse({
                'success': False,
                'message': 'Faltan datos obligatorios: nombre o edad'
            }, status=400)

        # Transcribir audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        with open(temp_file_path, 'rb') as audio:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                language="es"
            )

        import os
        os.unlink(temp_file_path)

        # CORRECCIÓN: Construir datos_paciente correctamente según la etapa
        if stage == 'triaje':
            # En triaje, los síntomas vienen de la transcripción
            datos_paciente = {
                'nombre': nombre,
                'edad': int(edad),
                'sintomas': transcription.text,
                'telefono': telefono if telefono else None
            }
        else:
            # En otras etapas, necesitamos los síntomas originales del contexto
            # y la respuesta del usuario de la transcripción
            datos_paciente = {
                'nombre': nombre,
                'edad': int(edad),
                'sintomas': contexto.get('sintomas_originales', transcription.text),
                'telefono': telefono if telefono else None
            }
            # Usar la transcripción como respuesta del usuario
            respuesta_usuario = transcription.text

        agente_triaje, agente_bd = crear_agentes()
        tareas = []
        next_stage = stage
        next_contexto = contexto.copy() if contexto else {}

        # FLUJO DE ETAPAS CORREGIDO
        if stage == 'triaje':
            tareas = crear_tareas(agente_triaje, agente_bd, datos_paciente, 'triaje')
            crew = Crew(
                agents=[agente_triaje, agente_bd],
                tasks=tareas,
                process=Process.sequential,
                verbose=False
            )
            resultado = crew.kickoff()
            resultado_serializable = limpiar_dict_para_json(serializar_resultado_crew(resultado))
            
            # Extraer contexto del output del agente de triaje
            output = None
            if resultado_serializable.get('tareas') and len(resultado_serializable['tareas']) > 0:
                output = resultado_serializable['tareas'][0].get('output_completo')
            elif resultado_serializable.get('respuesta_completa'):
                output = resultado_serializable['respuesta_completa']
            else:
                output = ''
            
            nuevo_contexto = extraer_contexto_triaje(output)
            next_contexto = merge_contextos(contexto, nuevo_contexto)
            # CORRECCIÓN: Guardar los síntomas originales para las siguientes etapas
            next_contexto['sintomas_originales'] = transcription.text
            
            return JsonResponse({
                'success': True,
                'stage': 'sugerir_cita',
                'contexto': next_contexto,
                'resultado': resultado_serializable,
                'transcription': transcription.text
            })
            
        elif stage == 'sugerir_cita':
            confirm_words = ['si', 'sí', 'ok', 'acepto', 'quiero', 'confirmo', 'está bien', 'perfecto']
            if respuesta_usuario and any(word in respuesta_usuario.lower() for word in confirm_words):
                tareas = crear_tareas(agente_triaje, agente_bd, datos_paciente, 'sugerir_cita', contexto)
                next_stage = 'confirmar_cita'
                
                crew = Crew(
                    agents=[agente_triaje, agente_bd],
                    tasks=tareas,
                    process=Process.sequential,
                    verbose=False
                )
                resultado = crew.kickoff()
                resultado_serializable = limpiar_dict_para_json(serializar_resultado_crew(resultado))
                
                output = None
                if resultado_serializable.get('tareas') and len(resultado_serializable['tareas']) > 0:
                    output = resultado_serializable['tareas'][-1].get('output_completo')
                elif resultado_serializable.get('respuesta_completa'):
                    output = resultado_serializable['respuesta_completa']
                else:
                    output = ''
                
                nuevo_contexto = extraer_contexto_triaje(output)
                next_contexto = merge_contextos(contexto, nuevo_contexto)
                
                return JsonResponse({
                    'success': True,
                    'stage': next_stage,
                    'contexto': next_contexto,
                    'resultado': resultado_serializable,
                    'transcription': transcription.text
                })
            else:
                return JsonResponse({
                    'success': True,
                    'stage': 'finalizado',
                    'message': 'No se agenda cita. Si necesitas otra recomendación, vuelve a describir tus síntomas.',
                    'transcription': transcription.text
                })
                
        elif stage == 'confirmar_cita':
            required_fields = ['doctor_id', 'doctor_nombre', 'fecha', 'hora']
            missing = [f for f in required_fields if not contexto.get(f)]
            if missing:
                return JsonResponse({
                    'success': False,
                    'message': f'Faltan datos en el contexto para confirmar la cita: {", ".join(missing)}. Por favor, vuelve a la etapa anterior.',
                    'transcription': transcription.text
                }, status=400)
                
            confirm_words = ['si', 'sí', 'ok', 'acepto', 'confirmo', 'está bien', 'perfecto']
            if respuesta_usuario and any(word in respuesta_usuario.lower() for word in confirm_words):
                tareas = crear_tareas(agente_triaje, agente_bd, datos_paciente, 'confirmar_cita', contexto)
                next_stage = 'finalizado'
            elif respuesta_usuario:
                # Usuario pide otra fecha
                tareas = crear_tareas(agente_triaje, agente_bd, datos_paciente, 'negociar_fecha', contexto)
                next_stage = 'confirmar_cita'
            else:
                return JsonResponse({
                    'success': True,
                    'stage': 'finalizado',
                    'message': 'No se agenda cita. Si necesitas otra recomendación, vuelve a describir tus síntomas.',
                    'transcription': transcription.text
                })
                
            crew = Crew(
                agents=[agente_triaje, agente_bd],
                tasks=tareas,
                process=Process.sequential,
                verbose=False
            )
            resultado = crew.kickoff()
            resultado_serializable = limpiar_dict_para_json(serializar_resultado_crew(resultado))
            
            return JsonResponse({
                'success': True,
                'stage': next_stage,
                'contexto': next_contexto,
                'resultado': resultado_serializable,
                'transcription': transcription.text
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Etapa desconocida: {stage}',
                'transcription': transcription.text
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error en procesamiento de voz: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generar_audio_respuesta(request):
    """
    Vista para convertir texto a audio usando TTS de OpenAI
    """
    try:
        data = json.loads(request.body)
        texto = data.get('texto')
        
        if not texto:
            return JsonResponse({
                'success': False,
                'message': 'No se proporcionó texto para convertir'
            }, status=400)
        
        # Generar audio con TTS
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="nova",  # Opciones: alloy, echo, fable, onyx, nova, shimmer
            input=texto,
            response_format="mp3"
        )
        
        # Crear respuesta HTTP con el audio
        audio_response = HttpResponse(
            response.content,
            content_type='audio/mpeg'
        )
        audio_response['Content-Disposition'] = 'attachment; filename="respuesta.mp3"'
        
        return audio_response
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Error: El cuerpo de la petición no es un JSON válido.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error en generación de audio: {str(e)}'
        }, status=500)