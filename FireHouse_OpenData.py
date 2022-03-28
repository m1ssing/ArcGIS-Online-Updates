import arcpy
import datetime
import numpy
import time
import os
import arcgis
start = time.time()
arcpy.env.overwriteOutput = True
#Stor all month tables in dataset
#Then make a YOY Table with all of the months with stored mean/90th Percentile
CallType_dict ={"EMS":["311 ", "321 ", "371 ", "381 ", "554 ", "721 "],
            "FIRE":['110 ', '111 ', '112 ', '113 ', '114 ', '115 ', '116 ', '117 ', '118 ', '120 ', '121 ', '122 ', '123 ', '131 ', '132 ', '134 ', '135 ', '136 ', '137 ', '138 ', '140 ', '141 ', '142 ', '143 ', '150 ', '151 ', '152 ', '153 ', '154 ', '155 ', '160 ', '161 ', '162 ', '163 ', '164 ', '170 ', '171 ', '172 ', '173 ', '210 ', '211 ', '212 ', '213 ', '220 ', '222 ', '223 ', '231 ', '240 ', '241 ', '242 ', '243 ', '251 ', '441 ', '442 ', '443 ', '444 ', '462 ', '710 ', '711 ', '712 ', '713 ', '714 ', '715 ', '730 ', '731 ', '732 ', '733 ', '734 ', '735 ', '736 ', '740 ', '741 ', '742 ', '743 ', '744 ', '746 '],
            }

def main():
    #ParentTable()
    #FieldCreation()
    #UnitTable()
    #IncidentJoin()
    #IncidentJoin()
    #IncidentFieldMap()
    #IncidentTimeCalc()
    ERF()
    #GeocodeTable() 
    #addrTable()
    #addrSpatialJoin()
    #addrCalculateField()
    #addrStandardDeviation()
    #addrResponseType()
    #addrCallType()
    #addrFieldMap()
    ##SummarizeWithin()
    #SummarizeWithinLayerCreation()
    #SummarizeWithinByDistrict()
    #addrFieldMap()
    ##YTDDash()
    #PastYearTable()
    #YTDTable()
    #UnitPastYearTable()
    #UnitYTDTable()
    PublishMaps()
    ##MapTime()
    ##MonthTable()
    #CreateSummaryTable()
    #InsertSummaryTable()


def ParentTable():
    #Purpose: Creates FireHouseMain table from FireHouse dB table inc_main
    originalTable = "\\\\GISAPP\\Workspace\\sdeFiles\\FireHouse.sde\\Firehouse.dbo.inc_main"
    mainPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb"
    mainFC = "FireHouseMain"
    mainTable = mainPath + "\\" + mainFC
    if arcpy.Exists(mainTable) == True:
        arcpy.Delete_management(mainTable)
        arcpy.TableToTable_conversion(originalTable, mainPath, mainFC, "alm_date >= GETDATE () -365")
    else:
        arcpy.TableToTable_conversion(originalTable, mainPath, mainFC, "alm_date >= GETDATE () -365")
    print("done")
    #Time: 1.49 minutes

def FieldCreation():
    #Purpose: Creates a concantenated Address Field and strips excess whitespace that exists in FireHouse. Artifical Whitespace added back for Geocoding later.
    #         FOR loop needs to account for Street Prefix not existing for every address. 
    ytdTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouseMain"
    arcpy.AddField_management(ytdTable, "Address", "TEXT")
    fields = ["Address", "st_prefix", "street", "st_type", "number"]
    with arcpy.da.UpdateCursor(ytdTable, fields) as Ucur:
        for row in Ucur:
            if row[1] == "  ":
                row[0] = row[4].rstrip() + " " + row[2].rstrip() + " " + row[3]
                Ucur.updateRow(row)
            else:
                row[0] = row[4].rstrip() + " " + row[1] + row[2].rstrip() + " " + row[3]
                Ucur.updateRow(row)
    #Time: .20 min

def UnitTable():
    #Purpose: Creates Unit Main table, multiple Units can answer to the same incident. This table will join through the inci_no with FireHouseMain 1:M relationship.
    originalTable = "\\\\GISAPP\\Workspace\\sdeFiles\\FireHouse.sde\\Firehouse.dbo.inc_unit"
    mainPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb"
    mainFC = "UnitMain"
    mainTable = mainPath + "\\" + mainFC
    if arcpy.Exists(mainTable) == True:
        arcpy.Delete_management(mainTable)
        arcpy.TableToTable_conversion(originalTable, mainPath, mainFC, "alm_date >= GETDATE () -365")
    else:
        arcpy.TableToTable_conversion(originalTable, mainPath, mainFC, "alm_date >= GETDATE () -365")
    #Time: .37 min

