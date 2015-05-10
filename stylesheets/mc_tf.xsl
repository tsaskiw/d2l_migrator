<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="Question[Type=1 or Type=4]">
    <xsl:variable name="lid_ident" select="concat('TLM_QUES_', ID, '_LID')" />
    <item xmlns:d2l_2p0="http://desire2learn.com/xsd/d2lcp_v2p0" ident="TLM_OBJ_{ID}" label="TLM_QUES_{ID}" d2l_2p0:page="1" title="{Title}">
        <itemmetadata>
          <qtimetadata>
            <qti_metadatafield>
              <fieldlabel>qmd_computerscored</fieldlabel>
              <fieldentry>yes</fieldentry>
            </qti_metadatafield>
            <qti_metadatafield>
              <fieldlabel>qmd_questiontype</fieldlabel>
              <xsl:if test="Type=1">
                  <fieldentry>Multiple Choice</fieldentry>
              </xsl:if>
              <xsl:if test="Type=4">
                  <fieldentry>True/False</fieldentry>
              </xsl:if>
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
                        <xsl:for-each select="pp_answers/pp_answer">
                            <flow_label class="Block">
                                <response_label ident="TLM_QUES_{ancestor::Question/child::ID}_RESP_{id}">
                                    <flow_mat>
                                        <material>
                                            <xsl:if test="responsetype = 'text/html'">
                                                <mattext texttype="text/html">&lt;p&gt;<xsl:value-of select="text" />&lt;/p&gt;</mattext>
                                            </xsl:if>
                                            <xsl:if test="responsetype = 'text/plain'">
                                                <mattext texttype="text/plain"><xsl:value-of select="text" /></mattext>
                                            </xsl:if>
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
            <xsl:for-each select="pp_answers/pp_answer">
                <xsl:variable name="fb_ident" select="concat('TLM_QUES_', ancestor::Question/child::ID, '_FB_', id)" />
                <xsl:variable name="resp_ident" select="concat('TLM_QUES_', ancestor::Question/child::ID, '_RESP_', id)" />
                <respcondition title="Response Condition {number}">
                    <conditionvar>
                        <varequal respident="{$lid_ident}"><xsl:value-of select="$resp_ident" /></varequal>
                    </conditionvar>
                    <xsl:if test="value = 1">
                        <setvar action="Set">100.000000000</setvar>
                    </xsl:if>
                    <xsl:if test="value = 0">
                        <setvar action="Set">0.000000000</setvar>
                    </xsl:if>
                    <displayfeedback feedbacktype="Response" linkrefid="{$fb_ident}" />
                </respcondition>
            </xsl:for-each>
        </resprocessing>
        <xsl:for-each select="pp_answers/pp_answer">
            <xsl:variable name="fb_ident" select="concat('TLM_QUES_', ancestor::Question/child::ID, '_FB_', id)" />
                <itemfeedback ident="{$fb_ident}">
                    <material>
                        <xsl:variable name="fb" select="feedback" />
                        <xsl:if test="not($fb = '')">
                            <mattext texttype="text/html">&lt;p&gt;<xsl:value-of select="$fb" />&lt;/p&gt;</mattext>
                        </xsl:if>
                        <xsl:if test="$fb = ''">
                            <mattext texttype="text/html" />
                        </xsl:if>
                    </material>
                </itemfeedback>
        </xsl:for-each>
    </item>
</xsl:template>

</xsl:stylesheet>
