import React from 'react'
import { Trees, Waves, Sprout, Mountain, Bird } from 'lucide-react'

const ECOSYSTEMS = [
  {
    id: 'default',
    name: 'General',
    icon: Bird,
    color: '#6366f1',
    description: 'General purpose detection'
  },
  {
    id: 'simlipal',
    name: 'Simlipal Tiger Reserve',
    icon: Mountain,
    color: '#FF8C00',
    description: 'Wildlife in sal forests'
  },
  {
    id: 'chilika',
    name: 'Chilika Lake',
    icon: Waves,
    color: '#0080C8',
    description: 'Aquatic species & birds'
  },
  {
    id: 'paddy',
    name: 'Paddy Fields',
    icon: Sprout,
    color: '#50C850',
    description: 'Agricultural pest detection'
  },
  {
    id: 'bhitarkanika',
    name: 'Bhitarkanika Mangroves',
    icon: Trees,
    color: '#00B496',
    description: 'Mangrove ecosystem'
  },
  {
    id: 'kandhamal',
    name: 'Kandhamal Forests',
    icon: Trees,
    color: '#8B4513',
    description: 'Tropical deciduous forest'
  }
]

const OdishaSceneSelector = ({ selected, onSelect, disabled }) => {
  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 mb-3">
        Select Ecosystem Context
      </label>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {ECOSYSTEMS.map((eco) => {
          const Icon = eco.icon
          const isSelected = selected === eco.id
          
          return (
            <button
              key={eco.id}
              onClick={() => !disabled && onSelect(eco.id)}
              disabled={disabled}
              className={`
                relative p-4 rounded-xl border-2 transition-all duration-200 text-left
                ${isSelected 
                  ? 'border-odisha-primary bg-odisha-cream shadow-md' 
                  : 'border-gray-200 hover:border-odisha-secondary hover:bg-gray-50'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              <div className="flex items-start gap-3">
                <div 
                  className="p-2 rounded-lg"
                  style={{ backgroundColor: `${eco.color}20` }}
                >
                  <Icon 
                    className="w-5 h-5" 
                    style={{ color: eco.color }}
                  />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm text-gray-900 truncate">
                    {eco.name}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {eco.description}
                  </p>
                </div>
              </div>
              
              {isSelected && (
                <div className="absolute top-2 right-2 w-3 h-3 rounded-full bg-odisha-primary" />
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default OdishaSceneSelector
