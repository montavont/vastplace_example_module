# Copyright (c) 2012 Institut Mines-Telecom / Telecom Bretagne. All rights reserved.
#
# This file is part of Wi2Me.
#
# Wi2Me is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Wi2Me is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Wi2Me.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import sqlite3
from gridfs import GridFS
from bson.objectid import ObjectId

from storage import database
from datetime import datetime

class csv_parser:
	def __init__(self, fileId):
		self.fileId = fileId
		self.tags = []

	def getEvents(self):
		retval = []

		client = database.getClient()
		file_db = client.trace_database
		fs = GridFS(file_db)
		traceFile = fs.get(ObjectId(self.fileId))

		#Copy the original db file
		outPath = '/tmp/mongo_tmpfile_' + self.fileId
		outF = open(outPath, 'w')
		line = traceFile.readline()
		while len(line) > 0:
			outF.write(line)
			line = traceFile.readline()
		outF.close()

		fIn = open(outPath)
		line = fIn.readline()
		lastGpsFix = (-1, -1)
		while len(line) > 0:
			data = line.rstrip('\n').split(',')
			if len(data) >= 2:
				date_data, lat, lon, value  = data
				lat = float(lat)
				lon = float(lon)
				value = float(value)

				ts_str = date_data[:-6]
				tz = date_data[-6:]

				dt = datetime.strptime(ts_str[:26], '%Y-%m-%dT%H:%M:%S.%f')
				timestamp =float(dt.strftime('%s'))

				#Use timezone information to convert back to UTC (+00:00)
				if tz[0] == '+':
					offsetSign = -1
				else:
					offsetSign = 1
				offset_hours, offset_minutes = tz[1:].split(':')
				offset_hours = int(offset_hours)
				offset_minutes = int(offset_minutes)

				timestamp += offsetSign * (offset_hours * 3600 + offset_minutes * 60)

				if (lat, lon) != lastGpsFix:
					retval.append({
        				                "sourceId":ObjectId(self.fileId),
       			        	                "sensorName" : "example_module",
                       				        "sensorID" : "example_module",
							"vTimestamp" : timestamp,
	                               			"tstype" : "epoch",
        		        	        	"sensorType" : "GPS",
	       	        		                "sensorValue" : (lat, lon)
		                       	})
					lastGpsFix = (lat, lon)

				retval.append({
        			                "sourceId":ObjectId(self.fileId),
       		        	                "sensorName" : "example_module",
                       			        "sensorID" : "example_module",
						"vTimestamp" : timestamp,
	                               		"tstype" : "epoch",
        		        	        "sensorType" : "PM2.5",
       	        		                "sensorValue" : value
	                       	})

			line = fIn.readline()

		return retval