def IncidentJoin():
    #Purpose: Joins UnitMain and FireHouseMain together with inci_no in a 1:M relationship.
    inciTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouseMain"
    joinTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\UnitMain"
    inciJoinPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb"
    inciJoinName = "InciJoin"
    inciJoin = inciJoinPath + "\\" + inciJoinName
    inciJoinTable = arcpy.AddJoin_management(inciTable, "inci_no",
                                             joinTable, "inci_no")
    if arcpy.Exists(inciJoin):
        arcpy.Delete_management(inciJoin)
        arcpy.TableToTable_conversion(inciJoinTable, inciJoinPath, inciJoinName)
    else:
        arcpy.TableToTable_conversion(inciJoinTable, inciJoinPath, inciJoinName)
    #Time: .46 min

def IncidentFieldMap():
    #Purpose: This is primarily to clean up fields that had name changes due to the Join and drop hundreds of unwanted fields from the two tables. 
    #         For future use it is more beneficial to have the indiviual unit Arrival and Clear time which have a "_1" that we want to get rid of for future Field Calculation so the Alias matches the Field Name.
    #         Also for future Time Calculation we add the fields for TURNOUT and TRAVEL times to be calculated later.
    inciTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\InciJoin"
    inciJoinPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb"
    inciJoinName = "InciMain"
    inciJoin = inciJoinPath + "\\" + inciJoinName

    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(inciTable)
    
    KEEP_LIST = ["inci_no", "Address", "unit", "alm_dttm", "station", "inci_type", "notif_dttm", "roll_dttm", "disp_dttm", "arv_dttm_1", "clr_dttm_1"]
    for f in fieldmappings.fields:
        if f.name not in KEEP_LIST:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(f.name))

    if arcpy.Exists(inciJoin):
        arcpy.Delete_management(inciJoin)
        arcpy.TableToTable_conversion(inciTable, inciJoinPath, inciJoinName, "", fieldmappings)
    else:
        arcpy.TableToTable_conversion(inciTable, inciJoinPath, inciJoinName, "", fieldmappings)

    arcpy.AlterField_management(inciJoin, "arv_dttm_1", "arv_dttm", "arv_dttm")
    arcpy.AlterField_management(inciJoin, "clr_dttm_1", "clr_dttm", "clr_dttm")
    arcpy.AddField_management(inciJoin, "alarmhandling_dttm", "FLOAT")
    arcpy.AddField_management(inciJoin, "turnout_dttm", "FLOAT")
    arcpy.AddField_management(inciJoin, "travel_dttm", "FLOAT")
    arcpy.AddField_management(inciJoin, "response_dttm", "FLOAT")
    
    #Time: .58 min

def IncidentTimeCalc():
    #Purpose: Calculate TURNOUT and TRAVEL time in minutes
    #         Subtracting to datetime fields produces a timedelta that can't be used in any esri/SQL field type. We must use .seconds to the get the raw time from the timedelta then divide by 60 to get minutes.
    inciTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\InciMain"
    fields = ["alm_dttm", "notif_dttm", "roll_dttm", "arv_dttm", "disp_dttm", "alarmhandling_dttm", "turnout_dttm", "travel_dttm", "response_dttm"]
    with arcpy.da.UpdateCursor(inciTable, fields) as Ucur:
        for row in Ucur:
            if row[2] == None or row[3] == None or row[1] == None or row[4] == None:
                pass
            else:
                #response = arv - disp
                row[8] = row[3] - row[4]
                row[8] = row[8].seconds/60
                Ucur.updateRow(row)
                #alarm handling = notif - disp
                row[5] = row[2] - row[4]
                row[5] = row[5].seconds/60
                Ucur.updateRow(row)
                #turnout = roll - notif
                row[6] = row[2] - row[1]
                row[6] = row[6].seconds/60
                Ucur.updateRow(row)
                #travel = arv - roll
                row[7] = row[3] - row[2]
                row[7] = row[7].seconds/60
                Ucur.updateRow(row)
    #Time: .03 min

