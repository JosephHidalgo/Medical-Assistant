"use client"
import { useState } from "react"
import { useAuth } from "@/contexts/AuthContext"
import { useRouter } from "next/navigation"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export function RegisterForm({ className, ...props }) {
  const [formData, setFormData] = useState({
    nombres: "",
    apellidos: "",
    email: "",
    celular: "",
    edad: "",
    password: "",
    confirmPassword: "",
  })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const router = useRouter()

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    if (!formData.nombres || !formData.apellidos || !formData.email || !formData.celular || !formData.edad || !formData.password || !formData.confirmPassword) {
      setError("Todos los campos son obligatorios")
      setLoading(false)
      return
    }

    if (formData.password.length < 6) {
      setError("La contraseña debe tener al menos 6 caracteres")
      setLoading(false)
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Las contraseñas no coinciden")
      setLoading(false)
      return
    }

    const edad = Number.parseInt(formData.edad)
    if (isNaN(edad) || edad < 18 || edad > 120) {
      setError("La edad debe ser un número válido entre 18 y 120 años")
      setLoading(false)
      return
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(formData.email)) {
      setError("Por favor ingresa un email válido")
      setLoading(false)
      return
    }

    const celularRegex = /^[0-9]{10,15}$/
    if (!celularRegex.test(formData.celular.replace(/\s/g, ""))) {
      setError("El número de celular debe tener entre 10 y 15 dígitos")
      setLoading(false)
      return
    }

    const datosRegistro = {
      nombres: formData.nombres,
      apellidos: formData.apellidos,
      correo_electronico: formData.email,
      numero_telefono: formData.celular,
      edad: formData.edad,
      contraseña: formData.password,
      confirmar_contraseña: formData.confirmPassword,
    };
    const result = await register(datosRegistro);
    console.log(result)

    if (result.success) {
      router.push("/")
    } else {
      setError(result.message)
    }

    setLoading(false)
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card className="overflow-hidden">
        <CardContent className="grid p-0 md:grid-cols-2">
          <form className="p-6 md:p-8" onSubmit={handleSubmit}>
            <div className="flex flex-col gap-6">
              <div className="flex flex-col items-center text-center">
                <h1 className="text-2xl font-bold text-indigo-800">Crea tu cuenta</h1>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="nombres">Nombres</Label>
                  <Input
                    id="nombres"
                    type="text"
                    placeholder="Juan Carlos"
                    required
                    value={formData.nombres}
                    onChange={(e) => handleInputChange("nombres", e.target.value)}
                    disabled={loading}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="apellidos">Apellidos</Label>
                  <Input
                    id="apellidos"
                    type="text"
                    placeholder="García López"
                    required
                    value={formData.apellidos}
                    onChange={(e) => handleInputChange("apellidos", e.target.value)}
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="email">Correo electrónico</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="juan@example.com"
                  required
                  value={formData.email}
                  onChange={(e) => handleInputChange("email", e.target.value)}
                  disabled={loading}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="celular">Número de celular</Label>
                  <Input
                    id="celular"
                    type="tel"
                    placeholder="3001234567"
                    required
                    value={formData.celular}
                    onChange={(e) => handleInputChange("celular", e.target.value)}
                    disabled={loading}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="edad">Edad</Label>
                  <Input
                    id="edad"
                    type="number"
                    placeholder="25"
                    min="18"
                    max="120"
                    required
                    value={formData.edad}
                    onChange={(e) => handleInputChange("edad", e.target.value)}
                    disabled={loading}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="password">Contraseña</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    required
                    value={formData.password}
                    onChange={(e) => handleInputChange("password", e.target.value)}
                    disabled={loading}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="confirmPassword">Confirmar contraseña</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="••••••••"
                    required
                    value={formData.confirmPassword}
                    onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                    disabled={loading}
                  />
                </div>
              </div>

              {error && <div className="text-red-500 text-sm text-center">{error}</div>}

              <Button type="submit" className="w-full bg-indigo-500 hover:bg-indigo-600" disabled={loading}>
                {loading ? "Creando cuenta..." : "Crear cuenta"}
              </Button>

              <div className="text-center text-sm">
                ¿Ya tienes una cuenta?{" "}
                <a href="/login" className="underline underline-offset-4">
                  Iniciar sesión
                </a>
              </div>
            </div>
          </form>
          <div className="relative hidden bg-muted md:block">
            <img
              src="/logo.png"
              alt="Image"
              className="absolute inset-0 h-full w-full object-cover dark:brightness-[0.2] dark:grayscale"
            />
          </div>
        </CardContent>
      </Card>
      <div className="text-balance text-center text-xs text-muted-foreground [&_a]:underline [&_a]:underline-offset-4 hover:[&_a]:text-primary">
        Al continuar, aceptas nuestros <a href="#">Términos de Servicio</a> y <a href="#">Política de Privacidad</a>.
      </div>
    </div>
  )
}