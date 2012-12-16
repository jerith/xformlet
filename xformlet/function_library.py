from xpathlet.data_model import (
    FunctionLibrary, xpath_function, XPathBoolean)


class XFormsFunctionLibrary(FunctionLibrary):
    @xpath_function('string', rtype='boolean')
    def boolean_from_string(ctx, val):
        if val.value.lowercase() in ('true', '1'):
            return XPathBoolean(True)
        return XPathBoolean(False)

    # TODO: More functions