def ERF():
    #ERF is typically building fires
    table = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\InciMain"
    dictARV = {0:["test"]}
    dictDISP = {0:["test"]}
    dictROLL = {0:["test"]}
    dictADDR = {0:["test"]}
    fieldsARV = ["inci_no", "arv_dttm"]
    fieldsDISP = ["inci_no", "disp_dttm"]
    fieldsROLL = ["inci_no", "roll_dttm"]
    fieldsADDR = ["inci_no", "Address"]
    lst = []

    with arcpy.da.SearchCursor(table, fieldsARV) as Scur:
        for row in Scur:
            if row[0] in dictARV.keys():
                if row[1] != None:
                    dictARV[row[0]].append(row[1])
            else:
                if row[1] != None:
                    dictARV[row[0]] = [row[1]]

    with arcpy.da.SearchCursor(table, fieldsDISP) as Scur:
        for row in Scur:
            if row[0] in dictDISP.keys():
                if row[1] != None:
                    dictDISP[row[0]].append(row[1])
            else:
                if row[1] != None:
                    dictDISP[row[0]] = [row[1]]

    with arcpy.da.SearchCursor(table, fieldsROLL) as Scur:
        for row in Scur:
            if row[0] in dictROLL.keys():
                if row[1] != None:
                    dictROLL[row[0]].append(row[1])
            else:
                if row[1] != None:
                    dictROLL[row[0]] = [row[1]]

    with arcpy.da.SearchCursor(table, fieldsADDR) as Scur:
        for row in Scur:
            if row[0] in dictADDR.keys():
                if row[1] != None:
                    dictADDR[row[0]].append(row[1])
            else:
                if row[1] != None:
                    dictADDR[row[0]] = [row[1]]
    print("pls")
    lstTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\ReportsTable"
    if arcpy.Exists(lstTable):
        arcpy.TruncateTable_management(lstTable)
    else:
        arcpy.management.CreateTable("\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb", "ReportsTable")
        arcpy.management.AddField(lstTable, "inci_no", "TEXT")
        arcpy.management.AddField(lstTable, "disp_time", "DATE")
        arcpy.management.AddField(lstTable, "arv_time", "DATE")
        arcpy.management.AddField(lstTable, "erf_time", "FLOAT")
        arcpy.management.AddField(lstTable, "response_dttm", "TEXT")

    lstfields = ["inci_no", "disp_time", "arv_time", "erf_time"]
    newlst = []
    print(dictARV)
    for key,value in dictARV.items():
        lst.append(key)
    myset = set(lst)
    mylst = list(myset)


    Icur = arcpy.da.InsertCursor(lstTable, lstfields)

    for x in mylst:
        Icur.insertRow((x, datetime.datetime.now(), datetime.datetime.now(), 0.0))
    del Icur

    with arcpy.da.UpdateCursor(lstTable, lstfields) as Scur:
        for row in Scur:
            for key,value in dictARV.items():
                if key == row[0]:
                    if value == None:
                        pass
                    row[2] = max(value)
                    Scur.updateRow(row)
            for key,value in dictDISP.items():
                if key == row[0]:
                    if value == None:
                        pass
                    row[1] = min(value)
                    Scur.updateRow(row)

    with arcpy.da.UpdateCursor(lstTable, lstfields) as Ucur:
        for row in Ucur:
            if row[1] == None or row[2] == None or row[0] == None:
                pass
            else:
                #turnout = roll - disp
                row[3] = row[2] - row[1]
                row[3] = row[3].seconds/60
                Ucur.updateRow(row)
    codeblock_Resp = """
def sym(resp):
    if resp > 11.5:
        return ('Not Acceptable')
    if resp <= 11.5:
        return ('Acceptable')

    """
    expression_Resp = "sym(!erf_time!)"
    arcpy.management.CalculateField(lstTable, "response_dttm",expression_Resp, "PYTHON3", codeblock_Resp)

    inJoin = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouseYTD"
    joinTable = arcpy.management.AddJoin(inJoin, "inci_no", lstTable, "inci_no")
    erfCopy = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\ERF_initial"
    arcpy.management.CopyFeatures(joinTable, erfCopy)
    fcPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb"
    fcName = "ERF_Display"
    arcpy.conversion.FeatureClassToFeatureClass(erfCopy, fcPath, fcName, "FireHouseYTD_inci_type IN ('111', '121')")

