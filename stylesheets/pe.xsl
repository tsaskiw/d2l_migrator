<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="Question[Type=6.3]">
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
                  <fieldentry>Arithmetic</fieldentry>
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
                    <mat_extension>
                        <xsl:for-each select="ParserExpression/pp_variables/pp_variable">
                            <variable name="{pp_var_name}">
                                <minvalue><xsl:value-of select="pp_var_min"/></minvalue>
                                <maxvalue><xsl:value-of select="pp_var_max"/></maxvalue>
                                <decimalplaces><xsl:value-of select="pp_var_decimal_places"/></decimalplaces>
                                <step><xsl:value-of select="pp_var_step"/></step>
                            </variable>
                        </xsl:for-each>
                        <xsl:if test="ParserExpression/pp_formula">
                            <formula><xsl:value-of select="ParserExpression/pp_formula"/></formula>
                        </xsl:if>
                    </mat_extension>
                </material>
                <response_num ident="{$ques_label}_NUM" rcardinality="Single" rtiming="no">
                    <render_fib fibtype="Decimal" prompt="Box">
                        <response_label ident="{$ques_label}_A1"/>
                    </render_fib>
                </response_num>
                <response_str ident="{$ques_label}_STR" rcardinality="Single" rtiming="no">
                    <render_fib fibtype="String" prompt="Box">
                        <response_label ident="{$ques_label}_A2"/>
                    </render_fib>
                </response_str>
            </flow>
        </presentation>
        <resprocessing>
            <respcondition title="Single Condition">
                <respcond_extension>
                    <formula><xsl:value-of select="ParserExpression/pp_formula"/></formula>
                    <precision type="decimalplaces" d2l_2p0:precision_enforced="no"><xsl:value-of select="ParserExpression/pp_decimal_places"/></precision>
                    <tolerance type="units">0</tolerance>
                    <units d2l_2p0:worth="0" casesensitive="no"/>
                </respcond_extension>
                <conditionvar>
                    <other/>
                </conditionvar>
                <setvar action="Set">100</setvar>
            </respcondition>
        </resprocessing>
        <itemfeedback ident="{$ques_label}">
            <material>
                <mattext texttype="text/html"><xsl:value-of select="pp_feedback" /></mattext>
            </material>
        </itemfeedback>
   </item>    
</xsl:template>

</xsl:stylesheet>
