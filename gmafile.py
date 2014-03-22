#!/usr/bin/env python3
"""The structure of a GMA file, parsing and building"""

import os
from construct import *
from time import time
from binascii import crc32
from struct import pack

GMA_VERSION = "\x03"

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
        return b"".join(obj)

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

)

GMAVerifiedContents = Struct("GMAVerifiedContents",
    Embed(GMAContents),
    Optional(ULInt32("addon_crc")),
    Terminator
)

def build_gma(addon, file_list, addon_path='.'):
    file_meta = []
    file_contents = []

    for i in range(0, len(file_list)):
        file_path = os.path.join(addon_path, file_list[i])

        with open(file_path, 'rb') as f:
            contents = f.read()

            file_meta.append(Container(
                file_name = file_list[i],
                file_number = i + 1,
                file_crc = crc32(contents) & 0xffffffff,
                file_size = len(contents)
            ))

            file_contents.append(contents)

    # Dummy end file
    file_meta.append(Container(file_number = 0))

    container = Container()
    container.format_version = GMA_VERSION
    container.steamid = addon.getsteamid()
    container.timestamp = int(time())
    container.required_content = ""
    container.addon_name = addon.gettitle()
    container.addon_description = addon.get_description_json()
    container.addon_author = addon.getauthor()
    container.addon_version = addon.getversion()
    container.GMAFile = file_meta
    container.all_file_contents = file_contents

    return GMAContents.build(container)

def write(addon, destination_path='.'):
    file_list = addon.getfiles()
    addon_path = addon.getpath()
    gma = build_gma(addon, file_list, addon_path)
    crc = crc32(gma)

    destination = os.path.isfile(destination_path) and destination_path or os.path.join(destination_path, "out.gma")

    # Force .gma extension
    destination = os.path.splitext(destination)[0] + ".gma"

    with open(destination, 'wb+') as file:
        file.write(gma)
        file.write(pack('i', crc))


def extract(file_path, destination_path):
    pass
