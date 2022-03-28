import arcpy
import datetime
import os
import arcgis

arcpy.env.overwriteOutput = True
def main():
    TableImport()
    ##Duration()
    #Compliance()
    #FirstInspection()
    #Dashboard()
    #Geocode()
    #CaseAge()
    #ActiveCase()
    #Update()

def TableImport():
    ceTables = {"CASE_MAIN" : ["STARTED", "1500"], "CASE_INSPECTIONS": ["COMPLETED_DATE", "1500"], "Case_Actions": ["COMPLETED_DATE", "1500"], "Case_Violations2": ["DATE_OBSERVED", "1500"], "LICENSE2_Main": ["ISSUED", "1500"], "LICENSE2_Inspections": ["COMPLETED_DATE", "1500"], "LICENSE2_Actions": ["COMPLETED_DATE", "365"], "Permit_Reviews": ["DATE_SENT", "365"], "LICENSE2_REVIEWS": ["DATE_SENT", "365"], "Inspections": ["COMPLETED_DATE", "365"], "LICENSE2_Inspections": ["COMPLETED_DATE", "365"]}
    originalPath = "\\\\GISAPP\\Workspace\\sdeFiles\\LogosLive.sde"
    newPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb"
    for key, value in ceTables.items():
        originalFile = originalPath + "\\CRW_PROD.dbo." + key
        sql = value[0] + ">= CURRENT_DATE - " + value[1]
        in_mem_table = arcpy.management.CopyRows(originalFile, r"in_memory\tbl")
        arcpy.conversion.TableToTable(in_mem_table, newPath, key, sql)
        del in_mem_table

def Duration():
    #Calculate Case Duration for CODE ENFORCEMENT Cases
    mainPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\CASE_MAIN"
    arcpy.management.AddField(mainPath, "DurationDays", "Double")
    fields = ["STARTED", "CLOSED", "DurationDays"]
    with arcpy.da.UpdateCursor (mainPath, fields) as Ucur:
        for row in Ucur:
            if row[1] is None and row[0] is not None:
                duration = datetime.datetime.today() - row[0]
                row[2] = duration.days
                Ucur.updateRow(row)
            if row[1] is not None and row[0] is not None:
                duration = row[1] - row[0]
                row[2] = duration.days
            else:
                pass

    #Calculate Inspection Duration from Complaint to Inspection
    inspectionPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\CASE_INSPECTIONS"
    arcpy.management.AddField( inspectionPath, "DurationDays", "Double")
    fields = ["CREATED_DATE", "COMPLETED_DATE", "DurationDays"]
    with arcpy.da.UpdateCursor ( inspectionPath, fields) as Ucur:
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

    #Calculate Violation duration
    violationPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Case_Violations2"
    arcpy.management.AddField(violationPath, "ViolationDuration", "Double")
    fields = ["DATE_OBSERVED", "DATE_CORRECTED", "ViolationDuration", "CASE_NO"]
    with arcpy.da.UpdateCursor (violationPath, fields) as Ucur:
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

def Compliance():
    #Calculate compliance of Violation 10 days ultimate goal/ 30 day fallback goal
    violationPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Case_Violations2"
    arcpy.management.AddField(violationPath, "GoalCompliance", "TEXT")
    fields = ["DATE_OBSERVED", "DATE_CORRECTED", "GoalCompliance"]
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
                    row[2] = "Complaince to be Determined"
                    Ucur.updateRow(row)
                if comply > 10:
                    row[2] = "Not within Compliance"
                    Ucur.updateRow(row)

    arcpy.management.AddField(violationPath, "Compliance", "TEXT")
    fields = ["DATE_OBSERVED", "DATE_CORRECTED", "Compliance"]
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
                    row[2] = "Complaince to be Determined"
                    Ucur.updateRow(row)
                if comply > 30:
                    row[2] = "Not within Compliance"
                    Ucur.updateRow(row)

