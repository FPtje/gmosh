#!/usr/bin/env python3
"""The structure of a GMA file, parsing and building"""

import os
import sys
import tempfile
import webbrowser # Useful for opening files
import subprocess
from datetime import datetime
from construct import *
from time import time
from binascii import crc32
from struct import pack
import json

GMA_VERSION = u"\x03"

GMAFile = 'all_file_meta'/Struct(
    'file_number'/Int32ul,
    'data'/IfThenElse(this.file_number != 0,
        'data'/Struct(
            'file_name'/CString("utf8"),
            'file_size'/Int64sl,
            'file_crc'/Int32ul
        ),
        Pass
    )
)

class FileContents(Adapter):
    def _encode(self, obj, context, path):
        return b''.join(obj)

    def _decode(self, obj, context, path):
        contents = []
        begin = 0
        for filemeta in context.data.all_file_meta:
            # ignore the dummy file with file number 0
            if filemeta.file_number == 0:
                break

            size = filemeta.data.file_size
            contents.append(obj[begin:begin + size])
            begin += size

        return contents

def file_content_size(context):
    total = 0
    for filemeta in context.all_file_meta:
        if filemeta.file_number == 0:
            return total

        total += filemeta.data.file_size

GMAContents = 'content'/Struct(
    'signature'/Const(b'GMAD'),
    'format_version'/PaddedString(1, "utf8"),
    'steamid'/Int64sl,
    'timestamp'/Int64sl,
    'required_content'/CString("utf8"),
    'addon_name'/CString("utf8"),
    'addon_description'/CString("utf8"),
    'addon_author'/CString("utf8"),
    'addon_version'/Int32sl,
    # For each file get the metadata
    'all_file_meta'/RepeatUntil(lambda x,lst,ctx: x['file_number'] == 0, GMAFile),
    'all_file_contents'/Lazy(FileContents(Bytes(file_content_size)))
)

GMAVerifiedContents = 'GMAVerifiedContents'/Struct(
    GMAContents,
    Optional('addon_crc'/Int32ul),
    Optional("MagicValue"/Int8ul)
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
            containeredData = Container(
                file_number = i + 1,
                data = Container(
                    file_name = file_list[i],
                    file_crc = crc32(contents) & 0xffffffff,
                    file_size = len(contents)
                )
            )
            file_meta.append(containeredData)
            file_contents.append(contents)

    # Dummy end file
    file_meta.append(Container(file_number = 0, data=Container()))

    container = Container()
    container.format_version = GMA_VERSION
    container.steamid = addon.getsteamid()
    container.timestamp = int(time())
    container.required_content = u''
    container.addon_name = addon.gettitle()
    container.addon_description = addon.get_description_json()
    container.addon_author = addon.getauthor()
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
            gma_file_name = meta.data.file_name

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

        for i in range(0, len(gma.content.all_file_meta) - 1):
            meta = gma.content.all_file_meta[i]
            gma_file_name = meta.data.file_name
            for prefix in fil:
                    if gma_file_name.startswith(prefix): break
            else:
                continue

            _, filename = os.path.split(gma_file_name)

            print('Extracting "%s"' % filename)

            prefix, extension = os.path.splitext(filename)
            # Don't delete, otherwise it'll be deleted before it gets opened
            with tempfile.NamedTemporaryFile(prefix = prefix, suffix = extension, delete = False) as output:
                output.write(gma.content.all_file_contents.value[i])
                if sys.platform == "darwin":
                    subprocess.call(['open', output.name])
                else:
                    webbrowser.open(output.name)

def getfiles(file_path):
    """Get the list of files that exist in the GMA file"""
    with open(file_path, 'rb') as file:
        gma = GMAVerifiedContents.parse_stream(file)

    res = []
    for i in range(0, len(gma.content.all_file_meta) - 1):
        res.append(gma.content.all_file_meta[i].data.file_name)

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

        for filemeta in gma.content.all_file_meta:
            if filemeta.file_number == 0: break

            files.append(filemetaStr.format(
                name = filemeta.data.file_name,
                size = sizeof_fmt(filemeta.data.file_size),
                crc  = filemeta.data.file_crc
            ))

        return gmaStr.format(
            crc                 = gma.addon_crc,
            magic               = gma.MagicValue,
            format_version      = gma.content.format_version,
            steamid             = gma.content.steamid,
            timestamp           = datetime.fromtimestamp(int(gma.content.timestamp)).strftime('%Y-%m-%d %H:%M:%S'),
            required_content    = gma.content.required_content,
            addon_name          = gma.content.addon_name,
            addon_description   = gma.content.addon_description,
            addon_author        = gma.content.addon_author,
            addon_version       = gma.content.addon_version,
            files               = "\n".join(files)
            )

def gmaInfo(file_path):
    res = dict()
    with open(file_path, 'rb', 0) as file:
        gma = GMAVerifiedContents.parse_stream(file)

        res['files']               = []
        res['crc']                 = gma.addon_crc
        res['magic']               = gma.MagicValue
        res['format_version']      = gma.content.format_version
        res['steamid']             = gma.content.steamid
        res['timestamp']           = int(gma.content.timestamp)
        res['required_content']    = gma.content.required_content
        res['addon_name']          = gma.content.addon_name
        res['addon_description']   = gma.content.addon_description
        res['addon_author']        = gma.content.addon_author
        res['addon_version']       = gma.content.addon_version

        try:
            data = json.loads(res['addon_description'])
            res['description'] = data['description']
            res['tags'] = data['tags']
            res['type'] = data['type']
        except Exception: pass

        for filemeta in gma.all_file_meta:
            if filemeta.file_number == 0: break

            res['files'].append({
                'name': filemeta.data.file_name,
                'size': sizeof_fmt(filemeta.data.file_size),
                'puresize': filemeta.data.file_size,
                'crc':  filemeta.data.file_crc
            })

        return res

