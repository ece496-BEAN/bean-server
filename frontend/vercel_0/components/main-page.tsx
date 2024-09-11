'use client'

import React from 'react'
import { Bell, Camera, DollarSign, Home, PieChart, Settings, Sparkles, TrendingUp, TrendingDown, Calendar } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

const RingChart = ({ percentage, color, size = 100 }) => {
  const strokeWidth = 10
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  return (
    <div className="relative">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-2xl font-bold">{percentage}%</span>
      </div>
    </div>
  )
}

export function MainPage() {
  const recentTransactions = [
    { id: 1, description: 'Grocery Store', amount: -75.50, date: '2023-06-15' },
    { id: 2, description: 'Monthly Salary', amount: 3000, date: '2023-06-01' },
    { id: 3, description: 'Restaurant Dinner', amount: -45.00, date: '2023-06-10' },
    { id: 4, description: 'Utility Bill', amount: -120.00, date: '2023-06-05' },
  ]

  const totalSpending = 2500
  const monthlyBudget = 3000
  const spendingPercentage = (totalSpending / monthlyBudget) * 100

  const spendingCategories = [
    { name: 'Housing', percentage: 40, color: '#4CAF50' },
    { name: 'Food', percentage: 20, color: '#FFC107' },
    { name: 'Transportation', percentage: 15, color: '#2196F3' },
    { name: 'Entertainment', percentage: 10, color: '#9C27B0' },
    { name: 'Others', percentage: 15, color: '#FF5722' },
  ]

  const notifications = [
    { id: 1, message: 'Rent due in 3 days', type: 'warning' },
    { id: 2, message: 'You\'ve exceeded your restaurant budget', type: 'alert' },
  ]

  const aiSuggestions = [
    "Consider cooking at home more often to reduce food expenses.",
    "You might save on transportation by using public transit twice a week.",
  ]

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <header className="bg-gradient-to-r from-purple-700 to-indigo-800 text-white p-4">
        <h1 className="text-2xl font-bold">Financial Dashboard</h1>
      </header>
      
      <main className="flex-grow p-4 overflow-y-auto">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Spending Summary */}
          <Card className="col-span-full bg-white shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-semibold text-gray-700">Monthly Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-500">Total Spending</span>
                <span className="text-2xl font-bold text-indigo-600">${totalSpending.toFixed(2)}</span>
              </div>
              <Progress value={spendingPercentage} className="h-2 mb-1" />
              <div className="flex justify-between text-xs text-gray-500">
                <span>0%</span>
                <span>{spendingPercentage.toFixed(1)}% of ${monthlyBudget}</span>
                <span>100%</span>
              </div>
            </CardContent>
          </Card>

          {/* Spending Categories */}
          <Card className="bg-white shadow-lg lg:row-span-2">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-semibold text-gray-700">Spending Categories</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap justify-center gap-4">
                {spendingCategories.map((category, index) => (
                  <div key={index} className="flex flex-col items-center">
                    <RingChart percentage={category.percentage} color={category.color} />
                    <span className="mt-2 text-sm font-medium text-gray-600">{category.name}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Transactions */}
          <Card className="bg-white shadow-lg md:col-span-2 lg:row-span-2">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-semibold text-gray-700">Recent Transactions</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {recentTransactions.map(transaction => (
                  <li key={transaction.id} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                    <div className="flex items-center">
                      <div className={`p-2 rounded-full mr-3 ${transaction.amount >= 0 ? 'bg-green-100' : 'bg-red-100'}`}>
                        {transaction.amount >= 0 ? <TrendingUp className="w-4 h-4 text-green-600" /> : <TrendingDown className="w-4 h-4 text-red-600" />}
                      </div>
                      <div>
                        <p className="font-medium text-gray-700">{transaction.description}</p>
                        <p className="text-xs text-gray-500">{transaction.date}</p>
                      </div>
                    </div>
                    <span className={`font-semibold ${transaction.amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {transaction.amount >= 0 ? '+' : '-'}${Math.abs(transaction.amount).toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Notifications */}
          <Card className="bg-white shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-lg font-semibold text-gray-700">
                <Bell className="w-5 h-5 mr-2 text-indigo-500" />
                Notifications
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {notifications.map(notification => (
                  <li key={notification.id} className={`flex items-center p-2 rounded-lg ${notification.type === 'warning' ? 'bg-yellow-50 text-yellow-700' : 'bg-red-50 text-red-700'}`}>
                    <Calendar className="w-4 h-4 mr-2" />
                    <span className="text-sm">{notification.message}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* AI Suggestions */}
          <Card className="bg-white shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center text-lg font-semibold text-gray-700">
                <Sparkles className="w-5 h-5 mr-2 text-yellow-500" />
                AI Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {aiSuggestions.map((suggestion, index) => (
                  <li key={index} className="flex items-start p-2 bg-blue-50 rounded-lg">
                    <Sparkles className="w-4 h-4 mr-2 mt-1 text-blue-500" />
                    <span className="text-sm text-blue-700">{suggestion}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      </main>

      <nav className="bg-white shadow-lg">
        <ul className="flex justify-around items-center h-16">
          <li>
            <Button variant="ghost" size="icon" className="text-gray-600 hover:text-indigo-600">
              <Home className="w-6 h-6" />
            </Button>
          </li>
          <li>
            <Button variant="ghost" size="icon" className="text-gray-600 hover:text-indigo-600">
              <PieChart className="w-6 h-6" />
            </Button>
          </li>
          <li>
            <Button 
              variant="default" 
              size="icon" 
              className="w-16 h-16 rounded-full -mt-8 bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg hover:from-purple-700 hover:to-indigo-700"
            >
              <Camera className="w-8 h-8" />
            </Button>
          </li>
          <li>
            <Button variant="ghost" size="icon" className="text-gray-600 hover:text-indigo-600">
              <DollarSign className="w-6 h-6" />
            </Button>
          </li>
          <li>
            <Button variant="ghost" size="icon" className="text-gray-600 hover:text-indigo-600">
              <Settings className="w-6 h-6" />
            </Button>
          </li>
        </ul>
      </nav>
    </div>
  )
}