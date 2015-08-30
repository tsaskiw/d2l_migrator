<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="xml" indent="yes" omit-xml-declaration="no" encoding="utf-8" />

<xsl:include href="sa.xsl" />
<xsl:include href="cs_mc_tf.xsl" />
<xsl:include href="msa.xsl" />

<xsl:template match="/">
<questestinterop xmlns:d2l_2p0="http://desire2learn.com/xsd/d2lcp_v2p0">
    <xsl:for-each select="TLMPackage/Assessment">
        <assessment d2l_2p0:id="{position()}" title="{Title}" ident="TLM_{ID}"> 
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

<xsl:template match="Question" />

</xsl:stylesheet>
