import arcgis
import arcpy
import os
import sys
import time
arcpy.env.overwriteOutput = True

start = time.time()
def main ():
     #AdminBoundaries()
     #Planning()
     #Drainage()
     #ParksandRec()
     #Schools()
     #Utilities()
     #CIP()
     VT()

def AdminBoundaries():
    #Boundary Layers on Interactive Map are also included. PUC layers are in ExternalAgencies in Horizon.
    prjPath = "\\\\GISAPP\\Workspace\\Horizon\\ArcGISPro_Projects\\FeatureServices\\InteractiveMap\\AdminBoundaries.aprx"

    dict = {"City Boundaries": ["City_Boundaries","City Boundaries, City Limits, ETJ, General, Administrative Boundaries, Polygon", "This layer contains the City Limits and Extra Territorial Jurisdiction (ETJ) for the City of Pearland.",0],
            "Counties": ["Counties", "Counties, General, Administrative Boundaries, Polygon, Interactive Map", "This layer contains the boundaries of the various Counties in and around the City of Pearland.", 1],
            "County Commissioners":["County_Commissioners", "County Commissioners, Adminitrative Boundaries, Local Governemnt, Polygon, Interactive Map", "This layer contains the County Comissioner areas located in the City of Pearland.", 2],
            "Drainage Districts": ["Drainage_Districts", "Drainage Districts, Administrative Boundaries, Polygon, Interactive Map", "This layer contains the various Drainage Districts in the City of Pearland", 3],
            "Emergency Service Districts": ["Emergency_Service_Districts", "Emergency Service Districts, ESD, Fire Department, Administrative Boundaries, Polygon, Fire, Interactive Map", "This layers shows the Emergency Service Districts (ESD) that Pearland Fire Department Services.", 4],
            "Municipal Utility Districts": ["Municipal_Utility_Districts", "Municipal Utility Districts, MUD, Administrative Boundaries, Polygon, Interactive Map", "This layer shows the various Municipal Utility Districts (MUD) within the City of Pearland.", 5],
            "Neighborhoods": ["Neighborhoods", "Neighborhoods, Subdivisions, Administrative Boundaries, Polygon, Interactive Map", "This layer shows the various Neighborhoods within the City of Pearland.", 6],
            "Ordinance": ["Ordinance", "Ordinance, Annexation, Administrative Boundaries, Polygon, Interactive Map", "This layer show a history of the Annexations that have taken place in the City of Pearland.", 7],
            "Zip Codes": ["Zip_Codes", "Zip Codes, Administrative Boundaries, Polygon, Interactive Map", "This layer shows the boundaries for the Zip Codes in and around the City of Pearland.", 8],
            "PUC_CCN_SEWER":["PUC_CCN_SEWER","PUC_CCN_SEWER, Administrative Boundaries, Polygon, Interactive Map","This layer shows the boundaries for the PUC_CCN_Sewer in and around the City of Pearland.",9],
            "PUC_CCN_WATER":["PUC_CCN_WATER","PUC_CCN_WATER, Administrative Boundaries, Polygon, Interactive Map","This layer shows the boundaries for the PUC_CCN_Water in and around the City of Pearland.",10]}
    n=0
    #"Drainage Districts": ["Drainage_Districts", "Drainage Districts, Administrative Boundaries, Polygon", "This layer contains the various Drainage Districts in the City of Pearland", 2],
    for key, value in dict.items():

        sd_fs_name = "{}".format(key)
        portal = "https://pearland.maps.arcgis.com"
        user = "MapService_Admin"
        password = "Sdesde81"

        shrOrg = True
        shrEveryone = True
        shrGroups = "c0c1883a34bf479b863dbeaa9a6adffd"

        relPath = "\\\\GISAPP\\Workspace\\Horizon\\Scripts"
        sddraft = os.path.join(relPath, "WebUpdate.sddraft")
        sd = os.path.join(relPath, "WebUpdate.sd")

        arcpy.env.overwriteOutput = True
        prj = arcpy.mp.ArcGISProject(prjPath)
        m = prj.listMaps('Map')[0]
        mp = m.listLayers()[value[3]]
        arcpy.mp.CreateWebLayerSDDraft(mp, sddraft, sd_fs_name, 'MY_HOSTED_SERVICES', 'FEATURE_ACCESS','Administrative_Boundaries', True, True, False, True)
        arcpy.StageService_server(sddraft, sd)

        gis = arcgis.GIS(portal, user, password)
        searchItem = gis.content.search(query="title:"+ value[0] + " AND owner: " + user, item_type="Service Definition", sort_field='title', sort_order='asc')
        for item in searchItem:
            print(item["title"])
            if item["title"] == key:
                sdItem = item
        sdItem.update(data=sd)
        sdItem.update(item_properties={'tags': '{}'.format(value[1]), 'snippet': "This Layer is updated automatically through a Python Script.",
                                       'description': '{}'.format(value[2])}, thumbnail="\\\\GISAPP\\Workspace\\Horizon\\Thumbnails\\AdminBoundaries\\{}.png".format(value[0]))

        fs = sdItem.publish(overwrite=True)
        fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)
        print(sd_fs_name, "done")
        n+=1

