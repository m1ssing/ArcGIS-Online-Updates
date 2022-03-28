import arcgis
import arcpy
import os
import sys
import time
arcpy.env.overwriteOutput = True


prjPath = "\\\\GISAPP\\Workspace\\Horizon\\ArcGISPro_Projects\\FeatureServices\\InformationTechnology\\CGR.aprx"

dict = {"Connected Grid Routers":["Connected_Grid_Routers", "IT, CGR, Point, AMI", "This Layer shows where Connected Grid Routers(CGR) are located throughout the City.", 0],
        "AMI_Points":["AMI_Points", "UB, AMI, Point", "This Layer shows the AMI meter locations throughout the City.", 1],
        }
n=0
for key, value in dict.items():

    sd_fs_name = "{}".format(key)
    portal = "https://pearland.maps.arcgis.com"
    user = ""
    password = ""

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
    arcpy.mp.CreateWebLayerSDDraft(mp, sddraft, sd_fs_name, 'MY_HOSTED_SERVICES', 'FEATURE_ACCESS','AMI', True, True, False, True)
    arcpy.StageService_server(sddraft, sd)

    gis = arcgis.GIS(portal, user, password)
    searchItem = gis.content.search(query="title:"+ value[0] + " AND owner: " + user, item_type="Service Definition", sort_field='title', sort_order='asc')
    for item in searchItem:
        print(item["title"])
        if item["title"] == key:
            sdItem = item
    sdItem.update(data=sd)
    sdItem.update(item_properties={'tags': '{}'.format(value[1]), 'snippet': "This Layer is updated automatically through a Python Script.",
                                    'description': '{}'.format(value[2])})

    fs = sdItem.publish(overwrite=True)
    fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)
    n+=1

print(".")
