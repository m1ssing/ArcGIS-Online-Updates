import arcpy
import arcgisscripting
import os
from arcgis.gis import GIS
import arcgis.gis.admin
import time

def main():
    RebuildLocators()
    #AssetMgmt()
    InteractiveMap()

def RebuildLocators():

    arcpy.env.overwriteOutput = True
    rebuild = ["AM_Intersections.loc", "AM_Parks.loc", "DualRangeGeocoder.loc", "AM_Facilities.loc", "IM_Address.loc", "IM_Streets.loc", "IM_Neighborhoods.loc", "AM_Composite.loc", "IM_Composite.loc"]
    for locName in rebuild:
        locUpdate = "\\\\GISAPP\\Workspace\\MyArcGIS\\Geocoders\\" + locName
        print(locUpdate)
        arcpy.geocoding.RebuildAddressLocator(locUpdate)

def AssetMgmt():
        
    arcpy.SignInToPortal("https://gis.pearlandtx.gov/arcgis/", "portaladmin", "Horizon81")
    locPath = "\\\\GISAPP\\Workspace\\MyArcGIS\\Geocoders\\AM_Composite.loc"
    sddraftFile = "\\\\GISAPP\\Workspace\\Horizon\\Scripts\\GeocodeUpdate.sddraft"
    sdFile = "\\\\GISAPP\\Workspace\\Horizon\\Scripts\\GeocodeUpdate.sd"
    geocodeService = ["AM_Composite"]
    summary = "Geocoder for Use in CityWorks"
    tags = "Geocoder"
    serverFile = "https://gis.pearlandtx.gov/hosting/rest/services"
    for x in geocodeService:

        analyze_messages = arcpy.CreateGeocodeSDDraft(locPath, sddraftFile, x, server_type= "ARCGIS_SERVER", connection_file_path= serverFile, copy_data_to_server=True, summary=summary, tags=tags, max_result_size=20, max_batch_size=1000, suggested_batch_size=1000,  overwrite_existing_service=True)

        if analyze_messages['errors'] == {}:
            try:
                arcpy.server.StageService(sddraftFile, sdFile)
                arcpy.server.UploadServiceDefinition(sdFile, serverFile)
                print("The geocode service was successfully published")
            except arcpy.ExecuteError:
                print("An error occurred")
                print(arcpy.GetMessages(2))

    gis = arcgis.GIS("https://gis.pearlandtx.gov/arcgis/", "portaladmin", "Horizon81")
    searchItem = gis.content.search(query="title: "+ "AM_Composite" + " AND owner: " + "portaladmin", item_type = "Geocode Service", sort_field='title', sort_order='asc')
    for item in searchItem:
        print(item["title"])
        if item["title"] == "AM_Composite":
            sdItem = item
    sdItem.share(everyone=True)

def InteractiveMap():
    arcpy.SignInToPortal("https://gis.pearlandtx.gov/arcgis/", "portaladmin", "Horizon81")
    locPath = "\\\\GISAPP\\Workspace\\MyArcGIS\\Geocoders\\IM_Composite.loc"
    sddraftFile = "\\\\GISAPP\\Workspace\\Horizon\\Scripts\\GeocodeUpdate.sddraft"
    sdFile = "\\\\GISAPP\\Workspace\\Horizon\\Scripts\\GeocodeUpdate.sd"
    geocodeService = ["IM_Composite"]
    summary = "Geocoder for Use in CityWorks"
    tags = "Geocoder"
    serverFile = "https://gis.pearlandtx.gov/hosting/rest/services"
    for x in geocodeService:

        analyze_messages = arcpy.CreateGeocodeSDDraft(locPath, sddraftFile, x, server_type= "ARCGIS_SERVER", connection_file_path= serverFile, copy_data_to_server=True, summary=summary, tags=tags, max_result_size=20, max_batch_size=1000, suggested_batch_size=1000,  overwrite_existing_service=True)

        if analyze_messages['errors'] == {}:
            try:
                arcpy.server.StageService(sddraftFile, sdFile)
                arcpy.server.UploadServiceDefinition(sdFile, serverFile)
                print("The geocode service was successfully published")
            except arcpy.ExecuteError:
                print("An error occurred")
                print(arcpy.GetMessages(2))

    gis = arcgis.GIS("https://gis.pearlandtx.gov/arcgis/", "portaladmin", "Horizon81")
    searchItem = gis.content.search(query="title: "+ "IM_Composite" + " AND owner: " + "portaladmin", item_type = "Geocode Service", sort_field='title', sort_order='asc')
    for item in searchItem:
        print(item["title"])
        if item["title"] == "IM_Composite":
            sdItem = item
    sdItem.share(everyone=True)
main()
print(".")