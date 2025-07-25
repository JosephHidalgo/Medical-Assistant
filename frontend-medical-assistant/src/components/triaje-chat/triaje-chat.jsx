"use client"

import { useState, useRef, useEffect, useContext } from "react"
import { AuthContext } from '@/contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Send, Bot, User, ArrowLeft, Clock, AlertCircle } from "lucide-react"

export default function TriajeChat({ onBack }) {
  const { nombres, edad, numeroTelefono, paciente, pacienteId } = useContext(AuthContext);
  const [messages, setMessages] = useState([
    {
      id: "1",
      content:
        "¡Hola! Soy tu asistente médico de triaje. Estoy aquí para ayudarte a evaluar tus síntomas y determinar el nivel de urgencia de tu consulta. ¿Podrías contarme qué síntomas estás experimentando?",
      sender: "agent",
      timestamp: new Date(),
      type: "text",
    },
  ])
  const [inputMessage, setInputMessage] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [stage, setStage] = useState('triaje')
  const [contexto, setContexto] = useState({})
  const [sintomas, setSintomas] = useState("")
  const [inputDisabled, setInputDisabled] = useState(false)
  const scrollAreaRef = useRef(null)
  const inputRef = useRef(null)

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  // Simulated agent responses
//   const getAgentResponse = (userMessage) => {
//     const lowerMessage = userMessage.toLowerCase()

//     if (lowerMessage.includes("dolor") && lowerMessage.includes("pecho")) {
//       return {
//         id: Date.now().toString(),
//         content:
//           "Entiendo que tienes dolor en el pecho. Esta es una situación que requiere atención inmediata. ¿El dolor es intenso? ¿Se irradia hacia el brazo izquierdo, cuello o mandíbula? ¿Tienes dificultad para respirar?",
//         sender: "agent",
//         timestamp: new Date(),
//         type: "urgent",
//       }
//     } else if (lowerMessage.includes("fiebre") || lowerMessage.includes("temperatura")) {
//       return {
//         id: Date.now().toString(),
//         content:
//           "¿Podrías decirme qué temperatura tienes? ¿Desde cuándo tienes fiebre? ¿Tienes otros síntomas como dolor de cabeza, dolor de garganta o malestar general?",
//         sender: "agent",
//         timestamp: new Date(),
//         type: "text",
//       }
//     } else if (lowerMessage.includes("dolor de cabeza") || lowerMessage.includes("cefalea")) {
//       return {
//         id: Date.now().toString(),
//         content:
//           "Comprendo que tienes dolor de cabeza. ¿Podrías describir el tipo de dolor? ¿Es pulsátil, constante, o punzante? ¿En qué parte de la cabeza lo sientes más? ¿Del 1 al 10, qué intensidad tiene?",
//         sender: "agent",
//         timestamp: new Date(),
//         type: "text",
//       }
//     } else {
//       return {
//         id: Date.now().toString(),
//         content:
//           "Gracias por la información. ¿Podrías ser más específico sobre tus síntomas? Por ejemplo: ¿cuándo comenzaron?, ¿qué intensidad tienen del 1 al 10?, ¿hay algo que los mejore o empeore?",
//         sender: "agent",
//         timestamp: new Date(),
//         type: "text",
//       }
//     }
//   }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || inputDisabled) return

    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: "user",
      timestamp: new Date(),
      type: "text",
    }

    setMessages((prev) => [...prev, userMessage])
    setIsTyping(true)
    setInputMessage("")

    // Construir el contexto con el id del paciente
    const contextoConId = {
      ...contexto,
      paciente_id: paciente?.id || pacienteId,
    }

    // Construir el payload según la etapa
    let payload = {
      stage,
      nombre: nombres,
      edad: edad,
      telefono: numeroTelefono,
      sintomas: stage === 'triaje' ? inputMessage : sintomas,
      respuesta_usuario: stage !== 'triaje' ? inputMessage : undefined,
      contexto: contextoConId,
    }
    console.log("payload", payload)
    // Si el usuario pide otra fecha, puedes pedirla con un input especial y añadir aquí:
    // payload.fecha_deseada = ...
    // payload.hora_deseada = ...
    // Limpiar campos undefined
    Object.keys(payload).forEach(key => payload[key] === undefined && delete payload[key])

    try {
      const response = await fetch("http://localhost:8000/asistente/atender/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
      const data = await response.json()
      // Extraer el mensaje del agente
      let agentMessage = "No se recibió respuesta del backend."
      if (data.resultado) {
        console.log(data.resultado)
        // Buscar respuesta conversacional en el resultado
        if (data.resultado.tareas && data.resultado.tareas.length > 0) {
          // Usar el output completo de la última tarea
          agentMessage = data.resultado.tareas[data.resultado.tareas.length - 1].output_completo
        } else if (data.resultado.respuesta_completa) {
          agentMessage = data.resultado.respuesta_completa
        }
      } else if (data.message) {
        agentMessage = data.message
      }
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          content: agentMessage,
          sender: "agent",
          timestamp: new Date(),
          type: "text",
        },
      ])
      // Actualizar stage y contexto
      if (data.stage) setStage(data.stage)
      if (data.contexto) setContexto(data.contexto)
      // Guardar los síntomas originales para las siguientes etapas
      if (stage === 'triaje') setSintomas(inputMessage)
      // Si la conversación terminó, deshabilitar input
      if (data.stage === 'finalizado') setInputDisabled(true)
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          content: "Ocurrió un error al contactar al backend.",
          sender: "agent",
          timestamp: new Date(),
          type: "text",
        },
      ])
    }
    setIsTyping(false)
  }

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