def GeocodeTable():
    #
    inciTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\InciMain"
    addrLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\AddressInci"
    geoLocator = "\\\\GISAPP\Workspace\\MyArcGIS\\Geocoders\\DualRangeGeocoder.loc"
    geoParam =  "'Address or Place' Address VISIBLE NONE;Address2 <None> VISIBLE NONE;Address3 <None> VISIBLE NONE;Neighborhood <None> VISIBLE NONE;City City VISIBLE NONE;County <None> VISIBLE NONE;State State VISIBLE NONE;ZIP <None> VISIBLE NONE;ZIP4 <None> VISIBLE NONE;Country <None> VISIBLE NONE"
    addrParam = "'Full Address' Address VISIBLE NONE"
    arcpy.AddField_management(inciTable, "City", "TEXT")
    arcpy.CalculateField_management(inciTable, "City", "'Pearland'")
    arcpy.AddField_management(inciTable, "State", "TEXT")
    arcpy.CalculateField_management(inciTable, "State", "'Texas'")
    if arcpy.Exists(addrLayer) ==  True:
        print("y")
        arcpy.Delete_management(addrLayer)
        arcpy.GeocodeAddresses_geocoding(inciTable, geoLocator, geoParam, addrLayer)
    else:
        arcpy.GeocodeAddresses_geocoding(inciTable, geoLocator, geoParam, addrLayer)

    arcpy.AlterField_management(addrLayer,"USER_alm_dttm","alm_dttm")
    arcpy.AlterField_management(addrLayer,"USER_inci_no","inci_no")
    arcpy.AlterField_management(addrLayer,"USER_inci_type","inci_type")
    arcpy.AlterField_management(addrLayer,"USER_station","station")
    arcpy.AlterField_management(addrLayer,"USER_Address","Address")
    arcpy.AlterField_management(addrLayer,"USER_unit","unit")
    arcpy.AlterField_management(addrLayer,"USER_notif_dttm","notif_dttm")
    arcpy.AlterField_management(addrLayer,"USER_roll_dttm","roll_dttm")
    arcpy.AlterField_management(addrLayer,"USER_arv_dttm","arv_dttm")
    arcpy.AlterField_management(addrLayer,"USER_disp_dttm","disp_dttm")
    arcpy.AlterField_management(addrLayer,"USER_clr_dttm","clr_dttm")
    arcpy.AlterField_management(addrLayer,"USER_turnout_dttm","turnout_dttm")
    arcpy.AlterField_management(addrLayer,"USER_travel_dttm","travel_dttm")
    arcpy.AlterField_management(addrLayer,"USER_alarmhandling_dttm","alarmhandling_dttm")
    arcpy.AlterField_management(addrLayer,"USER_response_dttm","response_dttm")

    #Time: 3.3 min

def addrTable():
    addrLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\AddressInci"
    fmPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb"
    fmName = "AddressInci_FM"
    fmLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\AddressInci_FM"
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(addrLayer)
    KEEP_LIST = ["ObjectID", "alm_dttm", "inci_no", "inci_type", "station", "Address", "unit", "notif_dttm", "roll_dttm", "arv_dttm", "disp_dttm", "clr_dttm", "turnout_dttm", "travel_dttm", "alarmhandling_dttm", "erf_dttm", "inci_status", "response_dttm"]

    for f in fieldmappings.fields:
        if f.name not in KEEP_LIST:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(f.name))

    if arcpy.Exists(fmLayer):
        arcpy.Delete_management(fmLayer)
        arcpy.FeatureClassToFeatureClass_conversion(addrLayer, fmPath, fmName, "", fieldmappings)
    else:
        arcpy.FeatureClassToFeatureClass_conversion(addrLayer, fmPath, fmName, "", fieldmappings)

    #Time: .37 min

def addrSpatialJoin():
    mainTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\AddressInci_FM"
    FD_layer = "\\\\GISAPP\\Workspace\\\sdeFiles\\Horizon_Owner.sde\\Horizon.DBO.EmergencyServices\\Horizon.DBO.FireDistricts"
    CL_layer = "\\\\GISAPP\\Workspace\\sdeFiles\\Horizon_Owner.sde\\Horizon.DBO.AdministrativeBoundaries\\Horizon.DBO.CityLimits"
    ESD_layer = "\\\\GISAPP\\Workspace\\sdeFiles\\Horizon_Owner.sde\\Horizon.DBO.AdministrativeBoundaries\\Horizon.DBO.ESD"


    FD_Join = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouseYTD_FDSJ"
    CL_Join = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouseYTD_CLSJ"
    ESD_Join = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouseYTD_ESDSJ"

    if arcpy.Exists(FD_Join):
        arcpy.management.Delete(FD_Join)

    if arcpy.Exists(CL_Join):
        arcpy.management.Delete(CL_Join)

    if arcpy.Exists(ESD_Join):
        arcpy.management.Delete(ESD_Join)

    arcpy.analysis.SpatialJoin(mainTable, FD_layer, FD_Join)
    arcpy.analysis.SpatialJoin(FD_Join , CL_layer, CL_Join)
    arcpy.analysis.SpatialJoin(CL_Join , ESD_layer, ESD_Join)

def addrCalculateField():

    mainTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouseYTD_ESDSJ"
    arcpy.management.AddField(mainTable, "LocationType", "TEXT")


    codeblock_LocationType = """
def Status(station, num, Boundary):
    if station == num:
        return ("Within District")
    if station != num and Boundary == "City Limit":
        return ("Within City Limit")
    if station != num and Boundary != "City Limit":
        return ("Mutual Aid")


    """
    expression_LocationType = "Status(!station!, !StationNumber!, !Boundary!)"

    arcpy.management.CalculateField(mainTable, "LocationType",expression_LocationType, "PYTHON3", codeblock_LocationType)

    arcpy.management.AddField(mainTable, "RespondingStation", "TEXT")
    arcpy.management.CalculateField(mainTable, "RespondingStation", "'ST' + !station!.rstrip()")
    #Time: .57min

