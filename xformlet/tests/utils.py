from StringIO import StringIO


XML_TEMPLATE = '<foo xmlns:xforms="http://www.w3.org/2002/xforms">\n%s\n</foo>'


def make_doc(xml):
    return StringIO(XML_TEMPLATE % (xml,))
