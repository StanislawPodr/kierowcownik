export async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  let token = localStorage.getItem('access_token')

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  let res = await fetch(url, {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
  })

  if (res.status === 401) {
    const refreshToken = localStorage.getItem('refresh_token')
    if (refreshToken) {
      try {
        const refreshRes = await fetch('/api/auth/refresh/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh: refreshToken }),
        })
        if (refreshRes.ok) {
          const data = await refreshRes.json()
          localStorage.setItem('access_token', data.access)

          const retryHeaders = {
            ...headers,
            Authorization: `Bearer ${data.access}`,
            ...options.headers,
          }
          res = await fetch(url, {
            ...options,
            headers: retryHeaders,
          })
        }
      } catch (err) {
        console.error('Session refresh failed:', err)
      }
    }
  }

  return res
}
