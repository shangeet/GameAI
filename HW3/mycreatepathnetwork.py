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

import sys, pygame, math, numpy, random, time, copy, operator
import itertools
from pygame.locals import *

from constants import *
from utils import *
from core import *

def isPolyUsed(A, B, C, polys):
	used = False
	for poly in polys:
		if A in poly and B in poly and C in poly:
			return True
	return used

def checkCollision(world, pointA, pointB, pointC, polys):
	lines = world.getLines()
	for triangle in polys:
		lines.append((triangle[0], triangle[1]))
		lines.append((triangle[1], triangle[2]))
		lines.append((triangle[0], triangle[2]))

	for line in lines:
		if rayTraceNoEndpoints(pointA, pointB, line) is not None and ((pointA, pointB) not in lines) and ((pointB, pointA) not in lines):
			return True
		if rayTraceNoEndpoints(pointB, pointC, line) is not None and ((pointB, pointC) not in lines) and ((pointC, pointB) not in lines):
			return True
		if rayTraceNoEndpoints(pointA, pointC, line) is not None and ((pointA, pointC) not in lines) and ((pointC, pointA) not in lines):
			return True
	return False

def isTriOverlap(world, pointA, pointB, pointC, polys, obstacles):
	lines = world.getLines()
	for triangle in polys:
		lines.append((triangle[0], triangle[1]))
		lines.append((triangle[1], triangle[2]))
		lines.append((triangle[0], triangle[2]))

	for obstacle in obstacles:
		AB = midpoint(pointA, pointB)
		AC = midpoint(pointA, pointC)
		BC = midpoint(pointB, pointC)	
		obLines = obstacle.getLines()
		obPoints = obstacle.getPoints()

		#Check if triangle inside obstacle

		if pointInsidePolygonLines(AB, obLines) and (pointA, pointB) not in lines and ((pointB, pointA) not in lines):
			return True
		if pointInsidePolygonLines(AC, obLines) and (pointA, pointC) not in lines and ((pointC, pointA) not in lines):
			return True
		if pointInsidePolygonLines(BC, obLines) and (pointB, pointC) not in lines and ((pointC, pointB) not in lines):
			return True

		#check if obstacle inside triangle
		obMidpoint = centerOfPoints(obPoints)

		if pointInsidePolygonPoints(obMidpoint, (pointA, pointB, pointC)):
			return True
	return False

def checkAgentCollision(line, obstacles, agentSize):
	for obstacle in obstacles:
		for point in obstacle.getPoints():
			if minimumDistance(line, point) <= agentSize:
				return True
	return False

def centerOfPoints(points):
	xTotal = 0.0
	yTotal = 0.0
	for point in points:
		xTotal += point[0]
		yTotal += point[1]
	return (xTotal/len(points), yTotal/len(points))

def midpoint(A,B):
	return ((A[0] + B[0])/2.0, (A[1] + B[1])/2.0)				

def calculateAngle(center, point):
	return math.atan2(center[1] - point[1], center[0] - point[0])

def clockwiseDistance(points):
	centroid = centerOfPoints(points)
	arranged = sorted(points, key=lambda point: calculateAngle(centroid, point))
	return arranged

def mergeShapes(A,B): ##############################TODO Fix Merge Shapes##############################
	#remove common lines
	polyPoints = list(set(A + B))
	path = clockwiseDistance(polyPoints)
	return path

# Creates a path node network that connects the midpoints of each nav mesh together
def myCreatePathNetwork(world, agent = None):
	nodes = []
	edges = []
	polys = []
	### YOUR CODE GOES BELOW HERE ###
	points = world.getPoints()
	obstacles = world.getObstacles()
	agentSize = agent.getMaxRadius()
	#Step 1: Finding triangles
	#Get all combinations of points
	combinations = list(itertools.combinations(points, 3))
	#random.shuffle(combinations)

	for points in combinations:
		pointA, pointB, pointC = points
		canAdd = True
		#Make sure triangle formed is not already used
		canAdd = canAdd and not isPolyUsed(pointA, pointB, pointC, polys)
		#Make sure triangle formed does not overlap other obstacles
		canAdd = canAdd and not isTriOverlap(world, pointA, pointB, pointC, polys, obstacles)
		#Make sure triangle formed does not collide with another triangle
		canAdd = canAdd and not checkCollision(world, pointA, pointB, pointC, polys)

		if canAdd:
			polys.append([pointA, pointB, pointC])

	#Step 1.5: Optimization
	#Check if adjacent triangles can be merged
	for i in range(len(polys)):
		for shapeA in polys:
			for shapeB in polys:
				if shapeA != shapeB:
					if polygonsAdjacent(shapeA, shapeB):
						shapeAB = mergeShapes(shapeA, shapeB)
						if isConvex(shapeAB):
							polys.remove(shapeA)
							polys.remove(shapeB)
							if shapeAB not in polys:
								polys.append(shapeAB)
							break

	#Step 2: Node placement/Create path edges between nodes
	#Add nodes in center of lines (make sure all lines are unique)
	#Add nodes in the corners (offset by agent radius
	#Create edges between all path nodes of same poly 
	#Create edges between path nodes that participate in the same convex hull

	cornerLines = set(world.getLines()) - set(world.getLinesWithoutBorders())
	cornerPoints = []
	for line in cornerLines:
		for p in line:
			if p not in cornerPoints:
				cornerPoints.append(p)

	for polyA in polys:
		aNodes = []
		for polyB in polys:
			if polyA != polyB:
				if polygonsAdjacent(polyA, polyB):
					line = commonPoints(polyA, polyB)
					mp = midpoint(line[0], line[1])
					if mp not in nodes:
						nodes.append(mp)
					aNodes.append(mp)

		for n in range(len(aNodes) - 1):
			aLine = [aNodes[n], aNodes[n + 1]]
			if not checkAgentCollision(aLine, obstacles, agentSize):
				edges.append(tuple(aLine))

		for n in range(len(aNodes)):
			for corner in cornerPoints:
				if not rayTraceWorldNoEndPoints(aNodes[n], corner, world.getLines()):
					if not checkAgentCollision([corner, aNodes[n]], obstacles, agentSize): 
						edges.append((aNodes[n], corner))

		aLine = [aNodes[0], aNodes[len(aNodes) - 1]]
		if not checkAgentCollision(aLine, obstacles, agentSize):
			edges.append(aLine)

	#now add nodes for all corners
	### YOUR CODE GOES ABOVE HERE ###
	return nodes, edges, polys

	
