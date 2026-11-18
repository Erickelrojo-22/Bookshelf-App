package com.example.bookshelf

import com.example.bookshelf.data.BooksRepository
import com.example.bookshelf.model.Book
import com.example.bookshelf.ui.BooksUiState
import com.example.bookshelf.ui.BooksViewModel
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import retrofit2.HttpException
import retrofit2.Response
import okhttp3.ResponseBody.Companion.toResponseBody
import java.io.IOException

@OptIn(ExperimentalCoroutinesApi::class)
class BooksViewModelTest {
    private val dispatcher = StandardTestDispatcher()
    @Before fun setUp() = Dispatchers.setMain(dispatcher)
    @After fun tearDown() = Dispatchers.resetMain()

    private class FakeRepository : BooksRepository {
        var handler: suspend (String) -> List<Book> = { listOf(Book("one", "Jazz", "Ada", null)) }
        override suspend fun searchBooks(query: String) = handler(query)
    }
    @Test fun loadingThenSuccessFromInjectedRepository() = runTest(dispatcher) {
        val vm = BooksViewModel(FakeRepository())
        assertTrue(vm.uiState is BooksUiState.Loading)
        advanceUntilIdle()
        assertEquals("Jazz", (vm.uiState as BooksUiState.Success).books.single().title)
    }
    @Test fun emptyResponseHasDedicatedState() = runTest(dispatcher) {
        val vm = BooksViewModel(FakeRepository().apply { handler = { emptyList() } })
        advanceUntilIdle()
        assertTrue(vm.uiState is BooksUiState.Empty)
    }
    @Test fun retryRecoversFromOfflineFailure() = runTest(dispatcher) {
        val repo = FakeRepository().apply { handler = { throw IOException("offline") } }
        val vm = BooksViewModel(repo)
        advanceUntilIdle()
        assertTrue(vm.uiState is BooksUiState.Error)
        repo.handler = { listOf(Book("two", "Recovered", "", null)) }
        vm.retry()
        advanceUntilIdle()
        assertEquals("Recovered", (vm.uiState as BooksUiState.Success).books.single().title)
    }
    @Test fun quotaFailureExplainsApiKeyRequirement() = runTest(dispatcher) {
        val vm = BooksViewModel(FakeRepository().apply { handler = {
            throw HttpException(Response.error<Any>(429, "quota".toResponseBody()))
        } })
        advanceUntilIdle()
        assertEquals(429, (vm.uiState as BooksUiState.Error).httpCode)
    }
    @Test fun newSearchCancelsOldResults() = runTest(dispatcher) {
        val repo = FakeRepository().apply { handler = { query ->
            if (query == "jazz history") delay(10_000)
            listOf(Book(query, query, "", null))
        } }
        val vm = BooksViewModel(repo)
        runCurrent()
        vm.search("kotlin")
        advanceUntilIdle()
        assertEquals("kotlin", (vm.uiState as BooksUiState.Success).books.single().title)
    }
    @Test fun whitespaceOnlySearchProducesEmptyState() = runTest(dispatcher) {
        val vm = BooksViewModel(FakeRepository())
        advanceUntilIdle()
        vm.search("   ")
        advanceUntilIdle()
        assertTrue(vm.uiState is BooksUiState.Empty)
    }
}
