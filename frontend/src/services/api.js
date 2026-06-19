const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

async function parseResponse(response) {
  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.detail || 'The EKOS API request failed.')
  }

  return data
}

export async function getHealth() {
  const response = await fetch(`${API_BASE_URL}/health`)
  return parseResponse(response)
}

export async function uploadDocuments(files) {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    body: formData,
  })

  return parseResponse(response)
}

export async function askGraphRAG(question) {
  const response = await fetch(`${API_BASE_URL}/graphrag/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  })

  return parseResponse(response)
}