//   const quickResponses = ["Dolor de cabeza", "Fiebre", "Dolor de pecho", "Náuseas", "Mareos", "Dolor abdominal"]

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-2rem)] bg-gray-50">
      {/* Header */}
      <Card className="rounded-b-none border-b-0">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Button variant="ghost" size="sm" onClick={onBack} className="p-2">
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <Avatar className="h-10 w-10 bg-purple-100">
                <AvatarFallback>
                  <Bot className="h-5 w-5 text-purple-600" />
                </AvatarFallback>
              </Avatar>
              <div>
                <CardTitle className="text-lg">Agente de Triaje IA</CardTitle>
                <span className="text-sm text-gray-500 flex items-center">
                  <span className="w-2 h-2 bg-green-400 rounded-full mr-2 inline-block"></span>
                  En línea - Evaluación médica
                </span>
              </div>
            </div>
            <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
              <Clock className="h-3 w-3 mr-1" />
              Triaje Activo
            </Badge>
          </div>
        </CardHeader>
      </Card>

      {/* Messages Area */}
      <Card className="flex-1 rounded-none border-x-0 border-t-0">
        <CardContent className="p-0 h-full">
          <ScrollArea className="h-[400px] p-4" ref={scrollAreaRef}>
            <div className="space-y-4">
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`flex items-start space-x-2 max-w-[80%] ${message.sender === "user" ? "flex-row-reverse space-x-reverse" : ""}`}
                  >
                    <Avatar className="h-8 w-8 flex-shrink-0">
                      <AvatarFallback className={message.sender === "user" ? "bg-gray-100" : "bg-purple-100"}>
                        {message.sender === "user" ? (
                          <User className="h-4 w-4 text-gray-600" />
                        ) : (
                          <Bot className="h-4 w-4 text-purple-600" />
                        )}
                      </AvatarFallback>
                    </Avatar>
                    <div
                      className={`rounded-lg p-3 ${
                        message.sender === "user"
                          ? "bg-purple-600 text-white"
                          : message.type === "urgent"
                            ? "bg-red-50 border border-red-200 text-red-900"
                            : "bg-white border border-gray-200 text-gray-900"
                      }`}
                    >
                      {message.type === "urgent" && (
                        <div className="flex items-center mb-2">
                          <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
                          <span className="text-xs font-semibold text-red-600">ATENCIÓN URGENTE</span>
                        </div>
                      )}
                      <p className="text-sm">{message.content}</p>
                      <p className={`text-xs mt-1 ${message.sender === "user" ? "text-purple-200" : "text-gray-500"}`}>
                        {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </p>
                    </div>
                  </div>
                </div>
              ))}

              {/* Typing indicator */}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-2">
                    <Avatar className="h-8 w-8">
                      <AvatarFallback className="bg-purple-100">
                        <Bot className="h-4 w-4 text-purple-600" />
                      </AvatarFallback>
                    </Avatar>
                    <div className="bg-white border border-gray-200 rounded-lg p-3">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: "0.1s" }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                          style={{ animationDelay: "0.2s" }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Quick Responses
      <Card className="rounded-none border-x-0 border-b-0">
        <CardContent className="p-4">
          <div className="mb-3">
            <p className="text-xs text-gray-500 mb-2">Respuestas rápidas:</p>
            <div className="flex flex-wrap gap-2">
              {quickResponses.map((response) => (
                <Button
                  key={response}
                  variant="outline"
                  size="sm"
                  className="text-xs h-7 bg-white hover:bg-purple-50 hover:border-purple-300"
                  onClick={() => setInputMessage(response)}
                >
                  {response}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card> */}

      {/* Input Area */}
      <Card className="rounded-t-none border-t-0">
        <CardContent className="p-4">
          <div className="flex space-x-2">
            <Input
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Describe tus síntomas..."
              className="flex-1"
              disabled={isTyping || inputDisabled}
            />
            <Button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isTyping || inputDisabled}
              className="bg-purple-600 hover:bg-purple-700"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Presiona Enter para enviar. Esta evaluación no reemplaza una consulta médica profesional.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}