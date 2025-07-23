import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Menu, Home, ChevronDown, Bell } from "lucide-react"

export default function Header({ isMobile, setSidebarOpen, activeSection }) {
  return (
    <header className="bg-white border-b border-gray-200 flex items-center justify-between px-4 py-4 md:px-6">
      <div className="flex items-center">
        {isMobile && (
          <Button variant="ghost" size="icon" className="mr-2" onClick={() => setSidebarOpen(true)}>
            <Menu className="h-5 w-5" />
          </Button>
        )}
        <h1 className="text-xl font-semibold text-gray-800">
          {activeSection === "dashboard"
            ? "Dashboard"
            : activeSection === "check-in-out"
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
                        : "Premium Version"}
        </h1>
      </div>
      <div className="flex items-center space-x-4">
        {/* Hotel Selector
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="flex items-center gap-2 px-3 py-2 h-auto bg-transparent">
              <div className="w-6 h-6 bg-gray-200 rounded flex items-center justify-center">
                <Home className="h-4 w-4" />
              </div>
              <span className="hidden md:inline">Hotel Hilton Garden Inn</span>
              <ChevronDown className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>Hotel Marriott</DropdownMenuItem>
            <DropdownMenuItem>Hotel Hyatt</DropdownMenuItem>
            <DropdownMenuItem>Hotel Sheraton</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu> */}
        {/* Notifications */}
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          <span className="absolute top-0 right-0 h-2 w-2 bg-red-500 rounded-full"></span>
        </Button>
        {/* User Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-8 w-8 rounded-full">
              <Avatar className="h-8 w-8">
                <AvatarImage src="/placeholder.svg?height=32&width=32" alt="User" />
                <AvatarFallback>U</AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Settings</DropdownMenuItem>
            <DropdownMenuItem>Logout</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
} 