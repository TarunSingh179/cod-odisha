import React, { useState, useEffect } from 'react'
import { Grid, List, Trash2, Download, Image as ImageIcon } from 'lucide-react'
import { getEcosystems } from '../api'

const Dashboard = () => {
  const [results, setResults] = useState([])
  const [viewMode, setViewMode] = useState('grid') // 'grid' or 'list'
  const [ecosystems, setEcosystems] = useState([])

  useEffect(() => {
    // Load ecosystems info
    getEcosystems().then(data => {
      setEcosystems(data.ecosystems || [])
    })

    // TODO: Load from localStorage or backend storage
    const saved = localStorage.getItem('cod_odisha_results')
    if (saved) {
      setResults(JSON.parse(saved))
    }
  }, [])

  const clearHistory = () => {
    setResults([])
    localStorage.removeItem('cod_odisha_results')
  }

  const getEcosystemColor = (id) => {
    const eco = ecosystems.find(e => e.id === id)
    return eco?.color || '#6366f1'
  }

  const getEcosystemName = (id) => {
    const eco = ecosystems.find(e => e.id === id)
    return eco?.name?.en || id
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-odisha-primary">Detection History</h1>
          <p className="text-gray-600">View and manage your past detections</p>
        </div>

        <div className="flex items-center gap-3">
          {/* View toggle */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-md transition-colors ${
                viewMode === 'grid' ? 'bg-white shadow-sm text-odisha-primary' : 'text-gray-600'
              }`}
            >
              <Grid className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-md transition-colors ${
                viewMode === 'list' ? 'bg-white shadow-sm text-odisha-primary' : 'text-gray-600'
              }`}
            >
              <List className="w-5 h-5" />
            </button>
          </div>

          {/* Clear button */}
          <button
            onClick={clearHistory}
            disabled={results.length === 0}
            className="btn-secondary flex items-center gap-2 py-2 px-4"
          >
            <Trash2 className="w-4 h-4" />
            Clear
          </button>
        </div>
      </div>

      {/* Results */}
      {results.length === 0 ? (
        <div className="card flex flex-col items-center justify-center py-20">
          <ImageIcon className="w-16 h-16 text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-700 mb-2">No detections yet</h3>
          <p className="text-gray-500 mb-4">Your detection history will appear here</p>
          <a href="/" className="btn-primary">
            Go Detect
          </a>
        </div>
      ) : (
        <div className={viewMode === 'grid' 
          ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
          : 'space-y-4'
        }>
          {results.map((result, idx) => (
            <div key={idx} className="card hover:shadow-lg transition-shadow">
              {/* Thumbnail */}
              {result.images?.overlay && (
                <div className="mb-4 rounded-lg overflow-hidden bg-gray-100">
                  <img
                    src={`data:image/png;base64,${result.images.overlay}`}
                    alt="Detection result"
                    className="w-full h-48 object-cover"
                  />
                </div>
              )}

              <div className="flex items-start justify-between">
                <div>
                  {/* Ecosystem badge */}
                  <span
                    className="inline-block px-2 py-1 rounded text-xs font-medium text-white mb-2"
                    style={{ backgroundColor: getEcosystemColor(result.ecosystem) }}
                  >
                    {getEcosystemName(result.ecosystem)}
                  </span>

                  {/* Confidence */}
                  <p className="text-sm text-gray-600">
                    Confidence: <span className="font-medium">{Math.round(result.confidence * 100)}%</span>
                  </p>

                  {/* Timestamp */}
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(result.timestamp).toLocaleString()}
                  </p>
                </div>

                {/* Actions */}
                <button
                  onClick={() => {
                    if (result.images?.overlay) {
                      const link = document.createElement('a')
                      link.href = `data:image/png;base64,${result.images.overlay}`
                      link.download = `cod-result-${idx}.png`
                      link.click()
                    }
                  }}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <Download className="w-4 h-4 text-gray-600" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Stats */}
      {results.length > 0 && (
        <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="card py-4 text-center">
            <p className="text-2xl font-bold text-odisha-primary">{results.length}</p>
            <p className="text-sm text-gray-600">Total Detections</p>
          </div>
          <div className="card py-4 text-center">
            <p className="text-2xl font-bold text-odisha-secondary">
              {Math.round(results.reduce((a, r) => a + (r.confidence || 0), 0) / results.length * 100)}%
            </p>
            <p className="text-sm text-gray-600">Avg Confidence</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
