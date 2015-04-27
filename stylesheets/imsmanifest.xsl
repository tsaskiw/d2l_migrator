<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/root">
    
<manifest identifier="D2L_1" xmlns:d2l_2p0="http://desire2learn.com/xsd/d2lcp_v2p0" xmlns:scorm_1p2="http://www.adlnet.org/xsd/adlcp_rootv1p2" xmlns="http://www.imsglobal.org/xsd/imscp_v1p1">
    <resources>
        <resource identifier="res_quiz_{assessment_id}" type="webcontent" d2l_2p0:material_type="d2lquiz" d2l_2p0:link_target="" href="{file_name}" title="{title}" />
    </resources>
</manifest>

</xsl:template>

</xsl:stylesheet>
