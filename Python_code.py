Crater = ''
output = ''
slopeproj= 
demproj = 
dem = 
slope = 

csv_file = 
output_pc = 
output_me = 
output_me_select = 
output_pc_select = 
output_line = 
output_merge =
output_base = 
output_merge_baserim = 
output_line_slope = 
output_alllines = 
output_poly =

#------- Reprojection ----------------
point = iface.activeLayer()
feat = point

fieldcalc = processing.run("qgis:fieldcalculator", {'INPUT':feat,'FIELD_NAME':'x','FIELD_TYPE':0,'FIELD_LENGTH':10,'FIELD_PRECISION':3,'NEW_FIELD':True,'FORMULA':'to_dm(x(transform($geometry,\'USER:100000\',\'EPSG:104969\')), \'x\', 2)','OUTPUT':'memory:'})
fieldcalc2 = processing.run("qgis:fieldcalculator", {'INPUT':fieldcalc['OUTPUT'],'FIELD_NAME':'y','FIELD_TYPE':0,'FIELD_LENGTH':10,'FIELD_PRECISION':3,'NEW_FIELD':True,'FORMULA':'to_dm(y(transform($geometry,\'USER:100000\',\'EPSG:104969\')), \'x\', 2)','OUTPUT':'memory:'})

layer = fieldcalc2['OUTPUT']
featfeat=layer.getFeatures()#get first feature
list_coord =[]
for featurecent in featfeat:
    list_coord.append(featurecent['x'])
    list_coord.append(featurecent['y'])

my_crs = QgsCoordinateReferenceSystem()
my_crs.createFromProj4("+proj=stere +lat_0="+list_coord[1]+" +lon_0="+list_coord[0]+" +x_0=0 +y_0=0 +a=1188300 +b=1188300 +units=m +no_defs")
my_crs.saveAsUserCrs("crater")
QgsProject.instance().setCrs(my_crs)

