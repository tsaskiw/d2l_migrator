<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" indent="yes" omit-xml-declaration="no" encoding="utf-8" cdata-section-elements="Title catalog langstring metadatascheme Body Link ParserExpression NumericTolerance ChoicesType Text Feedback Caption NodeID Description Comments Keywords Statement FileName QuestionType Code PrereqText Goals Resources GradeFormula"/>

<xsl:template match="/">
<questestinterop xmlns:d2l_2p0="http://desire2learn.com/xsd/d2lcp_v2p0">
    <xsl:for-each select="TLMPackage/Assessment[1]">
<!--<xsl:for-each select="TLMPackage/Assessment"> -->
        <assessment d2l_2p0:id="{position()}" title="{Title}" ident="tlm_{ID}"> 
            <xsl:apply-templates select="." />
        </assessment>
    </xsl:for-each>
</questestinterop>
</xsl:template>

<xsl:template match="Assessment">
    <section ident="CONTAINER_SECTION" xmlns:d2l_2p0="http://desire2learn.com/xsd/d2lcp_v2p0">
        <xsl:for-each select="Selections/AssessmentSelection/ContentSelectionSets/Question">
            <xsl:apply-templates select="." />
        </xsl:for-each>
    </section>
</xsl:template>

<xsl:template match="Question[Type = 1]">
    <item xmlns:d2l_2p0="http://desire2learn.com/xsd/d2lcp_v2p0" ident="tlm_ques_{ID}" d2l_2p0:page="1" title="{Title}">
        <presentation>
            <flow>
                <material>
                    <mattext texttype="text/html">&lt;p&gt;<xsl:value-of select="Parts/QuestionPart/Text" />&lt;/p&gt;</mattext>
                </material>
                <response_extension>
                  <d2l_2p0:display_style>2</d2l_2p0:display_style>
                  <d2l_2p0:enumeration>5</d2l_2p0:enumeration>
                  <d2l_2p0:grading_type>0</d2l_2p0:grading_type>
                </response_extension>
            </flow>
        </presentation>
    </item>
</xsl:template>

<xsl:template match="Question" />

</xsl:stylesheet>
