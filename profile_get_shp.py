import requests
import time
import zipfile
from urllib.parse import urlencode
from urllib.request import urlretrieve

from shp_visualize import line_visualize


base_url = "https://ags.cuzk.cz/arcgis2/rest/services/Profile_DMR5G/GPServer/ProfileDMR5G/submitJob"
base_url_job = "https://ags.cuzk.cz/arcgis2/rest/services/Profile_DMR5G/GPServer/ProfileDMR5G/jobs"

arg_names = ["VstupniLinie","JakyProfil","SampleDistance","env:outSR","env:processSR","returnZ",
             "returnM","returnTrueCurves","context","f"]
arg_vals = ["""{
    "displayFieldName": "",
    "geometryType": "esriGeometryPolyline",
    "spatialReference": {
    "wkid": 102067,
    "latestWkid": 5514
    },
    "fields": [
    {
    "name": "OBJECTID",
    "type": "esriFieldTypeOID",
    "alias": "OBJECTID"
    },
    {
    "name": "SHAPE_Length",
    "type": "esriFieldTypeDouble",
    "alias": "SHAPE_Length"
    }
    ],
    "features": [{"geometry": {
    "paths": [[
        [
        -743208,
        -1044206
        ],
        [
        -743458,
        -1044206
        ],
        [
        -743458,
        -1044456
        ],
        [
        -743208,
        -1044456
        ],
        [
        -743208,
        -1044206
        ]
    ]],
    "spatialReference": {"wkid": 102067}
    }}],
    "exceededTransferLimit": false
    }""",
    
    "Profil", #Profil + stoupání a klesání

    "null","","","true","false","false","","json"
]

args = dict()
for i in range(len(arg_names)):
    args[arg_names[i]] = arg_vals[i]

encoded_params = urlencode(args)
full_url = f"{base_url}?{encoded_params}"

response = requests.get(full_url)
response = response.json()

job_id = response['jobId']

url_zip = "http://ags.cuzk.cz/arcgis2/rest/directories/arcgisjobs/profile_dmr5g_gpserver/{}/scratch/VysledekLinieSHP.zip".format(job_id)


start_t = time.time()
while True: 
    try:
        urlretrieve(url_zip, "/home/aherold/katastr/result.zip")
        print("T = {} s: Job's done.".format(int(time.time() - start_t)))
        break
    except:
        print("T = {} s: Job's not done yet.".format(int(time.time() - start_t)))
        time.sleep(5)

    if time.time() - start_t >= 300:
        print("Job did not get done in under 300 s. Terminating.")


with zipfile.ZipFile("result.zip", 'r') as zip_ref:
    zip_ref.extract("vystupProfileLine.shp","/home/aherold/katastr")


shp_file_path = '/home/aherold/katastr/vystupProfileLine.shp'

print("Resulting SHP file is located at {}.".format(shp_file_path))

line_visualize(shp_file_path)