# Fusioncharts Exporter Handler

FusionCharts export handler for Django.

## Installation

1. Add fusioncharts_export_server.py file to your project:
2. Import fusioncharts_export_server in **views.py**
3. call this method **_export = FcExporterController(request).init()_** with request as parameter and return the response.


## Introduction

### What is it?
FusionCharts Suite XT uses JavaScript to generate charts in the browser, using SVG and VML (for older IE). If you need to export the charts as images or PDF, you need a server-side helper library to convert the SVG to image/PDF. These export handlers allow you to take the SVG from FusionCharts charts and convert to image/PDF.

### How does the export handler work?
- A chart is generated in the browser. When the export to image or PDF button is clicked, the chart generates the SVG string to represent the current state and sends to the export handler. The export handler URL is configured via chart attributes.
- The export handler accepts the SVG string along with chart configuration like chart type, width, height etc., and uses [InkScape](https://inkscape.org/en/) and [ImageMagick](http://www.imagemagick.org/) library to convert to image or PDF.
- The export handler either writes the image or PDF to disk, based on the configuration provided by chart, or streams it back to the browser.

## Pre-requisites
You will have to install the following applications without which the exporter will fail to run.
- [Inkscape](http://inkscape.org/en/download/)
- [ImageMagick](http://www.imagemagick.org/script/download.php
)


## Configuration
The following are the configurables to be modified as required in the 
1. `settings.py`:
2. `urls.py`
3. `views.py`

Location of the Inkscape executable.

`inkscape_path`

Location on the server where the image will be saved.

`save_path`

## Mount the application
You will have to specify the end point of the export server. In order to do this, you will have to mount the export handler to your django application. Add the following lines in `urls.py`.

~~~
url(r'^<PATH>/', views.export_chart, name='exportChart'),
~~~

For eg., if you want your export server hosted at `http://<my-website>/fc_exporter`, then add the following lines:
~~~
url(r'^fc_exporter/', views.export_chart, name='exportChart'),
~~~
