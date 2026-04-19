const FLASK_URL = process.env.FLASK_API_URL || 'http://127.0.0.1:5000/api'
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || 'cdc33e44d693a3a58451898d4ec9df862c65b954'

export default async function handler(req, res) {
  const { path } = req.query
  const url = `${FLASK_URL}/${path.join('/')}${req.url.includes('?') ? '?' + req.url.split('?')[1] : ''}`

  const response = await fetch(url, {
    method: req.method,
    headers: {
      'X-API-Key': API_KEY,
      'Content-Type': 'application/json',
    },
    body: req.method !== 'GET' && req.method !== 'HEAD' ? JSON.stringify(req.body) : undefined,
  })

  const data = await response.json()
  res.status(response.status).json(data)
}
