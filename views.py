# Create your views here.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

import base64
from bson.objectid import ObjectId
from datetime import datetime
from gridfs import GridFS
import json
import numpy as np
import os

from storage import database
from centraldb.decorators import cached_call
from mapper.utils import osm_latlon_to_tile_number, osm_tile_number_to_latlon
from mapper.cell_utils import getMergedCells
from mapper.utils import pointStyle
from plotting.utils import plotBarGraph, plotCDF

def index(request):
    return air_map(request)

@cached_call
def air_map_get_points_bysource(srcId):
	retval = []
	client = database.getClient()
	point_collection = client.point_database.sensors.find({'sourceId':ObjectId(srcId)})
	GPS = (-1,-1)
	for point in point_collection:
		if point['sensorType'] == 'GPS':
			GPS = point['sensorValue']
		elif point['sensorType'] == 'PM2.5':
			if GPS != (-1, -1):
				retval.append(GPS + [point['sensorValue']])
	client.close()
	return retval

def tile_map(request):
	tiling_level = 17
	response = None
	client = database.getClient()
	db = client.trace_database
	fs = GridFS(db)
	responseData = {'trajectories':[], 'points':[], 'rectangles':[]}
	tiledMeasures = {}
	for traceFile in fs.find():
		if 'sourceTypes' in traceFile.metadata and "vastplace_example" in traceFile.metadata['sourceTypes']:
			points = air_map_get_points_bysource(traceFile._id)
			responseData['trajectories'].append({'points': [[lon, lat] for lat, lon, _ in points], 'id':traceFile._id})
			for lat, lon, val in points:
				tile_number = osm_latlon_to_tile_number(lon, lat, tiling_level)
				if tile_number not in tiledMeasures:
					tiledMeasures[tile_number] = []
				tiledMeasures[tile_number].append(val)

	for tileX, tileY in tiledMeasures:
		x1, y1 = osm_tile_number_to_latlon(tileX, tileY, tiling_level)
		x2, y2 = osm_tile_number_to_latlon(tileX + 1, tileY + 1, tiling_level)
		mean = np.mean(tiledMeasures[tileX, tileY])
		mean_str = "%.3f" % mean
		if mean > 10:
            		color = 'rgba(255, 0, 0, 0.3)'
		else:
            		color = 'rgba(0, 255, 0, 0.3)'
		responseData['rectangles'].append((x1, x2, y1, y2, mean_str, color))

	client.close()
        return render(request, 'mapper/map.html', responseData)



def cell_map(request):
    osm_zoom = 17


    responseData = {'trajectories':[], 'points':[]}
    responseData['point_styles'] = []

    pm2point5_cells = getMergedCells('vastplace_example', 'PM2.5', osm_zoom)

    for u in pm2point5_cells:
        gps, average = u
        color = intToGreenRedColor(average, 0, 25)
        responseData['point_styles'].append(pointStyle(color[1:], color, 3))
    	responseData['points'] +=  [{'lonlat':[gps[-1], gps[0]], 'style':color[1:]}]

    responseData['trajectories'].append({'points': [[u[0][1], u[0][0]], [u[0][-1], u[0][0]]]})

    return render(request, 'mapper/map.html', responseData)

def intToGreenRedColor(pInt, minValue, maxValue):
    """ Red means value equals to max, green, equals to min"""
    if pInt < minValue:
        pInt = minValue
    if pInt > maxValue:
        pInt = maxValue

    ratio = int(float(pInt - minValue) / (maxValue - minValue)  * 255)

    red_hex = hex(ratio)
    green_hex = hex(255 - ratio)


    red_str = str(red_hex)[2:]
    if len(red_str) == 1:
        red_str = "0" + red_str
    green_str = str(green_hex)[2:]
    if len(green_str) == 1:
        green_str = "0" + green_str

    retval = "#%s%s00" % (red_str, green_str)

    return retval
