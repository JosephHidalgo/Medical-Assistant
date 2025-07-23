"use client"

import { useState, useEffect } from "react"
import {
  BarChart,
  ChevronLeft,
  ChevronDown,
  Bell,
  Home,
  CalendarIcon,
  MessageSquare,
  Star,
  Award,
  CreditCard,
  Utensils,
  Menu,
} from "lucide-react"
import Sidebar from "./Sidebar"
import Header from "./Header"
import MainContent from "./MainContent"

export default function DashboardSimple() {
  const [activeSection, setActiveSection] = useState("dashboard")
  const [isMobile, setIsMobile] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768)
    }
    handleResize()
    window.addEventListener("resize", handleResize)
    return () => {
      window.removeEventListener("resize", handleResize)
    }
  }, [])

  const sidebarItems = [
    { id: "dashboard", label: "Dashboard", icon: BarChart },
    { id: "citas", label: "Citas", icon: CalendarIcon },
    { id: "anuncios", label: "Anuncios", icon: Home },
    { id: "mensajes", label: "Mensajes", icon: MessageSquare },
    // { id: "customer-review", label: "Customer Review", icon: Star },
    // { id: "billing", label: "Billing System", icon: CreditCard },
    // { id: "food-delivery", label: "Food Delivery", icon: Utensils },
    { id: "premium", label: "Try Premium Version", icon: Award },
  ]

  const statsCards = [
    {
      title: "Arrival",
      subtitle: "(This week)",
      value: "73",
      change: "+24%",
      changeType: "positive",
      previousValue: "Previous week: 35",
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6 text-blue-500"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M5 12h14"></path>
          <path d="M12 5l7 7-7 7"></path>
        </svg>
      ),
      bgColor: "bg-blue-50",
    },
    {
      title: "Departure",
      subtitle: "(This week)",
      value: "35",
      change: "-12%",
      changeType: "negative",
      previousValue: "Previous week: 97",
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6 text-amber-500"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M19 12H5"></path>
          <path d="M12 19l-7-7 7-7"></path>
        </svg>
      ),
      bgColor: "bg-amber-50",
    },
    {
      title: "Booking",
      subtitle: "(This week)",
      value: "237",
      change: "+31%",
      changeType: "positive",
      previousValue: "Previous week: 187",
      icon: (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-6 w-6 text-cyan-500"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="16" y1="2" x2="16" y2="6"></line>
          <line x1="8" y1="2" x2="8" y2="6"></line>
          <line x1="3" y1="10" x2="21" y2="10"></line>
        </svg>
      ),
      bgColor: "bg-cyan-50",
    },
  ]

  const todayActivities = {
    roomAvailable: 5,
    roomBlocked: 10,
    guests: 15,
    totalRevenue: "Rs.35k",
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Mobile Sidebar Toggle */}
      {isMobile && (
        <button
          className="fixed bottom-4 right-4 z-50 rounded-full h-12 w-12 shadow-lg bg-white"
          onClick={() => setSidebarOpen(true)}
        >
          <Menu className="h-6 w-6" />
        </button>
      )}
      {/* Sidebar */}
      <Sidebar
        isMobile={isMobile}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        activeSection={activeSection}
        setActiveSection={setActiveSection}
        sidebarItems={sidebarItems}
      />
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header
          isMobile={isMobile}
          setSidebarOpen={setSidebarOpen}
          activeSection={activeSection}
        />
        <MainContent
          activeSection={activeSection}
          statsCards={statsCards}
          todayActivities={todayActivities}
          setActiveSection={setActiveSection}
        />
      </div>
    </div>
  )
}
