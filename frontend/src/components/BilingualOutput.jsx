import React from 'react'
import { Languages, Info, Shield, Leaf } from 'lucide-react'

const BilingualOutput = ({ description, isLoading }) => {
  if (isLoading) {
    return (
      <div className="card">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/3" />
          <div className="h-16 bg-gray-100 rounded" />
          <div className="h-16 bg-gray-100 rounded" />
        </div>
      </div>
    )
  }
  
  if (!description) return null
  
  const { en, or, species, conservation_status, ecological_notes } = description
  
  // Determine status color
  const getStatusColor = (status) => {
    if (!status) return 'gray'
    const status_lower = status.toLowerCase()
    if (status_lower.includes('endangered')) return 'red'
    if (status_lower.includes('vulnerable')) return 'orange'
    if (status_lower.includes('threatened')) return 'yellow'
    if (status_lower.includes('least')) return 'green'
    return 'gray'
  }
  
  const statusColor = getStatusColor(conservation_status)
  const statusBg = {
    red: 'bg-red-50 text-red-700 border-red-200',
    orange: 'bg-orange-50 text-orange-700 border-orange-200',
    yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    green: 'bg-green-50 text-green-700 border-green-200',
    gray: 'bg-gray-50 text-gray-700 border-gray-200'
  }[statusColor]
  
  return (
    <div className="card animate-slide-up">
      <div className="flex items-center gap-2 mb-4">
        <Languages className="w-5 h-5 text-odisha-primary" />
        <h3 className="text-lg font-semibold text-gray-900">Species Identification</h3>
      </div>
      
      {/* English description */}
      <div className="mb-4">
        <span className="inline-block px-2 py-1 bg-blue-50 text-blue-700 text-xs font-medium rounded mb-2">
          English
        </span>
        <p className="text-gray-800 leading-relaxed">{en}</p>
      </div>
      
      {/* Odia description */}
      <div className="mb-4 p-4 bg-amber-50/50 rounded-lg border border-amber-100">
        <span className="inline-block px-2 py-1 bg-amber-100 text-amber-800 text-xs font-medium rounded mb-2">
          ଓଡ଼ିଆ (Odia)
        </span>
        <p className="text-gray-800 leading-relaxed text-lg">{or}</p>
      </div>
      
      {/* Species info grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
        {species && (
          <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
            <Leaf className="w-5 h-5 text-odisha-secondary mt-0.5" />
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wide">Species</p>
              <p className="font-medium text-gray-900">{species}</p>
            </div>
          </div>
        )}
        
        {conservation_status && (
          <div className={`flex items-start gap-3 p-3 rounded-lg border ${statusBg}`}>
            <Shield className="w-5 h-5 mt-0.5" />
            <div>
              <p className="text-xs opacity-75 uppercase tracking-wide">Status</p>
              <p className="font-medium">{conservation_status}</p>
            </div>
          </div>
        )}
      </div>
      
      {/* Ecological notes */}
      {ecological_notes && (
        <div className="mt-4 p-3 bg-odisha-cream rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <Info className="w-4 h-4 text-odisha-earth" />
            <span className="text-sm font-medium text-odisha-earth">Ecological Notes</span>
          </div>
          <p className="text-sm text-gray-700">{ecological_notes}</p>
        </div>
      )}
    </div>
  )
}

export default BilingualOutput
