import { CheckCircle2, FileText, LoaderCircle, UploadCloud, X } from 'lucide-react'
import { useRef, useState } from 'react'
import PageHeader from '../components/PageHeader'
import { uploadDocument } from '../services/api'

function DocumentUpload({ onUploadComplete }) {
  const inputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [isDragging, setIsDragging] = useState(false)

  function selectFile(selectedFile) {
    setResult(null)
    setError('')

    if (!selectedFile) return
    if (selectedFile.type !== 'application/pdf') {
      setFile(null)
      setError('Select a PDF file.')
      return
    }
    setFile(selectedFile)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!file) return

    setIsUploading(true)
    setError('')

    try {
      const uploadResult = await uploadDocument(file)
      setResult(uploadResult)
      onUploadComplete(uploadResult)
    } catch (uploadError) {
      setError(uploadError.message)
    } finally {
      setIsUploading(false)
    }
  }

  function handleDrop(event) {
    event.preventDefault()
    setIsDragging(false)
    selectFile(event.dataTransfer.files[0])
  }

  return (
    <div className="page page--narrow">
      <PageHeader
        eyebrow="Documents"
        title="Document Upload"
        description="PDF ingestion and vector indexing."
      />

      <form className="upload-panel" onSubmit={handleSubmit}>
        <input
          ref={inputRef}
          className="visually-hidden"
          type="file"
          accept="application/pdf,.pdf"
          onChange={(event) => selectFile(event.target.files[0])}
        />

        <button
          className={`drop-zone ${isDragging ? 'drop-zone--active' : ''}`}
          type="button"
          onClick={() => inputRef.current?.click()}
          onDragEnter={() => setIsDragging(true)}
          onDragLeave={() => setIsDragging(false)}
          onDragOver={(event) => event.preventDefault()}
          onDrop={handleDrop}
        >
          <span className="upload-icon">
            <UploadCloud size={25} />
          </span>
          <strong>PDF document</strong>
          <span>Drop file or browse</span>
        </button>

        {file && (
          <div className="selected-file">
            <div className="file-type-icon">
              <FileText size={20} />
            </div>
            <div>
              <strong>{file.name}</strong>
              <span>{(file.size / 1024).toFixed(1)} KB</span>
            </div>
            <button
              className="icon-button"
              type="button"
              aria-label="Remove selected file"
              onClick={() => setFile(null)}
            >
              <X size={18} />
            </button>
          </div>
        )}

        {error && <div className="alert alert--error">{error}</div>}

        {result && (
          <div className="upload-success">
            <CheckCircle2 size={20} />
            <div>
              <strong>{result.message}</strong>
              <span>
                {result.total_characters.toLocaleString()} characters ·{' '}
                {result.total_chunks} chunks
              </span>
            </div>
          </div>
        )}

        <div className="form-actions">
          <button
            className="primary-button"
            type="submit"
            disabled={!file || isUploading}
          >
            {isUploading ? (
              <LoaderCircle className="spin" size={18} />
            ) : (
              <UploadCloud size={18} />
            )}
            {isUploading ? 'Indexing' : 'Upload and index'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default DocumentUpload
