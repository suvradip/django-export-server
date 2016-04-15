'''
Dependencies to run the program
  1.) wand - url http://docs.wand-py.org/en/0.4.2/
  2.) inkscape - url - https://inkscape.org/

Installing wand and inkscape in ubuntu
  inkscape installation command
    1.)  $ sudo apt-get install inkscape
  wand installation command
    2.)  $ apt-get install libmagickwand-dev
    3.)  $ pip install Wand
'''
import os, sys, subprocess, shutil, re, json
from django.http import HttpResponse
# Importing wand module
from wand.image import Image


class FcExporterController:

  # settings variable declaration begins
  SAVE_PATH = "export/exported_images/"
  # settings variable declaration ends

  '''
  in the view, import the fusioncharts_export_server module and this method should be called from view like
  def export_chart(request):
    export = FcExporterController(request).init()
    return export

  set the url dispatcher in urls.py as
  url(r'^fc_exporter/', views.export_chart, name='exportChart'),

  add exporthandler in fusioncharts datasouce as
  "exportHandler" : "http://localhost:<PORT-NUMBER(eg. 3000)>/fc_exporter/"
  '''

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

        if(requestObject['imageData']):
          stream = self.replaceImageToSVG(stream, requestObject['imageData'])
        
        response = self.convertSVGtoImage(stream, requestObject['exportFileName'] ,requestObject['exportFormat'])
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
  	exportAction = ""
  
  	if(requestData.has_key("stream")):
  		stream = requestData["stream"]
  	else:
  		return self.raiseError(100)

  	if(requestData.has_key("encodedImgData")):
  		imageData = requestData["encodedImgData"]
  	
  	
  	if(requestData["meta_width"]!="" and requestData["meta_height"] !=""):
  		width = requestData["meta_width"]
  		height = requestData["meta_height"]
  	else:
  		return self.raiseError(101)
  	
  	
  	if(requestData["parameters"] != ""):
  		parametersArray = requestData["parameters"].split("|")
  	else:
  		return self.raiseError(100)

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
        
      svgString = re.sub(match, imageData, svgString); # replacing the image href with image data
  
    return svgString
    

  # This function coverts the provided SVG string to image or pdf file		
  def convertSVGtoImage(self, svgString, exportFileName, exportFileFormat):
    completeFileName = self.SAVE_PATH+exportFileName+"."+exportFileFormat
    
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
      # Close opend file
      fo.close()

      #using inkscape to conver SVG to PDF 
      p=subprocess.call(['/usr/bin/inkscape', '--file='+ self.SAVE_PATH +'temp.svg', '--export-pdf='+ self.SAVE_PATH +'tempExp.pdf'])
      f = open(self.SAVE_PATH +"tempExp.pdf", "r")
      exportedData  = f.read()
      f.close()

      # removing created directory and under its file
      shutil.rmtree(self.SAVE_PATH, ignore_errors=True)
      
    else:
      return "invalid file format."

    # this code sends the provided file as downloadable to the browser as a response 
    response = HttpResponse(content_type='application/'+exportFileFormat)
    response.write(exportedData )
    response["Content-Disposition"]= "attachment; filename=converted." + exportFileFormat  
    
    return response
