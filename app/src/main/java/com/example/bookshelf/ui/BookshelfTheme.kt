package com.example.bookshelf.ui

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LibraryColors = lightColorScheme(
    primary = Color(0xFF245747), onPrimary = Color.White,
    primaryContainer = Color(0xFFDCE9E1), onPrimaryContainer = Color(0xFF173D31),
    secondaryContainer = Color(0xFFDCE9E1), onSecondaryContainer = Color(0xFF173D31),
    background = Color(0xFFFAF8F4), onBackground = Color(0xFF242D28),
    surface = Color(0xFFFAF8F4), onSurface = Color(0xFF242D28),
    surfaceVariant = Color(0xFFEFECE5), onSurfaceVariant = Color(0xFF636B64),
    outline = Color(0xFFB8C0B7)
)

@Composable
fun BookshelfTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = LibraryColors, content = content)
}
