import glob
import os
import urllib.request
import re
from bs4 import BeautifulSoup
import zipfile
from tqdm import tqdm

import cycle
import projection


def is_in(area, lon, lat):
    x_u, y_u, x_l, y_l = area
    if lat <= y_u and lat >= y_l and lon >= x_u and lon <= x_l:
        return True
    return False


def list_crawl(url, match):
    charts = []
    html_page = urllib.request.urlopen(url)
    soup = BeautifulSoup(html_page, "html.parser")
    for link in tqdm(soup.findAll('a'), desc="Scanning website links"):
        link_x = link.get('href')
        if link_x is None:
            continue
        if re.search(match, link_x):
            charts.append(link_x)
    list_set = set(charts)  # unique
    return list(list_set)


def download(url):
    name = url.split("/")[-1]
    # check if exists
    if not os.path.isfile(name):
        urllib.request.urlretrieve(url, name)
    if name.endswith(".zip"):  # if a zipfile, unzip first
        with zipfile.ZipFile(name, 'r') as zip_ref:
            zip_ref.extractall(".")


def download_list(charts):
    for cc in tqdm(range(len(charts)), desc="Downloading/unzipping"):
        download(charts[cc])


def make_main_vrt(name, vrt_list):
    try:
        os.remove(name + ".vrt")
    except FileNotFoundError as e:
        pass

    all_vrts = "".join([" '" + vrt + "' " for vrt in vrt_list])
    os.system("gdalbuildvrt -r cubicspline -srcnodata 51 -vrtnodata 51 -resolution highest -overwrite " + name + ".vrt " + all_vrts)


def make_vrt(name):
    no_extension_name = name.split(".")[0]
    try:
        os.remove(no_extension_name + ".vrt")
        os.remove(no_extension_name + "rgb.vrt")
    except FileNotFoundError as e:
        pass

    os.system("gdal_translate -of vrt -r cubicspline -expand rgb '" + name + "' '" + no_extension_name + "rgb.vrt'")
    os.system(
        "gdalwarp -of vrt -r cubicspline -dstnodata 51 -t_srs 'EPSG:3857' -cutline '" + no_extension_name + ".geojson' " + "-crop_to_cutline '" + no_extension_name + "rgb.vrt' '" + no_extension_name + ".vrt'")

    return no_extension_name + ".vrt"


def make_vrt_list(charts):
    ret = []
    for cc in tqdm(range(len(charts)), desc="Making VRT files"):
        ret.append(make_vrt(charts[cc]))
    return ret


def get_files(match):
    return glob.glob(match)


def zip_files(list_of_all_tiles, chart):
    # US geo regions

    try:
        os.remove("NW_" + chart + ".zip")
        os.remove("SW_" + chart + ".zip")
        os.remove("NC_" + chart + ".zip")
        os.remove("SC_" + chart + ".zip")
        os.remove("NE_" + chart + ".zip")
        os.remove("SE_" + chart + ".zip")
        os.remove("NW_" + chart)
        os.remove("SW_" + chart)
        os.remove("NC_" + chart)
        os.remove("SC_" + chart)
        os.remove("NE_" + chart)
        os.remove("SE_" + chart)
    except FileNotFoundError as e:
        pass

    nw_file = zipfile.ZipFile("NW_" + chart + ".zip", "w")
    sw_file = zipfile.ZipFile("SW_" + chart + ".zip", "w")
    nc_file = zipfile.ZipFile("NC_" + chart + ".zip", "w")
    sc_file = zipfile.ZipFile("SC_" + chart + ".zip", "w")
    ne_file = zipfile.ZipFile("NE_" + chart + ".zip", "w")
    se_file = zipfile.ZipFile("SE_" + chart + ".zip", "w")
    nw_file_manifest = open("NW_" + chart, "w+")
    sw_file_manifest = open("SW_" + chart, "w+")
    nc_file_manifest = open("NC_" + chart, "w+")
    sc_file_manifest = open("SC_" + chart, "w+")
    ne_file_manifest = open("NE_" + chart, "w+")
    se_file_manifest = open("SE_" + chart, "w+")

    nw_file_manifest.write(cycle.get_cycle() + "\n")
    sw_file_manifest.write(cycle.get_cycle() + "\n")
    nc_file_manifest.write(cycle.get_cycle() + "\n")
    sc_file_manifest.write(cycle.get_cycle() + "\n")
    ne_file_manifest.write(cycle.get_cycle() + "\n")
    se_file_manifest.write(cycle.get_cycle() + "\n")

    nw = (-125, 50, -105, 40)
    sw = (-125, 40, -105, 20)
    nc = (-105, 50, -80,  40)
    sc = (-105, 40, -80,  20)
    ne = (-80,  50, -60,  40)
    se = (-80,  40, -60,  20)

    for tile in tqdm(list_of_all_tiles, desc="Zipping up tiles in Areas"):
        tokens = tile.split("/")
        y_tile = int(tokens[len(tokens) - 1].split(".")[0])
        x_tile = int(tokens[len(tokens) - 2])
        z_tile = int(tokens[len(tokens) - 3])
        lon_tile, lat_tile, lon1_tile, lat1_tile = projection.findBounds(x_tile, y_tile, z_tile)
        # include 7 and below in every chart
        if is_in(nw, lon_tile, lat_tile) or z_tile <= 7:
            nw_file.write(tile)
            nw_file_manifest.write(tile + "\n")
        if is_in(sw, lon_tile, lat_tile) or z_tile <= 7:
            sw_file.write(tile)
            sw_file_manifest.write(tile + "\n")
        if is_in(nc, lon_tile, lat_tile) or z_tile <= 7:
            nc_file.write(tile)
            nc_file_manifest.write(tile + "\n")
        if is_in(sc, lon_tile, lat_tile) or z_tile <= 7:
            sc_file.write(tile)
            sc_file_manifest.write(tile + "\n")
        if is_in(ne, lon_tile, lat_tile) or z_tile <= 7:
            ne_file.write(tile)
            ne_file_manifest.write(tile + "\n")
        if is_in(se, lon_tile, lat_tile) or z_tile <= 7:
            se_file.write(tile)
            se_file_manifest.write(tile + "\n")

    nw_file_manifest.close()
    sw_file_manifest.close()
    nc_file_manifest.close()
    sc_file_manifest.close()
    ne_file_manifest.close()
    se_file_manifest.close()

    # write manifest
    nw_file.write("NW_" + chart)
    sw_file.write("SW_" + chart)
    nc_file.write("NC_" + chart)
    sc_file.write("SC_" + chart)
    ne_file.write("NE_" + chart)
    se_file.write("SE_" + chart)

    nw_file.close()
    sw_file.close()
    nc_file.close()
    sc_file.close()
    ne_file.close()
    se_file.close()


def make_tiles(name, index, max_zoom):
    os.system("rm -rf tiles/" + index)
    os.system("gdal2tiles.py -t " + name + " --tilesize=512 --tiledriver=WEBP --webp-quality=60 --exclude --webviewer=all -c MUAVLLC --no-kml --resume --processes 8 -z 0-" + max_zoom + " -r near " + name + ".vrt tiles/" + index)