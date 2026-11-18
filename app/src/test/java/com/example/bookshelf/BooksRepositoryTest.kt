package com.example.bookshelf

import com.example.bookshelf.data.NetworkBooksRepository
import com.example.bookshelf.network.BooksApiService
import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import retrofit2.HttpException
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class BooksRepositoryTest {
    private val server = MockWebServer()
    private lateinit var repository: NetworkBooksRepository
    @Before fun setUp() {
        server.start()
        repository = NetworkBooksRepository(Retrofit.Builder().baseUrl(server.url("/"))
            .addConverterFactory(GsonConverterFactory.create()).build().create(BooksApiService::class.java))
    }
    @After fun tearDown() = server.shutdown()

    // Catches using search summaries instead of requesting each volume's detail.
    @Test fun searchFetchesDetailsAndUpgradesThumbnailToHttps() = runTest {
        server.enqueue(MockResponse().setBody("""{"items":[{"id":"one"},{"id":"two"}]}"""))
        server.enqueue(MockResponse().setBody("""{"id":"one","volumeInfo":{"title":"Jazz","authors":["Ada"],"imageLinks":{"thumbnail":"http://books.google.com/one"}}}"""))
        server.enqueue(MockResponse().setBody("""{"id":"two","volumeInfo":{"title":"History"}}"""))
        val books = repository.searchBooks("jazz history")
        assertEquals(listOf("Jazz", "History"), books.map { it.title })
        assertEquals("https://books.google.com/one", books[0].thumbnailUrl)
        assertEquals("Ada", books[0].authors)
        assertNull(books[1].thumbnailUrl)
        assertEquals("/volumes?q=jazz%20history&maxResults=12", server.takeRequest().path)
        assertEquals("/volumes/one", server.takeRequest().path)
        assertEquals("/volumes/two", server.takeRequest().path)
    }
    @Test fun absentItemsProducesEmptyList() = runTest {
        server.enqueue(MockResponse().setBody("""{"totalItems":0}"""))
        assertTrue(repository.searchBooks("no matches").isEmpty())
        assertEquals(1, server.requestCount)
    }
    @Test fun blankQueryDoesNotCallNetwork() = runTest {
        assertTrue(repository.searchBooks("   ").isEmpty())
        assertEquals(0, server.requestCount)
    }
    @Test fun duplicateIdsAreRequestedOnlyOnce() = runTest {
        server.enqueue(MockResponse().setBody("""{"items":[{"id":"one"},{"id":"one"}]}"""))
        server.enqueue(MockResponse().setBody("""{"id":"one","volumeInfo":{"title":"Only once"}}"""))
        assertEquals(1, repository.searchBooks("jazz").size)
        assertEquals(2, server.requestCount)
    }
    @Test fun quotaFailureIsPropagated() = runTest {
        server.enqueue(MockResponse().setResponseCode(429))
        try { repository.searchBooks("jazz"); fail("Expected HTTP failure") }
        catch (error: HttpException) { assertEquals(429, error.code()) }
    }
    @Test fun detailFailureIsNotDisguisedAsSuccess() = runTest {
        server.enqueue(MockResponse().setBody("""{"items":[{"id":"one"}]}"""))
        server.enqueue(MockResponse().setResponseCode(503))
        try { repository.searchBooks("jazz"); fail("Expected detail failure") }
        catch (error: HttpException) { assertEquals(503, error.code()) }
    }
}
