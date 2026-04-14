import React, { useState } from 'react'
import { AlertCircle } from 'lucide-react'
import ImageUploader from '../components/ImageUploader'
import OdishaSceneSelector from '../components/OdishaSceneSelector'
import ResultViewer from '../components/ResultViewer'
import BilingualOutput from '../components/BilingualOutput'
import { detectImage, describeSpecies } from '../api'

const Home = () => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [ecosystem, setEcosystem] = useState('default')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [description, setDescription] = useState(null)
  const [error, setError] = useState(null)

  const handleDetect = async () => {
    if (!selectedFile) return
    
    setIsLoading(true)
    setError(null)
    setResult(null)
    setDescription(null)
    
    try {
      // Run detection
      const detectionResult = await detectImage(selectedFile, ecosystem)
      setResult(detectionResult)
      
      // Get species description
      if (detectionResult.success) {
        const descResult = await describeSpecies({
          ecosystem: ecosystem,
          confidence: detectionResult.confidence,
          mask_area_pct: detectionResult.detection?.mask_area_pct || 0
        })
        setDescription(descResult)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Detection failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-10">
        <h1 className="text-3xl md:text-4xl font-bold text-odisha-primary mb-3">
          COD-Odisha
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Camouflaged Object Detection for Odisha Biodiversity. 
          Detect wildlife, pests, and aquatic species in their natural habitats.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left column - Upload and Controls */}
        <div className="space-y-6">
          {/* Image Upload */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Upload Image
            </h2>
            <ImageUploader 
              onImageSelect={setSelectedFile}
              selectedFile={selectedFile}
              disabled={isLoading}
            />
          </div>

          {/* Ecosystem Selector */}
          <div className="card">
            <OdishaSceneSelector
              selected={ecosystem}
              onSelect={setEcosystem}
              disabled={isLoading}
            />
          </div>

          {/* Error display */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {/* Detect Button */}
          <button
            onClick={handleDetect}
            disabled={!selectedFile || isLoading}
            className="btn-primary w-full py-4 text-lg"
          >
            {isLoading ? 'Detecting...' : 'Detect Camouflaged Object'}
          </button>
        </div>

        {/* Right column - Results */}
        <div className="space-y-6">
          {/* Detection Result */}
          <ResultViewer 
            result={result} 
            isLoading={isLoading && !result}
          />

          {/* Species Description */}
          <BilingualOutput 
            description={description}
            isLoading={isLoading && !description}
          />

          {/* Empty state */}
          {!result && !isLoading && (
            <div className="card flex flex-col items-center justify-center py-16 text-center">
              <div className="w-16 h-16 bg-odisha-cream rounded-full flex items-center justify-center mb-4">
                <span className="text-3xl">🦎</span>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Ready to Detect
              </h3>
              <p className="text-gray-500 max-w-xs">
                Upload an image and click "Detect" to find camouflaged objects in your photo.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Footer info */}
      <div className="mt-12 pt-8 border-t border-gray-200 text-center">
        <p className="text-sm text-gray-500">
          Powered by CCSIM + SGFL architecture • Simlipal • Chilika • Paddy Fields • Bhitarkanika
        </p>
      </div>
    </div>
  )
}

export default Home
