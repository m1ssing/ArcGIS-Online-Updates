import arcpy
import arcgis 
import datetime
import os
import numpy

arcpy.env.overwriteOutput = True
def main():
    #TableImport()
    #caseBaseTable()
    violationsBaseTable()
    #actionsBaseTable()
    #Action()
    #Inspection()
    #Contact()
    Duration()
    #Compliance()
    #stDev()
    #Employee()
    #AddressField()
    #Geocode()
    #Update()

def TableImport():
    ceTables = {"CASE_MAIN" : ["STARTED", "1500"], "CASE_INSPECTIONS": ["COMPLETED_DATE", "1500"], "Case_Actions": ["COMPLETED_DATE", "1500"], "Case_Violations2": ["DATE_OBSERVED", "365"], "LICENSE2_Main": ["ISSUED", "1500"], "LICENSE2_Inspections": ["COMPLETED_DATE", "1500"], "LICENSE2_Actions": ["COMPLETED_DATE", "365"], "Permit_Reviews": ["DATE_SENT", "365"], "LICENSE2_REVIEWS": ["DATE_SENT", "365"], "Inspections": ["COMPLETED_DATE", "365"], "LICENSE2_Inspections": ["COMPLETED_DATE", "365"]}
    originalPath = "\\\\GISAPP\\Workspace\\sdeFiles\\LogosLive.sde"
    newPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb"
    for key, value in ceTables.items():
        originalFile = originalPath + "\\CRW_PROD.dbo." + key
        sql = value[0] + ">= CURRENT_DATE - " + value[1]
        in_mem_table = arcpy.management.CopyRows(originalFile, r"in_memory\tbl")
        arcpy.conversion.TableToTable(in_mem_table, newPath, key, sql)
        del in_mem_table

def caseBaseTable():
    #Creates Base Table to be consumed by Dashboard
    caseMain = ["CASE_NO", "STARTED", "CLOSED", "CaseSubType", "STATUS", "SITE_ADDR"]
    caseTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\CASE_MAIN"
    newTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb"
    #Creating Field mapping
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(caseTable)
    #Removing all Fields that aren't needed in the end product
    for f in fieldmappings.fields:
            if f.name not in caseMain:
                fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(f.name))
    arcpy.conversion.TableToTable(caseTable, newTable, "Dashboard_Case", "", fieldmappings)

def violationsBaseTable():
    #Creates Base Table to be consumed by Dashboard
    violationsMain = ["CASE_NO", "DATE_OBSERVED", "DATE_CORRECTED", "Violation_Type", "USERID", "STATUS"]
    violationsTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Case_Violations2"
    newTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb"
    #Creating Field mapping
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(violationsTable)
    #Removing all Fields that aren't needed in the end product
    for f in fieldmappings.fields:
            if f.name not in violationsMain:
                fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(f.name))
    arcpy.conversion.TableToTable(violationsTable, newTable, "Dashboard_Violations", "", fieldmappings)
    print("done")
def actionsBaseTable():
    #Creates Base Table to be consumed by Dashboard
    violationsMain = ["CASE_NO", "ACTION_BY", "ACTION_DATE", "COMPLETED_DATE", "ACTION_TYPE"]
    violationsTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Case_Actions"
    newTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb"
    #Creating Field mapping
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(violationsTable)
    #Removing all Fields that aren't needed in the end product
    for f in fieldmappings.fields:
            if f.name not in violationsMain:
                fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(f.name))
    arcpy.conversion.TableToTable(violationsTable, newTable, "Dashboard_Actions", "", fieldmappings)

