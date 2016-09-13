# FusionCharts Exporter is a python script that handles 
# FusionCharts (since v3.5.0) Server Side Export feature.
# This in conjuncture with various export classes would 
# process FusionCharts Export Data POSTED to it from FusionCharts 
# and convert the data to image or PDF and subsequently save to the 
# server or response back as http response to client side as download.
#
# This script might be called as the FusionCharts Exporter - main module 
#
#    @author FusionCharts
#    @description FusionCharts Exporter (Server-Side - ROR)
#    @version 1.0 [ 13 Sept 2016 ]
#  
#
#
#  ChangeLog / Version History:
#  ----------------------------
#       
#   1.0 [ 13 Sept 2016 ] 
#       - Integrated with new Export feature of FusionCharts 3.11.0
#       - Support for export if direct image is base64 encoded
#         (data provided by the FusionCharts v3.11.0)
#         Add a comment to this line
#       - Support for download in the XLS format
#       - Export with images suppported for every format including svg 
#         if browser is capable of sending the image data as SVG format.
#       - can process chart data to jpg image and response back to client side as download.
#       - Support for JavaScript Chart (SVG)
#       - can save to server side directory
#       - can save as PDF/JPG/PNG
#
#
# Copyright (c) 2016 InfoSoft Global Private Limited. All Rights Reserved
# 
#
#  GENERAL NOTES
#  -------------
#
#  Chart would POST export data (which consists of encoded image data stream,  
#  width, height, background color and various other export parameters like 
#  exportFormat, exportFileName, exportAction, exportTargetWindow) to this script. 
#  
#  The script would process this data using appropriate resource classes & build 
#  export binary (PDF/image) 
#
#  It either saves the binary as file to a server side directory or push it as
#  Download to client side.
#
#
#
#   Dependencies to run the Export Handler
#   -------------------------------------
#     1.) wand - url http://docs.wand-py.org/en/0.4.2/
#     2.) inkscape - url - https://inkscape.org/
#
#   Installing wand and inkscape in ubuntu
#   --------------------------------------
#     inkscape installation command
#       1.)  $ sudo apt-get install inkscape
#     
#     wand installation command
#       2.)  $ apt-get install libmagickwand-dev
#       3.)  $ pip install Wand
#
#
#   Setup Export Handler in Django application
#   ------------------------------------------
#    In the view, from FCExporter import FcExporterController and 
#    this should be called from view like this
#
#     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     |   #importing export Handler                          |
#     |   from FCExporter import FcExporterControlle         |
#     |   def exportChart(request):                          |  
#     |     #sending request object to the Export handler    |
#     |     export = FcExporterController(request).init()    |      
#     |     return export                                    |
#     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#
#   Setup the url dispatcher in urls.py as
#   --------------------------------------
#     In order to call export handler, you need to design a URL patterns like this
#
#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   |   url(r'^FCExporter/', views.exportChart, name='exportChart'),    |
#   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#
#   Add Export Handler in the fusioncharts datasouce as
#   ----------------------------------------------------
#
#   "exportHandler" : "http://localhost:<PORT-NUMBER(eg. 3000)>/FCExporter/"
# 

import os, sys, subprocess, re, json
from django.http import HttpResponse
# Importing wand module
from wand.image import Image