def addrStandardDeviation():
    mainTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouseYTD_ESDSJ"
    fields = ["response_dttm"]
    outlst =[]
    percentlst = []
    with arcpy.da.SearchCursor(mainTable, fields) as Scur:
        for row in Scur:
            if row[0] != None:
                outlst.append(row[0])
            else:
                pass

    arcpy.management.AddField(mainTable, "inci_status", "TEXT")
    stdv = numpy.std(outlst)
    avgOutlier= sum(outlst) / len(outlst)
    sdtvOutlier = avgOutlier + stdv * 3
    fields = ["response_dttm", "inci_status"]
    with arcpy.da.UpdateCursor(mainTable, fields) as Scur:
        for row in Scur:
            if row[0] == None:
                pass
            elif row[0] >= sdtvOutlier:
                row[1] = "Outlier"
                Scur.updateRow(row)
            else:
                percentlst.append(row[0])

    newPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb"
    newName = "FireHouse_YTD"
    newFC = newPath + "\\" + newName
    arcpy.conversion.FeatureClassToFeatureClass(mainTable, newPath, newName, "inci_status NOT IN ('Outlier')")
    avg = sum(percentlst) / len(percentlst)
    numPercentile = numpy.percentile(percentlst, 90)
    print(avg, numPercentile)
    statusField = ["inci_status", "response_dttm"]
    with arcpy.da.UpdateCursor(newFC, statusField) as Ucur:
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
def addrResponseType():
    #7:30 call time
    #erf - 11:30
    mainTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouse_YTD"
    arcpy.management.AddField(mainTable, "ResponseType", "TEXT")
    codeblock_Resp = """
def sym(resp):
    if resp > 7.5:
        return ('Not Acceptable')
    if resp <= 7.5:
        return ('Acceptable')

    """
    expression_Resp = "sym(!response_dttm!)"
    arcpy.management.CalculateField(mainTable, "ResponseType",expression_Resp, "PYTHON3", codeblock_Resp)

def addrCallType():
    mainTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouse_YTD"
    arcpy.management.AddField(mainTable, "CallType", "TEXT")
    fields = ["inci_type", "CallType"]
    with arcpy.da.UpdateCursor(mainTable, fields) as Ucur:
        for row in Ucur:
            for key, value in CallType_dict.items():
                if row[0] in value:
                    row[1] = key
                    Ucur.updateRow(row)

def PastYearTable():
    mainTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\InciMain"
    yearList = ["2014","2015","2016","2017","2018","2019","2020"]
    
    
    for x in yearList:
        yearName = "FireHouse_{}".format(x)
        yearPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb"
        query = "alm_dttm >= date '{}/01/01 00:00:00' AND alm_dttm <= date '{}/12/31 00:00:00'".format(x, x)
        yearFC = yearPath + "\\" + yearName
        if arcpy.Exists(yearFC):
            arcpy.Delete_management(yearFC)
        arcpy.TableToTable_conversion(mainTable, yearPath, yearName, query)

def YTDTable():
    mainTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\AddressInci_FM"
    ytdPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb"
    ytdName = "FireHouseYTD"
    ytdFC = ytdPath + "\\" + ytdName
    currentTime = datetime.datetime.now()
    pastTime = datetime.datetime.now() - datetime.timedelta(days = 365)
    query = "alm_dttm >= date '{}' AND alm_dttm <= date '{}'".format(pastTime, currentTime)
    if arcpy.Exists(ytdFC) == True:
        arcpy.Delete_management(ytdFC)
    arcpy.FeatureClassToFeatureClass_conversion(mainTable, ytdPath, ytdName, query)

