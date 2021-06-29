import os

import pytest
from mypy import api


script_template = """
from datetime import datetime
from tests.definitions import typed_function

typed_function({argument})
"""


real_world_json = """
{
  "glossary": {
    "title": "example glossary",
    "GlossDiv": {
      "title": "S",
      "GlossList": {
        "GlossEntry": {
          "ID": "SGML",
          "SortAs": "SGML",
          "GlossTerm": "Standard Generalized Markup Language",
          "Acronym": "SGML",
          "Abbrev": "ISO 8879:1986",
          "GlossDef": {
            "para": "A meta-markup language, used to create markup languages such as DocBook.",
            "GlossSeeAlso": [
              "GML",
              "XML"
            ]
          },
          "GlossSee": "markup"
        }
      }
    }
  }
}
"""


@pytest.mark.parametrize(
    "expression",
    [
        # scalar types
        "-1",  # negative numbers
        "1",  # positive numbers
        "1.234",  # floats
        "\"any str\"",  # strings
        "None",  # nulls
        "True",  # booleans
        "False",
        # non-scalar types
        "[]",  # empty list
        "{}",  # empty objects
        "[1, None, \"any str\", {\"key\": 0}, [1, True, None]]",  # mixed types in list
        # very deep object
        "{\"1\": [{\"2\": [{\"3\": [{\"4\": [{\"5\": [{\"6\": [None]}, {}]}, True]}, None]}, \"any str\"]}, 1]}",
        real_world_json,
    ]
)
def test_complete_successfully(expression):
    """
    check that mypy returns 0 on correct data
    """
    out, _, rc = api.run(["-c", script_template.format(argument=expression)])
    assert rc == 0, out


@pytest.mark.parametrize(
    "expression",
    [
        "{10: \"value\"}",  # number as key
        "{None: \"value\"}",  # null as key
        "{\"1\": [{\"2\": [{3: []}, None]}, True]}",  # wrong key is in the deepest key
        "datetime.now()",  # not json compatible type
        "{\"1\": [{\"2\": [{\"3\": [datetime.now()]}, None]}, True]}",  # wrong type is in the depth of object
        "{(1,): None}",  # tuple as key
    ]
)
def test_fail(expression):
    """
    check that mypy fails on incorrect data
    """
    out, _, rc = api.run(["-c", script_template.format(argument=expression)])
    assert rc == 1, out
