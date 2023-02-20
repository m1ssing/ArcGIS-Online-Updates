import arcpy
import arcgis
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
MapList = ["General Reference", "Light Canvas", "Night Canvas", "Imagery Reference Layers"]
prjPath = "\\\\GISAPP\\Workspace\\Horizon\\ArcGISPro_Projects\\VectorTiles\\VectorTiles.aprx"
prj = arcpy.mp.ArcGISProject(prjPath)
arcpy.env.overwriteOutput = True
for m in prj.listMaps():
    if m.name in ["Muted Colors Dashboard", "Imagery Hybrid"]:
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

msg = MIMEMultipart('alternative')
s = smtplib.SMTP('mail.pearlandtx.gov')

msg['Subject'] = "Task Scheduler - Vector Tiles"
msg['From'] = 'cschultz@pearlandtx.gov'
msg['To'] = 'cschultz@pearlandtx.gov, jalexander@pearlandtx.gov'
msg['X-priority'] = '2'


# Create the body of the message (a plain-text and an HTML version).

html = """\
<html>
    <head></head>
    <body>
    <p> I can't believe it actually worked.
      
    </p>
    </body>
</html>
"""

text = "The Garage Sale Table has been updated and is ready to be used in this week's report.\n \\COPFS\\City Hall\\Planning\\GarageSaleReports"

### Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(html, 'html')
part2 = MIMEText(text, 'text')
msg.attach(part1)
msg.attach(part2)

s.sendmail(msg['From'], msg['To'].split(","), msg.as_string())