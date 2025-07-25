"use client"
import { useState, useRef, useEffect, useContext } from 'react';
import { AuthContext } from '@/contexts/AuthContext';

const VoiceAssistant = () => {
  const { paciente, pacienteId, nombres, edad, numeroTelefono, isAuthenticated } = useContext(AuthContext);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [response, setResponse] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [stage, setStage] = useState('triaje');
  const [contexto, setContexto] = useState({});
  const [inputDisabled, setInputDisabled] = useState(false);
  const [respuestaUsuario, setRespuestaUsuario] = useState('');

  // REFS PARA MANTENER VALORES ACTUALES
  const stageRef = useRef(stage);
  const contextoRef = useRef(contexto);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);

  // ACTUALIZAR REFS CUANDO CAMBIEN LOS ESTADOS
  useEffect(() => {
    stageRef.current = stage;
  }, [stage]);

  useEffect(() => {
    contextoRef.current = contexto;
  }, [contexto]);

  // Inicializar MediaRecorder
  const initializeRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      });
      
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { 
          type: 'audio/webm;codecs=opus' 
        });
        processAudio(audioBlob);
        audioChunksRef.current = [];
      };
      
    } catch (error) {
      console.error('Error al acceder al micrófono:', error);
      alert('Error al acceder al micrófono. Verifica los permisos.');
    }
  };

  useEffect(() => {
    initializeRecording();
    return () => {
      if (mediaRecorderRef.current?.stream) {
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Iniciar grabación
  const startRecording = () => {
    if (!isAuthenticated || !nombres || !edad || inputDisabled) {
      alert('Debes iniciar sesión y tener tus datos completos para grabar.');
      return;
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'inactive') {
      audioChunksRef.current = [];
      mediaRecorderRef.current.start();
      setIsRecording(true);
      setTranscription('');
      setResponse('');
      setAudioUrl('');
    }
  };

  // Detener grabación
  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsProcessing(true);
    }
  };

  // FUNCIÓN PROCESSAUDIO CORREGIDA CON ID PACIENTE EN CONTEXTO
  const processAudio = async (audioBlob) => {
    try {
      // PASO 1: PRIMERO TRANSCRIBIR EL AUDIO
      const transcribeFormData = new FormData();
      transcribeFormData.append('audio', audioBlob, 'recording.webm');
      
      const transcribeResponse = await fetch('http://localhost:8000/transcribir-audio/', {
        method: 'POST',
        body: transcribeFormData,
      });
      
      const transcribeData = await transcribeResponse.json();
      
      if (!transcribeData.success) {
        alert(`Error en transcripción: ${transcribeData.message}`);
        return;
      }
      
      const nuevaTranscripcion = transcribeData.transcription;
      
      // PASO 2: USAR VALORES ACTUALES DE LOS REFS
      const currentStage = stageRef.current;
      const currentContexto = contextoRef.current;
      // AGREGAR ID DEL PACIENTE AL CONTEXTO
      const contextoConId = {
        ...currentContexto,
        paciente_id: paciente?.id || pacienteId,
      };
      
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      formData.append('nombre', nombres);
      formData.append('edad', edad);
      formData.append('telefono', numeroTelefono || '');
      formData.append('stage', currentStage);
      formData.append('contexto', JSON.stringify(contextoConId));
      
      // USAR LA NUEVA TRANSCRIPCIÓN COMO RESPUESTA_USUARIO
      if (currentStage !== 'triaje') {
        formData.append('respuesta_usuario', nuevaTranscripcion);
      }

      console.log("Enviando:", {
        stage: currentStage,
        contexto: contextoConId, 
        respuesta_usuario: currentStage !== 'triaje' ? nuevaTranscripcion : 'N/A'
      });

      const response = await fetch('http://localhost:8000/procesar-consulta-voz/', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      console.log("Respuesta del backend:", data);

      if (data.success) { 
        // ACTUALIZAR ESTADOS
        if (data.stage) {
          setStage(data.stage);
        }
        if (data.contexto) {
          setContexto(data.contexto);
        }
        
        setTranscription(data.transcription);
        setResponse(data.resultado.respuesta_completa);
        await generateResponseAudio(data.resultado.respuesta_completa);
        
        // Si la conversación terminó, deshabilitar input
        if (data.stage === 'finalizado') setInputDisabled(true);
        
        // Resetear respuestaUsuario después de procesar
        setRespuestaUsuario('');
      } else {
        alert(`Error: ${data.message}`);
      }
    } catch (error) {
      console.error('Error al procesar audio:', error);
      alert('Error al procesar el audio. Intenta nuevamente.');
    } finally {
      setIsProcessing(false);
    }
  };

  // Generar audio de la respuesta
  const generateResponseAudio = async (text) => {
    try {
      const response = await fetch('http://localhost:8000/generar-audio/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ texto: text }),
      });

      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioUrl(audioUrl);
      }
    } catch (error) {
      console.error('Error al generar audio de respuesta:', error);
    }
  };

  // Reproducir audio de respuesta
  const playResponse = () => {
    if (audioRef.current && audioUrl) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  // Manejar fin de reproducción
  const handleAudioEnd = () => {
    setIsPlaying(false);
  };

  // Permitir grabar nueva respuesta si el flujo no ha terminado
  const puedeGrabar = isAuthenticated && !isProcessing && !inputDisabled;

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-center mb-6 text-blue-600">
        Asistente Médico por Voz
      </h2>

      {/* Mostrar advertencia si no autenticado */}
      {!isAuthenticated && (
        <div className="mb-6 p-4 bg-yellow-100 text-yellow-800 rounded">
          Debes iniciar sesión para usar el asistente por voz.
        </div>
      )}

      {/* Estado del flujo */}
      <div className="mb-4 text-sm text-gray-500 text-center">
        <span className="font-semibold">Etapa actual:</span> {stage}
      </div>

      {/* Controles de grabación */}
      <div className="text-center mb-6">
        <div className="mb-4">
          {!isRecording ? (
            <button
              onClick={startRecording}
              disabled={!puedeGrabar}
              className="bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-6 rounded-full transition-colors disabled:bg-gray-400"
            >
              🎤 {stage === 'triaje' ? 'Iniciar Grabación' : 'Responder por Voz'}
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="bg-red-700 hover:bg-red-800 text-white font-bold py-3 px-6 rounded-full animate-pulse"
            >
              ⏹️ Detener Grabación
            </button>
          )}
        </div>

        {isRecording && (
          <p className="text-red-600 font-medium">
            🔴 Grabando... {stage === 'triaje' ? 'Describe tus síntomas claramente' : 'Responde a la pregunta del asistente'}
          </p>
        )}

        {isProcessing && (
          <p className="text-blue-600 font-medium">
            ⏳ Procesando audio y consultando con el asistente médico...
          </p>
        )}
      </div>

      {/* Transcripción */}
      {transcription && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-2">Transcripción:</h3>
          <p className="text-gray-700">{transcription}</p>
        </div>
      )}

      {/* Respuesta del asistente */}
      {response && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-semibold text-blue-800">Respuesta del Asistente Médico:</h3>
            {audioUrl && (
              <button
                onClick={playResponse}
                disabled={isPlaying}
                className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm disabled:bg-gray-400"
              >
                {isPlaying ? '🔊 Reproduciendo...' : '🔊 Escuchar'}
              </button>
            )}
          </div>
          <div className="text-blue-700 whitespace-pre-line">
            {response}
          </div>
        </div>
      )}

      {/* Audio element para reproducir respuesta */}
      {audioUrl && (
        <audio
          ref={audioRef}
          src={audioUrl}
          onEnded={handleAudioEnd}
          className="hidden"
        />
      )}
    </div>
  );
};

export default VoiceAssistant;