def Planning():
    prjPath = "\\\\GISAPP\\Workspace\\Horizon\\ArcGISPro_Projects\\Planning\\Planning.aprx"

    dict = {#"Plats":["Plats", "Plats, Planning, Polygon, Interactive Map", "This Layer shows the platted properties throughout the City of Pearland.", 0],
            "Thoroughfare Plan": ["Thoroughfare_Plan", "Thoroughfare Plan, Thoroughfare, Streets, Planning, Line, Interactive Map", "This Layer shows the Thoroughfare Plan for the City of Pearland.", 1],
            "Thoroughfare Intersections": ["Thoroughfare_Intersections", "Thoroughfare Intersections, Thoroughfare, Intersections, Planning, Point, Interactive Map", "This Layer shows the Thoroughfare Intersections for the City of Pearland.", 2],
            "Conditional and Special Use Permits": ["Conditional_and_Special_Use_Permits", "CUP, SUP, Permits, Special Use Permits, Conditional Use Permits, Planning, Polygon, Interactive Map", "This Layer shows the various Special Use permits throughout the City of Pearland.", 3],
            "Zoning": ["Zoning", "Zoning, Planning, Polygon, Interactive Map", "This Layer shows the Zoning within the City of Pearland.", 4],
            "Management Districts": ["Management_Districts", "Management Districts, PEDC, Planning, Polygon, Interactive Map", "This Layer shows the Management Districts within the City of Pearland.", 5],
            "Corridor Overlay District": ["Corridor_Overlay_District", "Corridor Overlay Districts, Corridors, Major Roads, Planning, Line, Interactive Map", "This Layer shows some of the Major Corridors within the City of Pearland.", 6],
            "Future Land Use Plan 2015": ["Future_Land_Use_Plan_2015", "Future Land Use Plan 2015, FLUP, Planning, Polygon, Interactive Map", "This Layer shows the Future Land Use Plan drafted in 2015 for the City of Pearland.", 7],
            "Right of Way Management": ["Right_of_Way_Management", "Right of Way Management, ROW Management, ROW, Planning, Polygon, Interactive Map", "This Layer shows some of the surrounding areas around roads in the City of Pearland.", 8],
            "Street Jurisdiction":["Street_Jurisdiction", "Street Jurisdiction, Public Road, Private Road, Roads, Centerline, Planning, Line, Interactive Map", "This Layer shows Road Ownership throughout the City of Pearland.", 9],
            "Lane Miles":["Lane_Miles", "Lane Miles, Mileage, Road Miles, Public Works, Centerline, Planning, Line, Interactive Map", "This Layer shows the Lane Miles fore individual roads in the City of Pearland.", 10],
            #"PDs":["PDs", "PDs, Planned Developments, Planning, Polygon, Interactive Map", "This Layer shows various Planned Developments throughout the City of Pearland.", 11],
            "Tax Increment Reinvestment Zone":["Tax_Increment_Reinvestment_Zone", "TIRZ, Shadow Creek Ranch, Planning, Polygon, Interactive Map", "This Layer shows the TIRZ in the City of Pearland.", 12]}
    n = 0
    for key, value in dict.items():
        sd_fs_name = "{}".format(key)
        portal = "https://pearland.maps.arcgis.com"
        user = "MapService_Admin"
        password = "Sdesde81"

        shrOrg = True
        shrEveryone = True
        shrGroups = "c0c1883a34bf479b863dbeaa9a6adffd"
        relPath = "\\\\GISAPP\\Workspace\\Horizon\\Scripts"
        sddraft = os.path.join(relPath, "WebUpdate.sddraft")
        sd = os.path.join(relPath, "WebUpdate.sd")

        arcpy.env.overwriteOutput = True
        prj = arcpy.mp.ArcGISProject(prjPath)
        m = prj.listMaps('Map')[0]
        mp = m.listLayers()[value[3]]
        arcpy.mp.CreateWebLayerSDDraft(mp, sddraft, sd_fs_name, 'MY_HOSTED_SERVICES', 'FEATURE_ACCESS',
                                       'Planning', True, True, False, True)
        arcpy.StageService_server(sddraft, sd)
        gis = arcgis.GIS(portal, user, password)
        searchItem = gis.content.search(query="title:"+ value[0] + " AND owner: " + user, item_type="Service Definition", sort_field='title', sort_order='asc')

        for item in searchItem:
            print(item["title"])
            if item["title"] == key:
                sdItem = item

        sdItem.update(data=sd)
        sdItem.update(item_properties={'tags': '{}'.format(value[1]),
                                       'snippet': "This Layer is updated automatically through a Python Script.",
                                       'description': '{}'.format(value[2])}, thumbnail="\\\\GISAPP\\Workspace\\Horizon\\Thumbnails\\Planning\\{}.png".format(value[0]))

        fs = sdItem.publish(overwrite=True)
        fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)
        n += 1

