package bm.darkland

import bm.darkland.parser.CatalogueParser
import bm.darkland.parser.GeneralListParser
import java.io.File
import java.nio.charset.Charset

const val NUM_SAINT_OFFSET = 0;
const val FIRST_SAINT_OFFSET = 1;
const val SAINT_SIZE = 168;

fun main(args: Array<String>) {
    val saintsFile = File("DARKLAND/DARKLAND.SNT");
    val imapsCatalogueFile = "DARKLAND/IMAPS.CAT"
    val einfoCatalogueFile = "DARKLAND/E00C.CAT"

    val numberOfSaintBytes = saintsFile.readBytes()

    val catalogueParser = CatalogueParser()

//    val darklandExeName = "DARKLAND/DARKLAND.EXE"
//    val darklandBytes = File(darklandExeName).inputStream().readBytes()
//    var lastByte = 1u.toUByte()
//    for (i in 2 until darklandBytes.size) {
//        val currentByte = darklandBytes[i].toUByte()
//        if (lastByte == 20u.toUByte() && currentByte == 80.toUByte()) {
//            println("found something at offset $i in hex ${i.toString(16)}")
//        }
//        lastByte = currentByte
//    }

//    val imapsCatalogue = catalogueParser.parse(imapsCatalogueFile)
//    val catalogue = catalogueParser.parse(einfoCatalogueFile)
//
//    catalogue.entries.forEach {
//        println("catalogue entry $it")
//    }

    val generalListParser = GeneralListParser()
    generalListParser.parseGeneralList("DARKLAND/")

//    val numberOfSaints = numberOfSaintBytes[0].toUByte()
//    println ("number of saints $numberOfSaints")

//    saintsFile.inputStream().buffered(SAINT_SIZE).use { inputStream ->
//        val noSaints = inputStream.readNBytes(1)[0].toUByte().toInt()
//        println ("number of saints $noSaints")
//        for (i in 1 .. noSaints){
//            processSaint(inputStream.readNBytes(SAINT_SIZE))
//        }
//    }
}

fun processSaint(bytes: ByteArray) : String {
    val saintDetails = String(bytes, Charset.forName("US-ASCII")).trim()
    println(saintDetails)
return saintDetails
}