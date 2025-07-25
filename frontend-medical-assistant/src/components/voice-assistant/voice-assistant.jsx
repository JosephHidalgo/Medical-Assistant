"use client"
import { useState, useRef, useEffect } from 'react';

const VoiceAssistant = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [response, setResponse] = useState('');
  const [audioUrl, setAudioUrl] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);

  // Datos del paciente
  const [patientData, setPatientData] = useState({
    nombre: 'Benito',
    edad: '20',
    telefono: '1234567890'
  });

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);

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

  // Inicializar al montar el componente
  useEffect(() => {
    initializeRecording();
    
    return () => {
      // Limpiar recursos
      if (mediaRecorderRef.current?.stream) {
        mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Iniciar grabación
  const startRecording = () => {
    if (!patientData.nombre || !patientData.edad) {
      alert('Por favor, completa los datos del paciente antes de grabar.');
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
    console.log(patientData.nombre);
    console.log(patientData.edad);
    console.log(patientData.telefono);

    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsProcessing(true);
    }
  };

  // Procesar audio grabado
  const processAudio = async (audioBlob) => {
    try {
      console.log(patientData.nombre);
      console.log(patientData.edad);
      console.log(patientData.telefono);

      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');
      formData.append('nombre', patientData.nombre);
      formData.append('edad', patientData.edad);
      formData.append('telefono', patientData.telefono);

      

      const response = await fetch('http://localhost:8000/procesar-consulta-voz/', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        setTranscription(data.transcription);
        setResponse(data.resultado.respuesta_completa);
        
        // Generar audio de la respuesta
        await generateResponseAudio(data.resultado.respuesta_completa);
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

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-center mb-6 text-blue-600">
        Asistente Médico por Voz
      </h2>

      {/* Formulario de datos del paciente */}
      <div className="mb-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nombre del Paciente
          </label>
          <input
            type="text"
            value={patientData.nombre}
            onChange={(e) => setPatientData({...patientData, nombre: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Ingresa el nombre completo"
            disabled={isRecording || isProcessing}
          />
        </div>
        
        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Edad
            </label>
            <input
              type="number"
              value={patientData.edad}
              onChange={(e) => setPatientData({...patientData, edad: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Edad"
              disabled={isRecording || isProcessing}
            />
          </div>
          
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Teléfono (Opcional)
            </label>
            <input
              type="tel"
              value={patientData.telefono}
              onChange={(e) => setPatientData({...patientData, telefono: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Número de teléfono"
              disabled={isRecording || isProcessing}
            />
          </div>
        </div>
      </div>

      {/* Controles de grabación */}
      <div className="text-center mb-6">
        <div className="mb-4">
          {!isRecording ? (
            <button
              onClick={startRecording}
              disabled={isProcessing}
              className="bg-red-500 hover:bg-red-600 text-white font-bold py-3 px-6 rounded-full transition-colors disabled:bg-gray-400"
            >
              🎤 Iniciar Grabación
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
            🔴 Grabando... Describe tus síntomas claramente
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