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
from plotting.utils import plotBarGraph, plotCDF, plotStep

def view_data(request, trace_id):
    responseData = {}
    return render(request, 'vastplace_example_module/overview.html', responseData)

def index(request):
    responseData = {}
    return render(request, 'vastplace_example_module/overview.html', responseData)

def get_points_bysource(srcId):
	retval = []
	client = database.getClient()
	point_collection = client.point_database.sensors.find({'sourceId':ObjectId(srcId)})
	GPS = (-1,-1)
	for point in point_collection:
		if point['sensorType'] == 'GPS':
			GPS = point['sensorValue']
		elif point['sensorType'] == 'metal':
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
			points = get_points_bysource(traceFile._id)
			responseData['trajectories'].append({'points': [[lon, lat] for lat, lon, _ in points], 'id':traceFile._id})
			for lat, lon, val in points:
                                val = float(val)
				tile_number = osm_latlon_to_tile_number(lon, lat, tiling_level)
				if tile_number not in tiledMeasures:
					tiledMeasures[tile_number] = []
				tiledMeasures[tile_number].append(val)

	for tileX, tileY in tiledMeasures:
		x1, y1 = osm_tile_number_to_latlon(tileX, tileY, tiling_level)
		x2, y2 = osm_tile_number_to_latlon(tileX + 1, tileY + 1, tiling_level)
		mean = np.mean(tiledMeasures[tileX, tileY])
		mean_str = "%.3f" % mean
		if mean > 10000:
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

    pm2point5_cells = getMergedCells('vastplace_example', 'metal', osm_zoom)

    for u in pm2point5_cells:
        gps, average = u
        color = intToGreenRedColor(average, 6000, 60000)
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

def get_example_points_for_source(sourceId):
	retval = []
	client = database.getClient()
	points = client.point_database.sensors.find({'sourceId':sourceId})

	for point in points:
		if point['sensorType'] == "metal":
			retval.append((point['vTimestamp'],point['sensorValue']))
	return retval


def metal_cdf(request):
	all_points = []

	client = database.getClient()
	fs = GridFS(client.trace_database)

	for traceFile in fs.find():
		if 'sourceTypes' in traceFile.metadata and "vastplace_example" in traceFile.metadata['sourceTypes']:
			points = get_example_points_for_source(traceFile._id)
			all_points += [p[1] for p in points]

	buf = plotCDF([
			{
				'data':all_points,
				'label' : "metal points",
				'color' : 'green'
			},
		],
		xlabel = ' Metal',
		ylabel = 'CDF',
		legend = False)

	return HttpResponse(buf, content_type='image/svg+xml')


def metal_bar(request):
	bins = {
                    30000 : 0,
                    60000 : 0
                }

	client = database.getClient()
	fs = GridFS(client.trace_database)

	for traceFile in fs.find():
		if 'sourceTypes' in traceFile.metadata and "vastplace_example" in traceFile.metadata['sourceTypes']:
			points = get_example_points_for_source(traceFile._id)
                        for point in points:
                            if point[1] <= 30000:
                                bins[30000] += 1
                            else:
                                bins[60000] += 1

	buf = plotBarGraph([
			{
				'X':[int(u) for u in bins.keys()],
				'Y':[bins[k] for k in bins],
				'label' : "Bin count",
				'width' : 5000,
				'color' : 'red'
			},
			{
				'X':[int(u) + 5000 for u in bins.keys()],
				'Y':[20 for k in bins],
				'label' : "always 20",
				'width' : 5000,
				'color' : 'green'
			}
		],
		xlabel = 'Sample bar graph',
		ylabel = 'The y axis label',
		legend = True)

	return HttpResponse(buf, content_type='image/svg+xml')


@api_view(['GET'])
def metal_rest(request):
	bins = {
                    'under 30000' : 0,
                    'over 30000' : 0
                }

	client = database.getClient()
	fs = GridFS(client.trace_database)

	for traceFile in fs.find():
		if 'sourceTypes' in traceFile.metadata and "vastplace_example" in traceFile.metadata['sourceTypes']:
			points = get_example_points_for_source(traceFile._id)
                        for point in points:
                            if point[1] <= 30000:
                                bins['under 30000'] += 1
                            else:
                                bins['over 30000'] += 1
	return Response(bins, status=status.HTTP_200_OK)


def metal_step(request):
	all_points = []

	client = database.getClient()
	fs = GridFS(client.trace_database)

	for traceFile in fs.find():
		if 'sourceTypes' in traceFile.metadata and "vastplace_example" in traceFile.metadata['sourceTypes']:
			points = get_example_points_for_source(traceFile._id)
			all_points += points

        all_points = sorted(all_points, key = lambda x : x[0])

	buf = plotStep([
			{
				'x':[u[0] - all_points[0][0] for u in all_points],
				'y':[u[1] for u in all_points],
				'label' : "metal points",
				'color' : 'green'
			},
		],
		xlabel = ' Time(s)',
		ylabel = 'Metal',
		legend = False)

	return HttpResponse(buf, content_type='image/svg+xml')

