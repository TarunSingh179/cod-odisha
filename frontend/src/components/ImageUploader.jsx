import React, { useState, useCallback } from 'react'
import { Upload, X, Image as ImageIcon, Check } from 'lucide-react'

const ImageUploader = ({ onImageSelect, selectedFile, disabled }) => {
  const [isDragActive, setIsDragActive] = useState(false)
  const [preview, setPreview] = useState(null)

  const handleFile = (file) => {
    if (file && file.type.startsWith('image/')) {
      onImageSelect(file)
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => setPreview(reader.result)
      reader.readAsDataURL(file)
    }
  }

  const handleDragEnter = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)
  }, [])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)
    
    const files = e.dataTransfer.files
    if (files && files[0]) {
      handleFile(files[0])
    }
  }, [])

  const handleInputChange = (e) => {
    const file = e.target.files[0]
    if (file) handleFile(file)
  }

  const clearSelection = () => {
    onImageSelect(null)
    setPreview(null)
  }

  return (
    <div className="w-full">
      {!selectedFile ? (
        <div
          className={`upload-zone ${isDragActive ? 'upload-zone-active' : ''}`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => !disabled && document.getElementById('file-input').click()}
        >
          <input
            id="file-input"
            type="file"
            accept="image/*"
            onChange={handleInputChange}
            className="hidden"
            disabled={disabled}
          />
          <Upload className="w-12 h-12 mx-auto mb-4 text-odisha-secondary" />
          <p className="text-lg font-medium text-gray-700 mb-2">
            Drag & drop your image here
          </p>
          <p className="text-sm text-gray-500">
            or click to browse (JPG, PNG supported)
          </p>
        </div>
      ) : (
        <div className="relative rounded-xl overflow-hidden border-2 border-odisha-primary">
          <img
            src={preview}
            alt="Preview"
            className="w-full h-64 object-contain bg-gray-50"
          />
          <button
            onClick={clearSelection}
            disabled={disabled}
            className="absolute top-2 right-2 p-2 bg-white rounded-full shadow-md hover:bg-red-50 transition-colors"
          >
            <X className="w-5 h-5 text-red-500" />
          </button>
          <div className="absolute bottom-2 left-2 px-3 py-1 bg-odisha-primary text-white text-sm rounded-full flex items-center gap-2">
            <Check className="w-4 h-4" />
            {selectedFile.name}
          </div>
        </div>
      )}
    </div>
  )
}

export default ImageUploader