buff =processing.run("native:buffer", {'INPUT':feat,'DISTANCE':100000,'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'OUTPUT':'TEMPORARY_OUTPUT'})
clip=processing.run("gdal:cliprasterbymasklayer", {'INPUT':dem,'MASK':buff['OUTPUT'],'SOURCE_CRS':None,'TARGET_CRS':None,'NODATA':None,'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':False,'SET_RESOLUTION':False,'X_RESOLUTION':None,'Y_RESOLUTION':None,'MULTITHREADING':False,'OPTIONS':'','DATA_TYPE':0,'OUTPUT':'TEMPORARY_OUTPUT'})
clip2=processing.run("gdal:cliprasterbymasklayer", {'INPUT':slope,'MASK':buff['OUTPUT'],'SOURCE_CRS':None,'TARGET_CRS':None,'NODATA':None,'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':False,'SET_RESOLUTION':False,'X_RESOLUTION':None,'Y_RESOLUTION':None,'MULTITHREADING':False,'OPTIONS':'','DATA_TYPE':0,'OUTPUT':'TEMPORARY_OUTPUT'})

layer1 = QgsRasterLayer(clip['OUTPUT'])
layer2 = QgsRasterLayer(clip2['OUTPUT'])


crsup = iface.mapCanvas().mapSettings().destinationCrs().authid()
warp1 = processing.run("gdal:warpreproject", {'INPUT':layer1,'SOURCE_CRS':QgsCoordinateReferenceSystem('USER:100000'),'TARGET_CRS':QgsCoordinateReferenceSystem(crsup),'RESAMPLING':0,'NODATA':None,'TARGET_RESOLUTION':None,'OPTIONS':'','DATA_TYPE':0,'TARGET_EXTENT':None,'TARGET_EXTENT_CRS':None,'MULTITHREADING':False,'EXTRA':'','OUTPUT':output_dem})
warp2 = processing.run("gdal:warpreproject", {'INPUT':layer2,'SOURCE_CRS':QgsCoordinateReferenceSystem('USER:100000'),'TARGET_CRS':QgsCoordinateReferenceSystem(crsup),'RESAMPLING':0,'NODATA':None,'TARGET_RESOLUTION':None,'OPTIONS':'','DATA_TYPE':0,'TARGET_EXTENT':None,'TARGET_EXTENT_CRS':None,'MULTITHREADING':False,'EXTRA':'','OUTPUT':output_slope})

#---------------------Delineation ------------------------------------------------------
poly = iface.activeLayer()

save_poly = QgsVectorFileWriter.writeAsVectorFormat(poly, output_poly  , "UTF-8", poly.crs(), "ESRI Shapefile")

list_data = []
list_data2 = [list_data]
list_data.append(''+crater+'')
crs = iface.mapCanvas().mapSettings().destinationCrs().authid()
fieldcalculator1 = processing.run("qgis:fieldcalculator",
                   {'INPUT': poly, 'FIELD_NAME': '1.3-field', 'FIELD_TYPE': 0, 'FIELD_LENGTH': 10, 'FIELD_PRECISION': 3,
                    'NEW_FIELD': True,
                    'FORMULA': '((length(shortest_line(centroid($geometry),boundary($geometry)))))*1.3',
                    'OUTPUT': 'memory:'})
fieldcalculator2 = processing.run("qgis:fieldcalculator",
                    {'INPUT': poly, 'FIELD_NAME': '1-4_raio', 'FIELD_TYPE': 0, 'FIELD_LENGTH': 10, 'FIELD_PRECISION': 3,
                     'NEW_FIELD': True,
                     'FORMULA': '((length(shortest_line(centroid($geometry),boundary($geometry)))))/4.5',
                     'OUTPUT': 'memory:'})
fieldcalculator3 = processing.run("qgis:fieldcalculator",
                     {'INPUT': poly, 'FIELD_NAME': '8_raio', 'FIELD_TYPE': 0, 'FIELD_LENGTH': 10, 'FIELD_PRECISION': 3,
                      'NEW_FIELD': True,
                      'FORMULA': '((length(shortest_line(centroid($geometry),boundary($geometry)))))/8',
                      'OUTPUT': 'memory:'})
polytoline = processing.run("native:polygonstolines", {'INPUT': fieldcaculator2['OUTPUT'], 'OUTPUT': 'TEMPORARY_OUTPUT'})
centroid = processing.run("saga:polygoncentroids",
                   {'POLYGONS': fieldcalulator1['OUTPUT'], 'METHOD         ': True, 'CENTROIDS': 'TEMPORARY_OUTPUT'})
buffervar = processing.run("saga:variabledistancebuffer",
                   {'SHAPES': centroid['CENTROIDS'], 'DIST_FIELD': '1.3-field', 'DIST_SCALE': 1, 'NZONES': 1, 'DARC': 5,
                    'DISSOLVE       ': True, 'POLY_INNER       ': False, 'BUFFER': 'TEMPORARY_OUTPUT'})
polytoline2 = processing.run("native:polygonstolines", {'INPUT': c['BUFFER'], 'OUTPUT': 'TEMPORARY_OUTPUT'})
desify = processing.run("native:densifygeometriesgivenaninterval",
                   {'INPUT': polytoline2['OUTPUT'], 'INTERVAL': 600, 'OUTPUT': 'TEMPORARY_OUTPUT'})
vertice = processing.run("native:extractvertices", {'INPUT': densify['OUTPUT'], 'OUTPUT': 'TEMPORARY_OUTPUT'})
geometry = processing.run("qgis:exportaddgeometrycolumns",
                   {'INPUT': vertice['OUTPUT'], 'CALC_METHOD': 0, 'OUTPUT': 'TEMPORARY_OUTPUT'})
geometry2 = processing.run("qgis:exportaddgeometrycolumns",
                   {'INPUT': centroid['CENTROIDS'], 'CALC_METHOD': 0, 'OUTPUT': 'TEMPORARY_OUTPUT'})
fieldcalculator4 = processing.run("qgis:fieldcalculator",
                    {'INPUT': geometry2['OUTPUT'], 'FIELD_NAME': 'ID', 'FIELD_TYPE': 0, 'FIELD_LENGTH': 10,
                     'FIELD_PRECISION': 3, 'NEW_FIELD': True, 'FORMULA': '0', 'OUTPUT': 'memory:'})
join = processing.run("native:joinattributestable",
                   {'INPUT': geometry['OUTPUT'], 'FIELD': 'ID', 'INPUT_2': h2['OUTPUT'], 'FIELD_2': 'ID', 'FIELDS_TO_COPY': [],
                    'METHOD': 1, 'DISCARD_NONMATCHING': False, 'PREFIX': '', 'OUTPUT': 'TEMPORARY_OUTPUT'})
xyline = processing.run("shapetools:xy2line",
                   {'InputLayer': join['OUTPUT'], 'InputCRS': QgsCoordinateReferenceSystem(crs),
                    'OutputCRS': QgsCoordinateReferenceSystem(crs), 'LineType': 0, 'StartUseLayerGeom': False,
                    'StartXField': 'xcoord_2', 'StartYField': 'ycoord_2', 'EndUseLayerGeom': False,
                    'EndXField': 'xcoord', 'EndYField': 'ycoord', 'ShowStartPoint': True, 'ShowEndPoint': True,
                    'DateLineBreak': False, 'OutputLineLayer': 'TEMPORARY_OUTPUT',
                    'OutputPointLayer': 'TEMPORARY_OUTPUT'})
profile = processing.run("saga:profilesfromlines",
                   {'DEM': dem, 'VALUES': '', 'LINES': j['OutputLineLayer'], 'NAME': 'fid', 'SPLIT         ': False,
                    'PROFILE': 'TEMPORARY_OUTPUT', 'PROFILES': 'TEMPORARY_OUTPUT'})
valuetopoint = processing.run("saga:addrastervaluestopoints",
                   {'SHAPES': profile['PROFILE'], 'GRIDS': slope, 'RESAMPLING': 0, 'RESULT': 'TEMPORARY_OUTPUT'})
buffervar2 = processing.run("saga:variabledistancebuffer",
                   {'SHAPES': polytoline['OUTPUT'], 'DIST_FIELD': '1-4_raio', 'DIST_SCALE': 1, 'NZONES': 1, 'DARC': 5,
                    'DISSOLVE       ': True, 'POLY_INNER       ': False, 'BUFFER': 'TEMPORARY_OUTPUT'})
clip = processing.run("saga:clippointswithpolygons",
                   {'POINTS': valuetopoint['RESULT'], 'POLYGONS': m['BUFFER'], 'FIELD': 'Drawings', 'METHOD': 0,
                    'CLIPS': 'TEMPORARY_OUTPUT'})
centroid2 = processing.run("saga:polygoncentroids",
                    {'POLYGONS': fieldcalculator3['OUTPUT'], 'METHOD         ': True, 'CENTROIDS': 'TEMPORARY_OUTPUT'})
buffervar3 = processing.run("saga:variabledistancebuffer",
                    {'SHAPES': centroid2['CENTROIDS'], 'DIST_FIELD': '8_raio', 'DIST_SCALE': 1, 'NZONES': 1, 'DARC': 5,
                     'DISSOLVE       ': True, 'POLY_INNER       ': False, 'BUFFER': 'TEMPORARY_OUTPUT'})
difference = processing.run("native:difference", {'INPUT': valuetopoint['RESULT'], 'OVERLAY': a5['BUFFER'], 'OUTPUT': 'TEMPORARY_OUTPUT'})

layer11 = difference['OUTPUT']
QgsProject.instance().addMapLayer(layer11)
layer1 = QgsVectorLayer(clip['CLIPS'])
QgsProject.instance().addMapLayer(layer1)

# Maximum Elevation
byexoress = processing.run("qgis:selectbyexpression",
                   {'INPUT': layer1, 'EXPRESSION': '\"Z\" = maximum(\"z\",\"LINE_ID\")', 'METHOD': 0})
saveselected = processing.run("native:saveselectedfeatures", {'INPUT': layer1, 'OUTPUT': output_me})
layer1.removeSelection()
layer2 = QgsVectorLayer(o2['OUTPUT'])


# Delineation
all_features = layer2.getFeatures()
all_features2 = layer2.getFeatures()
all_features3 = layer2.getFeatures()

lista_repetition = []
for alllineids in all_features:
    lista_repetition.append(alllineids['LINE_ID'])
repetition = max(lista_repetition)

lista_repetition2 = []
for alllineids2 in all_features2:
    lista_repetition2.append(alllineids2['LINE_ID'])
repetition2 = max(lista_repetition2)

lista_repetition3 = []
for alllineids3 in all_features3:
    lista_repetition3.append(alllineids3['LINE_ID'])
repetition3 = max(lista_repetition2)

layer1.startEditing()
layer2.startEditing()
layer11.startEditing()
idx1 = layer2.fields().indexFromName('LINE_ID')
u1 = layer2.minimumValue(idx1)
processing.run("qgis:selectbyexpression",
               {'INPUT': layer2, 'EXPRESSION': '\"fid\"= maximum (\"fid\",\"LINE_ID\") AND \"LINE_ID\" = {}'.format(u1),
                'METHOD': 0})
selected_features = layer2.selectedFeatures()
for point in selected_features:
    u2 = point['fid']
#print(u1)
#print(u2)
exp_me0 = QgsExpression("\"LINE_ID\"='{}'AND\"fid\"='{}'".format(u1, u2))
feature_me = layer2.getFeatures(QgsFeatureRequest(exp_me0))
x = u1
lista = list(map(str, range(repetition + 1)))
listlayer1 = []
listlayer2 = []
for f in feature_me:
    geom_me0 = f.geometry()
for times in range(repetition + 1):
    x = x + 1
    #print('for1')
    #print(x)
    y = 0
    try:
        lineid = lista[x]
    except IndexError:
        continue
    exp_me = QgsExpression('\"LINE_ID\" = (' + lineid + ')')
    exp_control = QgsExpression('\"LINE_ID\" = (' + lineid + ')')
    feature_me = layer2.getFeatures(QgsFeatureRequest(exp_me))
    feature_control = layer1.getFeatures(QgsFeatureRequest(exp_control))
    for f_me in feature_me:
        geom_me = f_me.geometry()
        dist2 = geom_me0.distance(geom_me)
        #print('forme')
        # print(f_me['ID'])
        # print(lineid)
        if dist2 < 1000:
            geom_me0 = geom_me
            #print('me')
            #print(f_me['LINE_ID'])
            #print(f_me['ID'])
            layer2.select(f_me.id())
            break
        else:
            list_id_key = []
            list_dist_value = []
            list2_id_key = []
            list2_dist_value = []
            for f_control in feature_control:
                geom_control = f_control.geometry()
                dist3 = geom_me0.distance(geom_control)
                list_id_key.append(f_control['ID'])
                list_dist_value.append(dist3)
                keys = list_id_key
                values = list_dist_value
                dictionary = dict(zip(keys, values))
                dictionary2 = dict(zip(keys, values))
            list_pcid = []
            for times in range(3):
                min_val = min(dictionary.values())
                for k, v in dictionary.items():
                    if v == min_val:
                        list_pcid.append(k)
                        del dictionary[k]
                        break
            lista2 = list(map(str, list_pcid))
            y = 0
            for times in range(3):
                lineid2 = lista2[y]
                exp_control2 = QgsExpression('\"ID\" = (' + lineid2 + ') ')
                feature_pcid1 = layer1.getFeatures(QgsFeatureRequest(exp_control2))
                y = y + 1
                for f_pcid1 in feature_pcid1:
                    feature_pcid1_geom = f_pcid1.geometry()
                    dist4 = geom_me.distance(feature_pcid1_geom)
                    list2_id_key.append(f_pcid1['ID'])
                    list2_dist_value.append(dist4)
            ke = list2_id_key
            va = list2_dist_value
            dictionary_dist = dict(zip(ke, va))
            min_val2 = min(dictionary_dist.values())
            for ky, vs in dictionary_dist.items():
                if vs == min_val2:
                    new_select_pcid = ky
            pc_slect_str = str(new_select_pcid)
            exp_control3 = QgsExpression('\"ID\" = (' + pc_slect_str + ') ')
            feature_pcid2 = layer1.getFeatures(QgsFeatureRequest(exp_control3))
            for pc_feature in feature_pcid2:
                geom_me0 = pc_feature.geometry()
                #print('pc1')
                #print(pc_feature['LINE_ID'])
                #print(pc_feature['ID'])
                # print(list_pcid)
                # print(dictionary_dist)
                # print(new_select_pcid)
            layer1.selectByExpression('\"ID\" IN (' + pc_slect_str + ')', QgsVectorLayer.AddToSelection)
        break

listtostr = list(map(str, listlayer1))
p = 0
for feature in listlayer1:
    pointtoselect = listtostr[p]
    layer1.selectByExpression('\"ID\" IN (' + pointtoselect + ')', QgsVectorLayer.AddToSelection)
    p = p + 1

saveselected_pc = processing.run("native:saveselectedfeatures", {'INPUT': layer1, 'OUTPUT': output_pc_select})
saveselected_me = processing.run("native:saveselectedfeatures", {'INPUT': layer2, 'OUTPUT': output_me_select})

layer_pc_select = QgsVectorLayer(saveselected_pc['OUTPUT'])
layer_me_select = QgsVectorLayer(saveselected_me['OUTPUT'])

merge = processing.run("native:mergevectorlayers",
                   {'LAYERS': [layer_pc_select, layer_me_select], 'CRS': None, 'OUTPUT': output_merge})

pointtopath = processing.run("qgis:pointstopath",
                   {'INPUT': merge['OUTPUT'], 'ORDER_FIELD': 'LINE_ID', 'GROUP_FIELD': None, 'DATE_FORMAT': '',
                    'OUTPUT':output_line})
layer_line = QgsVectorLayer(merge['OUTPUT'])
QgsProject.instance().addMapLayer(layer_line)


# rim hight
import statistics

layer_points = QgsVectorLayer(merge['OUTPUT'])
feature_points = layer_points.getFeatures()

list_altura = []
for alturas in feature_points:
    list_altura.append(alturas['Z'])

features_selected = layer_points.selectAll()
numb_feature = layer_points.selectedFeatureCount()
layer_points.removeSelection()
sum_ = sum(list_altura)
medium_hight = sum_ / (numb_feature)

hight_variance = statistics.stdev(list_altura)

# depth
layer_all = QgsVectorLayer(valuetopoint['RESULT'])
feature_all = layer_all.getFeatures()
list_zmin = []

for z in feature_all:
    list_zmin.append(z['Z'])

depth = medium_hight - min(list_zmin)

# radius
rim = QgsVectorLayer(merge['OUTPUT'])
QgsProject.instance().addMapLayer(rim)

pointtopath2 = processing.run("qgis:pointstopath", 
                    {'INPUT':rim,'ORDER_FIELD':'LINE_ID','GROUP_FIELD':None,'DATE_FORMAT':'','OUTPUT':'TEMPORARY_OUTPUT'})
linetopoly2 = processing.run("qgis:linestopolygons", {'INPUT':pointtopath2['OUTPUT'],'OUTPUT':'TEMPORARY_OUTPUT'})
centroid3 = processing.run("saga:polygoncentroids", {'POLYGONS':linetopoly2['OUTPUT'],'METHOD         ':True,'CENTROIDS':'TEMPORARY_OUTPUT'})
layer_centroid = QgsVectorLayer(centroid3['CENTROIDS'])
feature_points = layer_points.getFeatures()
feature_centroid = layer_centroid.getFeatures()
list_radious = []
list_radious2 = []
for centroid in feature_centroid:
    geom_centrois = centroid.geometry()
for points in feature_points:
    geom_points = points.geometry()
    dist = geom_centrois.distance(geom_points)
    list_radious.append(dist)
    list_radious2.append(dist)
features_selected = layer_points.selectAll()
numb_feature = layer_points.selectedFeatureCount()
layer_points.removeSelection()
sum_ = sum(list_radious)
diameter = sum_ * 2
medium_diameter = diameter/(numb_feature)

#base and wall
i = 0
lista2 = list(map(str, range(repetition2 + 1)))
for time in range(repetition2 + 1):
    i = i + 1
    try:
        lineid2 = lista2[i]
    except IndexError:
        continue
    exp_slope = QgsExpression('\"LINE_ID\" = (' + lineid2 + ') ')
    feature_slope = layer11.getFeatures(QgsFeatureRequest(exp_slope))
    list_zmin = []
    select_wall_list = []
    parede_id = []
    for f_slope in feature_slope:
        list_zmin.append(f_slope['Z'])
    z_max = max(list_zmin)
    z_min = min(list_zmin)
    profundidade2 = z_max - z_min
    z_min_prox = z_min + ((profundidade2 / 5))
    for zs in list_zmin:
        if zs >= z_min_prox:
            select_wall_list.append(zs)

    base_wall = (str(min(select_wall_list)))

    layer11.selectByExpression('\"Z\" IN (' + base_wall + ') AND \"LINE_ID\" = (' + lineid2 + ')',
                               QgsVectorLayer.AddToSelection)
list_data.append ((str(medium_diameter)))
list_data.append ((str(depth)))
list_data.append ((str(hight_variance)))

saveselectedbase = processing.run("native:saveselectedfeatures", {'INPUT': layer11, 'OUTPUT': output_base})
join2 = processing.run("native:joinattributestable",
                   {'INPUT': saveselectedbase ['OUTPUT'], 'FIELD': 'LINE_ID', 'INPUT_2': merge['OUTPUT'], 'FIELD_2': 'LINE_ID',
                    'FIELDS_TO_COPY': [], 'METHOD': 1, 'DISCARD_NONMATCHING': False, 'PREFIX': '',
                    'OUTPUT': 'TEMPORARY_OUTPUT'})
xytoline2 = processing.run("shapetools:xy2line",
                   {'InputLayer': join2['OUTPUT'], 'InputCRS': QgsCoordinateReferenceSystem(crs),
                    'OutputCRS': QgsCoordinateReferenceSystem(crs), 'LineType': 0, 'StartUseLayerGeom': False,
                    'StartXField': 'X', 'StartYField': 'Y', 'EndUseLayerGeom': False, 'EndXField': 'X_2',
                    'EndYField': 'Y_2', 'ShowStartPoint': True, 'ShowEndPoint': True, 'DateLineBreak': False,
                    'OutputLineLayer': output_line_slope, 'OutputPointLayer': 'TEMPORARY_OUTPUT'})

densify2 = processing.run("native:densifygeometriesgivenaninterval",
                   {'INPUT': xytoline2['OutputLineLayer'], 'INTERVAL': 300, 'OUTPUT': 'TEMPORARY_OUTPUT'})
vertices2 = processing.run("native:extractvertices", {'INPUT': densify2['OUTPUT'], 'OUTPUT': 'TEMPORARY_OUTPUT'})
valuetopoint2 = processing.run("saga:addrastervaluestopoints",
                   {'SHAPES': vertices2['OUTPUT'], 'GRIDS': slope, 'RESAMPLING': 0, 'RESULT': 'TEMPORARY_OUTPUT'})

layer12 = QgsVectorLayer(valuetopoint2['RESULT'])

layer13 = QgsVectorLayer(xytoline2['OutputLineLayer'])
QgsProject.instance().addMapLayer(layer13)
i = 0
listslope = []
lista3 = list(map(str, range(repetition3 + 1)))
for time in range(repetition3 + 1):
    i = i + 1
    # print('for1')
    # print(c)
    try:
        lineid3 = lista3[i]
    except IndexError:
        continue
    exp_lineslope = QgsExpression('\"LINE_ID\" = (' + lineid3 + ') ')
    feature_lineslope = layer12.getFeatures(QgsFeatureRequest(exp_lineslope))
    for slop in feature_lineslope:
        listslope.append(slop[''+slopeproj+''])
print ('sloepe='+ (str(statistics.mean(listslope))))
print('stdv slope ='+(str(statistics.stdev(listslope))))
list_data.append ((str(statistics.mean(listslope))))
list_data.append ((str(statistics.stdev(listslope))))

#wall widht and base_diameter
x = processing.run("qgis:exportaddgeometrycolumns",
                {'INPUT':t['OutputLineLayer'],'CALC_METHOD':0,'OUTPUT':'TEMPORARY_OUTPUT'})
layer14 = x['OUTPUT']
QgsProject.instance().addMapLayer(layer14)
featparede = layer14.getFeatures()
parede = []
for f in featparede:
    parede.append(f['length'])
wall_widht = statistics.mean(parede)

base_diameter = media_diametro - (espessura_parede * 2)

# lat long
feat = QgsVectorLayer(b['CENTROIDS'])
featfeat = feat.getFeatures()  # get first feature
for featurecent in featfeat:
    geo = QgsGeometry.asPoint(featurecent.geometry())  # get the geometry of the feature
    pxy = QgsPointXY(geo)

list_data.append ((str((pxy.x()))))
list_data.append ((pxy.y()))
list_data.append ((wall_widht))
list_data.append ((base_diameter))

# ---------------------------------------------------------------------
# depht error

feature_points2 = rim.getFeatures()
list_hight = []
for hights in feature_points2:
    list_hight.append(hights['Z'])
hight_variation = statistics.stdev(list_hight)
medium_hight = statistics.mean(list_hight)
number_hight = len(list_hight)
filtro = midium_hight - hight_variation
list_points_filto = []
for points in list_hight:
    if points >= filtro:
        list_points_filto.append(points)
mediun_high2 = statistics.mean(list_points_filto)
hight_variation2 = statistics.stdev(list_points_filto)
number_hight2 = len(list_points_filto)

rim2 = QgsVectorLayer(merge['OUTPUT'])

assignporj= processing.run("native:assignprojection", 
                {'INPUT':rim2,
                'CRS':QgsCoordinateReferenceSystem(crs),'OUTPUT':'TEMPORARY_OUTPUT'})

pointtopath4 = processing.run("qgis:pointstopath", {'INPUT':assignporj['OUTPUT'],'ORDER_FIELD':'LINE_ID','GROUP_FIELD':None,'DATE_FORMAT':'','OUTPUT':'TEMPORARY_OUTPUT'})
linetopoly4 = processing.run("qgis:linestopolygons", {'INPUT':pointtopath4['OUTPUT'],'OUTPUT':'TEMPORARY_OUTPUT'})
fieldcalculator5 = processing.run("qgis:fieldcalculator",
                   {'INPUT':linetopoly4['OUTPUT'],'FIELD_NAME':'raio','FIELD_TYPE':0,'FIELD_LENGTH':10,'FIELD_PRECISION':3,
                    'NEW_FIELD':True,'FORMULA':'((length(shortest_line(centroid($geometry),boundary($geometry)))))/2','OUTPUT':'memory:'})
centroid4 = processing.run("saga:polygoncentroids",
                   {'POLYGONS':fieldcalculator5['OUTPUT'],'METHOD         ':True,'CENTROIDS':'TEMPORARY_OUTPUT'})

buffervar5 = processing.run("saga:variabledistancebuffer",
                   {'SHAPES': centroid4 ['CENTROIDS'], 'DIST_FIELD': 'raio', 'DIST_SCALE': 1, 'NZONES': 1, 'DARC': 5,
                    'DISSOLVE       ': True, 'POLY_INNER       ': False, 'BUFFER': 'TEMPORARY_OUTPUT'})
pixels = processing.run("qgis:generatepointspixelcentroidsinsidepolygons",
                   {'INPUT_RASTER': dem, 'INPUT_VECTOR': buffervar5['BUFFER'], 'OUTPUT': 'TEMPORARY_OUTPUT'})
valuetopoint5 = processing.run("saga:addrastervaluestopoints",
                   {'SHAPES': pixels['OUTPUT'], 'GRIDS': dem, 'RESAMPLING': 0, 'RESULT': 'TEMPORARY_OUTPUT'})

base_layer = QgsVectorLayer(valuetopoint['RESULT'])
feature_points_base = base_layer.getFeatures()
QgsProject.instance().addMapLayer(base_layer)
list_base = []
for hights in feature_points_base:
    list_base.append((hights[''+demproj+'']))
variation_base = statistics.stdev(list_base)
medium_base = statistics.mean(list_base)
number_base = len(list_base)
filtro2 = medium_base - variation_base
list_points_filtro_base = []
for points2 in list_base:
    if points2 <= filtro2:
        list_points_filtro_base.append(points2)
medium_base2 = statistics.mean(list_points_filtro_base)
variation_base2 = statistics.stdev(list_points_filtro_base)
number_base2 = len(list_points_filtro_base)

erro_hight = (math.sqrt(number_altura2 * (550 ** 2))) / number_hight2
erro_hight2 = math.sqrt((erro_alt ** 2) + hight_variation2)

erro_base = (math.sqrt(number_base2 * (550 ** 2))) / number_base2
erro_base2 = math.sqrt((erro_base ** 2) + variation_base2)

error_depth = math.sqrt((erro_alt2 ** 2) + (erro_base2 ** 2))

# diameter error
medium_radius = statistics.mean(list_radious2)
list_var= []
for dist in list_radious2:
    var = dist - medium_radius
    list_var.append(var)

square_var = []
for var in list_var:
    var_square = var**2
    square_var.append(var_square)

mean_squarevar = (sum(square_var))/ (numb_feature - 1)

error_diam = math.sqrt(mean_squarevar)

list_data.append ((str(error_depth)))
list_data.append ((str(error_diam)))

#-------------------------------------

import csv
file2 = open(''+csv_file+'','a',newline="")
writer = csv.writer(file2)
data= list_data2
writer.writerows(data)
file2.close()
