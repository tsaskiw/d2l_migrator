<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="Question[Type=3]">
    <xsl:variable name="ques_label" select="concat('TLM_QUES_',ID)"/>
    <item xmlns:d2l_2p0="http://desire2learn.com/xsd/d2lcp_v2p0" ident="TLM_OBJ_{ID}" label="{$ques_label}" d2l_2p0:page="1" title="{Title}">
        <itemmetadata>
          <qtimetadata>
            <qti_metadatafield>
              <fieldlabel>qmd_computerscored</fieldlabel>
              <fieldentry>yes</fieldentry>
            </qti_metadatafield>
            <qti_metadatafield>
              <fieldlabel>qmd_questiontype</fieldlabel>
                  <fieldentry>Short Answer</fieldentry>
            </qti_metadatafield>
            <qti_metadatafield>
              <fieldlabel>qmd_weighting</fieldlabel>
              <fieldentry>1.000000000</fieldentry>
            </qti_metadatafield>
            <qti_metadatafield>
              <fieldlabel>qmd_displayid</fieldlabel>
              <fieldentry><xsl:value-of select="/TLMPackage/ECourse/Title" /></fieldentry>
            </qti_metadatafield>
          </qtimetadata>
        </itemmetadata>
        <xsl:for-each select="Parts/QuestionPart">
            <presentation>
                <flow>
                    <material>
                        <mattext texttype="text/html">&lt;p&gt;<xsl:value-of select="Text" />&lt;/p&gt;</mattext>
                        <response_str ident="TLM_QUES_{ID}_STR" rcardinality="Single">
                            <render_fib rows="1" columns="40" prompt="Box" fibtype="String">
                                <response_label ident="TLM_QUES_{ID}_ANS" />
                            </render_fib>
                        </response_str>
                    </material>
                </flow>
            </presentation>
            <resprocessing>
                <outcomes>
                    <decvar type="Integer" minvalue="0" maxvalue="100" varname="Blank_1"/>
                </outcomes>
            <xsl:for-each select="Answers/QuestionAnswer[Value > 0]">
                <xsl:variable name="resp_ident" select="ID" />
                <respcondition>
                    <conditionvar>
                        <xsl:variable name="ignore_case">
                            <xsl:choose>
                                <xsl:when test="ancestor::QuestionPart/ShortAnsIgnoreCase='True'">no</xsl:when>
                                <xsl:otherwise>yes</xsl:otherwise>
                            </xsl:choose>
                        </xsl:variable>
                        <varequal respident="{$resp_ident}" case="{$ignore_case}"><xsl:value-of select="Text" /></varequal>
                    </conditionvar>
                    <setvar action="Set"><xsl:value-of select="Value"/></setvar>
                </respcondition>
            </xsl:for-each>
                <itemfeedback ident="{$ques_label}_FB">
                    <material>
                        <mattext texttype="text/html">
            <xsl:for-each select="Answers/QuestionAnswer[Value = 0]">
                <xsl:if test="not(Feedback = '')">&lt;p&gt;<xsl:value-of select="Feedback"/>&lt;/p&gt;</xsl:if>
            </xsl:for-each>
                        </mattext>
                    </material>
                </itemfeedback>
            </resprocessing>
        </xsl:for-each>
    </item>
</xsl:template>

</xsl:stylesheet>
