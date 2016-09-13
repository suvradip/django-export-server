from django.shortcuts import render
from FCExporter import FcExporterController
def fc(request):
 	return  render(request, 'fusioncharts.html')

def export_chart(request):
  export = FcExporterController(request).init()
  return export

