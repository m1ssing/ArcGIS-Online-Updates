import arcpy
import arcgis
import datetime
import time
import numpy
start = time.time()
table = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\InciMain"
dictARV = {0:["test"]}
dictNOT = {0:["test"]}
fields = ["inci_no", "arv_dttm", "unit"]
fields1 = ["inci_no", "notif_dttm"]
lst = []

with arcpy.da.SearchCursor(table, fields) as Scur:
    for row in Scur:
        if row[0] in dictARV.keys():
            if row[1] != None:
                dictARV[row[0]].append(row[1])
        else:
            if row[1] != None:
                dictARV[row[0]] = [row[1]]

with arcpy.da.SearchCursor(table, fields1) as Scur:
    for row in Scur:
        if row[0] in dictNOT.keys():
            if row[1] != None:
                dictNOT[row[0]].append(row[1])
        else:
            if row[1] != None:
                dictNOT[row[0]] = [row[1]]
print(dictARV)
lstTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\ERFTEST_Dict1"
lstfields = ["inci_no", "notif_time", "arv_time", "time_diff"]

for key,value in dictARV.items():
        lst.append(key)
myset = set(lst)
mylst = list(myset)

if arcpy.Exists(lstTable):
    arcpy.TruncateTable_management(lstTable)

Icur = arcpy.da.InsertCursor(lstTable, lstfields)

for x in mylst:
    Icur.insertRow((x, datetime.datetime.now(), datetime.datetime.now(), 0.0))
del Icur

newTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\ERFTEST_Dict1"
fields2 = ["inci_no", "notif_time", "arv_time"]

with arcpy.da.UpdateCursor(newTable, fields2) as Scur:
    for row in Scur:
        for key,value in dictARV.items():
            if key == row[0]:
                if value == None:
                    pass
                row[2] = max(value)
                Scur.updateRow(row)
        for key,value in dictNOT.items():
            if key == row[0]:
                if value == None:
                    pass
                row[1] = min(value)
                Scur.updateRow(row)

percentlst = []

with arcpy.da.SearchCursor(lstTable, lstfields) as Scur:
    for row in Scur:
        percentlst.append(row[3])
pls = numpy.percentile(percentlst, 90)
inciTable = "\\\\GISAPP\\Workspace\\GIS Staff Workspace\\cschultz\\FireHouseAnalytics.gdb\\ERFTEST_Dict1"
fields = ["inci_no", "notif_time", "arv_time", "time_diff"]
with arcpy.da.UpdateCursor(inciTable, fields) as Ucur:
    for row in Ucur:
        if row[1] == None or row[2] == None or row[0] == None:
            pass
        else:
            #turnout = roll - notif
            row[3] = row[2] - row[1]
            row[3] = row[3].seconds/60
            Ucur.updateRow(row)
print("percentile",pls)
stdv = numpy.std(percentlst)
print("standard deviation: ", stdv)



print(".")