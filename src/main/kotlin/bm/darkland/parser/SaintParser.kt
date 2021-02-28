package bm.darkland.parser

import bm.darkland.model.CatalogueEntry
import bm.darkland.model.Saint
import java.io.File


class SaintParser {
    fun parseSaint(darklandRoot: String): List<Saint> {

        val darklandLstFile = File(darklandRoot + LIST_FILE)
        val darklandSaintFile = File(darklandRoot + SAINT_DESCRIPTION_FILE)

        val saints = mutableListOf<Saint>()


        darklandLstFile.inputStream().buffered(BUFFER_SIZE).use { inputStream ->
            val numberOfItemDefs= inputStream.readNBytes(1)[0].toUByte().toInt()
            val numberOfSaints = inputStream.readNBytes(1)[0].toUByte().toInt()
            println("number of catalogue entries $numberOfSaints")
            for (i in 0 until numberOfSaints) {
                val entryBytes = inputStream.readNBytes(ENTRY_SIZE)
//                val entryDetails = parseEntry(i, entryBytes)
//                entries.add(CatalogueEntry(i, entryDetails.fileName, entryDetails.timestamp, entryDetails.length, entryDetails.offset, ByteArray(0)))
            }
        }

        return saints
    }
}