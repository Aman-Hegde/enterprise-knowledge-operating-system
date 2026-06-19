import { CheckCircle2, FileText, LoaderCircle, UploadCloud, X } from 'lucide-react'
import { useRef, useState } from 'react'
import PageHeader from '../components/PageHeader'
import { uploadDocuments } from '../services/api'

function DocumentUpload({ onUploadComplete }) {
  const inputRef = useRef(null)
  const [files, setFiles] = useState([])
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [isDragging, setIsDragging] = useState(false)

  function selectFiles(selectedFiles) {
    setResult(null)
    setError('')

    const nextFiles = Array.from(selectedFiles || [])
    if (!nextFiles.length) return

    if (nextFiles.some((file) => file.type !== 'application/pdf')) {
      setError('Select PDF files only.')
      return
    }

    // Keep each selected file once, based on its browser-provided identity.
    setFiles((current) => {
      const combined = [...current, ...nextFiles]
      return combined.filter(
        (file, index, allFiles) =>
          allFiles.findIndex(
            (candidate) =>
              candidate.name === file.name &&
              candidate.size === file.size &&
              candidate.lastModified === file.lastModified,
          ) === index,
      )
    })
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!files.length) return

    setIsUploading(true)
    setError('')

    try {
      const uploadResult = await uploadDocuments(files)
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
    selectFiles(event.dataTransfer.files)
  }

  function removeFile(fileToRemove) {
    setFiles((current) => current.filter((file) => file !== fileToRemove))
  }

  return (
    <div className="page page--narrow">
      <PageHeader
        eyebrow="Documents"
        title="Document Upload"
        description="Multi-PDF ingestion, vector indexing, and graph extraction."
      />

      <form className="upload-panel" onSubmit={handleSubmit}>
        <input
          ref={inputRef}
          className="visually-hidden"
          type="file"
          accept="application/pdf,.pdf"
          multiple
          onChange={(event) => selectFiles(event.target.files)}
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
          <strong>PDF documents</strong>
          <span>Drop files or browse</span>
        </button>

        {files.length > 0 && (
          <div className="selected-files">
            {files.map((file) => (
              <div className="selected-file" key={`${file.name}-${file.size}`}>
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
                  aria-label={`Remove ${file.name}`}
                  onClick={() => removeFile(file)}
                >
                  <X size={18} />
                </button>
              </div>
            ))}
          </div>
        )}

        {error && <div className="alert alert--error">{error}</div>}

        {result && (
          <div className="upload-success">
            <CheckCircle2 size={20} />
            <div>
              <strong>{result.message}</strong>
              <span>
                {result.total_documents} documents, {result.total_chunks} chunks
              </span>
              <ul className="uploaded-filenames">
                {result.uploaded_filenames.map((filename, index) => (
                  <li key={`${filename}-${index}`}>
                    {filename} · {result.graph_extraction_status[filename]}
                  </li>
                ))}
              </ul>
              {result.warnings.map((warning) => (
                <span className="upload-warning" key={warning}>
                  {warning}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="form-actions">
          <button
            className="primary-button"
            type="submit"
            disabled={!files.length || isUploading}
          >
            {isUploading ? (
              <LoaderCircle className="spin" size={18} />
            ) : (
              <UploadCloud size={18} />
            )}
            {isUploading
              ? 'Indexing'
              : `Upload ${files.length || ''} and index`}
          </button>
        </div>
      </form>
    </div>
  )
}

export default DocumentUpload
