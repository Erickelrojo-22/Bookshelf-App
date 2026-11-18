package com.example.bookshelf

import androidx.compose.ui.test.*
import androidx.compose.runtime.remember
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.bookshelf.data.BooksRepository
import com.example.bookshelf.model.Book
import com.example.bookshelf.ui.BooksViewModel
import com.example.bookshelf.ui.BookshelfApp
import com.example.bookshelf.ui.BookshelfTheme
import kotlinx.coroutines.awaitCancellation
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import java.io.IOException

@RunWith(AndroidJUnit4::class)
class BookshelfUiTest {
    @get:Rule val compose = createComposeRule()
    private val books = (1..12).map { Book("$it", "Libro de prueba $it", "Autor de prueba", null) }
    private fun show(handler: suspend (String) -> List<Book>) {
        val repository = object : BooksRepository {
            override suspend fun searchBooks(query: String) = handler(query)
        }
        compose.setContent { BookshelfTheme {
            val viewModel = remember { BooksViewModel(repository) }
            BookshelfApp(viewModel)
        } }
    }
    @Test fun gridDisplaysBooksAndScrolls() {
        show { books }
        compose.onNodeWithText("Libro de prueba 1", useUnmergedTree = true).assertIsDisplayed()
        compose.onNodeWithTag("booksGrid").performScrollToIndex(11)
        compose.onNodeWithText("Libro de prueba 12", useUnmergedTree = true).assertIsDisplayed()
    }
    @Test fun loadingIsVisibleWhileRequestIsPending() {
        show { awaitCancellation() }
        compose.onNodeWithTag("loading").assertIsDisplayed()
        compose.onNodeWithText("Buscando libros…").assertIsDisplayed()
    }
    @Test fun emptyResultsAreExplained() {
        show { emptyList() }
        compose.onNodeWithText("Sin resultados").assertIsDisplayed()
    }
    @Test fun retryButtonRecoversFromFailure() {
        var offline = true
        show { if (offline) throw IOException("offline") else books }
        compose.onNodeWithText("No pudimos cargar los libros").assertIsDisplayed()
        offline = false
        compose.onNodeWithText("Reintentar").performClick()
        compose.onNodeWithTag("booksGrid").assertIsDisplayed()
    }
    @Test fun searchUsesEnteredQuery() {
        show { query -> listOf(Book("query", query, "", null)) }
        compose.onNodeWithTag("searchInput").performTextReplacement("kotlin")
        compose.onNodeWithText("Buscar").performClick()
        compose.onNode(hasText("kotlin") and hasAnyAncestor(hasTestTag("booksGrid")),
            useUnmergedTree = true).assertIsDisplayed()
    }
}
