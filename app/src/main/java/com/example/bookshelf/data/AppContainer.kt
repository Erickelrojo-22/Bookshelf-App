package com.example.bookshelf.data

import com.example.bookshelf.BuildConfig
import com.example.bookshelf.network.BooksApiService
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

interface AppContainer { val booksRepository: BooksRepository }

class DefaultAppContainer : AppContainer {
    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(20, TimeUnit.SECONDS)
        .addInterceptor { chain ->
            val request = chain.request()
            val key = BuildConfig.BOOKS_API_KEY
            val authenticated = if (key.isBlank()) request else request.newBuilder()
                .url(request.url.newBuilder().addQueryParameter("key", key).build()).build()
            chain.proceed(authenticated)
        }.build()

    private val service: BooksApiService by lazy {
        Retrofit.Builder().baseUrl("https://www.googleapis.com/books/v1/")
            .client(client).addConverterFactory(GsonConverterFactory.create())
            .build().create(BooksApiService::class.java)
    }
    override val booksRepository: BooksRepository by lazy { NetworkBooksRepository(service) }
}
