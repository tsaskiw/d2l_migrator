<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="Question[Type=6.1]">
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
                  <fieldentry>Fill in the Blanks</fieldentry>
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
                <xsl:for-each select="Parts/QuestionPart">
                    <xsl:variable name="ques_part_label" select="concat($ques_label, '_A', ID)"/>
                    <material>
                        <mattext texttype="text/html">&lt;p&gt;<xsl:value-of select="Text" />&lt;/p&gt;</mattext>
                    </material>
                    <response_str ident="{$ques_part_label}_STR" rcardinality="Single">
                        <xsl:variable name="cols">
                            <xsl:choose>
                                <xsl:when test="pp_is_tf='True'">1</xsl:when>
                                <xsl:otherwise>20</xsl:otherwise>
                            </xsl:choose>
                        </xsl:variable> 
                        <render_fib rows="1" columns="{$cols}" prompt="Box" fibtype="String">
                            <response_label ident="{$ques_part_label}_ANS" />
                        </render_fib>
                    </response_str>
                </xsl:for-each>
            </flow>
        </presentation>
        <resprocessing>
            <xsl:for-each select="Parts/QuestionPart">
                <xsl:variable name="ques_part_label" select="concat($ques_label, '_A', ID)"/>
                <xsl:variable name="case">
                    <xsl:choose>
                        <xsl:when test="ShortAnsIgnoreCase='True'">no</xsl:when>
                        <xsl:otherwise>yes</xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>
                <respcondition>
                    <conditionvar>
                        <varequal respident="{$ques_part_label}_ANS" case="{$case}"><xsl:value-of select="pp_answers" /></varequal>
                        <var_extension>
                            <d2l_2p0:answer_is_regexp>yes</d2l_2p0:answer_is_regexp>
                        </var_extension>
                        <setvar action="Set"><xsl:value-of select="pp_value" /></setvar>
                    </conditionvar>
                </respcondition>
            </xsl:for-each>
        </resprocessing>
        <itemfeedback ident="{$ques_label}">
            <material>
                <mattext texttype="text/html"><xsl:value-of select="pp_feedback" /></mattext>
            </material>
        </itemfeedback>
   </item>    
</xsl:template>

</xsl:stylesheet>
