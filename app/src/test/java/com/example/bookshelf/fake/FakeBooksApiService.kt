package com.example.bookshelf.fake

import com.example.bookshelf.model.ImageLinks
import com.example.bookshelf.model.Volume
import com.example.bookshelf.model.VolumeInfo
import com.example.bookshelf.model.VolumesResponse
import com.example.bookshelf.network.BooksApiService

/** Deterministic service for the codelab's dependency injection exercise. No network. */
class FakeBooksApiService : BooksApiService {
    override suspend fun searchVolumes(query: String, maxResults: Int) =
        VolumesResponse(listOf(Volume(id = "fake-one")))

    override suspend fun getVolume(id: String) = Volume(id, VolumeInfo(
        title = "Kotlin de prueba", authors = listOf("Autora de prueba"),
        imageLinks = ImageLinks(smallThumbnail = "http://books.google.com/fake-cover")))
}
