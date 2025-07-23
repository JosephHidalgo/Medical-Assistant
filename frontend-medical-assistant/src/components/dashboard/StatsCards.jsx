import { Card, CardContent } from "@/components/ui/card"

function TodayActivitiesCard({ todayActivities }) {
  return (
    <Card>
      <CardContent className="p-4">
        <p className="text-sm text-gray-500 mb-2">Today Activities</p>
        <div className="flex justify-between mb-2">
          <div className="text-center">
            <div className="bg-blue-500 text-white rounded-full w-10 h-10 flex items-center justify-center mx-auto mb-1">
              <span>{todayActivities.roomAvailable}</span>
            </div>
            <p className="text-xs">
              Room
              <br />
              Available
            </p>
          </div>
          <div className="text-center">
            <div className="bg-blue-500 text-white rounded-full w-10 h-10 flex items-center justify-center mx-auto mb-1">
              <span>{todayActivities.roomBlocked}</span>
            </div>
            <p className="text-xs">
              Room
              <br />
              Blocked
            </p>
          </div>
          <div className="text-center">
            <div className="bg-blue-500 text-white rounded-full w-10 h-10 flex items-center justify-center mx-auto mb-1">
              <span>{todayActivities.guests}</span>
            </div>
            <p className="text-xs">Guest</p>
          </div>
        </div>
        <div className="mt-4">
          <p className="text-xs text-gray-500">Total Revenue</p>
          <p className="text-lg font-bold">{todayActivities.totalRevenue}</p>
        </div>
      </CardContent>
    </Card>
  )
}

export default function StatsCards({ statsCards, todayActivities }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-6">
      {statsCards.map((card, index) => (
        <Card key={index}>
          <CardContent className="p-4 flex items-center">
            <div className={`${card.bgColor} p-3 rounded-full mr-4`}>{card.icon}</div>
            <div>
              <p className="text-sm text-gray-500">
                {card.title} <span className="text-xs">{card.subtitle}</span>
              </p>
              <div className="flex items-center">
                <h3 className="text-2xl font-bold mr-2">{card.value}</h3>
                <span
                  className={`text-xs px-1.5 py-0.5 rounded ${
                    card.changeType === "positive" ? "bg-green-100 text-green-600" : "bg-red-100 text-red-600"
                  }`}
                >
                  {card.change}
                </span>
              </div>
              <p className="text-xs text-gray-500">{card.previousValue}</p>
            </div>
          </CardContent>
        </Card>
      ))}
      <TodayActivitiesCard todayActivities={todayActivities} />
    </div>
  )
} 