from django.shortcuts import render
from django.http import HttpResponse
from export_server import FcExporterController

def fc(request):
 	return  render(request, 'fusioncharts.html')

def export_chart(request):
	export = FcExporterController(request)
	export_data = export.init()
	return export_data


