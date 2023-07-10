#!/usr/bin/env python3
"""Utilities related to interacting with the steam workshop"""

import http.client
import json
import lzma
import os
import re
import sys
import urllib.request

import gmafile


def workshopinfo(addons):
    url = "http://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1"
    connection = http.client.HTTPConnection("api.steampowered.com")
    addonStr = []

    for i in range(len(addons)):
        addonStr.insert(i, "publishedfileids[%i]=%s" % (i, addons[i]))

    connection.request(
        "POST",
        url,
        body="itemcount=%i&%s" % (len(addons), "&".join(addonStr)),
        headers={"Content-type": "application/x-www-form-urlencoded"},
    )

    response = connection.getresponse()

    if response.status < 200 or response.status > 300:
        print("Error getting addon info! %s" % response.reason)
        return

    return json.loads(response.read().decode("utf-8"))["response"][
        "publishedfiledetails"
    ]


def download(addons, path, extr):
    info = workshopinfo(addons)
    for res in info:
        if not "title" in res:
            print("Addon does not exist!")
            return

        if not "file_url" in res or res["file_url"] == "":
            print("Steam did not provide a direct download URL!")
            return

        name = res["title"]
        download_url = res["file_url"]

        print("Downloading '%s' from the workshop" % name)

        lzmafile = os.path.join(path, "%s.gma.lzma" % res["publishedfileid"])
        outfile = os.path.join(path, "%s.gma" % res["publishedfileid"])

        urllib.request.urlretrieve(
            download_url,
            lzmafile,
            lambda x, y, z: sys.stdout.write("\r{0:.2f}%".format(x * y / z * 100)),
        )
        sys.stdout.write("\r100.00%\n")

        print(f"Downloaded '{name}' from the workshop. Decompressing...")
        with lzma.open(lzmafile) as lzmaF:
            with open(outfile, "wb") as gma:
                gma.write(lzmaF.read())

        os.remove(lzmafile)

        if not extr:
            return

        name = os.path.join(path, re.sub('[\\/:"*?<>|]+', "_", name))
        gmafile.extract(outfile, name)
