package com.example.bookshelf

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import com.example.bookshelf.ui.BooksViewModel
import com.example.bookshelf.ui.BookshelfApp
import com.example.bookshelf.ui.BookshelfTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val repository = (application as BookshelfApplication).container.booksRepository
        setContent {
            BookshelfTheme {
                val booksViewModel: BooksViewModel = viewModel(factory = viewModelFactory {
                    initializer { BooksViewModel(repository) }
                })
                BookshelfApp(booksViewModel)
            }
        }
    }
}