def Drainage():
    prjPath = "\\\\GISAPP\\Workspace\\Horizon\\ArcGISPro_Projects\\Drainage\\Drainage.aprx"

    dict = {"Benchmarks": ["Benchmarks", "Benchmark, Engineering, GPS, Drainage, Point", "This layer shows the Benchmark network for the City of Pearland.", 0],
            "Detention Locations": ["Detention_Locations", "Detention Locations, Engineering, Drainage, Point, FEMA, EOC", "This layer shows the Detention Locations located throughout the City of Pearland.", 1],
            "Watersheds": ["Watersheds", "Watersheds, Engineering, Drainage, Polygon, FEMA, EOC", "This layer shows the Watersheds within the City of Pearland.", 2],
            "Flood Gauges": ["Flood_Gauges", "Flood Gauges, Engineering, Drainage, EOC, Point", "This layer shows the Flood Gauges located along major creeks within the City of Pearland.", 3]}
    n = 0
    for key, value in dict.items():

        sd_fs_name = "{}".format(key)
        portal = "https://pearland.maps.arcgis.com"
        user = "MapService_Admin"
        password = "Sdesde81"

        shrOrg = True
        shrEveryone = True
        shrGroups = "c0c1883a34bf479b863dbeaa9a6adffd"

        relPath = "\\\\GISAPP\\Workspace\\Horizon\\Scripts"
        sddraft = os.path.join(relPath, "WebUpdate.sddraft")
        sd = os.path.join(relPath, "WebUpdate.sd")

        arcpy.env.overwriteOutput = True
        prj = arcpy.mp.ArcGISProject(prjPath)
        m = prj.listMaps('Map')[0]
        mp = m.listLayers()[value[3]]
        arcpy.mp.CreateWebLayerSDDraft(mp, sddraft, sd_fs_name, 'MY_HOSTED_SERVICES', 'FEATURE_ACCESS','Administrative_Boundaries', True, True, False, True)
        arcpy.StageService_server(sddraft, sd)

        gis = arcgis.GIS(portal, user, password)
        searchItem = gis.content.search(query="title:"+ value[0] + " AND owner: " + user, item_type="Service Definition", sort_field='title', sort_order='asc')
        for item in searchItem:
            print(item["title"])
            if item["title"] == key:
                sdItem = item
        sdItem.update(data=sd)
        sdItem.update(item_properties={'tags': '{}'.format(value[1]), 'snippet': "This Layer is updated automatically through a Python Script.",
                                       'description': '{}'.format(value[2])}, thumbnail="\\\\GISAPP\\Workspace\\Horizon\\Thumbnails\\Drainage\\{}.png".format(value[0]))

        fs = sdItem.publish(overwrite=True)
        fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)
        n+=1