def YTDDash():
    ytdTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouse_YTD"
    FD_layer = "\\\\GISAPP\\Workspace\\\sdeFiles\\Horizon_Owner.sde\\Horizon.DBO.EmergencyServices\\Horizon.DBO.FireDistricts"
    CL_layer = "\\\\GISAPP\\Workspace\\sdeFiles\\Horizon_Owner.sde\\Horizon.DBO.AdministrativeBoundaries\\Horizon.DBO.CityLimits"


    FD_Join = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouseYTD_FDSJ"
    CL_Join = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouseYTD_CLSJ"

    if arcpy.Exists(FD_Join):
        arcpy.Delete_management(FD_Join)

    if arcpy.Exists(CL_Join):
        arcpy.Delete_management(CL_Join)

    arcpy.SpatialJoin_analysis(ytdTable, FD_layer, FD_Join)
    arcpy.SpatialJoin_analysis(FD_Join , CL_layer, CL_Join)

    arcpy.AddField_management(CL_Join, "OnScene_Minutes", "DOUBLE")
    arcpy.CalculateField_management(CL_Join, "Onscene_Minutes", "!USER_Onscene_Seconds! / 60")
    arcpy.AddField_management(CL_Join, "GoalTime", "TEXT")

    codeblock_GoalTime = """
def GoalTime(Time):
    if Time > 8:
        return "No"
    if Time <= 8:
        return "Yes"

    """
    expression_GoalTime = "GoalTime(!Onscene_Minutes!)"

    arcpy.CalculateField_management(CL_Join, "GoalTime",expression_GoalTime, "PYTHON3", codeblock_GoalTime)

    arcpy.AddField_management(CL_Join, "Status", "TEXT")

    codeblock_Status = """
def Status(station, num, CODE):
    if station == num:
        return ("Within District")
    if station != num and CODE == "CITY":
        return ("Within City Limit")
    if station != num and CODE != "CITY":
        return ("Mutual Aid")


    """
    expression_Status = "Status(!station!, !StationNumber!, !CODE!)"

    arcpy.CalculateField_management(CL_Join, "Status",expression_Status, "PYTHON3", codeblock_Status)

    arcpy.AddField_management(CL_Join, "Station_txt", "TEXT")

    arcpy.CalculateField_management(CL_Join, "Station_txt", "'ST' + !station!")

    KEEP_LIST = ["inci_no", "unit", "Address", "arv_dttm", "FIreDistrict", "OnScene_Minutes", "GoalTime", "Status", "Station_txt"]
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(CL_Join)

    for f in fieldmappings.fields:
        if f.name not in KEEP_LIST:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(f.name))

    dash_Path = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb"
    dash_Name = "FireHouse_Dash"
    dashLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouse_Dash"
    if arcpy.Exists(dashLayer):
        arcpy.Delete_management(dashLayer)

    arcpy.FeatureClassToFeatureClass_conversion(CL_Join, dash_Path, dash_Name, "", fieldmappings)

def UnitPastYearTable():
    mainTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\UnitMain"
    yearList = ["2014","2015","2016","2017","2018","2019"]
    yearPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb"
    
    for x in yearList:
        yearFC = "Unit_{}".format(x)
        query = "notif_dttm >= date '{}/01/01 00:00:00' AND notif_dttm <= date '{}/12/31 00:00:00'".format(x, x)
        arcpy.TableToTable_conversion(mainTable, yearPath, yearFC, query)

def UnitYTDTable():
    mainTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\UnitMain"
    ytdPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb"
    ytdName = "UnitYTD"
    ytdFC = ytdPath + "\\" + ytdName
    currentTime = datetime.datetime.now()
    pastTime = datetime.datetime.now() - datetime.timedelta(days = 365)
    query = "notif_dttm >= date '{}' AND notif_dttm <= date '{}'".format(pastTime, currentTime)
    if arcpy.Exists(ytdFC) == True:
        arcpy.Delete_management(ytdFC)
        arcpy.TableToTable_conversion(mainTable, ytdPath, ytdName, query)
    else:
        arcpy.TableToTable_conversion(mainTable, ytdPath, ytdName, query)

def addrFieldMap():
    mainTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouse_YTD"
    newPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb"
    newName = "FireHouseYTD_Display"
    KEEP_LIST = ["inci_no", "inci_type", "Address", "unit", "alm_dttm", "notif_dttm", "roll_dttm", "arv_dttm", "disp_dttm", "clr_dttm", "alarmhandling_dttm", "turnout_dttm", "travel_dttm", "response_dttm", "ESD", "LocationType", "RespondingStation", "inci_status", "CallType", "ResponseType"]
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(mainTable)

    for f in fieldmappings.fields:
        if f.name not in KEEP_LIST:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(f.name))
    arcpy.conversion.FeatureClassToFeatureClass(mainTable, newPath, newName, "", fieldmappings)


    finalLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouseYTD_Display"
    arcpy.management.AddField(finalLayer, "Acceptable", "LONG")
    
    
    codeblock_Resp = """
def sym(resp):
    if resp == "Acceptable":
        return 1
    """
    expression_Resp = "sym(!ResponseType!)"
    arcpy.management.CalculateField(finalLayer, "Acceptable",expression_Resp, "PYTHON3", codeblock_Resp)
       
