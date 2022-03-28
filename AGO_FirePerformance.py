import arcpy
import arcgis 
import datetime
import os
import numpy

arcpy.env.overwriteOutput = True
arcpy.env.workspace = "\\\\gisapp\\Workspace\\gis staff workspace\\cschultz\\FireDashboard.gdb"
def main():
    #FireHouseTable()
    #SummarizeWithin()
    print(".")
def FireHouseTable():
    #FireHouse view starts in 2018
    vwFireHouse = "\\\\GISAPP\\Workspace\\sdeFiles\\FireHouse.sde\\Firehouse.dbo.FirehouseReport_VIEW"
    pointLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireDashboard.gdb\\FireHouseWGS84"
    arcpy.management.XYTableToPoint(vwFireHouse, pointLayer, "longitude", "latitude", "", 4326)

    finalXYLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireDashboard.gdb\\FireHouseXY"
    arcpy.management.Project(pointLayer, finalXYLayer, 2278)
    arcpy.management.Delete(pointLayer)

    ytdPath = "\\\\gisapp\\Workspace\\gis staff workspace\\cschultz\\FireDashboard.gdb"
    ytdName = "FireHouse_YTD"
    ytdQuery = "disp_date >= (current_date- 365) And longitude NOT IN (0, 1) And latitude NOT IN (0, 1)"
    arcpy.conversion.FeatureClassToFeatureClass(finalXYLayer, ytdPath, ytdName, ytdQuery)
    
    inDissolve = "\\\\gisapp\\Workspace\\gis staff workspace\\cschultz\\FireDashboard.gdb\\FireHouse_YTD"
    outDissolve = "\\\\gisapp\\Workspace\\gis staff workspace\\cschultz\\FireDashboard.gdb\\FireHouse_YTD_Incident"
    arcpy.analysis.PairwiseDissolve(inDissolve, outDissolve, "inci_id;station", "unit UNIQUE", "SINGLE_PART")
    arcpy.management.AlterField(outDissolve, "UNIQUE_unit", "UnitCount", "UnitCount")

    outSpatialJoin = "\\\\gisapp\\Workspace\\gis staff workspace\\cschultz\\FireDashboard.gdb\\FireHouse_YTD_ESDJoin"
    esdSpatialJoin = "\\\\GISAPP\\Workspace\\sdeFiles\\Horizon_Viewer.sde\\Horizon.DBO.AdministrativeBoundaries\\Horizon.DBO.ESD"
    arcpy.analysis.SpatialJoin(outDissolve, esdSpatialJoin, outSpatialJoin)
    arcpy.management.DeleteField(outSpatialJoin, ["Join_Count", "TARGET_FID"])

def SummarizeWithin():
    summarizeWithin = {"Incident": "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireDashboard.gdb\\FireHouse_YTD_Incident"}

    for key, value in summarizeWithin.items():
        gridLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireDashboard.gdb\\summarizeGrid"
        outLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireDashboard.gdb\\" + key 
        outTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireDashboard.gdb\\" + key 
        print(outLayer,"\n", outTable)
        arcpy.analysis.SummarizeWithin(gridLayer, value, outLayer, "ONLY_INTERSECTING", "UnitCount Sum", "NO_SHAPE_SUM", "", "station", "NO_MIN_MAJ", "NO_PERCENT", outTable)
main()
arcpy.analysis.SummarizeWithin(r"\\gisapp\Workspace\gis staff workspace\cschultz\FireDashboard.gdb\summarizeGrid", r"\\gisapp\Workspace\gis staff workspace\cschultz\FireDashboard.gdb\FireHouse_YTD_Incident", r"\\gisapp\Workspace\gis staff workspace\cschultz\FireDashboard.gdb\IncidentReport_YTD_SummarizeWithin", "ONLY_INTERSECTING", "UnitCount Sum", "ADD_SHAPE_SUM", '', "station", "NO_MIN_MAJ", "NO_PERCENT", r"\\gisapp\Workspace\gis staff workspace\cschultz\FireDashboard.gdb\IncidentReport_SummaryTable")
print("--AGO Fire Performance.--")
