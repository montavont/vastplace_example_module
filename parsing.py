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

		line = traceFile.readline()
		while len(line) > 0:
			data = line.rstrip('\n').split('\t')
			if len(data) >= 1:
                            if data[1] == "GPS":
				timestamp, _, lat, lon = data
				lat = float(lat)
				lon = float(lon)

				retval.append({
       				                "sourceId":ObjectId(self.fileId),
     		        	                "sensorName" : "example_module",
                 				"sensorID" : "example_module",
						"vTimestamp" : int(timestamp),
                               			"tstype" : "epoch",
        		        	        "sensorType" : "GPS",
	       	        		        "sensorValue" : (lat, lon)
		                       	})
                            elif data[1] == "metal":
				timestamp, _, value = data
				retval.append({
        			                "sourceId":ObjectId(self.fileId),
       		        	                "sensorName" : "example_module",
                       			        "sensorID" : "example_module",
						"vTimestamp" : int(timestamp),
	                               		"tstype" : "epoch",
        		        	        "sensorType" : "metal",
       	        		                "sensorValue" : float(value)
	                       	})

		        line = traceFile.readline()

		return retval
