"""Utilities for WS."""
from lxml import etree
from jinja2 import Environment, PackageLoader


def remove_empty_tags(xml, ouput_as_string=True):
    """Remove empty tags with xslt transformation.

    param: xml a string or a etree type
    return: unicode string or lxml.etree._XSLTResultTree
    """
    # use Jinja env for getting the path of template file
    # pkg_resouces may be an alternative, but we already
    # have Jinja
    env = Environment(
        loader=PackageLoader('roulier', 'templates'),
        extensions=['jinja2.ext.with_'])
    template = env.get_template("remove_empty_tags.xsl")
    xsl = etree.parse(open(template.filename))
    transform = etree.XSLT(xsl)

    if isinstance(xml, basestring):
        xml = etree.fromstring(xml)
    # else we asume xml is an lxml.etree
    if ouput_as_string:
        return unicode(transform(xml))
    else:
        return transform(xml)