def SummarizeWithin():
    polyTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\KeyMapGrid"
    pointTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouseYTD_Display"
    newLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\SummarizeWithin"
    newTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\SummarizeTable"

    arcpy.analysis.SummarizeWithin(polyTable, pointTable, newLayer, "", "Acceptable Sum", "ADD_SHAPE_SUM", '', "RespondingStation", "ADD_MIN_MAJ", "NO_PERCENT", newTable)

    joinTable = arcpy.management.AddJoin(newLayer, "JOIN_ID", newTable, "JOIN_ID")
    finalLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\Summarize_Display"
    arcpy.management.CopyFeatures(joinTable, finalLayer)

    arcpy.management.AddField(finalLayer, "LocationType", "TEXT")

    codeblock_Location = """
def LocationType(RS, ST1, ST2, ST3, ST4, ST5, ST6, ST7, ST8, ST9, ST10, ST11):
    if RS == "ST1":
        return ST1
    if RS == "ST2":
        return ST2
    if RS == "ST3":
        return ST3
    if RS == "ST4":
        return ST4
    if RS == "ST5":
        return ST5
    if RS == "ST6":
        return ST6
    if RS == "ST7":
        return ST7
    if RS == "ST8":
        return ST8
    if RS == "ST9":
        return ST9
    if RS == "ST10":
        return ST10
    if RS == "ST11":
        return ST11
    """
    expression_Location = "LocationType(!SummarizeTable_RespondingStation!,!SummarizeWithin_ST1!,!SummarizeWithin_ST2!,!SummarizeWithin_ST3!,!SummarizeWithin_ST4!,!SummarizeWithin_ST5!,!SummarizeWithin_ST6!,!SummarizeWithin_ST7!,!SummarizeWithin_ST8!,!SummarizeWithin_ST9!,!SummarizeWithin_ST10!,!SummarizeWithin_ST11!)"
    arcpy.management.CalculateField(finalLayer, "LocationType",expression_Location, "PYTHON3", codeblock_Location)
    arcpy.management.AddField (finalLayer, "swPercentage", "LONG")

    codeblock_byDistrict = """
def byDistrict (sum, count):
    percent = (sum / count) * 100
    return percent
    """
    expression_byDistrict = "byDistrict(!SummarizeTable_SUM_Acceptable!, !SummarizeTable_Point_Count!)"
    arcpy.management.CalculateField(finalLayer, "swPercentage", expression_byDistrict, "PYTHON3", codeblock_byDistrict)
    #Time: 1.4 min

def SummarizeWithinLayerCreation():
    inTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouseYTD_Display"
    outPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb"
    outName = "FireHouseYTD_swByDistrict"

    arcpy.conversion.FeatureClassToFeatureClass(inTable, outPath, outName, "LocationType = 'Within District' AND inci_status = 'Within 90th Percentile'")

    layerName = outPath + "//" + outName
    arcpy.management.AddField (layerName, "Acceptable", "LONG")

    codeblock_byDistrict = """
def byDistrict (Response):
    if Response == "Acceptable":
        return 1
    """
    expression_byDistrict = "byDistrict(!ResponseType!)"
    arcpy.management.CalculateField(layerName, "Acceptable", expression_byDistrict, "PYTHON3", codeblock_byDistrict)


def SummarizeWithinByDistrict():
    #FireDistrict_Divide was created with Subdivide Polygon on the Fire Districts (.5 sq miles)(Equal Areas)
    inPoly = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireDistrict_Divide"
    inLayer = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\FireHouseYTD_swByDistrict"
    outPoly = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\SummarizeDistrict_Display"

    arcpy.analysis.SummarizeWithin(inPoly, inLayer, outPoly, "KEEP_ALL", "Acceptable Sum")

    arcpy.management.AddField (outPoly, "swPercentage", "LONG")

    codeblock_byDistrict = """
def byDistrict (sum, count):
    percent = (sum / count) * 100
    return percent
    """
    expression_byDistrict = "byDistrict(!SUM_Acceptable!, !Point_Count!)"
    arcpy.management.CalculateField(outPoly, "swPercentage", expression_byDistrict, "PYTHON3", codeblock_byDistrict)




def MapTime():
    table = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\TimePoly"
    fields = ["Mean_USER_OnScene_seconds", "Time"]
    arcpy.AddField_management(table, "Time", "TEXT")
    with arcpy.da.UpdateCursor(table, fields) as Ucur:
        for row in Ucur:
            num = str(datetime.timedelta(seconds=row[0]))
            print(num)
            temp = datetime.datetime.strptime(num, "%H:%M:%S.%f")
            num_fixed = temp.strftime("%H:%M:%S")
            row[1] = num_fixed
            print(row[1])
            Ucur.updateRow(row)

