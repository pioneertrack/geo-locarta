from osgeo import ogr
import os
'''
sqlite = "out.sqlite"
driver = ogr.GetDriverByName("sqlite")
dataSource = driver.Open(sqlite, 1)
layer = dataSource.GetLayer()
i=0
for feature in layer:
    print i
    i=i+1
    geom = feature.GetGeometryRef()
    extent = geom.GetEnvelope()
    #feature.SetField("xmin", extent[0])
    #feature.SetField("ymax", extent[3])
    #layer.SetFeature(feature)
'''
def importData():
    db="out2.sqlite"
    inDriver = ogr.GetDriverByName("sqlite")
    sqlite = "out.sqlite"
    inDataSource = inDriver.Open(sqlite, 0)
    inLayer = inDataSource.GetLayer()
    outDriver = ogr.GetDriverByName('SQLite')
    if os.path.exists(db):
        outDataSource = outDriver.Open(db, 1) 
    else:
        outDataSource = outDriver.CreateDataSource(db, options=['SPATIALITE=yes'])
    outLayer = outDataSource.CreateLayer( "out2", geom_type=ogr.wkbPolygon )

    # Add input Layer Fields to the output Layer if it is the one we want
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        fieldName = fieldDefn.GetName()
        outLayer.CreateField(fieldDefn)

    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()

    # Add features to the ouput Layer
    for inFeature in inLayer:
        # Create output Feature
        outFeature = ogr.Feature(outLayerDefn)

        # Add field values from input Layer
        for i in range(0, outLayerDefn.GetFieldCount()):
            fieldDefn = outLayerDefn.GetFieldDefn(i)
            fieldName = fieldDefn.GetName()

            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(),
                inFeature.GetField(i))
           

        # Set geometry as centroid
        geom = inFeature.GetGeometryRef()
        extent = geom.GetEnvelope()
        outFeature.SetField("xmin", extent[0])
        outFeature.SetField("ymax", extent[3])
        outFeature.SetField("index", 0)
        outFeature.SetGeometry(geom.Clone())
        # Add new feature to output Layer
        outLayer.CreateFeature(outFeature)
        outFeature = None

    # Save and close DataSources
    inDataSource = None
    outDataSource = None

if __name__ == '__main__':
    importData()
    '''
    --create table outresult as select * from out2 order by xmin DESC ,ymax ASC
    --create table Oregon as select rowid as idn,* from outresult
    select * from Oregon
    '''