def Action():
    firstAction = {}
    recentAction = {}
    #Identify First Action(Chronology or Inspection) taken on a case for use in the Dashboard
    #Search through Actions to find first response
    actionsLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Case_Actions"
    actionsFields = ["CASE_NO", "ACTION_BY", "ACTION_TYPE", "COMPLETED_DATE"]
    #Create Working Dictionary to determine which Action is first before adding to the First Action Dictionary
    workingDict = {}
    with arcpy.da.SearchCursor(actionsLayer, actionsFields) as Scur:
        for row in Scur:
            if row[0] in workingDict.keys():
                workingDict[row[0]].append(row[3])
            else:
                workingDict[row[0]] = [row[3]]


    dashLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Dashboard_Case"
    arcpy.management.AddField(dashLayer, "firstActionDate", "DATE")
    arcpy.management.AddField(dashLayer, "recentActionDate", "DATE")

    fieldsFA = ["CASE_NO", "firstActionDate", "recentActionDate"]
    with arcpy.da.UpdateCursor(dashLayer, fieldsFA) as Ucur:
        for row in Ucur:
            for key, value in workingDict.items():
                if key == row[0]:
                    fA = min(value)
                    rA = max(value)
                    row[1] = fA
                    row[2] = rA
                    Ucur.updateRow(row)

def Inspection():
    inspection = {}
    actionsLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Inspections"
    actionsFields = ["ActivityID", "COMPLETED_DATE"]

    workingDict = {}
    with arcpy.da.SearchCursor(actionsLayer, actionsFields) as Scur:
        for row in Scur:
            if row[0] in workingDict.keys():
                workingDict[row[0]].append(row[1])
            else:
                workingDict[row[0]] = [row[1]]


    dashLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Dashboard_Case"
    arcpy.management.AddField(dashLayer, "firstInspectionDate", "DATE")
    arcpy.management.AddField(dashLayer, "recentInspectionDate", "DATE")
    fields = ["CASE_NO", "firstInspectionDate", "recentInspectionDate"]
    with arcpy.da.UpdateCursor(dashLayer, fields) as Ucur:
        for row in Ucur:
            for key, value in workingDict.items():
                if key == row[0]:
                    ins = min(value)
                    newins = max(value)
                    row[1] = ins
                    row[2] = newins
                    Ucur.updateRow(row)

def Contact():
    dashLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Dashboard_Case"
    arcpy.management.AddField(dashLayer, "firstContactDate", "DATE")
    fields = ["firstActionDate", "firstInspectionDate", "firstContactDate"]
    with arcpy.da.UpdateCursor(dashLayer, fields) as Ucur:
        for row in Ucur:
            if row[0] is not None and row[1] is not None:
                datelst = []
                datelst.append(row[0])
                datelst.append(row[1])
                newDate = min(datelst)
                row[2] = newDate
                Ucur.updateRow(row)
            if row[0] is not None and row[1] is None:
                row[2] = row[0]
                Ucur.updateRow(row)
            if row[0] is None and row[1] is not None:
                row[2] = row[1]
                Ucur.updateRow(row)

    dashLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Dashboard_Case"
    arcpy.management.AddField(dashLayer, "recentContactDate", "DATE")
    fields = ["recentActionDate", "recentInspectionDate", "recentContactDate"]
    with arcpy.da.UpdateCursor(dashLayer, fields) as Ucur:
        for row in Ucur:
            if row[0] is not None and row[1] is not None:
                datelst = []
                datelst.append(row[0])
                datelst.append(row[1])
                newDate = min(datelst)
                row[2] = newDate
                Ucur.updateRow(row)
            if row[0] is not None and row[1] is None:
                row[2] = row[0]
                Ucur.updateRow(row)
            if row[0] is None and row[1] is not None:
                row[2] = row[1]
                Ucur.updateRow(row)

