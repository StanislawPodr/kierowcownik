export function mediaUrl(question: { media_url: string; url_type: string }): string {
  if (!question.media_url?.trim()) return ''
  let path = question.media_url.replace(/^\//, '')
  if (question.url_type === 'V') path = path.replace(/\.wmv$/i, '.mp4')
  return `/${path}`
}
