package bm.darkland.model

data class Attribute(val position: Int, val name: String, val shortName: String)

val ENDURANCE = Attribute(0, "Endurance", "end")
val STRENGTH = Attribute(1, "Strength", "str")
val AGILITY = Attribute(2, "Agility", "agl")
val PERCEPTION = Attribute(3, "Perception", "per")
val INTELLIGENCE = Attribute(4, "Intelligence", "int")
val CHARISMA = Attribute(5, "Charisma", "chr")
val DIVINE_FAVOR = Attribute(6, "Divine favor", "df")