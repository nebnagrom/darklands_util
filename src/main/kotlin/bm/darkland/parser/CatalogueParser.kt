package bm.darkland.parser

import bm.darkland.model.Catalogue
import bm.darkland.model.CatalogueEntry
import java.io.File
import java.nio.ByteBuffer
import java.nio.charset.Charset

const val ENTRY_SIZE = 24
const val BUFFER_SIZE = 256

class CatalogueParser {
    fun parse(filename: String): Catalogue {

        val file = File(filename);

        val entries = mutableListOf<CatalogueEntry>()

        file.inputStream().buffered(BUFFER_SIZE).use { inputStream ->
            val numberEntries = inputStream.readNBytes(1)[0].toUByte().toInt()
            println("number of catalogue entries $numberEntries")
            for (i in 0 until numberEntries) {
                val entryBytes = inputStream.readNBytes(ENTRY_SIZE)
                val entryDetails = parseEntry(i, entryBytes)
                entries.add(CatalogueEntry(i, entryDetails.fileName, entryDetails.timestamp, entryDetails.length, entryDetails.offset, ByteArray(0)))
            }
        }
        return Catalogue(filename, entries)
    }

    fun parseEntry(position: Int, rawEntry: ByteArray): EntryDetails {
        val fileName = String(rawEntry.slice(0..11).toByteArray(), Charset.forName("US-ASCII")).trim()
        val timeStampBytes = rawEntry.slice(12..13).toByteArray()
        val timeStamp = ByteBuffer.wrap(timeStampBytes).short.toUShort()
        val lengthBytes = rawEntry.slice(14..15).toByteArray()
        val length = ByteBuffer.wrap(lengthBytes).short.toUShort()
        val offsetBytes = rawEntry.slice(15..16).toByteArray()
        val offset = ByteBuffer.wrap(offsetBytes).short.toUShort()
        return EntryDetails(position, fileName, timeStamp, length, offset);
    }
}

data class EntryDetails(val id: Int,
                                val fileName: String,
                                val timestamp: UShort,
                                val length: UShort,
                                val offset: UShort)