def FirstInspection():
    # Calculate time between case start and first inspection
    inPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb"
    inField = "FirstInspection"
    layer = inPath + "\\" + inField
    arcpy.management.CreateTable(inPath, inField)
    arcpy.management.AddField(layer, "Case_NO", "TEXT")
    arcpy.management.AddField(layer, "CaseStarted", "DATE")
    arcpy.management.AddField(layer, "InspectedDate", "DATE")
    arcpy.management.AddField(layer, "Duration", "DOUBLE")
    fields = ["Case_NO", "CaseStarted", "InspectedDate", "Duration"]

    #Case Started
    caseMain = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\CASE_MAIN"
    caseFields = ["CASE_NO", "STARTED"]
    caseDict = {}
    delta = datetime.timedelta(days = 365)
    with arcpy.da.SearchCursor(caseMain, caseFields) as Scur:
        timeframe = datetime.datetime.now() - delta
        print(timeframe)
        for row in Scur:
            if row[1] >= timeframe:
                caseDict[row[0]] = row[1]
    dictLength = len(caseDict)
    with arcpy.da.InsertCursor(layer, fields) as Icur:
        for key, value in caseDict.items():
            Icur.insertRow((key, value, datetime.datetime(2999, 12, 31, 0, 0), 0))
    del Icur

    #First Inspection
    inspectionDict = {}
    insMain = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\CASE_INSPECTIONS"
    insFields = ["CASE_NO", "COMPLETED_DATE"]
    with arcpy.da.SearchCursor(insMain, insFields) as Scur:
            for row in Scur:
                if row[0] in inspectionDict.keys():
                    if row[1] != None:
                        inspectionDict[row[0]].append(row[1])
                else:
                    if row[1] != None:
                        inspectionDict[row[0]] = [row[1]]
    with arcpy.da.UpdateCursor(layer, fields) as Ucur:
        for row in Ucur:
            for key, value in inspectionDict.items():
                if row[0] == key:
                    newlst = []
                    for x in value:  
                        if x >= row[1]:
                            newlst.append(x)
                        if newlst == []:
                            continue
                        row[2] = min(newlst)
                        Ucur.updateRow(row)

    #Duration
    with arcpy.da.UpdateCursor(layer, fields) as Ucur:
        for row in Ucur:
            duration = row[2] - row[1]
            row[3] = duration.days
            Ucur.updateRow(row)

                
def Dashboard():
    #Making the Cas Combined Live layer
    mainPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\CASE_MAIN"
    newTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\CASE_Combined"

    KEEP_LIST = ["CASE_NO", "CaseType", "CaseSubType", "STARTED", "DurationDays", "SITE_ADDR"]
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(mainPath)

    for f in fieldmappings.fields:
            if f.name not in KEEP_LIST:
                fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(f.name))

    arcpy.conversion.TableToTable(mainPath, "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb", "CASE_Combined", "PREFIX = 'CE'", fieldmappings)


    #Chronology
    table = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Case_Actions"
    dict = {}
    fields = ["CASE_NO", "COMPLETED_DATE"]
    delta = datetime.timedelta(days = 90)
    now = datetime.datetime.now()
    with arcpy.da.SearchCursor(table, fields) as Scur:
            for row in Scur:
                if row[0] in dict.keys():
                    if row[1] != None:
                        dict[row[0]].append(row[1])
                else:
                    if row[1] != None:
                        dict[row[0]] = [row[1]]

    arcpy.management.AddField(newTable, "Chronology", "LONG")
    ufields = ["CASE_NO", "Chronology", "STARTED"]

    with arcpy.da.UpdateCursor(newTable, ufields) as Ucur:
        for row in Ucur:
            
            if row[2] == None:
                continue
            else:
                for key,value in dict.items():
                    newRow = len(value)
                    if row[0] == key:            
                        row[1] = newRow
                        Ucur.updateRow(row)

    #Inspections

    table = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\CASE_INSPECTIONS"
    dict = {}
    fields = ["CASE_NO", "COMPLETED_DATE"]
    delta = datetime.timedelta(days = 90)
    now = datetime.datetime.now()
    with arcpy.da.SearchCursor(table, fields) as Scur:
            for row in Scur:
                if row[0] in dict.keys():
                    if row[1] != None:
                        dict[row[0]].append(row[1])
                else:
                    if row[1] != None:
                        dict[row[0]] = [row[1]]

    arcpy.management.AddField(newTable, "Inspections", "LONG")
    ufields = ["CASE_NO", "Inspections", "STARTED"]

    with arcpy.da.UpdateCursor(newTable, ufields) as Ucur:
        for row in Ucur:
            query = now - delta
            if row[2] == None:
                continue
            else:
                for key,value in dict.items():
                    newRow = len(value)
                    if row[0] == key:            
                        row[1] = newRow
                        Ucur.updateRow(row)

    #Violations

    table = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Case_Violations2"
    dict = {}
    fields = ["CASE_NO", "DATE_OBSERVED"]
    delta = datetime.timedelta(days = 90)
    now = datetime.datetime.now()
    with arcpy.da.SearchCursor(table, fields) as Scur:
            for row in Scur:
                if row[0] in dict.keys():
                    if row[1] != None:
                        dict[row[0]].append(row[1])
                else:
                    if row[1] != None:
                        dict[row[0]] = [row[1]]

    arcpy.management.AddField(newTable, "Violations", "LONG")
    ufields = ["CASE_NO", "Violations", "STARTED"]

    with arcpy.da.UpdateCursor(newTable, ufields) as Ucur:
        for row in Ucur:
            query = now - delta
            if row[2] == None:
                continue
            else:
                for key,value in dict.items():
                    newRow = len(value)
                    if row[0] == key:            
                        row[1] = newRow
                        Ucur.updateRow(row)

    #Duration
    table = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\Case_Violations2"
    dict = {}
    fields = ["CASE_NO", "ViolationDuration"]

    delta = datetime.timedelta(days = 90)
    now = datetime.datetime.now()
    with arcpy.da.SearchCursor(table, fields) as Scur:
            for row in Scur:
                if row[0] in dict.keys():
                    if row[1] != None:
                        dict[row[0]].append(row[1])
                else:
                    if row[1] != None:
                        dict[row[0]] = [row[1]]
    print(dict)
    arcpy.management.AddField(newTable, "ViolationDuration", "LONG")
    ufields = ["CASE_NO", "ViolationDuration"]

    with arcpy.da.UpdateCursor(newTable, ufields) as Ucur:
        for row in Ucur:
            for key,value in dict.items():
                newRow = sum(value) / len(value)
                if row[0] == key:            
                    row[1] = newRow
                    Ucur.updateRow(row)

    
