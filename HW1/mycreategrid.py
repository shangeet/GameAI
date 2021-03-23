'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import *

from constants import *
from utils import *
from core import *


def checkPIPL(points, lines):
	ans = False
	for point in points:
		ans = ans or pointInsidePolygonLines(point, lines)
	return ans

def checkPIP(points, obstacle):
	ans = False
	for point in points:
		ans = ans or obstacle.pointInside(point)
	return ans
	
# Creates a grid as a 2D array of True/False values (True = traversable). Also returns the dimensions of the grid as a (columns, rows) list.
def myCreateGrid(world, cellsize):
	grid = None
	dimensions = (0, 0)
	### YOUR CODE GOES BELOW HERE ###
	gridSize = world.getDimensions();
	xCellsLen = int(math.ceil(float(gridSize[0])/cellsize))
	yCellsLen = int(math.ceil(float(gridSize[1])/cellsize))
	dimensions = (xCellsLen, yCellsLen)
	grid = [[True for i in range(dimensions[1])] for j in range(dimensions[0])]
	obstacles = world.getObstacles()
	for y in range(dimensions[1]):
		for x in range(dimensions[0]):
			gridPoint = (x*cellsize, y*cellsize) #must convert point to grid dimensions
			gridPointRight = (gridPoint[0] + cellsize, gridPoint[1])
			gridPointTop = (gridPoint[0], gridPoint[1] + cellsize)
			gridPointDiag = (gridPoint[0] + cellsize, gridPoint[1] + cellsize)
			#Conditions:
			#1. Point should not be within any obstacle. Mark false
			for obstacle in obstacles:
				lines = obstacle.getLines()
				if checkPIPL([gridPoint, gridPointRight, gridPointTop, gridPointDiag], lines):
					grid[x][y] = False

				if checkPIP([gridPoint, gridPointRight, gridPointTop, gridPointDiag], obstacle):
					grid[x][y] = False
			#2. Obstacle line should not cross traversable grid cell. Mark false
				for line in lines:
					if rayTrace(gridPoint, gridPointRight, line) or rayTrace(gridPoint, gridPointTop, line) \
						or rayTrace(gridPointRight, gridPointDiag, line) or rayTrace(gridPointTop, gridPointDiag, line):
						grid[x][y] = False
			#3. Grid should not be traversable if cell exceeds dimensions
			maxXDim = (dimensions[0] - 1) * cellsize
			maxYDim = (dimensions[1] - 1) * cellsize
			if gridPointRight[0] > maxXDim or gridPointTop[1] > maxYDim:
			 	grid[x][y] = False

	### YOUR CODE GOES ABOVE HERE ###
	return grid, dimensions