def Duration():
    dashLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Dashboard_Case"
    arcpy.management.AddField(dashLayer, "DurationContact", "DOUBLE")
    fields = ["STARTED", "firstContactDate", "DurationContact"]
    with arcpy.da.UpdateCursor (dashLayer, fields) as Ucur:
        for row in Ucur:
            if row[1] is None and row[0] is not None:
                duration = datetime.datetime.today() - row[0]
                row[2] = duration.days
                Ucur.updateRow(row)
            if row[1] is not None and row[0] is not None:
                duration = row[1] - row[0]
                row[2] = duration.days
                Ucur.updateRow(row)
            else:
                pass
    
    dashLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Dashboard_Violations"
    arcpy.management.AddField(dashLayer, "DurationComply", "DOUBLE")
    fields = ["DATE_OBSERVED", "DATE_CORRECTED", "DurationComply"]
    with arcpy.da.UpdateCursor (dashLayer, fields) as Ucur:
        for row in Ucur:
            if row[1] is None and row[0] is not None:
                duration = datetime.datetime.today() - row[0]
                row[2] = duration.days
                Ucur.updateRow(row)
            if row[1] is not None and row[0] is not None:
                duration = row[1] - row[0]
                row[2] = duration.days
                Ucur.updateRow(row)
            else:
                pass

    dictFields = ["CASE_NO", "DurationComply"]
    testDict = {}
    with arcpy.da.SearchCursor(dashLayer, dictFields) as Scur:
        for row in Scur:
            if row[0] in testDict.keys():
                testDict[row[0]].append(row[1])
            else:
                testDict[row[0]] = [row[1]]
    testlst = []
    perclst = []
    for key, value in testDict.items():
        newset = set(value)
        for x in newset:
            testlst.append(x)

    

    percent = numpy.percentile(testlst, 90)
    print(percent)
    print(testlst)


def Compliance():
    #Calculate compliance of Violation 10 days ultimate goal/ 30 day fallback goal
    violationPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Dashboard_Violations"
    arcpy.management.AddField(violationPath, "Compliance10", "TEXT")
    fields = ["DATE_OBSERVED", "DATE_CORRECTED", "Compliance10"]
    with arcpy.da.UpdateCursor(violationPath, fields) as Ucur:
        for row in Ucur:
            if row[0] is not None and row[1] is not None:
                duration = row[1] - row[0]
                comply = duration.days
                if comply <= 10:
                    row[2] = "Full Compliance"
                    Ucur.updateRow(row)
                else:
                    row[2] = "Not within Compliance"
                    Ucur.updateRow(row)
            if row[0] is not None and row[1] is None:
                duration = datetime.datetime.today() - row[0]
                comply = duration.days
                if comply <= 10:
                    row[2] = "Compliance to be Determined"
                    Ucur.updateRow(row)
                if comply > 10:
                    row[2] = "Not within Compliance"
                    Ucur.updateRow(row)
        del Ucur

    arcpy.management.AddField(violationPath, "Compliance30", "TEXT")
    fields = ["DATE_OBSERVED", "DATE_CORRECTED", "Compliance30"]
    with arcpy.da.UpdateCursor(violationPath, fields) as Ucur:
        for row in Ucur:
            if row[0] is not None and row[1] is not None:
                duration = row[1] - row[0]
                comply = duration.days
                if comply <= 30:
                    row[2] = "Full Compliance"
                    Ucur.updateRow(row)
                else:
                    row[2] = "Not within Compliance"
                    Ucur.updateRow(row)
            if row[0] is not None and row[1] is None:
                duration = datetime.datetime.today() - row[0]
                comply = duration.days
                if comply <= 30:
                    row[2] = "Compliance to be Determined"
                    Ucur.updateRow(row)
                if comply > 30:
                    row[2] = "Not within Compliance"
                    Ucur.updateRow(row)

