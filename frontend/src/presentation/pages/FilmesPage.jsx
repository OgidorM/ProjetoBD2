import React from 'react'
import { useMovies } from '../hooks/useMovies'

const FilmesPage = () => {
  const { movies, loading, error } = useMovies()

  if (loading) return <div className="p-8">Carregando...</div>
  if (error) return <div className="p-8 text-red-500">Erro: {error}</div>

  return (
    <div className="p-8">
      <h1 className="text-3xl mb-6">Todos os Filmes</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {movies.map(m => (
          <div key={m.id} className="p-4 border rounded bg-neutral-900/40">
            <h3 className="font-bold">{m.title}</h3>
            <p className="text-sm">{m.description}</p>
            <p className="text-xs mt-2">Duração: {m.duration || 'N/A'}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default FilmesPage
