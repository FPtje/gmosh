#!/usr/bin/env python3
"""The structure of a GMA file, parsing and building"""

import os
import tempfile
import webbrowser # Useful for opening files
from datetime import datetime
from construct import *
from time import time
from binascii import crc32
from struct import pack
import json

GMA_VERSION = b"\x03"

GMAFile = Struct('all_file_meta',
    ULInt32('file_number'),
    If(lambda ctx: ctx['file_number'] != 0,
        Embed(
            Struct('GMAFileMeta',
                CString('file_name'),
                SLInt64('file_size'),
                ULInt32('file_crc')
            )
        )
    )
)

class FileContents(Adapter):
    def _encode(self, obj, context):
        return b''.join(obj)

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

GMAContents = Struct('GMAContents',
    Magic(b'GMAD'),
    String('format_version', 1),
    SLInt64('steamid'),
    SLInt64('timestamp'),
    CString('required_content'),
    CString('addon_name'),
    CString('addon_description'),
    CString('addon_author'),
    SLInt32('addon_version'),
    # For each file get the metadata
    RepeatUntil(lambda obj, ctx: obj['file_number'] == 0, GMAFile),
    OnDemand(FileContents(Field('all_file_contents', file_content_size))),
)

GMAVerifiedContents = Struct('GMAVerifiedContents',
    Embed(GMAContents),
    Optional(ULInt32('addon_crc')),
    Optional(ULInt8("MagicValue"))
    # Don't enforce terminator. Some GMA files appear to have 0-padding after the magic value
    # Terminator
)

def build_gma(addon, file_list, addon_path='.'):
    file_meta = []
    file_contents = []

    for i in range(0, len(file_list)):
        file_path = os.path.join(addon_path, file_list[i])

        with open(file_path, 'rb') as f:
            contents = f.read()

            file_meta.append(Container(
                file_name = bytes(file_list[i], 'utf-8'),
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
    container.required_content = b''
    container.addon_name = bytes(addon.gettitle(), 'utf-8')
    container.addon_description = bytes(addon.get_description_json(), 'utf-8')
    container.addon_author = bytes(addon.getauthor(), 'utf-8')
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
    destination = extension and destination_path or os.path.join(destination_path, 'out.gma')

    # Force .gma extension
    destination = os.path.splitext(destination)[0] + '.gma'

    with open(destination, 'wb') as file:
        file.write(gma)
        file.write(pack('I', crc))

def extract(file_path, destination_path, fil = set()):
    with open(file_path, 'rb') as file:
        gma = GMAVerifiedContents.parse_stream(file)

        for i in range(0, len(gma.all_file_meta) - 1):
            meta = gma.all_file_meta[i]
            gma_file_name = meta.file_name.decode('utf-8')

            # Discontinue extracting this file if it's not in the filter
            if fil:
                for prefix in fil:
                    if gma_file_name.startswith(prefix):

                        # Remove prefix, so it won't create all subfolders
                        strip, _ = os.path.split(prefix)
                        if not strip: break

                        gma_file_name = gma_file_name[len(strip) + 1:]
                        break
                else:
                    continue

            file_name = os.path.join(destination_path, gma_file_name)
            file_folder = os.path.dirname(file_name)

            if not os.path.exists(file_folder):
                os.makedirs(file_folder)

            print(file_name)

            with open(file_name, 'wb') as output:
                output.write(gma.all_file_contents.value[i])

def openFiles(gma_path, fil):
    with open(gma_path, 'rb') as file:
        gma = GMAVerifiedContents.parse_stream(file)

        for i in range(0, len(gma.all_file_meta) - 1):
            meta = gma.all_file_meta[i]
            gma_file_name = meta.file_name.decode('utf-8')
            for prefix in fil:
                    if gma_file_name.startswith(prefix): break
            else:
                continue

            _, filename = os.path.split(gma_file_name)

            print('Extracting "%s"' % filename)

            prefix, extension = os.path.splitext(filename)
            # Don't delete, otherwise it'll be deleted before it gets opened
            with tempfile.NamedTemporaryFile(prefix = prefix, suffix = extension, delete = False) as output:
                output.write(gma.all_file_contents.value[i])
                webbrowser.open(output.name)

def getfiles(file_path):
    """Get the list of files that exist in the GMA file"""
    with open(file_path, 'rb') as file:
        gma = GMAVerifiedContents.parse_stream(file)

    res = []
    for i in range(0, len(gma.all_file_meta) - 1):
        res.append(gma.all_file_meta[i].file_name.decode('utf-8'))

    return res

gmaStr = """crc                   = {crc}
Magic value           = {magic}
format version        = {format_version!r}
Steam ID              = {steamid}
Time created          = {timestamp}
required content      = "{required_content}"
addon name            = "{addon_name}"
addon description     = "{addon_description}"
addon author          = "{addon_author}"
addon version         = {addon_version}

Files: {files}
"""

filemetaStr = "{name} ({size}, crc: {crc})"

def sizeof_simple(num):
    n = num
    if num < 1024: return "%.0f bytes" % num

    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%.0f %s" % (num, x)
        num /= 1024.0
    return "%.0f %s" % (num, 'TB')

def sizeof_fmt(num):
    if num < 1024: return "%.0f bytes" % num

    size = sizeof_simple(num)

    return "%s, %s bytes" % (size, num)

def dump(file_path):
    with open(file_path, 'rb', 0) as file:
        gma = GMAVerifiedContents.parse_stream(file)

        files = []

        for filemeta in gma.all_file_meta:
            if filemeta.file_number == 0: break

            files.append(filemetaStr.format(
                name = filemeta.file_name.decode('utf-8'),
                size = sizeof_fmt(filemeta.file_size),
                crc  = filemeta.file_crc
            ))

        return gmaStr.format(
            crc                 = gma.addon_crc,
            magic               = gma.MagicValue,
            format_version      = gma.format_version.decode('utf-8'),
            steamid             = gma.steamid,
            timestamp           = datetime.fromtimestamp(int(gma.timestamp)).strftime('%Y-%m-%d %H:%M:%S'),
            required_content    = gma.required_content.decode('utf-8'),
            addon_name          = gma.addon_name.decode('utf-8'),
            addon_description   = gma.addon_description.decode('utf-8'),
            addon_author        = gma.addon_author.decode('utf-8'),
            addon_version       = gma.addon_version,
            files               = "\n".join(files)
            )

def gmaInfo(file_path):
    res = dict()
    with open(file_path, 'rb', 0) as file:
        gma = GMAVerifiedContents.parse_stream(file)

        res['files']               = []
        res['crc']                 = gma.addon_crc
        res['magic']               = gma.MagicValue
        res['format_version']      = gma.format_version.decode('utf-8')
        res['steamid']             = gma.steamid
        res['timestamp']           = int(gma.timestamp)
        res['required_content']    = gma.required_content.decode('utf-8')
        res['addon_name']          = gma.addon_name.decode('utf-8')
        res['addon_description']   = gma.addon_description.decode('utf-8')
        res['addon_author']        = gma.addon_author.decode('utf-8')
        res['addon_version']       = gma.addon_version

        try:
            data = json.loads(res['addon_description'])
            res['description'] = data['description']
            res['tags'] = data['tags']
            res['type'] = data['type']
        except Exception: pass

        for filemeta in gma.all_file_meta:
            if filemeta.file_number == 0: break

            res['files'].append({
                'name': filemeta.file_name.decode('utf-8'),
                'size': sizeof_fmt(filemeta.file_size),
                'puresize': filemeta.file_size,
                'crc':  filemeta.file_crc
            })

        return res

