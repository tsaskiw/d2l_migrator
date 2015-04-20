from lxml import etree

def transform_data(source_etree, stylesheet):
    xslt = etree.parse(stylesheet)
    transform = etree.XSLT(xslt)
    new_dom = transform(source_etree)
    return new_dom

def build_resource_paths(result_etree, base_url):
    pass
