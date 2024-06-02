import common
import glob

import cycle


# Chart specific code

# download add second entry for grand canyon charts
start_date = cycle.get_version_start(cycle.get_cycle_download())  # to download which cycle
all_charts = common.list_crawl("https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/vfr/", "^http.*" + start_date + "/heli_files/.*.zip$")
all_charts_2 = common.list_crawl("https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/vfr/", "^http.*" + start_date + "/grand_canyon_files/.*.zip$")
for nn in all_charts_2:
    all_charts.append(nn)
common.download_list(all_charts)
all_files = common.get_files("*HEL.tif")
all_files_2 = common.get_files("Grand Canyon*.tif")
for nn in all_files_2:
    all_files.append(nn)
# exclude these
all_files.remove("Dallas-Love Inset HEL.tif")
all_files.remove("Chicago O'Hare Inset HEL.tif")
all_files.remove("Boston Downtown HEL.tif")
all_files.remove("Washington Inset HEL.tif")
all_files.remove("Downtown Manhattan HEL.tif")
all_files.remove("Grand Canyon Air Tour Operators.tif")
# make tiles
vrts = common.make_vrt_list(all_files, "HEL")
common.make_main_vrt(vrts, "HEL")
common.make_tiles("9", "12", "HEL")

# zip
all_tiles = glob.glob("tiles/9/**/*.webp", recursive=True)
common.zip_files(all_tiles, "HEL")
