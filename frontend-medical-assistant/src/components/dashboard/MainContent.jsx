import StatsCards from "./StatsCards"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function MainContent({ activeSection, statsCards, todayActivities, setActiveSection }) {
  return (
    <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-gray-50">
      {activeSection === "dashboard" ? (
        <>
          {/* Date */}
          <div className="flex justify-end mb-4">
            <p className="text-sm text-gray-600">Wed // July 26th, 2023</p>
          </div>
          {/* Stats Cards */}
          <StatsCards statsCards={statsCards} todayActivities={todayActivities} />
          {/* Placeholder for additional content */}
          <div className="flex items-center justify-center h-64 bg-white rounded-lg border-2 border-dashed border-gray-300">
            <div className="text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Dashboard Content</h3>
              <p className="text-gray-500">Additional dashboard components would go here</p>
            </div>
          </div>
        </>
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