package com.example.bookshelf.model

data class Book(val id: String, val title: String, val authors: String, val thumbnailUrl: String?)

// Nullable fields reflect optional values in the Google Books response.
data class VolumesResponse(val items: List<Volume>? = null)
data class Volume(val id: String = "", val volumeInfo: VolumeInfo? = null)
data class VolumeInfo(val title: String? = null, val authors: List<String>? = null, val imageLinks: ImageLinks? = null)
data class ImageLinks(val thumbnail: String? = null, val smallThumbnail: String? = null)
