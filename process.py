# -*- coding: utf-8 -*-

import cv2
import numpy as np
import os
import re
import sys

OPACITY = 0.6
TOTAL_RADIUS = 17
LINE_RADIUS = 2

FILE_WIDTH = 1300
FILE_HEIGHT = 800

MAX_LAT = 51.9290250565189
MAX_LON = -69.12597687499999
MIN_LAT = 24.983569037855027
MIN_LON = -126.25488312499999

LAT_DELTA = MAX_LAT - MIN_LAT
LON_DELTA = MAX_LON - MIN_LON

LAT_STEP = LAT_DELTA / FILE_HEIGHT
LON_STEP = LON_DELTA / FILE_WIDTH

def getTime(fileName):
    s = re.split("\D+", fileName)
    if(s[3] != '21'):
        return None
    return s[4] + ':' + s[5] + ':00'

def getDateTime(fileName):
    s = re.split("\D+", fileName)
    return s[1] +"/"+ s[2] +"/"+ s[3] +" "+ s[4] + ":" + s[5] + " EDT"


def parseDec(dms):
    s = re.split("\D+", dms)
    d = float(s[0])
    m = (float(s[1]) + float(s[2])/100.0)/60
    dec = d + m
    return dec

def latLonToXY(lat, lon):
    center_x = int(((lon - MIN_LON) / LON_DELTA) * FILE_WIDTH) 
    center_y = FILE_HEIGHT - (int(((lat - MIN_LAT) / LAT_DELTA) * FILE_HEIGHT)) + 30
    return(center_x, center_y)

def parsePathData():
    path_data = {}
    path_data_file = open("path-data.txt", "r")
    for line in path_data_file:
        tkns = line.split()
        t = tkns[4]
        s = re.split("\D+", t)
        time = str(int(s[0]) - 4) + ":"+ s[1] + ":" + s[2] 

        lon = parseDec(tkns[0]) * -1
        lat_n = parseDec(tkns[1])
        lat_s = parseDec(tkns[2])
        lat_c = parseDec(tkns[3])
        path_data[time] = {"lon":lon, "lat_n":lat_n, "lat_s":lat_s, "lat_c":lat_c}
    return path_data

def drawEclipsePath(outfile):
    layer = np.copy(outfile)
    for path_time, path_vals in path_data.iteritems():
        center_lon = path_vals["lon"]
        center_lat = path_vals["lat_c"]
        north_lat = path_vals["lat_n"]
        south_lat = path_vals["lat_s"]

        center = latLonToXY(center_lat, center_lon)
        north = latLonToXY(north_lat, center_lon)
        south = latLonToXY(south_lat, center_lon)

        cv2.circle(layer, center, LINE_RADIUS, (200, 50, 50), thickness=-1)
        #cv2.circle(layer, north, LINE_RADIUS, (50, 50, 200), thickness=-1)
        #cv2.circle(layer, south, LINE_RADIUS, (50, 50, 200), thickness=-1)

    cv2.addWeighted(outfile, OPACITY, layer, 1 - OPACITY, 0, outfile)

def drawTotality(outfile, time):
    path_vals = path_data[time]
    center_lon = path_vals["lon"]
    center_lat = path_vals["lat_c"]

    center = latLonToXY(center_lat, center_lon)

    layer = np.copy(outfile)

    #cv2.circle(outfile, center, TOTAL_RADIUS, (50, 50, 50), thickness=2)
    cv2.circle(layer, center, TOTAL_RADIUS, (50, 50, 50), thickness=-1)
        
    cv2.addWeighted(outfile, OPACITY, layer, 1 - OPACITY, 0, outfile)


def drawTime(outfile, datetime):
    #cv2.putText(outfile,time, (100, 700), cv2.FONT_HERSHEY_SIMPLEX, 1, (155, 0, 255), 2)
    cv2.putText(outfile, datetime, (50, 750), cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 50), 1)
    #cv2.putText(outfile, 'E Shepherd', (50, 770), cv2.FONT_HERSHEY_SIMPLEX, .3, (50, 50, 50), 1)


if(len(sys.argv) <= 1):
    print sys.argv
    print "need to specify 'us' or 'sm'"
    exit(0)
print sys.argv
loc = sys.argv[1]

path_data = parsePathData()
regex = r""+loc+"-.*\.png"
files = [f for f in os.listdir('./'+ loc) if re.match(regex, f)]

for sourceFile in files:
    print sourceFile
    infile = cv2.imread('./'+ loc +'/'+sourceFile)
    outfile = np.copy(infile)
    drawEclipsePath(outfile)
    time = getTime(sourceFile)
    if((time is not None) and (time in path_data)):
        drawTotality(outfile, time)
    drawTime(outfile, getDateTime(sourceFile))

    cv2.imwrite("output/"+ loc +"/"+sourceFile + "out.png", outfile)

