import os
from django.http import HttpResponse

from wand.image import Image
import sys
sys.path.append('/usr/share/inkscape/extensions')

import subprocess
import shutil
import re

class FcExporterController:

  # settings variable declaration begins
  SAVE_PATH = "export/exported_images/"
  # settings variable declaration ends

  # this method should be called as http://localhost:<PORT-NUMBER(eg. 3000)>/fc_exporter/init/ from javascript
  def __init__(self, request):
    self.request = request

  def init(self):
    self.checkAndCreateDirectories([FcExporterController.SAVE_PATH])
    requestObject = self.parseRequestParams(self.request.POST)
    stream = requestObject['stream']
    print "tesss"
    # replacing single-quote with nothing because of converting in jpg image
    stream = re.sub(r'\'', "", stream)

    response = self.convertSVGtoImage(stream, requestObject['exportFileName'] ,requestObject['exportFormat'])
    return response
  
  # this function check for the directories needed to export image
  # if not present then it creates the directories
  def checkAndCreateDirectories(self, directoriesNameArray):
    for loc in directoriesNameArray:
      if(not os.path.isdir(loc)):
        os.mkdir(loc)
   

	# This function purse the request and create the request Data object
  def parseRequestParams(self, requestData):
  	# Following values are expected to have from request stream
  	stream = "" # expected to hold the SVG string coming from the chart
  	imageData = "" # if the request contains raw image data then those will go here
  	parametersArray = [] # holds the parameters
  	width = 0 # holds the width of exported image
  	height = 0 # holds the height of exported image
  	exportFileName = "" # holds the name of the exported file
  	exportFormat = "" # holds the format of the exported files
  	exportAction = ""
  	
  	if(requestData.has_key("stream")):
  		stream = requestData["stream"]
  	else:
  		print "raiseError(101)"	

  	if(requestData.has_key("encodedImgData")):
  		imageData = requestData["encodedImgData"]
  	
  	
  	if(requestData["meta_width"]!="" and requestData["meta_height"] !=""):
  		width = requestData["meta_width"]
  		height = requestData["meta_height"]
  	else:
  		print "raiseError(101)"	
  	
  	
  	if(requestData["parameters"] != ""):
  		parametersArray = requestData["parameters"].split("|")
  	else:
  		print "raiseError(100)"	 		
  	

  	if(parametersArray[0].split("=").pop() and parametersArray[1].split("=").pop() and parametersArray[2].split("=").pop()):
	  	exportFileName = parametersArray[0].split("=").pop()
	  	exportFormat = parametersArray[1].split("=").pop()
	  	exportAction = parametersArray[2].split("=").pop()

  	# preparing the request object
  	requestObject = {
  		"stream" : stream, 
  		"imageData" : imageData, 
  		"width" : width, 
  		"height" : height, 
  		"exportFileName" : exportFileName, 
  		"exportFormat" : exportFormat, 
  		"exportAction" : exportAction
  	}

  	return requestObject

  # This function coverts the provided SVG string to image or pdf file		
  def convertSVGtoImage(self, svgString, exportFileName, exportFileFormat):
    completeFileName = self.SAVE_PATH+exportFileName+"."+exportFileFormat
    print self.SAVE_PATH
    if(exportFileFormat.lower() == 'svg'):
      self.exportedData = svgString

    elif(exportFileFormat.lower() != 'pdf'):
      with Image( blob=str(svgString), format="svg" ) as img:
        img.UNIT_TYPES= "pixelsperinch"
        #img.save(filename=completeFileName)
        self.exportedData  = img.make_blob(exportFileFormat)
    
    elif(exportFileFormat.lower() == 'pdf'):
      fo = open(self.SAVE_PATH + "temp.svg", "wb")
      fo.write(svgString);

      # Close opend file
      fo.close()
      p=subprocess.call(['/usr/bin/inkscape', '--file='+ self.SAVE_PATH +'temp.svg', '--export-pdf='+ self.SAVE_PATH +'tempExp.pdf'])
      f = open(self.SAVE_PATH +"tempExp.pdf", "r")
      self.exportedData  = f.read()
      shutil.rmtree(self.SAVE_PATH, ignore_errors=True)
      
    # this code sends the provided file as downloadable to the browser as a response 
    response = HttpResponse(content_type='application/'+exportFileFormat)
    response.write(self.exportedData )
    response["Content-Disposition"]= "attachment; filename=converted." + exportFileFormat  
    
    return response  
