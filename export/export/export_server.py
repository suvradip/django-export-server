import os
import cairo, rsvg


from wand.api import library
import wand.color
import wand.image

class FcExporterController:

  # settings variable declaration begins
  SAVE_PATH = "export/exported_images/"
  # settings variable declaration ends

  # this method should be called as http://localhost:<PORT-NUMBER(eg. 3000)>/fc_exporter/init/ from javascript
  def __init__(self, request):
    self.request = request

  def start(self):
    self.checkAndCreateDirectories([FcExporterController.SAVE_PATH])
    requestObject = self.parseRequestParams(self.request.POST)
    stream = requestObject['stream']

    self.convertSVGtoImage(stream, requestObject['exportFileName'] ,requestObject['exportFormat'])
    print 'test'
    return requestObject
  
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
  		
  def convertSVGtoImage(self, svgString, exportFileName, exportFileFormat):
    #completeFileName = self.SAVE_PATH+exportFileName+"."+exportFileFormat
    ## cairosvg.svg2png(bytestring=svgString, write_to=completeFileName)
    # svg = rsvg.Handle(data=svgString) 
    # width = svg.props.width 
    # height = svg.props.height 
    # print width
    # # create PDF 
    # surf = cairo.PDFSurface('output.pdf', width, height) 
    # cr = cairo.Context(surf) 
    # svg.render_cairo (cr) 
    # surf.finish() 
    print "complete write" 

    with wand.image.Image(blob=str(svgString), format="svg") as image:
      with wand.color.Color('transparent') as background_color:
          library.MagickSetBackgroundColor(image.wand, background_color.resource) 
      #image.read(blob=svgString, format="svg")
      png_image = image.make_blob("png")

    with open('test.png', "wb") as out:
      out.write(png_image)  
