from django.shortcuts import render
from django.http import HttpResponse
from export_server import FcExporterController
import re
from xml.sax.saxutils import escape
def fc(request):
 	return  render(request, 'fusioncharts.html')

def export_chart(request):
  export = FcExporterController(request).init()
  return export