def stDev():
    mainTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Dashboard_Violations"
    fields = ["DurationComply"]
    outlst =[]
    percentlst = []
    with arcpy.da.SearchCursor(mainTable, fields) as Scur:
        for row in Scur:
            if row[0] != None:
                outlst.append(row[0])
            else:
                pass

    arcpy.management.AddField(mainTable, "num_status", "TEXT")
    stdv = numpy.std(outlst)
    avgOutlier= sum(outlst) / len(outlst)
    sdtvOutlier = avgOutlier + stdv * 3
    fields = ["DurationComply", "num_status"]
    with arcpy.da.UpdateCursor(mainTable, fields) as Scur:
        for row in Scur:
            if row[0] == None:
                pass
            elif row[0] >= sdtvOutlier:
                row[1] = "Outlier"
                Scur.updateRow(row)
            else:
                percentlst.append(row[0])

    avg = sum(percentlst) / len(percentlst)
    numPercentile = numpy.percentile(percentlst, 90)
    print(avg, numPercentile)
    statusField = ["num_status", "DurationComply"]
    with arcpy.da.UpdateCursor(mainTable, statusField) as Ucur:
        for row in Ucur:
            if row[1] == None:
                continue
            if row[1] >= sdtvOutlier or row[1] == None:
                pass
            if row[1] > numPercentile and row[1] < sdtvOutlier:
                row[0] = "Not within 90th Percentile"
                Ucur.updateRow(row)
            if row[1] <= numPercentile:
                row[0] = "Within 90th Percentile"
                Ucur.updateRow(row)

def Employee():
    employeeDict = {"0020": "Marisa Vazquez", "0021": "Ed Kimberly", "0022": "Belinda Cowan", "0023": "Rance Rhame", "0024": "Carey Blair", "0025": "James Polanco", "0026": "Darlene Estrada", "STHA": "Stephanie Hauck"}
    dashLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Dashboard_Violations"
    arcpy.management.AddField(dashLayer, "EmployeeName", "TEXT")
    fields = ["UserID", "EmployeeName"]
    with arcpy.da.UpdateCursor (dashLayer, fields) as Ucur:
        for row in Ucur:
            for key, value in employeeDict.items():
                if row[0] == key:
                    row[1] = value
                    Ucur.updateRow(row)

def AddressField():
    caseMain = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Dashboard_Case"
    caseMainFields = ["CASE_NO", "SITE_ADDR"]
    addrDict = {}
    with arcpy.da.SearchCursor(caseMain, caseMainFields) as Scur:
        for row in Scur:
            addrDict[row[0]] = row[1]
    print("a")

    caseViolations = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Dashboard_Violations"
    arcpy.management.AddField(caseViolations, "SITE_ADDR", "TEXT")
    caseViolationsFields =  ["CASE_NO", "SITE_ADDR"]
    with arcpy.da.UpdateCursor(caseViolations, caseViolationsFields) as Ucur:
        for row in Ucur:
            for key,value in addrDict.items():
                if key == row[0]:
                    row[1] = value
                    Ucur.updateRow(row)
    print("b")

    caseActions = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Dashboard_Actions"
    arcpy.management.AddField(caseActions, "SITE_ADDR", "TEXT")
    caseActionsFields =  ["CASE_NO", "SITE_ADDR"]
    with arcpy.da.UpdateCursor(caseActions, caseActionsFields) as Ucur:
        for row in Ucur:
            for key,value in addrDict.items():
                if key == row[0]:
                    row[1] = value
                    Ucur.updateRow(row)

def Geocode():
    layerName = ["Case"]
    for i in layerName:

        if arcpy.Exists("\\\\gisapp\\workspace\\gis staff workspace\\cschultz\\CodeEnforcement.gdb\\Analytics_{}".format(i)) == True:
            arcpy.management.Delete("\\\\gisapp\\workspace\\gis staff workspace\\cschultz\\CodeEnforcement.gdb\\Analytics_{}".format(i))
        arcpy.geocoding.GeocodeAddresses("\\\\gisapp\\workspace\\gis staff workspace\\cschultz\\CodeEnforcement.gdb\\Dashboard_{}".format(i), "\\\\gisapp\\Workspace\\MyArcGIS\\Geocoders\\AM_Composite.loc", "'Single Line Input' SITE_ADDR VISIBLE NONE", "\\\\gisapp\\workspace\\gis staff workspace\\cschultz\\CodeEnforcement.gdb\\Analytics_{}".format(i), "STATIC", None, '', None, "LOCATION_ONLY")
        print(i)

