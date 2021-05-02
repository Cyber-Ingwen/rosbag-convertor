# Copyright 2020-2021  Ternaris.
# SPDX-License-Identifier: Apache-2.0
"""Message definition parser tests."""

import pytest

from rosbags.typesys import TypesysError, get_types_from_idl, get_types_from_msg, register_types
from rosbags.typesys.base import Nodetype
from rosbags.typesys.types import FIELDDEFS

MSG = """
# comment

int32 global=42

std_msgs/Header header
std_msgs/msg/Bool bool
test_msgs/Bar sibling
float64 base
float64[] seq1
float64[] seq2
float64[4] array
"""

MULTI_MSG = """
std_msgs/Header header
byte b
char c
Other[] o

================================================================================
MSG: std_msgs/Header
time time

================================================================================
MSG: test_msgs/Other
uint64[3] Header
"""

IDL_LANG = """
// assign different literals and expressions

#ifndef FOO
#define FOO

#include <global>
#include "local"

const bool g_bool = TRUE;
const int8 g_int1 = 7;
const int8 g_int2 = 07;
const int8 g_int3 = 0x7;
const float64 g_float1 = 1.1;
const float64 g_float2 = 1e10;
const char g_char = 'c';
const string g_string1 = "";
const string<128> g_string2 = "str" "ing";

module Foo {
    const int64 g_expr1 = ~1;
    const int64 g_expr2 = 2 * 4;
};

#endif
"""

IDL = """
// comment in file
module test_msgs {
  // comment in module
  typedef std_msgs::msg::Bool Bool;

  module msg {
    // comment in submodule
    typedef Bool Balias;
    typedef test_msgs::msg::Bar Bar;
    typedef double d4[4];

    @comment(type="text", text="ignore")
    struct Foo {
        std_msgs::msg::Header header;
        Balias bool;
        Bar sibling;
        double x;
        sequence<double> seq1;
        sequence<double, 4> seq2;
        d4 array;
    };
  };
};
"""


def test_parse_msg():
    """Test msg parser."""
    with pytest.raises(TypesysError, match='Could not parse'):
        get_types_from_msg('', 'test_msgs/msg/Foo')
    ret = get_types_from_msg(MSG, 'test_msgs/msg/Foo')
    assert 'test_msgs/msg/Foo' in ret
    fields = ret['test_msgs/msg/Foo']
    assert fields[0][0][1] == 'std_msgs/msg/Header'
    assert fields[0][1][1] == 'header'
    assert fields[1][0][1] == 'std_msgs/msg/Bool'
    assert fields[1][1][1] == 'bool'
    assert fields[2][0][1] == 'test_msgs/msg/Bar'
    assert fields[2][1][1] == 'sibling'
    assert fields[3][0][0] == Nodetype.BASE
    assert fields[4][0][0] == Nodetype.SEQUENCE
    assert fields[5][0][0] == Nodetype.SEQUENCE
    assert fields[6][0][0] == Nodetype.ARRAY


def test_parse_multi_msg():
    """Test multi msg parser."""
    ret = get_types_from_msg(MULTI_MSG, 'test_msgs/msg/Foo')
    assert len(ret) == 3
    assert 'test_msgs/msg/Foo' in ret
    assert 'std_msgs/msg/Header' in ret
    assert 'test_msgs/msg/Other' in ret
    assert ret['test_msgs/msg/Foo'][0][0][1] == 'std_msgs/msg/Header'
    assert ret['test_msgs/msg/Foo'][1][0][1] == 'uint8'
    assert ret['test_msgs/msg/Foo'][2][0][1] == 'uint8'


def test_parse_idl():
    """Test idl parser."""
    ret = get_types_from_idl(IDL_LANG)
    assert ret == {}

    ret = get_types_from_idl(IDL)
    assert 'test_msgs/msg/Foo' in ret
    fields = ret['test_msgs/msg/Foo']
    assert fields[0][0][1] == 'std_msgs/msg/Header'
    assert fields[0][1][1] == 'header'
    assert fields[1][0][1] == 'std_msgs/msg/Bool'
    assert fields[1][1][1] == 'bool'
    assert fields[2][0][1] == 'test_msgs/msg/Bar'
    assert fields[2][1][1] == 'sibling'
    assert fields[3][0][0] == Nodetype.BASE
    assert fields[4][0][0] == Nodetype.SEQUENCE
    assert fields[5][0][0] == Nodetype.SEQUENCE
    assert fields[6][0][0] == Nodetype.ARRAY


def test_register_types():
    """Test type registeration."""
    assert 'foo' not in FIELDDEFS
    register_types({})
    register_types({'foo': [[(1, 'bool'), (2, 'b')]]})
    assert 'foo' in FIELDDEFS

    register_types({'std_msgs/msg/Header': []})
    assert len(FIELDDEFS['std_msgs/msg/Header']) == 2

    with pytest.raises(TypesysError, match='different definition'):
        register_types({'foo': [[(1, 'bool'), (2, 'x')]]})