def ParksandRec():
    prjPath = "\\\\GISAPP\\Workspace\\Horizon\\ArcGISPro_Projects\\ParksandRec\\ParksandRec.aprx"

    dict = {"Trails": ["Trails", "Trails, Parks, Trail Network, Line", "This layer shows the Trail network for the City of Pearland.", 0],
            "Golf Courses": ["Golf_Courses", "Golf Course, Parks, Polygon", "This layer shows the Golf Courses in the City of Pearland.", 1],
            "Parks": ["Parks", "Parks, Polygon, City Owned, Neighborhood", "This layer shows the neighborhood city owned Parks in the City of Pearland.", 2],
            "Park Zones": ["Park_Zones", "Park Zones, Polygon, Parks", "This layer shows the Park Zones in the City of Pearland.", 3],
            "Prairie Restoration":["Prairie_Restoration","Prairie_Restoration, Polygon, Parks","This layer shows the Prairie Restoration Project in the City of Pearland.",4]}
    n = 0
    for key, value in dict.items():

        sd_fs_name = "{}".format(key)
        portal = "https://pearland.maps.arcgis.com"
        user = "MapService_Admin"
        password = "Sdesde81"

        shrOrg = True
        shrEveryone = True
        shrGroups = "c0c1883a34bf479b863dbeaa9a6adffd"

        relPath = "\\\\GISAPP\\Workspace\\Horizon\\Scripts"
        sddraft = os.path.join(relPath, "WebUpdate.sddraft")
        sd = os.path.join(relPath, "WebUpdate.sd")

        arcpy.env.overwriteOutput = True
        prj = arcpy.mp.ArcGISProject(prjPath)
        m = prj.listMaps('Map')[0]
        mp = m.listLayers()[value[3]]
        arcpy.mp.CreateWebLayerSDDraft(mp, sddraft, sd_fs_name, 'MY_HOSTED_SERVICES', 'FEATURE_ACCESS','Administrative_Boundaries', True, True, False, True)
        arcpy.StageService_server(sddraft, sd)

        gis = arcgis.GIS(portal, user, password)
        searchItem = gis.content.search(query="title:"+ value[0] + " AND owner: " + user, item_type="Service Definition", sort_field='title', sort_order='asc')
        for item in searchItem:
            print(item["title"])
            if item["title"] == key:
                sdItem = item
        sdItem.update(data=sd)
        sdItem.update(item_properties={'tags': '{}'.format(value[1]), 'snippet': "This Layer is updated automatically through a Python Script.",
                                       'description': '{}'.format(value[2])}, thumbnail="\\\\GISAPP\\Workspace\\Horizon\\Thumbnails\\ParksandRec\\{}.png".format(value[0]))

        fs = sdItem.publish(overwrite=True)
        fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)
        n+=1

