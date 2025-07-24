import { Card, CardContent } from "@/components/ui/card"
import { Calendar, Clock, User, CheckCircle, AlertCircle, XCircle, Clock4 } from "lucide-react"

const appointmentData = [
  {
    id: 1,
    date: "2024-01-15",
    time: "09:30",
    specialty: "Cardiología",
    doctor: "Dr. María González",
    status: "confirmed",
    statusColor: "bg-green-100 text-green-700",
    statusIcon: <CheckCircle className="w-4 h-4" />,
  },
  {
    id: 2,
    date: "2024-01-18",
    time: "14:15",
    specialty: "Dermatología",
    doctor: "Dr. Carlos Ruiz",
    status: "pending",
    statusColor: "bg-yellow-100 text-yellow-700",
    statusIcon: <Clock4 className="w-4 h-4" />,
  },
  {
    id: 3,
    date: "2024-01-22",
    time: "11:00",
    specialty: "Neurología",
    doctor: "Dra. Ana Martínez",
    status: "cancelled",
    statusColor: "bg-red-100 text-red-700",
    statusIcon: <XCircle className="w-4 h-4" />,
  },
  {
    id: 4,
    date: "2024-01-25",
    time: "16:45",
    specialty: "Oftalmología",
    doctor: "Dr. Luis Hernández",
    status: "rescheduled",
    statusColor: "bg-blue-100 text-blue-700",
    statusIcon: <AlertCircle className="w-4 h-4" />,
  },
]

const getStatusText = (status) => {
  const statusMap = {
    confirmed: "Confirmada",
    pending: "Pendiente",
    cancelled: "Cancelada",
    rescheduled: "Reprogramada",
  }
  return statusMap[status] || status
}

export default function MedicalAppointments() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-6">
      {appointmentData.map((appointment) => (
        <Card key={appointment.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            {/* Fecha y Hora */}
            <div className="flex items-center mb-3">
              <Calendar className="w-4 h-4 text-blue-600 mr-2" />
              <div>
                <p className="text-sm font-medium">{appointment.date}</p>
                <div className="flex items-center mt-1">
                  <Clock className="w-3 h-3 text-gray-500 mr-1" />
                  <p className="text-xs text-gray-500">{appointment.time}</p>
                </div>
              </div>
            </div>

            {/* Especialidad */}
            <div className="mb-3">
              <p className="text-lg font-semibold text-gray-800">{appointment.specialty}</p>
            </div>

            {/* Doctor */}
            <div className="flex items-center mb-3">
              <User className="w-4 h-4 text-gray-600 mr-2" />
              <p className="text-sm text-gray-600">{appointment.doctor}</p>
            </div>

            {/* Estado */}
            <div className="flex items-center">
              <span
                className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${appointment.statusColor}`}
              >
                {appointment.statusIcon}
                <span className="ml-1">{getStatusText(appointment.status)}</span>
              </span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
