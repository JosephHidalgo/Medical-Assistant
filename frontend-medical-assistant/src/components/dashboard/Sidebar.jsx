import { Button } from "@/components/ui/button"
import { ChevronLeft, Menu } from "lucide-react"

export default function Sidebar({ isMobile, sidebarOpen, setSidebarOpen, activeSection, setActiveSection, sidebarItems }) {
  return (
    <div
      className={`$
        {isMobile ? "fixed inset-0 z-50 transform transition-transform duration-300 ease-in-out" : "w-64"}
        $
        {isMobile && !sidebarOpen ? "-translate-x-full" : "translate-x-0"}
        bg-white border-r border-gray-200 flex flex-col`}
    >
      {isMobile && (
        <div className="flex justify-end p-4">
          <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(false)}>
            <ChevronLeft className="h-6 w-6" />
          </Button>
        </div>
      )}
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-2xl font-semibold text-purple-600">MEDIAGENT</h1>
      </div>
      {/* Navigation */}
      <div className="flex-1 py-4 overflow-y-auto">
        <nav className="space-y-1 px-2">
          {sidebarItems.map((item) => {
            const IconComponent = item.icon
            return (
              <button
                key={item.id}
                onClick={() => {
                  setActiveSection(item.id)
                  if (isMobile) setSidebarOpen(false)
                }}
                className={`flex items-center w-full px-4 py-3 text-sm font-medium rounded-r-md transition-colors $
                  {activeSection === item.id
                    ? "text-blue-600 bg-blue-50 border-l-4 border-blue-600"
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"}
                `}
              >
                <IconComponent className="mr-3 h-5 w-5" />
                {item.label}
              </button>
            )
          })}
        </nav>
      </div>
    </div>
  )
} 