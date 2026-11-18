package com.example.bookshelf

import com.example.bookshelf.data.NetworkBooksRepository
import com.example.bookshelf.fake.FakeBooksApiService
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

class FakeServiceRepositoryTest {
    @Test fun fakeServiceIsInjectedAndSmallThumbnailIsSupported() = runTest {
        val book = NetworkBooksRepository(FakeBooksApiService()).searchBooks("kotlin").single()
        assertEquals("Kotlin de prueba", book.title)
        assertEquals("https://books.google.com/fake-cover", book.thumbnailUrl)
    }
}
