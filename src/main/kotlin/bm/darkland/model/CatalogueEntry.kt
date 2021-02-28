package bm.darkland.model

data class CatalogueEntry(val id: Int,
                          val fileName: String,
                          val timestamp: UShort,
                          val length: UShort,
                          val offset: UShort,
                          val data: ByteArray) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false

        other as CatalogueEntry

        if (id != other.id) return false
        if (fileName != other.fileName) return false
        if (timestamp != other.timestamp) return false
        if (length != other.length) return false
        if (offset != other.offset) return false
        if (!data.contentEquals(other.data)) return false

        return true
    }

    override fun hashCode(): Int {
        var result = id
        result = 31 * result + fileName.hashCode()
        result = 31 * result + timestamp.hashCode()
        result = 31 * result + length.hashCode()
        result = 31 * result + offset.hashCode()
        result = 31 * result + data.contentHashCode()
        return result
    }
}