<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:template match="/">
        <xsl:for-each select="//*">
            <xsl:value-of select="name()"/>,
        </xsl:for-each>
    <!--
    <xsl:template match="node()|@*">
        <xsl:copy>
            <xsl:apply-templates select="node()|@*"/>
        </xsl:copy>
    -->
    </xsl:template>

</xsl:stylesheet>