def MonthTable():
    year = ["2014","2015","2016","2017","2018","2019","2020"]
    month = ["01","02","03","04","05","06","07","08","09","10","11","12"]
    inTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\InciMain"
    newName = "test"
    for x in year:
        for z in month:
            inPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouse{}.gdb".format(x)
            newName = "FireHouse_{}_{}".format(z,x)
            newFC = inPath + "\\" + newName
            if arcpy.Exists(newFC) == True:
                arcpy.Delete_management(newFC)
            query = "notif_dttm >= date '{}/{}/01 00:00:00' AND notif_dttm <= date '{}/{}/31 00:00:00'".format(x,z,x,z)
            if z == "02":
                query = "notif_dttm >= date '{}/{}/01 00:00:00' AND notif_dttm <= date '{}/{}/28 00:00:00'".format(x,z,x,z)
            if z in ["04","06","09","11"]:
                query = "notif_dttm >= date '{}/{}/01 00:00:00' AND notif_dttm <= date '{}/{}/30 00:00:00'".format(x,z,x,z)
            arcpy.TableToTable_conversion(inTable, inPath, newName, query)

def CreateSummaryTable():
    newPath = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb"
    newName = "SummaryTable"
    newTable = newPath + "\\" + newName
    if arcpy.Exists(newTable):
        arcpy.Delete_management(newTable)
        arcpy.CreateTable_management(newPath, newName)
    else:
        arcpy.CreateTable_management(newPath, newName)

    arcpy.AddField_management(newTable, "Month", "TEXT")
    arcpy.AddField_management(newTable, "Year", "TEXT")
    arcpy.AddField_management(newTable, "OnScene_Seconds", "DOUBLE")
    arcpy.AddField_management(newTable, "Time", "TEXT")

def InsertSummaryTable():
    year = ["2014","2015","2016","2017","2018","2019","2020"]
    month = {"January":"01","February":"02","March":"03","April":"04","May":"05","June":"06","July":"07","August":"08","September":"09","October":"10","November":"11","December":"12"}
    lstrow = []
    for x in year:
        for key, value in month.items():
            inciTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouse{}.gdb\\FireHouse_{}_{}".format(x,value,x)
            fields = ["OnScene_seconds"]
            lst = []
            lstlst = []
            with arcpy.da.SearchCursor(inciTable, fields) as Scur:
                for row in Scur:
                    if row[0] != None:
                        lst.append(row[0])
            avg = sum(lst)/len(lst)
            num = str(datetime.timedelta(seconds=avg))
            temp = datetime.datetime.strptime(num, "%H:%M:%S.%f")
            num_fixed = temp.strftime("%H:%M:%S")
            lstlst.extend((key, x, avg, num_fixed))
            lstrow.append(lstlst)
    summaryTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\SummaryTable"
    fields = ["Month", "Year", "OnScene_Seconds", "Time"]
    with arcpy.da.InsertCursor(summaryTable, fields) as Icur:
        for x in lstrow:
            print(x)
            Icur.insertRow((x))

def PublishMaps():
    #Boundary Layers on Interactive Map are also included. PUC layers are in ExternalAgencies in Horizon.
    prjPath = "\\\\GISAPP\\Workspace\\Horizon\\ArcGISPro_Projects\\FeatureServices\\EmergencyServices\\FireDashboard.aprx"

    dict = {"SummarizeDistrict": ["SummarizeDistrict","Summarize District, Fire, Polygon", "This layer of summarized fire response time data.",0],
            "FireHouseYTD": ["FireHouseYTD","Fire Calls, Points", "This layer has fire call information.",1],
            "ERF_Display": ["ERF_Display", "ERF, Fire, Points", "This layer contains ERF calls",2]}
    n=0
    #"Drainage Districts": ["Drainage_Districts", "Drainage Districts, Administrative Boundaries, Polygon", "This layer contains the various Drainage Districts in the City of Pearland", 2],
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
        arcpy.mp.CreateWebLayerSDDraft(mp, sddraft, sd_fs_name, 'MY_HOSTED_SERVICES', 'FEATURE_ACCESS','Fire_Project', True, True, False, True)
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
        pub_params = {"dateFieldsTimeReference" : {"timeZone":"Central Standard Time"}, "dateFieldsRespectsDayLightSavingTime": "true"}
        fs = sdItem.publish(publish_parameters = pub_params, overwrite=True)
        fs.share(org=shrOrg)
        print(sd_fs_name, "done")
        n+=1

main()
end = time.time()
elapse = end - start 
print(elapse/60)
print(".")



#THIS IS USED TO DETERMINE YEAR IN PARENT TABLE FOR FUTRUE USE
#date = datetime.date.today()
#date1 = str(date)

#x = [a for a in date1.split('-') if a]
#print(x[:1])
