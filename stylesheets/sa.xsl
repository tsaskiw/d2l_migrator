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
        <presentation>
            <flow>
                <material>
                    <mattext texttype="text/html">&lt;p&gt;<xsl:value-of select="Parts/QuestionPart/Text" />&lt;/p&gt;</mattext>
                </material>
                <response_str ident="TLM_QUES_{ID}_STR" rcardinality="Single">
                    <render_fib rows="1" columns="40" prompt="Box" fibtype="String">
                        <response_label ident="TLM_QUES_{ID}_ANS" />
                    </render_fib>
                </response_str>
            </flow>
        </presentation>
        <resprocessing>
            <xsl:for-each select="pp_answers/pp_answer">
                <xsl:variable name="resp_ident" select="concat('TLM_QUES_', ancestor::Question/child::ID, '_ANS')" />
                <respcondition>
                    <conditionvar>
                        <xsl:variable name="ignore_case" select="ancestor::Question/child::pp_ignore_case" />
                        <xsl:if test="$ignore_case='False'">
                            <varequal respident="{$resp_ident}" case="yes">
                                <xsl:value-of select="text" />
                            </varequal>
                        </xsl:if>
                        <xsl:if test="$ignore_case='True'">
                            <varequal respident="{$resp_ident}" case="no">
                                <xsl:value-of select="text" />
                            </varequal>
                        </xsl:if>
                    </conditionvar>
                    <setvar action="Set"><xsl:value-of select="value * 100"/>.000000000</setvar>
                </respcondition>
            </xsl:for-each>
        </resprocessing>
        <xsl:for-each select="pp_feedback">
            <itemfeedback ident="{$ques_label}">
                <material>
                    <mattext texttype="text/html">&lt;p&gt;<xsl:value-of select="text"/>&lt;/p&gt;</mattext>
                </material>
            </itemfeedback>
        </xsl:for-each>
    </item>
</xsl:template>

</xsl:stylesheet>
