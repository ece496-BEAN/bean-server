'use client'

import React, { useState } from 'react'
import { PlusCircle, Home, PieChart, Settings, Camera, DollarSign } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export function BudgetPage() {
  const [categories, setCategories] = useState([
    { name: 'Groceries', amount: 300 },
    { name: 'Restaurant', amount: 150 },
    { name: 'Entertainment', amount: 100 },
    { name: 'Miscellaneous', amount: 50 },
    { name: 'Hobby', amount: 75 }
  ])
  const [newCategory, setNewCategory] = useState('')

  const addCategory = (e: React.FormEvent) => {
    e.preventDefault()
    if (newCategory.trim() !== '') {
      setCategories([...categories, { name: newCategory.trim(), amount: 0 }])
      setNewCategory('')
    }
  }

  const updateAmount = (index: number, amount: string) => {
    const updatedCategories = [...categories]
    updatedCategories[index].amount = parseFloat(amount) || 0
    setCategories(updatedCategories)
  }

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <header className="bg-black text-white p-4">
        <h1 className="text-2xl font-bold">Budget</h1>
      </header>
      
      <main className="flex-grow p-4 overflow-y-auto">
        <ul className="space-y-2 mb-4">
          {categories.map((category, index) => (
            <li key={index} className="flex items-center justify-between">
              <span>{category.name}</span>
              <div className="flex items-center">
                <DollarSign className="w-4 h-4 mr-1 text-gray-500" />
                <Input
                  type="number"
                  value={category.amount}
                  onChange={(e) => updateAmount(index, e.target.value)}
                  className="w-24 text-right"
                />
              </div>
            </li>
          ))}
        </ul>

        <form onSubmit={addCategory} className="flex space-x-2 mb-4">
          <Input
            type="text"
            value={newCategory}
            onChange={(e) => setNewCategory(e.target.value)}
            placeholder="Add new category"
            className="flex-grow"
          />
          <Button type="submit">
            <PlusCircle className="w-4 h-4 mr-2" />
            Add
          </Button>
        </form>
      </main>

      <nav className="bg-white shadow-lg">
        <ul className="flex justify-around items-center h-16">
          <li>
            <Button variant="ghost" size="icon">
              <Home className="w-6 h-6" />
            </Button>
          </li>
          <li>
            <Button variant="ghost" size="icon">
              <PieChart className="w-6 h-6" />
            </Button>
          </li>
          <li>
            <Button 
              variant="default" 
              size="icon" 
              className="w-16 h-16 rounded-full -mt-8 bg-primary text-primary-foreground shadow-lg"
            >
              <Camera className="w-8 h-8" />
            </Button>
          </li>
          <li>
            <Button variant="ghost" size="icon">
              <DollarSign className="w-6 h-6" />
            </Button>
          </li>
          <li>
            <Button variant="ghost" size="icon">
              <Settings className="w-6 h-6" />
            </Button>
          </li>
        </ul>
      </nav>
    </div>
  )
}