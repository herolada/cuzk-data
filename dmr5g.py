import urllib.request
import xml.etree.ElementTree as ET
from shapely import Polygon, MultiPolygon, Point
from rtree import index
from urllib.request import urlretrieve
import zipfile
import pylas
import matplotlib.pyplot as plt
import pyproj
import numpy as np

SJTSK = "EPSG:5514"
WGS = "EPSG:4326"
WGS_TO_SJTSK = pyproj.Transformer.from_crs(WGS,SJTSK)

class PointOutOfTileError(Exception):
    pass


class Dmr5gParser():
    def __init__(self) -> None:
        self.url = "https://atom.cuzk.cz/DMR5G-SJTSK/DMR5G-SJTSK.xml"   # URL of the XML file
        
        self.response, self.xml_data = self.open_url(self.url)

        self.namespace = {
            'atom': 'http://www.w3.org/2005/Atom',  # Replace with the appropriate namespace URI
            'georss': 'http://www.georss.org/georss'
        }

        self.root = ET.fromstring(self.xml_data)

        self.n = len(self.root.findall(f"{{{self.namespace['atom']}}}entry"))

        self.tile_idx, self.tile_polygons = self.get_tiles()


    def open_url(self, url):
        response = urllib.request.urlopen(url)
        xml_data = response.read().decode('utf-8')
        
        return response, xml_data

    def get_tiles(self):
        polygons = [((0.,0.),(0.,0.),(0.,0.),(0.,0.),(0.,0.))] * self.n
        i = 0

        idx = index.Index()

        # Access elements and extract data
        for entry in self.root.iter(f"{{{self.namespace['atom']}}}entry"):
            
            polygon = entry.find(f"{{{self.namespace['georss']}}}polygon")

            # Split the string by spaces to get individual float values
            float_list = polygon.text.split()

            # Convert the list of strings to a list of floats
            float_list = [float(value) for value in float_list]

            # Create a tuple of pairs of floats
            pairs = tuple((float_list[i], float_list[i + 1]) for i in range(0, len(float_list), 2))

            polygons[i] = pairs
            
            left, bottom, right, top = (float_list[1], float_list[0], float_list[3], float_list[4])
            idx.insert(i, (left, bottom, right, top))

            i += 1

        return idx,polygons
    
    def get_intersection_tile_ids(self, point):
        tile_ids = list(dmr5g.tile_idx.intersection(point))
        return tile_ids
    
    def get_tile_by_id(self, id):
        if id >= self.n:
            raise IndexError("id {} out of bounds of polygons list of len {}".format(id, self.n))

        return self.tile_polygons[id]
    
    def fix_tile_coords(self,tile):
        x,y = np.array(tile.exterior.coords.xy)
        
        x_fixed = np.copy(x)
        y_fixed = np.copy(y)

        x_mask = x%2500 < 1250
        
        x_fixed[x_mask] -= (x%2500)[x_mask]
        x_fixed[~x_mask] += 2500-(x%2500)[~x_mask]

        y_mask = y%2000 < 1000
        
        y_fixed[y_mask] -= (y%2000)[y_mask]
        y_fixed[~y_mask] += 2000-(y%2000)[~y_mask]

        return Polygon(zip(x_fixed,y_fixed))
    
    def get_tile_by_point(self,point):
        ids = self.get_intersection_tile_ids(point)

        point_sjtsk = Point(WGS_TO_SJTSK.transform(point[1], point[0]))


        if len(ids) > 1:
            for id in ids:
                tile = self.get_tile_by_id(id)
                tile_sjtsk = Polygon(np.array(WGS_TO_SJTSK.transform(np.array(tile)[:,0], np.array(tile)[:,1])).T)
                tile_sjtsk_fixed = self.fix_tile_coords(tile_sjtsk)
                
                if tile_sjtsk_fixed.contains(point_sjtsk):
                    return tile,id
                else:
                    pass

            raise PointOutOfTileError("None of selected tiles contains the point.")
            
        else:
            id = ids[0]
            tile = self.get_tile_by_id(id)
            tile_sjtsk = Polygon(np.array(WGS_TO_SJTSK.transform(np.array(tile)[:,0], np.array(tile)[:,1])).T)
            tile_sjtsk_fixed = self.fix_tile_coords(tile_sjtsk)
            
            if not tile_sjtsk_fixed.contains(point_sjtsk):
                raise PointOutOfTileError("Only one tile selected and it is not containing point.")
            else:
                return tile,id

    
    def get_tile_url_by_id(self,id):
        for i,entry in enumerate(self.root.iter(f"{{{self.namespace['atom']}}}entry")):
            if i == id:
                tile_url = entry.find(f"{{{self.namespace['atom']}}}id").text
                return tile_url
            
    def get_zip_url_by_id(self,id):
        tile_url = self.get_tile_url_by_id(id)
        response, tile_xml_data = self.open_url(tile_url)
        tile_root = ET.fromstring(tile_xml_data)
        entry = tile_root.find(f"{{{self.namespace['atom']}}}entry")
        zip_url = entry.find(f"{{{self.namespace['atom']}}}id").text
        
        return zip_url

    def download_tile_by_point(self,point):
        tile,id = self.get_tile_by_point(point)
        #d = self.get_intersection_tile_ids(point)
        zip_url = self.get_zip_url_by_id(id)

        urlretrieve(zip_url, "/home/aherold/katastr/tile.zip")
        
        with zipfile.ZipFile("/home/aherold/katastr/tile.zip", 'r') as zip_ref:
            file_name = zip_ref.namelist()[0]
            dir_name = "/home/aherold/katastr"
            zip_ref.extract(file_name,dir_name)

        return dir_name + '/' + file_name

    def visualize_laz(self,fn):
        with pylas.open(tile_fn) as fh:
            print('Num points:', fh.header.point_count)
            las = fh.read()
            x = las.x
            y = las.y
            z = las.z

            print(max(x),min(x))
            print(max(y),min(y))

            plt.figure()
            plt.scatter(x, y, s=1, c=z, cmap='viridis')
            plt.colorbar(label='Elevation')
            plt.xlabel('X')
            plt.ylabel('Y')
            plt.title('Point Cloud Visualization')
            plt.show()
    


point = (14.4180764, 50.0762969)
point_sjtsk = WGS_TO_SJTSK.transform(point[1],point[0])

dmr5g = Dmr5gParser()
tile_fn = dmr5g.download_tile_by_point(point)
print(dmr5g.get_tile_by_point(point))
dmr5g.visualize_laz(tile_fn)




