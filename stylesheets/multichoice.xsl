<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">


<xsl:template match="Question[Type = 1]">
    <xsl:variable name="lid_ident" select="concat('QUES_TLM_', ID, '_LID')" />
    <item xmlns:d2l_2p0="http://desire2learn.com/xsd/d2lcp_v2p0" ident="TLM_QUES_{ID}" d2l_2p0:page="1" title="{Title}">
        <itemmetadata>
          <qtimetadata>
            <qti_metadatafield>
              <fieldlabel>qmd_computerscored</fieldlabel>
              <fieldentry>yes</fieldentry>
            </qti_metadatafield>
            <qti_metadatafield>
              <fieldlabel>qmd_questiontype</fieldlabel>
              <fieldentry>Multiple Choice</fieldentry>
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
                <response_extension>
                  <d2l_2p0:display_style>2</d2l_2p0:display_style>
                  <d2l_2p0:enumeration>5</d2l_2p0:enumeration>
                  <d2l_2p0:grading_type>0</d2l_2p0:grading_type>
                </response_extension>
                <response_lid ident="{$lid_ident}" rcardinality="Single">
                    <render_choice shuffle="no">
                        <xsl:for-each select="Parts/QuestionPart/Choices/QuestionChoice">
                            <flow_label class="Block">
                                <response_label ident="QUES_TLM_{ancestor::Question/child::ID}_RESP_{ID}">
                                    <flow_mat>
                                        <material>
                                            <mattext texttype="text/html">&lt;p&gt;<xsl:value-of select="Text" />&lt;/p&gt;</mattext>
                                        </material>
                                    </flow_mat>
                                </response_label>
                            </flow_label>
                        </xsl:for-each>
                    </render_choice>
                </response_lid>
            </flow>
        </presentation>
        <resprocessing>
            <xsl:for-each select="Parts/QuestionPart/Answers/QuestionAnswer">
                <xsl:variable name="resp_ident" select="concat('QUES_TLM_', ancestor::Question/child::ID, '_RESP_', position())" />
                <xsl:variable name="fb_ident" select="concat('QUES_TLM_', ancestor::Question/child::ID, '_FB_', position())" />
                <respcondition title="Response Condition {position()}">
                    <conditionvar>
                        <varequal respident="{$lid_ident}"><xsl:value-of select="$resp_ident" /></varequal>
                    </conditionvar>
                    <xsl:if test="Value = 1">
                        <setvar action="Set">100.000000000</setvar>
                    </xsl:if>
                    <xsl:if test="Value = 0">
                        <setvar action="Set">0.000000000</setvar>
                    </xsl:if>
                    <displayfeedback feedbacktype="Response" linkrefid="{$fb_ident}" />
                </respcondition>
            </xsl:for-each>
            <!--<xsl:for-each select="Parts/QuestionPart/Answers/QuestionAnswer">
                <fb/>
            </xsl:for-each>-->
        </resprocessing>
    </item>
</xsl:template>

</xsl:stylesheet>
