<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" indent="yes" cdata-section-elements="Title catalog langstring metadatascheme Body Link ParserExpression NumericTolerance ChoicesType Text Feedback Caption NodeID Description Comments Keywords Statement FileName QuestionType Code PrereqText Goals Resources GradeFormula"/>

<xsl:template match="/">
    <QUESTIONS>
        <xsl:text>&#xa;</xsl:text>
        <xsl:for-each select="//Question[Type=1]">
            <xsl:copy-of select="."/>
            <xsl:text>&#xa;  </xsl:text>
        </xsl:for-each>
    </QUESTIONS>
</xsl:template>

</xsl:stylesheet>
