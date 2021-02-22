import xml.etree.ElementTree as ET
import pandas
import csv
import sys
from io import StringIO
# from https://github.com/Hodapp87/parse_13F/blob/master/parse_13f.py

# The dictionary of attributes from the XML file that we're interested
# in, and what types they should be.  (Specifically: key = desired
# column name, value = (conversion function, attribute).)
_13f_attribs = {
    "nameOfIssuer":           (str, "{0}nameOfIssuer"),
    "titleOfClass":           (str, "{0}titleOfClass"),
    "cusip":                  (str, "{0}cusip"),
    "value":                  (int, "{0}value"),
    "sshPrnamt":              (int, "{0}shrsOrPrnAmt/{0}sshPrnamt"),
    "sshPrnamtType":          (str, "{0}shrsOrPrnAmt/{0}sshPrnamtType"),
    "votingAuthoritySole":    (int, "{0}votingAuthority/{0}Sole"),
    "votingAuthorityShared":  (int, "{0}votingAuthority/{0}Shared"),
    "votingAuthorityNone":    (int, "{0}votingAuthority/{0}None"),
    "investmentDiscretion":   (str, "{0}investmentDiscretion"),
}

_sec_url_prefix = "{http://www.sec.gov/edgar/document/thirteenf/informationtable}"

def xml_to_dataframe(elements, attr_dict, prefix = ""):
    """Turn a list of elements into a Pandas DataFrame according to the
    attributes and conversions specified in 'attr_dict', which is a
    dictionary whose keys are the intended column name in that
    DataFrame and whose values are tuples containing (conversion
    function, XML path).  Conversion function is applied to the text
    at that XML path, and the XML path will have {0} replaced with
    optional 'prefix'.
    """
    def get_row(el):
        row = {}
        for k in _13f_attribs:
            fn, attr = _13f_attribs[k]
            row[k] = fn(el.find(attr.format(prefix)).text)
        return row
    # A row of dictionaries can be handled directly by Pandas:
    rows = [get_row(e) for e in elements]
    return rows
    #return pandas.DataFrame(rows)

def parse_13f(buffer):
    root = ET.fromstring(buffer.strip().replace(b'<XML>',b'').replace(b'</XML>', b'').strip())
    df = xml_to_dataframe(
        root.findall("{0}infoTable".format(_sec_url_prefix)),
        _13f_attribs,
        _sec_url_prefix)
    return df
#
# if __name__ == "__main__" and len(sys.argv) > 1:
#     # Parse from an example XML file:
#     tree = ET.parse(sys.argv[1])
#     root = tree.getroot()
#
#     url_prefix = "{http://www.sec.gov/edgar/document/thirteenf/informationtable}"
#     df = xml_to_dataframe(
#         root.findall("{0}infoTable".format(url_prefix)),
#         attribs,
#         url_prefix)
#
#     # Get table of (some) CUSIP IDs to ticker symbols.
#     cusip_to_symbol = pandas.read_csv("./cusip_to_symbol.csv")
#     # Note left join; we don't want to lose entries just because no symbol
#     # is available.
#     df = df.merge(cusip_to_symbol, how="left", on="cusip").fillna("")
#
#     # Dump to CSV and to screen:
#     df.to_csv(sys.stdout, index=False)
#     pandas.set_option("display.width", None)
#     print(df)
