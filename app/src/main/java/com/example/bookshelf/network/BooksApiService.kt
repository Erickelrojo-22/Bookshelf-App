package com.example.bookshelf.network

import com.example.bookshelf.model.Volume
import com.example.bookshelf.model.VolumesResponse
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface BooksApiService {
    @GET("volumes")
    suspend fun searchVolumes(@Query("q") query: String, @Query("maxResults") maxResults: Int = 12): VolumesResponse

    @GET("volumes/{id}")
    suspend fun getVolume(@Path("id") id: String): Volume
}
