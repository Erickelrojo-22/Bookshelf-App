package com.example.bookshelf.data

import com.example.bookshelf.model.Book
import com.example.bookshelf.network.BooksApiService

interface BooksRepository {
    suspend fun searchBooks(query: String): List<Book>
}

class NetworkBooksRepository(private val service: BooksApiService) : BooksRepository {
    override suspend fun searchBooks(query: String): List<Book> {
        if (query.isBlank()) return emptyList()
        val volumes = service.searchVolumes(query.trim()).items.orEmpty()
        // Search first, then request every volume's details, as required by the codelab.
        return volumes.distinctBy { it.id }.filter { it.id.isNotBlank() }.map { result ->
            val volume = service.getVolume(result.id)
            val info = volume.volumeInfo
            val thumbnail = info?.imageLinks?.thumbnail ?: info?.imageLinks?.smallThumbnail
            Book(
                id = result.id,
                title = info?.title?.takeIf { it.isNotBlank() } ?: "Sin título",
                authors = info?.authors.orEmpty().joinToString(", "),
                thumbnailUrl = thumbnail?.takeIf { it.isNotBlank() }?.replace("http://", "https://")
            )
        }
    }
}
