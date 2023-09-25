import os
from datetime import datetime, time, date
from dataclasses import dataclass, field
from collections import defaultdict, namedtuple

def _util_gen_elements(fields, names):
    results = []
    name_index = 0
    for field in fields:
        part_a, part_b, *_ = field
        if part_a is None:
            results.append(tuple([None, part_b]))
        else:
            results.append(tuple([names[name_index], part_a]))
            name_index += 1
    return results

_ElementTypes = namedtuple(
    "_ElementTypes",
    [
        # These are the canonical names of low-level element types:
        "c8",
        "i8",
        "u8",  # 3 int types of 1 byte
        "i16",
        "u16",  # 2 int types of 2 bytes
        "i32",
        "u32",  # 2 int types of 4 bytes
        "i64",
        "u64",  # 2 int types of 8 bytes
        "f32",  # 1 float type of 4 bytes
        "f64",  # 1 float type of 4 bytes
    ],
)
elemT = _ElementTypes(**dict(zip(_ElementTypes._fields, _ElementTypes._fields)))

def elemD_(name: str, fmt: str, count=1):
    return (name, (fmt, count))

map_size_to_fmt = dict(
    (
        (elemT.c8, ("c", "B", 1)),
        (elemT.i8, ("b", "b", 1)),
        (elemT.u8, ("B", "u1", 1)),
        (elemT.i16, ("h", "i2", 2)),
        (elemT.u16, ("H", "u2", 2)),
        (elemT.i32, ("i", "i4", 4)),
        (elemT.u32, ("I", "u4", 4)),
        (elemT.i64, ("q", "i8", 8)),
        (elemT.u64, ("Q", "u8", 8)),
        (elemT.f32, ("f", "f4", 4)),
        (elemT.f64, ("d", "f8", 8)),
    )
)

# _byte_order_fmt = "<" # Little Endian
_byte_order_fmt = ">" # Big Endian

class ASDXMLHeader:
    
    def __init__(self):
        pass

class ASDDataBlock:
    
    def __init__(self):
        pass
    
    
    