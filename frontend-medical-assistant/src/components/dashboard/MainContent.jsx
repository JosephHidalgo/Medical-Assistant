"use client"

import MedicalAppointments from "./StatsCards"
import TriajeChat from "@/components/triaje-chat/triaje-chat"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Stethoscope, Brain, Clock, Shield, Users, Activity, ArrowRight, Sparkles } from "lucide-react"

export default function MainContent({ activeSection, statsCards, todayActivities, setActiveSection }) {
  return (
    <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-gray-50">
      {activeSection === "dashboard" ? (
        <>
          {/* Date */}
          <div className="flex justify-end mb-6">
            <p className="text-sm text-gray-600 bg-white px-3 py-1 rounded-full shadow-sm">Wed // July 26th, 2023</p>
          </div>

          {/* Stats Cards */}
          <MedicalAppointments statsCards={statsCards} todayActivities={todayActivities} />

          {/* Hero Section - AI Medical Assistant */}
          <div className="mt-8 mb-8">
            <Card className="bg-gradient-to-r from-indigo-300 to-indigo-400 text-white border-0 shadow-xl">
              <CardContent className="p-8">
                <div className="flex flex-col lg:flex-row items-center justify-between">
                  <div className="flex-1 mb-6 lg:mb-0">
                    <div className="flex items-center mb-4">
                      <Brain className="h-8 w-8 mr-3" />
                      <Badge variant="secondary" className="bg-white/20 text-white border-white/30">
                        <Sparkles className="h-3 w-3 mr-1" />
                        IA Médica Avanzada
                      </Badge>
                    </div>
                    <h1 className="text-3xl lg:text-4xl font-bold mb-4">Asistente Médico Inteligente</h1>
                    <p className="text-lg text-blue-100 mb-6 max-w-2xl">
                      Revoluciona tu práctica médica con nuestro sistema de triaje inteligente. Evaluación rápida,
                      precisa y confiable para optimizar la atención al paciente.
                    </p>
                    <Button
                      size="lg"
                      className="bg-white text-purple-600 hover:bg-gray-50 font-semibold px-8 py-3 text-lg shadow-lg"
                      onClick={() => setActiveSection("triaje")}
                    >
                      Iniciar Triaje IA
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                  </div>
                  <div className="flex-shrink-0">
                    <div className="relative">
                      <div className="w-32 h-32 lg:w-40 lg:h-40 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                        <Stethoscope className="h-16 w-16 lg:h-20 lg:w-20 text-white" />
                      </div>
                      <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full animate-pulse"></div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <Card className="hover:shadow-lg transition-shadow duration-300 border-l-4 border-l-purple-500">
              <CardHeader className="pb-3">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg mr-3">
                    <Clock className="h-6 w-6 text-purple-600" />
                  </div>
                  <CardTitle className="text-lg">Triaje Rápido</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-gray-600">
                  Evaluación automática de síntomas en menos de 2 minutos con precisión del 95%
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow duration-300 border-l-4 border-l-green-500">
              <CardHeader className="pb-3">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg mr-3">
                    <Shield className="h-6 w-6 text-green-600" />
                  </div>
                  <CardTitle className="text-lg">Seguro y Confiable</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-gray-600">
                  Algoritmos validados clínicamente y cumplimiento total con normativas médicas
                </CardDescription>
              </CardContent>
            </Card>

            <Card className="hover:shadow-lg transition-shadow duration-300 border-l-4 border-l-gray-500">
              <CardHeader className="pb-3">
                <div className="flex items-center">
                  <div className="p-2 bg-gray-100 rounded-lg mr-3">
                    <Activity className="h-6 w-6 text-gray-600" />
                  </div>
                  <CardTitle className="text-lg">Monitoreo Continuo</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-gray-600">
                  Seguimiento en tiempo real del estado del paciente y alertas automáticas
                </CardDescription>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="h-5 w-5 mr-2 text-purple-600" />
                Acciones Rápidas
              </CardTitle>
              <CardDescription>Accede rápidamente a las funciones más utilizadas del sistema</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <Button
                  variant="outline"
                  className="h-20 flex-col space-y-2 hover:bg-purple-50 hover:border-purple-300 bg-white"
                  onClick={() => setActiveSection("triaje")}
                >
                  <Brain className="h-6 w-6 text-purple-600" />
                  <span className="text-sm font-medium">Nuevo Triaje</span>
                </Button>

                <Button
                  variant="outline"
                  className="h-20 flex-col space-y-2 hover:bg-green-50 hover:border-green-300 bg-white"
                  onClick={() => setActiveSection("patients")}
                >
                  <Users className="h-6 w-6 text-green-600" />
                  <span className="text-sm font-medium">Pacientes</span>
                </Button>

                <Button
                  variant="outline"
                  className="h-20 flex-col space-y-2 hover:bg-gray-50 hover:border-gray-300 bg-white"
                  onClick={() => setActiveSection("reports")}
                >
                  <Activity className="h-6 w-6 text-gray-600" />
                  <span className="text-sm font-medium">Reportes</span>
                </Button>

                <Button
                  variant="outline"
                  className="h-20 flex-col space-y-2 hover:bg-yellow-50 hover:border-yellow-300 bg-white"
                  onClick={() => setActiveSection("settings")}
                >
                  <Shield className="h-6 w-6 text-yellow-600" />
                  <span className="text-sm font-medium">Configuración</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </>
      ) : activeSection === "triaje" ? (
        <TriajeChat onBack={() => setActiveSection("dashboard")} />
      ) : (
        /* Other Sections Placeholder */
        <div className="flex items-center justify-center h-full">
          <Card className="w-full max-w-md">
            <CardContent className="p-6 text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Coming Soon</h3>
              <p className="text-gray-500 mb-4">
                The{" "}
                {activeSection === "check-in-out"
                    ? "Check In-Out"
                    : activeSection === "rooms"
                      ? "Rooms"
                      : activeSection === "messages"
                        ? "Messages"
                        : activeSection === "customer-review"
                          ? "Customer Review"
                          : activeSection === "billing"
                            ? "Billing System"
                            : activeSection === "food-delivery"
                              ? "Food Delivery"
                              : "Premium"}{" "}
                module is currently being built.
              </p>
              <Button onClick={() => setActiveSection("dashboard")}>Return to Dashboard</Button>
            </CardContent>
          </Card>
        </div>
      )}
    </main>
  )
}
