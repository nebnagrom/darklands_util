package bm.darkland.model

/**
 * Represents the data held in DARKLAND.LST
 * Items and formula not implementated
 */
data class DarklandList(val saints: List<SaintReference>)

/**
 * Saint details held in list file
 */
data class SaintReference(val position: Int, val fullName: String, val shortName: String)