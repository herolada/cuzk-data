import requests
import time
import zipfile
from urllib.parse import urlencode
from urllib.request import urlretrieve
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from visualize import plot_image


base_url = "https://ags.cuzk.cz/arcgis1/rest/services/ORTOFOTO/MapServer/export"

arg_names = [
"bbox",
"bboxSR",
"layers",
"layerDefs",
"size",
"imageSR",
"historicMoment",
"format",
"transparent",
"dpi",
"time",
"timeRelation",
"layerTimeOptions",
"dynamicLayers",
"gdbVersion",
"mapScale",
"rotation",
"datumTransformations",
"layerParameterValues",
"mapRangeValues",
"layerRangeValues",
"clipping",
"spatialFilter",	
"f"]

arg_vals = [
"-743188,-1044300,-743088,-1044200",
"",
"",
"",
"",
"",
"",
"png",
"false",
"",
"",
"esriTimeRelationOverlaps",
"",
"",
"",
"944.88",
"",
"",
"",
"",
"",
"",
"",
"json",
]

args = dict()
for i in range(len(arg_names)):
    args[arg_names[i]] = arg_vals[i]

encoded_params = urlencode(args)
full_url = f"{base_url}?{encoded_params}"

response = requests.get(full_url)
response = response.json()

png_url = response['href']

png_path = '/home/aherold/katastr/ortofoto.png'

start_t = time.time()
while True: 
    try:
        urlretrieve(png_url, png_path)
        print("T = {} s: Job's done.".format(int(time.time() - start_t)))
        break
    except:
        print("T = {} s: Job's not done yet.".format(int(time.time() - start_t)))
        time.sleep(0.5)

    if time.time() - start_t >= 10:
        raise TimeoutError("Job did not get done in under 10 s. Terminating.")


plot_image(png_path)