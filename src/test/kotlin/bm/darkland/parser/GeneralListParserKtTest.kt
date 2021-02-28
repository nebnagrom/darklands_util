package bm.darkland.parser

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import java.nio.charset.Charset
import java.nio.charset.StandardCharsets

class GeneralListParserKtTest {
    private val parser = GeneralListParser()

    @Test
    fun `extractNullDelimitedString returns no value when no delimited String`() {
        val testData = byteArrayOf(1, 2, 3)

        val result = extractNullDelimitedString(testData)

        Assertions.assertNull(result.value, "Value should not exist")
        Assertions.assertArrayEquals(testData, result.remaining, "data should be unchanged")
    }

    @Test
    fun `extractNullDelimitedString returns value when delimited String`() {
        val testData = byteArrayOf("a".toByteArray(StandardCharsets.US_ASCII)[0], 0, 3)

        val result = extractNullDelimitedString(testData)

        Assertions.assertEquals("a", result.value, "Value should not exist")
        Assertions.assertArrayEquals(byteArrayOf(3), result.remaining, "data should be unchanged")
    }

    @Test
    fun `extractNullDelimitedString returns first value when multiple delimited String`() {
        val testData = byteArrayOf("b".toByteArray(StandardCharsets.US_ASCII)[0], 0, "c".toByteArray(StandardCharsets.US_ASCII)[0], 0)

        val result = extractNullDelimitedString(testData)

        Assertions.assertEquals("b", result.value, "Value should not exist")
        Assertions.assertArrayEquals(byteArrayOf("c".toByteArray(StandardCharsets.US_ASCII)[0], 0), result.remaining, "data should be unchanged")
    }
}