def Update():

    prjPath = "\\\\GISAPP\\Workspace\\Horizon\\ArcGISPro_Projects\\FeatureServices\\CodeEnforcement\\CodeEnforcement.aprx"

    dict = {
            "License_Main": ["License_Main","City Boundaries, City Limits, ETJ, General, Administrative Boundaries, Polygon", "This layer contains the City Limits and Extra Territorial Jurisdiction (ETJ) for the City of Pearland.",0],
            "Permit_Reviews": ["Permit_Reviews","City Boundaries, City Limits, ETJ, General, Administrative Boundaries, Polygon", "This layer contains the City Limits and Extra Territorial Jurisdiction (ETJ) for the City of Pearland.",1],
            "License_Reviews": ["License_Reviews","City Boundaries, City Limits, ETJ, General, Administrative Boundaries, Polygon", "This layer contains the City Limits and Extra Territorial Jurisdiction (ETJ) for the City of Pearland.",2],
            "Inspections": ["Inspections","City Boundaries, City Limits, ETJ, General, Administrative Boundaries, Polygon", "This layer contains the City Limits and Extra Territorial Jurisdiction (ETJ) for the City of Pearland.",3],
            "Dashboard_Case": ["Dashboard_Case","City Boundaries, City Limits, ETJ, General, Administrative Boundaries, Polygon", "This layer contains the City Limits and Extra Territorial Jurisdiction (ETJ) for the City of Pearland.",4],
            "Dashboard_Actions": ["Dashboard_Actions","City Boundaries, City Limits, ETJ, General, Administrative Boundaries, Polygon", "This layer contains the City Limits and Extra Territorial Jurisdiction (ETJ) for the City of Pearland.",5],
            "Dashboard_Violations": ["Dashboard_Violations","City Boundaries, City Limits, ETJ, General, Administrative Boundaries, Polygon", "This layer contains the City Limits and Extra Territorial Jurisdiction (ETJ) for the City of Pearland.",6]
            }
    n=0

    for key, value in dict.items():
        sd_fs_name = "{}".format(key)
        portal = "https://pearland.maps.arcgis.com"
        user = ""
        password = ""

        shrOrg = True
        shrEveryone = True


        relPath = "\\\\GISAPP\\Workspace\\Horizon\\Scripts"
        sddraft = os.path.join(relPath, "WebUpdate.sddraft")
        sd = os.path.join(relPath, "WebUpdate.sd")

        arcpy.env.overwriteOutput = True
        prj = arcpy.mp.ArcGISProject(prjPath)
        m = prj.listMaps('Map')[0]
        mp = m.listTables()[value[3]]
        arcpy.mp.CreateWebLayerSDDraft(mp, sddraft, sd_fs_name, 'MY_HOSTED_SERVICES', 'FEATURE_ACCESS','CodeEnforcement', True, True, False, True)
        arcpy.StageService_server(sddraft, sd)

        gis = arcgis.GIS(portal, user, password)
        searchItem = gis.content.search(query="title:"+ value[0] + " AND owner: " + user, item_type="Service Definition", sort_field='title', sort_order='asc')
        print(searchItem)
        for item in searchItem:
            print(item["title"])
            if item["title"] == key:
                sdItem = item
        sdItem.update(data=sd)
        sdItem.update(item_properties={'tags': '{}'.format(value[1]), 'snippet': "This Table is updated automatically through a Python Script.",
                                        'description': '{}'.format(value[2])})

        fs = sdItem.publish(overwrite=True)
        fs.share(org=shrOrg, everyone=shrEveryone)
        print(sd_fs_name, "done")

main()
print(".")