def Geocode():
    #not sure if still needed
    inTable  = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\CASE_Combined"
    loc = "\\\\GISAPP\\Workspace\\MyArcGIS\\Geocoders\\DualRangeGeocoder.loc"
    inField = "SITE_ADDR"
    outTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\CASE_CombinedLIVE"
    arcpy.geocoding.GeocodeAddresses(inTable, loc, "'Single Line Input' SITE_ADDR VISIBLE NONE", outTable, "", "", "", "", "Minimal")

def CaseAge():
    #Determines if a case is new (Case start date within past 30 days)
    inTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\CASE_CombinedLIVE"
    arcpy.management.AddField(inTable, "NewCase", "TEXT")
    fields = ["STARTED", "NewCase"]
    now = datetime.datetime.today()
    delta = datetime.timedelta(days = 30)

    with arcpy.da.UpdateCursor(inTable, fields) as Ucur:
        timediff = now - delta
        for row in Ucur:
            if row[0] >= timediff and row[0] <= now:
                row[1] = "Yes"
                Ucur.updateRow(row)
            else:
                row[1] = "No"
                Ucur.updateRow(row)
                
def ActiveCase():
    #Determines if a case is active (Case being worked on within past 30 days)
    inTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\CodeEnforcement.gdb\\CASE_CombinedLIVE"
    arcpy.management.AddField(inTable, "ActiveCase", "TEXT")
    fields = ["Chronology", "Inspections", "Violations", "ActiveCase"]
    now = datetime.datetime.today()
    delta = datetime.timedelta(days = 30)

    with arcpy.da.UpdateCursor(inTable, fields) as Ucur:
        timediff = now - delta
        for row in Ucur:
            if row[0] is not None or row[1] is not None or row[2] is not None:
                row[3] = "Active"
                Ucur.updateRow(row)
            else:
                row[3] = "Not Active"
                Ucur.updateRow(row)
def Update():
    prjPath = "\\\\GISAPP\\Workspace\\Horizon\\ArcGISPro_Projects\\FeatureServices\\CodeEnforcementv2.aprx"

    dict = {"Case_Main": ["Case_Main","City Boundaries, City Limits, ETJ, General, Administrative Boundaries, Polygon", "This layer contains the City Limits and Extra Territorial Jurisdiction (ETJ) for the City of Pearland.",0],
            "License_Main": ["License_Main","City Boundaries, City Limits, ETJ, General, Administrative Boundaries, Polygon", "This layer contains the City Limits and Extra Territorial Jurisdiction (ETJ) for the City of Pearland.",1],
            "Permit_Reviews": ["Permit_Reviews","City Boundaries, City Limits, ETJ, General, Administrative Boundaries, Polygon", "This layer contains the City Limits and Extra Territorial Jurisdiction (ETJ) for the City of Pearland.",2],   
            "License_Reviews": ["License_Reviews","City Boundaries, City Limits, ETJ, General, Administrative Boundaries, Polygon", "This layer contains the City Limits and Extra Territorial Jurisdiction (ETJ) for the City of Pearland.",3],
            "Inspections": ["Inspections","City Boundaries, City Limits, ETJ, General, Administrative Boundaries, Polygon", "This layer contains the City Limits and Extra Territorial Jurisdiction (ETJ) for the City of Pearland.",4],
            "First_Inspection": ["First_Inspection","City Boundaries, City Limits, ETJ, General, Administrative Boundaries, Polygon", "This layer contains the City Limits and Extra Territorial Jurisdiction (ETJ) for the City of Pearland.",5],
            "Case_Violations": ["Case_violations","City Boundaries, City Limits, ETJ, General, Administrative Boundaries, Polygon", "This layer contains the City Limits and Extra Territorial Jurisdiction (ETJ) for the City of Pearland.",6]
            }
    n=0
    for key, value in dict.items():
        sd_fs_name = "{}".format(key)
        portal = "https://pearland.maps.arcgis.com"
        user = "MapService_Admin"
        password = "Sdesde81"

        shrOrg = True
        shrEveryone = True
        

        relPath = "\\\\GISAPP\\Workspace\\Horizon\\Scripts"
        sddraft = os.path.join(relPath, "WebUpdate.sddraft")
        sd = os.path.join(relPath, "WebUpdate.sd")

        arcpy.env.overwriteOutput = True
        prj = arcpy.mp.ArcGISProject(prjPath)
        m = prj.listMaps('Map')[0]
        mp = m.listTables()[value[3]]
        print(mp)
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
        n+=1
main()
print(".")