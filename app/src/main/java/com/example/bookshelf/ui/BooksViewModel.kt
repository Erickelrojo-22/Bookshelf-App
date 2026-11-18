package com.example.bookshelf.ui

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.bookshelf.data.BooksRepository
import com.example.bookshelf.model.Book
import com.google.gson.JsonParseException
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException

sealed interface BooksUiState {
    data object Loading : BooksUiState
    data class Success(val books: List<Book>) : BooksUiState
    data object Empty : BooksUiState
    data class Error(val httpCode: Int? = null) : BooksUiState
}

class BooksViewModel(private val repository: BooksRepository) : ViewModel() {
    var uiState: BooksUiState by mutableStateOf(BooksUiState.Loading)
        private set
    var query: String by mutableStateOf("jazz history")
        private set
    private var searchJob: Job? = null

    init { search(query) }

    fun search(value: String) {
        searchJob?.cancel()
        query = value.trim()
        if (query.isBlank()) {
            uiState = BooksUiState.Empty
            return
        }
        uiState = BooksUiState.Loading
        searchJob = viewModelScope.launch {
            uiState = try {
                val books = repository.searchBooks(query)
                if (books.isEmpty()) BooksUiState.Empty else BooksUiState.Success(books)
            } catch (error: IOException) {
                BooksUiState.Error()
            } catch (error: HttpException) {
                BooksUiState.Error(error.code())
            } catch (error: JsonParseException) {
                BooksUiState.Error()
            }
        }
    }
    fun retry() = search(query)
}