def Schools():
    prjPath = "\\\\GISAPP\\Workspace\\Horizon\\ArcGISPro_Projects\\Schools\\Schools.aprx"
    #key = Feature Service Name, value[0] = Service Definition Name, value[1] = Tags, value[2] = Description, value[3] = Layer Order
    dict = {"Schools": ["Schools", "Schools, School, ISD, PISD, Point", "This layer shows the various Schools located throughout the city.", 0],
            "School Zones": ["School_Zones", "School Zones, Speed Limit, PISD, Line", "This layer shows the School Zones in the city along with their active times and speeds.", 1],
            "Pearland ISD Property": ["Pearland_ISD_Property", "Pearland ISD Property, PISD, Polygon", "This layer shows the land owned by Pearland ISD.", 2],
            "School Districts": ["School_Districts", "School Districts, ISD, PISD, Polygon", "This layer shows the various Independent School Districts within the city.", 3]}
    n = 0
    for key, value in dict.items():

        sd_fs_name = "{}".format(key)
        portal = "https://pearland.maps.arcgis.com"
        user = "MapService_Admin"
        password = "Sdesde81"

        shrOrg = True
        shrEveryone = True
        shrGroups = "c0c1883a34bf479b863dbeaa9a6adffd"

        relPath = "\\\\GISAPP\\Workspace\\Horizon\\Scripts"
        sddraft = os.path.join(relPath, "WebUpdate.sddraft")
        sd = os.path.join(relPath, "WebUpdate.sd")

        arcpy.env.overwriteOutput = True
        prj = arcpy.mp.ArcGISProject(prjPath)
        m = prj.listMaps('Map')[0]
        mp = m.listLayers()[value[3]]
        arcpy.mp.CreateWebLayerSDDraft(mp, sddraft, sd_fs_name, 'MY_HOSTED_SERVICES', 'FEATURE_ACCESS','Schools', True, True, False, True)
        arcpy.StageService_server(sddraft, sd)

        gis = arcgis.GIS(portal, user, password)
        searchItem = gis.content.search(query="title:"+ value[0] + " AND owner: " + user, item_type="Service Definition", sort_field='title', sort_order='asc')
        for item in searchItem:
            print(item["title"])
            if item["title"] == key:
                sdItem = item
        sdItem.update(data=sd)
        sdItem.update(item_properties={'tags': '{}'.format(value[1]), 'snippet': "This Layer is updated automatically through a Python Script.",
                                       'description': '{}'.format(value[2])}, thumbnail="\\\\GISAPP\\Workspace\\Horizon\\Thumbnails\\Schools\\{}.png".format(value[0]))

        fs = sdItem.publish(overwrite=True)
        fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)
        n+=1

