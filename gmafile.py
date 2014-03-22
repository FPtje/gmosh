#!/usr/bin/env python3
"""The structure of a GMA file, parsing and building"""

from construct import *

GMAFile = Struct("GMAFile",
    ULInt32("file_number"),
    If(lambda ctx: ctx["file_number"] != 0,
        Embed(
            Struct("GMAFileMeta",
                CString("file_name"),
                SLInt64("file_size"),
                ULInt32("file_crc")
            )
        )
    )
)

class FileContents(Adapter):
    def _encode(self, obj, context):
        return "".join(obj)

    def _decode(self, obj, context):
        contents = []
        begin = 0
        for filemeta in context.GMAFile:
            # ignore the dummy file with file number 0
            if filemeta.file_number == 0:
                break

            size = filemeta.file_size
            contents.append(obj[begin:begin + size])
            begin += size

        return contents

def file_content_size(context):
    total = 0
    for filemeta in context.GMAFile:
        if filemeta.file_number == 0:
            return total

        total += filemeta.file_size

GMAContents = Struct("GMAContents",
    Magic(b"GMAD"),
    String("format_version", 1),
    SLInt64("steamid"),
    SLInt64("timestamp"),
    CString("required_content"),
    CString("addon_name"),
    CString("addon_description"),
    CString("addon_author"),
    SLInt32("addon_version"),
    # For each file get the metadata
    RepeatUntil(lambda obj, ctx: obj["file_number"] == 0, GMAFile),
    OnDemand(FileContents(Field("all_file_contents", file_content_size))),
    ULInt32("addon_crc")
)

# gmafile = open("test.gma", "rb")

# contents = gmafile.read()
# parsed = GMAContents.parse(contents)
# rebuilt = GMAContents.build(parsed)
# reparsed = GMAContents.parse(rebuilt)
# reparsed.all_file_contents.value
# print(parsed.all_file_contents.has_value)
# print(parsed)