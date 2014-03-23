#!/usr/bin/env python3
"""The structure of a GMA file, parsing and building"""

import os
from construct import *
from time import time
from binascii import crc32
from struct import pack

GMA_VERSION = b"\x03"

GMAFile = Struct("all_file_meta",
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
        for filemeta in context.all_file_meta:
            # ignore the dummy file with file number 0
            if filemeta.file_number == 0:
                break

            size = filemeta.file_size
            contents.append(obj[begin:begin + size])
            begin += size

        return contents

def file_content_size(context):
    total = 0
    for filemeta in context.all_file_meta:
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
                file_name = bytes(file_list[i], "utf-8"),
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
    container.required_content = b""
    container.addon_name = bytes(addon.gettitle(), "utf-8")
    container.addon_description = bytes(addon.get_description_json(), "utf-8")
    container.addon_author = bytes(addon.getauthor(), "utf-8")
    container.addon_version = addon.getversion()
    container.all_file_meta = file_meta
    container.all_file_contents = file_contents

    return GMAContents.build(container)

def write(addon, destination_path='.'):
    file_list = addon.getfiles()
    addon_path = addon.getpath()
    gma = build_gma(addon, file_list, addon_path)
    crc = crc32(gma)

    file_name, extension = os.path.splitext(destination_path)
    destination = extension and destination_path or os.path.join(destination_path, "out.gma")

    # Force .gma extension
    destination = os.path.splitext(destination)[0] + ".gma"

    with open(destination, 'wb') as file:
        file.write(gma)
        file.write(pack('I', crc))

def extract(file_path, destination_path):
    with open(file_path, 'rb') as file:
        contents = file.read()
        gma = GMAVerifiedContents.parse(contents)

        for i in range(0, len(gma.all_file_meta) - 1):
            meta = gma.all_file_meta[i]
            file_name = os.path.join(destination_path, meta.file_name.decode("utf-8"))
            file_folder = os.path.dirname(file_name)

            if not os.path.exists(file_folder):
                os.makedirs(file_folder)

            print("Extracting %s..." % file_name)

            with open(file_name, 'wb') as output:
                output.write(gma.all_file_contents.value[i])