def Utilities():
    prjPath = "\\\\GISAPP\\Workspace\\Horizon\\ArcGISPro_Projects\\Utilities\\Utilities.aprx"

    dict = {"Sewer Manhole":["Sewer_Manhole", "Sewer Manhole, Manholes, Public Works, Utilities, Point, Interactive Map", "This Layer shows Sewer Manholes around the City of Pearland.", 0],
            "Sewer Connections":["Sewer_Connections", "Sewer Connections, Public Works, Utilities, Point, Interactive Map", "This Layer shows Sewer Connections around the City of Pearland.", 1],
            "Lift Stations":["Lift_Stations", "Lift Stations, Public Works, Utilities, Point, Interactive Map", "This Layer shows Lift Stations around the City of Pearland.", 2],
            "Wastewater Treatment Plants":["Wastewater_Treatment_Plants","Wastewater Treatment Plants, WWTP, Public Works, Utilities, Point, Interactive Map", "This Layer shows Wastewater Treatment Plants around the City of Pearland.", 3],
            "Meter Boxes":["Meter_Boxes","Meter Boxes, SCADA, Utilities, Public Works, Point, Interactive Map", "This Layer shows Meter Boxes around the City of Pearland.", 4],
            "Hydrants":["Hydrants", "Hydrants, Fire, Public Works, Point, Interactive Map", "This Layer shows Hydrants around the City of Pearland.", 5],
            "Water Valve":["Water_Valve", "Water Valve, Public Works, Point, Interactive Map", "This Layer shows Water Valves around the City of Pearland.", 6],
            "Water Structure":["Water_Structure", "Water Structure, Public Works, Point, Interactive Map", "This Layer shows Water Structures around the City of Pearland.", 7],
            "Storm Inlet":["Storm_Inlet", "Storm Inlet, Public Works, Line, Interactive Map", "This Layer shows Storm Inlets around the City of Pearland.", 8],
            "Storm Manhole":["Storm_Manhole", "Storm Manhole, Public Works, Point, Interactive Map", "This Layer shows Storm Manholes around the City of Pearland.", 9],
            "Light Poles":["Light_Poles", "Light Poles, Public Works, Point, Interactive Map", "This Layer shows Light Poles around the City of Pearland.", 10],
            "Sewer Line":["Sewer_Line", "Sewer Line, Utilities, Public Works, Line, Interactive Map", "This Layer shows Sewer Lines around the City of Pearland.", 11],
            "Water Main":["Water_Main", "Water Main, Utilities, Public Works, Line, Interactive Map", "This Layer shows Water Mains around the City of Pearland.", 12],
            "Lateral":["Lateral", "Hydrant Lateral, Fire, Public Works, Line, Interactive Map", "This Layer shows Hydrant Lateral around the City of Pearland.", 13],
            "Storm Lines":["Storm_Lines", "Storm Lines, Public Works, Line, Interactive Map", "This Layer shows Storm Lines around the City of Pearland.", 14],
            "Wastewater Basins":["Wastewater_Basins", "Wastewater Basins, Public Works, Point, Interactive Map", "This Layer shows Wastewater Basins around the City of Pearland.", 15],
            "PW Grid":["PW_Grid", "PW Grid, Public Works, Point, Interactive Map", "This Layer shows the PW Grid around the City of Pearland.", 16],
            "High Water Markers":["High_Water_Markers", "High Water Markers, EOC, Public Works, Point, Interactive Map", "This Layer shows High Water Markers around the City of Pearland.", 17]}
    n=0
    #"Drainage Districts": ["Drainage_Districts", "Drainage Districts, Administrative Boundaries, Polygon", "This layer contains the various Drainage Districts in the City of Pearland", 2],
    for key, value in dict.items():

        sd_fs_name = "{}".format(key)
        portal = "https://pearland.maps.arcgis.com"
        user = "MapService_Admin"
        password = "Sdesde81"

        shrOrg = True
        shrEveryone = True
        shrGroups = "c0c1883a34bf479b863dbeaa9a6adffd"

        relPath = "\\\\GISAPP\\Workspace\\Horizon\\Scripts"
        sddraft = os.path.join(relPath, "WebUpdate.sddraft")
        sd = os.path.join(relPath, "WebUpdate.sd")

        arcpy.env.overwriteOutput = True
        prj = arcpy.mp.ArcGISProject(prjPath)
        m = prj.listMaps('Map')[0]
        mp = m.listLayers()[value[3]]
        arcpy.mp.CreateWebLayerSDDraft(mp, sddraft, sd_fs_name, 'MY_HOSTED_SERVICES', 'FEATURE_ACCESS','Utilities', True, True, False, True)
        arcpy.StageService_server(sddraft, sd)

        gis = arcgis.GIS(portal, user, password)
        searchItem = gis.content.search(query="title:"+ value[0] + " AND owner: " + user, item_type="Service Definition", sort_field='title', sort_order='asc')
        for item in searchItem:
            print(item["title"])
            if item["title"] == key:
                sdItem = item
        sdItem.update(data=sd)
        sdItem.update(item_properties={'tags': '{}'.format(value[1]), 'snippet': "This Layer is updated automatically through a Python Script.",
                                       'description': '{}'.format(value[2])}, thumbnail="\\\\GISAPP\\Workspace\\Horizon\\Thumbnails\\Utilities\\{}.png".format(value[0]))

        fs = sdItem.publish(overwrite=True)
        fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)
        n+=1

