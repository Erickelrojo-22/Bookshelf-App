package com.example.bookshelf.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.res.pluralStringResource
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.SubcomposeAsyncImage
import coil.compose.SubcomposeAsyncImageContent
import coil.request.ImageRequest
import androidx.compose.ui.platform.LocalContext
import com.example.bookshelf.R
import com.example.bookshelf.model.Book

@Composable
fun BookshelfApp(viewModel: BooksViewModel) {
    var searchText by rememberSaveable { mutableStateOf(viewModel.query) }
    val focus = LocalFocusManager.current
    val onSearch = { focus.clearFocus(); viewModel.search(searchText) }
    Scaffold { insets ->
        Column(Modifier.fillMaxSize().padding(insets)) {
            Column(Modifier.padding(horizontal = 20.dp, vertical = 16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(painterResource(R.drawable.ic_bookshelf), null,
                        Modifier.size(38.dp).clip(RoundedCornerShape(8.dp)), tint = androidx.compose.ui.graphics.Color.Unspecified)
                    Spacer(Modifier.width(12.dp))
                    Column {
                        Text(stringResource(R.string.app_name), fontSize = 30.sp,
                            fontFamily = FontFamily.Serif, fontWeight = FontWeight.Bold)
                        Text(stringResource(R.string.tagline), style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                Spacer(Modifier.height(20.dp))
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedTextField(searchText, { searchText = it }, Modifier.weight(1f).testTag("searchInput"),
                        label = { Text(stringResource(R.string.search_hint)) }, singleLine = true,
                        shape = RoundedCornerShape(12.dp),
                        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
                        keyboardActions = KeyboardActions(onSearch = { onSearch() }))
                    FilledTonalButton(onClick = onSearch, shape = RoundedCornerShape(12.dp),
                        contentPadding = PaddingValues(horizontal = 14.dp, vertical = 18.dp)) {
                        Text(stringResource(R.string.search))
                    }
                }
            }
            when (val state = viewModel.uiState) {
                BooksUiState.Loading -> StateMessage(R.string.loading, R.string.loading_detail, loading = true)
                BooksUiState.Empty -> StateMessage(R.string.empty_title, R.string.empty_detail)
                is BooksUiState.Error -> {
                    val message = when (state.httpCode) {
                        429 -> stringResource(R.string.quota_error)
                        null -> stringResource(R.string.network_error)
                        else -> stringResource(R.string.http_error, state.httpCode)
                    }
                    Column(Modifier.fillMaxSize().padding(28.dp), verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(stringResource(R.string.error_title), style = MaterialTheme.typography.titleLarge)
                        Spacer(Modifier.height(12.dp))
                        Text(message, style = MaterialTheme.typography.bodyMedium)
                        Spacer(Modifier.height(24.dp))
                        Button(onClick = viewModel::retry) { Text(stringResource(R.string.retry)) }
                    }
                }
                is BooksUiState.Success -> {
                    Text(stringResource(R.string.collection), Modifier.padding(horizontal = 20.dp),
                        style = MaterialTheme.typography.titleLarge, fontFamily = FontFamily.Serif)
                    Text(pluralStringResource(R.plurals.results, state.books.size, state.books.size, viewModel.query),
                        Modifier.padding(start = 20.dp, top = 4.dp, bottom = 12.dp),
                        style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    LazyVerticalGrid(columns = GridCells.Adaptive(150.dp), modifier = Modifier.weight(1f).testTag("booksGrid"),
                        contentPadding = PaddingValues(start = 20.dp, end = 20.dp, bottom = 20.dp),
                        horizontalArrangement = Arrangement.spacedBy(16.dp), verticalArrangement = Arrangement.spacedBy(20.dp)) {
                        items(state.books, key = { it.id }) { BookCard(it) }
                    }
                }
            }
        }
    }
}

@Composable
private fun StateMessage(title: Int, detail: Int, loading: Boolean = false) {
    Column(Modifier.fillMaxSize().padding(28.dp), verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally) {
        if (loading) {
            CircularProgressIndicator(Modifier.testTag("loading"))
            Spacer(Modifier.height(24.dp))
        }
        Text(stringResource(title), style = MaterialTheme.typography.titleLarge)
        Spacer(Modifier.height(12.dp))
        Text(stringResource(detail), style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
private fun BookCard(book: Book) {
    Column {
        Card(shape = RoundedCornerShape(10.dp), elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)) {
            SubcomposeAsyncImage(
                model = ImageRequest.Builder(LocalContext.current).data(book.thumbnailUrl).crossfade(true).build(),
                contentDescription = stringResource(R.string.cover_description, book.title),
                modifier = Modifier.fillMaxWidth().aspectRatio(0.68f), contentScale = ContentScale.Fit,
                loading = { Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator(Modifier.size(24.dp), strokeWidth = 2.dp)
                } },
                error = { Box(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.surfaceVariant),
                    contentAlignment = Alignment.Center) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.padding(12.dp)) {
                        Icon(painterResource(R.drawable.ic_book_placeholder), null, Modifier.size(40.dp),
                            tint = MaterialTheme.colorScheme.primary)
                        Spacer(Modifier.height(12.dp))
                        Text(stringResource(R.string.no_cover), style = MaterialTheme.typography.labelSmall)
                    }
                } },
                success = { SubcomposeAsyncImageContent() }
            )
        }
        Text(book.title, Modifier.padding(top = 10.dp), fontWeight = FontWeight.SemiBold,
            style = MaterialTheme.typography.bodyMedium, maxLines = 2, overflow = TextOverflow.Ellipsis)
        if (book.authors.isNotBlank()) Text(book.authors, Modifier.padding(top = 3.dp),
            style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant,
            maxLines = 1, overflow = TextOverflow.Ellipsis)
    }
}
