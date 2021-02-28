package bm.darkland.writer

import bm.darkland.model.Saint
import com.fasterxml.jackson.databind.ObjectMapper
import java.io.File

private val objectMapper = ObjectMapper()

class SaintJsonWriter {
    fun writeSaints(saints: List<Saint>) {
        val saintsFile = File("saints.json")
        saintsFile.createNewFile()
        objectMapper.writeValue(saintsFile.outputStream(), saints)
    }
}