class FcExporterController:

  # settings variable declaration begins
  SAVE_PATH = "export/Exported_Images/"
  INKSCAPE_PATH = "/usr/bin/inkscape"
  # settings variable declaration ends

  # initialinzing request object in instance variable
  def __init__(self, request):
    self.request = request


  # export related operation done here  
  def init(self):
    # this function `checkAndCreateDirectories` check for the directories needed to export image
    mkdirResponse = self.checkAndCreateDirectories(self.SAVE_PATH)

    if(not isinstance(mkdirResponse, HttpResponse)):
      # This function `parseRequestParams` purse the request and create the request Data object
      requestObject = self.parseRequestParams(self.request.POST)

      if(type(requestObject) is str):
        return self.raiseError(400)

      elif(type(requestObject) is dict):
        stream = requestObject['stream']
        # replacing single-quote with nothing because of converting in jpg image
        stream = re.sub(r'\'', "", stream)
        if(requestObject["stream_type"] == "IMAGE-DATA"):
          response = self.prepareAndSendFile(stream, requestObject)
        else:  
          if(requestObject['imageData']):
           stream = self.replaceImageToSVG(stream, requestObject['imageData'])

          response = self.convertSVGtoImage(stream, requestObject)

        # sends the respnse to the constructor instanec varibale
        return response

      elif(isinstance(requestObject, HttpResponse)):
        return requestObject
    else:
      return mkdirResponse        
  

  # this function check for the directories needed to export image and 
  # if not present then it creates the directories
  def checkAndCreateDirectories(self, location):
    if(not os.path.isdir(location)):
      try:
        os.mkdir(location)
        return 'success'
      except Exception, e:
        return HttpResponse(e)
   

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
  	exportAction = "" # by default it is as `download`
  
  	if(requestData.has_key("stream")):
  		stream = requestData["stream"]
  	else:
  		return self.raiseError(100)

  	if(requestData.has_key("stream_type")):
  		stream_type = requestData["stream_type"]
  	else:
  		return self.raiseError(100)

  	if(requestData.has_key("encodedImgData")):
  		imageData = requestData["encodedImgData"]

  	if(requestData["parameters"] != ""):
  		parametersArray = requestData["parameters"].split("|")
  	else:
  		return self.raiseError(100)
      
  	if(parametersArray[0].split("=").pop() and parametersArray[1].split("=").pop() and parametersArray[2].split("=").pop()):
	  	exportFileName = parametersArray[0].split("=").pop()
	  	exportFormat = parametersArray[1].split("=").pop()
	  	exportAction = parametersArray[2].split("=").pop()

  	if(requestData.has_key("meta_width") and requestData.has_key("meta_height")):
  		width = requestData["meta_width"]
  		height = requestData["meta_height"]
  	elif(exportFormat.lower() != "xls"):
  		return self.raiseError(101)

  	# preparing the request object
  	requestObject = {
  		"stream" : stream, 
  		"imageData" : imageData, 
  		"width" : width, 
  		"height" : height, 
  		"exportFileName" : exportFileName, 
  		"exportFormat" : exportFormat, 
  		"exportAction" : exportAction,
      "stream_type" : stream_type
  	}

  	return requestObject

  
  # this method raise the error based on the error code
  def raiseError(self, errorCode):
    errorArray = {
      100 : " Insufficient data.", 
      101 : " Width/height not provided.", 
      102 : " Insufficient export parameters.", 
      400 : " Bad request.", 
      401 : " Unauthorized access.", 
      403 : " Directory write access forbidden.", 
      404 : " Export Resource not found.",
      405 : " Writing permission denined"
    }
    return HttpResponse(errorArray[errorCode]) 
   

  # this function replaces the image href with image data 
  def replaceImageToSVG(self, svgString, imageData):
    imageDataArray = json.loads(imageData) # parsing the image data object
    keys = imageDataArray.keys() # holds the keys like image_1, image_2 etc
    # matches array holds the physical paths of images lies in the SVG  
    matches =re.findall(r'xlink:href\s*=\s*"([^"]*)"', svgString,  re.M|re.I) 
    
    # looping through all of the matches
    for match in matches:
      imageName = match.split("/").pop().split(".")[0]
      imageData = ""
      # looping through the images of json data 
      for key in keys:
        if(imageDataArray[key]['name'] == imageName):
            imageData = imageDataArray[key]['encodedData']
            break
      
      # replacing the image href with image data  
      svgString = re.sub(match, imageData, svgString);
  
    return svgString
    

  # This function coverts the provided SVG string to image or pdf file		
  def convertSVGtoImage(self, svgString, reqObj):
    exportFileName = reqObj['exportFileName']
    exportFileFormat = reqObj['exportFormat']
    self.SAVE_PATH = self.SAVE_PATH+exportFileName+"."+exportFileFormat
    
    if(exportFileFormat.lower() == 'svg'):
      exportedData = svgString

    elif(exportFileFormat.lower() != 'pdf'):
      with Image( blob=str(svgString), format="svg" ) as img:
        img.UNIT_TYPES= "pixelsperinch"
        #img.save(filename=completeFileName)
        exportedData  = img.make_blob(exportFileFormat)
    
    elif(exportFileFormat.lower() == 'pdf'):
      fo = open(self.SAVE_PATH + "temp.svg", "wb")
      fo.write(svgString);
      # Close the opend file
      fo.close()

      #using inkscape to conver SVG to PDF 
      p=subprocess.call([self.INKSCAPE_PATH, '--file='+ self.SAVE_PATH +'temp.svg', '--export-pdf='+ self.SAVE_PATH +'tempExp.pdf'])
      f = open(self.SAVE_PATH +"tempExp.pdf", "r")
      exportedData  = f.read()
      f.close()

    else:
      return "invalid file format."
      
    # this code creates the response that provide the file as downloadable to the browser
    response = HttpResponse(content_type='application/'+exportFileFormat)
    response.write(exportedData )
    response["Content-Disposition"]= "attachment; filename="+exportFileName+"."+exportFileFormat
    return response


  # if the stream type is IMAGE-DATA then this function will be called
  def prepareAndSendFile(self, stream, reqObj):
    exportFileName = reqObj['exportFileName']
    exportFileFormat = reqObj['exportFormat']
    self.SAVE_PATH = self.SAVE_PATH + exportFileName + "." + exportFileFormat
    imageData = stream.split(',')[1];
    fh = open(self.SAVE_PATH, "wb")
    fh.write(imageData.decode('base64'))
    fh.close()

    f = open(self.SAVE_PATH, "r")
    exportedData  = f.read()
    f.close()

    if(reqObj["exportAction"] == "download"):
      os.remove(self.SAVE_PATH)

    #create a response object and send the image file within response object
    response = HttpResponse(content_type='application/'+exportFileFormat)
    response.write(exportedData)
    response["Content-Disposition"]= "attachment; filename="+exportFileName+"."+exportFileFormat  
    return response  
          