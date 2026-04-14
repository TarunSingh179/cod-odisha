import React, { useState } from 'react'
import { Eye, Layers, Map, Maximize2, Download } from 'lucide-react'

const ResultViewer = ({ result, isLoading }) => {
  const [activeView, setActiveView] = useState('overlay')
  
  if (isLoading) {
    return (
      <div className="card flex flex-col items-center justify-center py-16">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-odisha-cream border-t-odisha-primary rounded-full animate-spin" />
          <div className="absolute inset-0 flex items-center justify-center">
            <Eye className="w-6 h-6 text-odisha-primary animate-pulse" />
          </div>
        </div>
        <p className="mt-4 text-gray-600 font-medium">Detecting camouflaged object...</p>
        <p className="text-sm text-gray-400">Analyzing image with CCSIM + SGFL</p>
      </div>
    )
  }
  
  if (!result) return null
  
  const { images, confidence, detection, labels } = result
  
  const viewOptions = [
    { id: 'overlay', label: 'Overlay', icon: Eye, image: images?.overlay },
    { id: 'mask', label: 'Mask', icon: Map, image: images?.mask },
    { id: 'heatmap', label: 'Heatmap', icon: Layers, image: images?.heatmap },
  ]
  
  const activeImage = viewOptions.find(v => v.id === activeView)?.image
  
  const downloadImage = () => {
    if (!activeImage) return
    const link = document.createElement('a')
    link.href = `data:image/png;base64,${activeImage}`
    link.download = `cod-odisha-${activeView}.png`
    link.click()
  }
  
  return (
    <div className="card animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Detection Result</h3>
          <div className="flex items-center gap-3 mt-1">
            <span className="text-sm text-gray-500">
              Confidence: <span className="font-medium text-odisha-primary">{Math.round(confidence * 100)}%</span>
            </span>
            <span className="text-sm text-gray-400">|</span>
            <span className="text-sm text-gray-500">
              Mask Area: <span className="font-medium">{detection?.mask_area_pct}%</span>
            </span>
          </div>
        </div>
        
        <button
          onClick={downloadImage}
          className="btn-secondary flex items-center gap-2 text-sm py-2 px-4"
        >
          <Download className="w-4 h-4" />
          Download
        </button>
      </div>
      
      {/* View selector tabs */}
      <div className="flex gap-2 mb-4 p-1 bg-gray-100 rounded-lg">
        {viewOptions.map((option) => {
          const Icon = option.icon
          return (
            <button
              key={option.id}
              onClick={() => setActiveView(option.id)}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all
                ${activeView === option.id
                  ? 'bg-white text-odisha-primary shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
                }
              `}
            >
              <Icon className="w-4 h-4" />
              {option.label}
            </button>
          )
        })}
      </div>
      
      {/* Image display */}
      <div className="relative rounded-xl overflow-hidden bg-gray-100">
        {activeImage ? (
          <img
            src={`data:image/png;base64,${activeImage}`}
            alt={activeView}
            className="w-full h-auto max-h-[500px] object-contain"
          />
        ) : (
          <div className="flex items-center justify-center h-64 text-gray-400">
            No image available
          </div>
        )}
      </div>
      
      {/* Detection summary */}
      {detection?.has_detection && (
        <div className="mt-4 p-4 bg-odisha-cream/50 rounded-lg border border-odisha-secondary/20">
          <div className="flex items-center gap-2 mb-2">
            <Maximize2 className="w-4 h-4 text-odisha-primary" />
            <span className="font-medium text-gray-900">Detection Summary</span>
          </div>
          <p className="text-sm text-gray-600">
            Camouflaged object detected with {Math.round(confidence * 100)}% confidence.
            The system identified a region of interest covering approximately {detection?.mask_area_pct}% of the image.
          </p>
        </div>
      )}
    </div>
  )
}

export default ResultViewer
