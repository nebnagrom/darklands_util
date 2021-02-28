package bm.darkland.parser

import bm.darkland.model.CatalogueEntry
import bm.darkland.model.DarklandList
import bm.darkland.model.Saint
import java.io.File
import java.nio.charset.Charset
import java.nio.charset.StandardCharsets
import java.nio.charset.StandardCharsets.US_ASCII

const val LIST_FILE = "DARKLAND.LST"

// Offsets for the DARKLAND.LST file
const val num_item_slots_position = 0
const val num_saints_position = 1
const val num_formulae_position = 2
const val item_definitions_position = 3
const val ITEM_DEFINITION_SIZE = 0x2e
const val LONG_SAINT_NAME = 24

class GeneralListParser {
    fun parseGeneralList(darklandRoot: String): DarklandList {

        val darklandLstFile = File(darklandRoot + LIST_FILE)

        val saints = mutableListOf<Saint>()

        darklandLstFile.inputStream().buffered(BUFFER_SIZE).use { inputStream ->

            // Read header info
            val numberOfItemDefs = inputStream.readNBytes(1)[0].toUByte().toInt()
            val numberOfSaints = inputStream.readNBytes(1)[0].toUByte().toInt()
            val numberOfFormala = inputStream.readNBytes(1)[0].toUByte().toInt()

            // Skip over item defs
            inputStream.skipNBytes(numberOfItemDefs * ITEM_DEFINITION_SIZE.toLong())

            var saintLongNames = mutableListOf<String>()
            var saintShortNames = mutableListOf<String>()

            var currentBytes = byteArrayOf()
            // read saints, null delimited
            for (i in 0..numberOfSaints) {

                // if there is no zero delimiter in the current block grab another chunk of saint names
                if (!currentBytes.contains(0)) {
                    currentBytes += inputStream.readNBytes(LONG_SAINT_NAME * 2)
                }
                // grab the first saint name
                val currentName = extractNullDelimitedString(currentBytes)
                currentName.value?.let { name ->
                    currentBytes = currentName.remaining
                    saintLongNames.add(name) }
            }
            println("fetched saints $saintLongNames")
//            for (i in 0 until numberOfSaints) {
//                inputStream.
//                val entryBytes = inputStream.readNBytes(ENTRY_SIZE)
//                val entryDetails = parseEntry(i, entryBytes)
//                entries.add(CatalogueEntry(i, entryDetails.fileName, entryDetails.timestamp, entryDetails.length, entryDetails.offset, ByteArray(0)))
//            }
        }

        return DarklandList(listOf())
    }
}

fun extractNullDelimitedString(bytes: ByteArray): StringAndRemainingBytes {

    if (!bytes.contains(0)) {
        return StringAndRemainingBytes(null, bytes);
    }
    val stringBytes = bytes.takeWhile { it != 0.toByte() }
    val stringValue = String(stringBytes.toByteArray(), Charset.forName("US-ASCII"))
    val remainingBytes = bytes.slice(stringBytes.size + 1 until bytes.size)

    return StringAndRemainingBytes(stringValue, remainingBytes.toByteArray());
}

data class StringAndRemainingBytes(val value: String?, val remaining: ByteArray) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false

        other as StringAndRemainingBytes

        if (value != other.value) return false
        if (!remaining.contentEquals(other.remaining)) return false

        return true
    }

    override fun hashCode(): Int {
        var result = value?.hashCode() ?: 0
        result = 31 * result + remaining.contentHashCode()
        return result
    }
}