def CIP():

    prjPath = "\\\\GISAPP\\Workspace\\Horizon\\ArcGISPro_Projects\\CIP\\CIPProjects.aprx"

    dict = {"CIPPoints":["CIPPoints", "CIP, Engineering, Point, Interactive Map", "This Layer shows the Point Layer for City Projects.", 0],
            "CIPPolylines":["CIPPolylines", "CIP, Engineering, Line, Interactive Map", "This Layer shows the Point Layer for City Projects.", 1],
            "CIPPolygons":["CIPPolygons", "CIP, Engineering, Polygon, Interactive Map", "This Layer shows the Point Layer for City Projects.", 2],
            }
    n=0
    for key, value in dict.items():

        sd_fs_name = "{}".format(key)
        portal = "https://pearland.maps.arcgis.com"
        user = "MapService_Admin"
        password = "Sdesde81"

        shrOrg = True
        shrEveryone = True
        shrGroups = "c0c1883a34bf479b863dbeaa9a6adffd"

        relPath = "\\\\GISAPP\\Workspace\\Horizon\\Scripts"
        sddraft = os.path.join(relPath, "WebUpdate.sddraft")
        sd = os.path.join(relPath, "WebUpdate.sd")

        arcpy.env.overwriteOutput = True
        prj = arcpy.mp.ArcGISProject(prjPath)
        m = prj.listMaps('Map')[0]
        mp = m.listLayers()[value[3]]
        arcpy.mp.CreateWebLayerSDDraft(mp, sddraft, sd_fs_name, 'MY_HOSTED_SERVICES', 'FEATURE_ACCESS','CIP', True, True, False, True)
        arcpy.StageService_server(sddraft, sd)

        gis = arcgis.GIS(portal, user, password)
        searchItem = gis.content.search(query="title:"+ value[0] + " AND owner: " + user, item_type="Service Definition", sort_field='title', sort_order='asc')
        for item in searchItem:
            print(item["title"])
            if item["title"] == key:
                sdItem = item
        sdItem.update(data=sd)
        sdItem.update(item_properties={'tags': '{}'.format(value[1]), 'snippet': "This Layer is updated automatically through a Python Script.",
                                       'description': '{}'.format(value[2])}, thumbnail="\\\\GISAPP\\Workspace\\Horizon\\Thumbnails\\CIP\\{}.png".format(value[0]))

        fs = sdItem.publish(overwrite=True)
        fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)
        n+=1

def VT():
        MapList = ["General Reference", "Light Canvas", "Night Canvas"]
        prjPath = "\\\\GISAPP\\Workspace\\Horizon\\ArcGISPro_Projects\\VectorTiles\\VectorTiles.aprx"
        prj = arcpy.mp.ArcGISProject(prjPath)

        for m in prj.listMaps():
            if m.name in ["Imagery Reference Layers", "Muted Colors Dashboard"]:
                continue
            updateMap = "\\\\GISAPP\\Workspace\\Horizon\\ArcGISPro_Projects\\VectorTiles\\" + m.name + ".vtpk"
            arcpy.management.CreateVectorTilePackage(m, updateMap, "EXISTING", "\\\\GISAPP\\Workspace\\Horizon\\ArcGISPro_Projects\\VectorTiles\\VTScheme.xml", "INDEXED")

            portal = "https://pearland.maps.arcgis.com"
            user = "MapService_Admin"
            password = "Sdesde81"
            arcpy.SignInToPortal(portal, user, password)
            gis = arcgis.GIS(portal, user, password)

            existingVTile = gis.content.search(m.name + " AND owner: " + user, "Vector Tile Layer")
            for item in existingVTile:
                print(item)
                if item["title"] == m.name:
                    print(item)
                    item.delete()

            existingVPackage = gis.content.search(m.name + " AND owner: " + user, "Vector Tile Package")
            for item in existingVPackage:
                print(item)
                if item["title"] == m.name:
                    print(item)
                    item.delete()

            vtpkItem = gis.content.add({}, updateMap, folder = "Vector Tiles")
            vtpkLayer = vtpkItem.publish()

            currentVTName = m.name + " VT"
            searchItem = gis.content.search(query="title:"+ currentVTName + " AND owner: " + user, item_type="Vector Tile Layer", sort_field='title', sort_order='asc')

            for item in searchItem:
                if item["title"] == currentVTName:
                    print(item)
                    sdItem = item
                    print(sdItem.id)
                    print(vtpkLayer.id)
                    archiveLayer = m.name + "_archive" + datetime.datetime.now().strftime("%m%d%y")
                    arcpy.server.ReplaceWebLayer(str(sdItem.id), archiveLayer, str(vtpkLayer.id), "REPLACE", "FALSE")

main()

end = time.time()
elapsed = end - start
elapsed_min = elapsed / 60
stuff = "\n{:.2f} minutes".format(elapsed_min)
print (stuff)
print("done")

