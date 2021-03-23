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

import sys, pygame, math, numpy, random, time, copy, heapq
from pygame.locals import * 

from constants import *
from utils import *
from core import *
from mycreatepathnetwork import *
from mynavigatorhelpers import *


###############################
### AStarNavigator
###
### Creates a path node network and implements the A* algorithm to create a path to the given destination.
			
class AStarNavigator(NavMeshNavigator):

	def __init__(self):
		NavMeshNavigator.__init__(self)
		

	### Create the path node network.
	### self: the navigator object
	### world: the world object
	def createPathNetwork(self, world):
		self.pathnodes, self.pathnetwork, self.navmesh = myCreatePathNetwork(world, self.agent)
		return None
		
	### Finds the shortest path from the source to the destination using A*.
	### self: the navigator object
	### source: the place the agent is starting from (i.e., its current location)
	### dest: the place the agent is told to go to
	def computePath(self, source, dest):
		self.setPath(None)
		### Make sure the next and dist matrices exist
		if self.agent != None and self.world != None: 
			self.source = source
			self.destination = dest
			### Step 1: If the agent has a clear path from the source to dest, then go straight there.
			###   Determine if there are no obstacles between source and destination (hint: cast rays against world.getLines(), check for clearance).
			###   Tell the agent to move to dest
			### Step 2: If there is an obstacle, create the path that will move around the obstacles.
			###   Find the path nodes closest to source and destination.
			###   Create the path by traversing the self.next matrix until the path node closest to the destination is reached
			###   Store the path by calling self.setPath()
			###   Tell the agent to move to the first node in the path (and pop the first node off the path)
			if clearShot(source, dest, self.world.getLinesWithoutBorders(), self.world.getPoints(), self.agent):
				self.agent.moveToTarget(dest)
			else:
				start = findClosestUnobstructed(source, self.pathnodes, self.world.getLinesWithoutBorders())
				end = findClosestUnobstructed(dest, self.pathnodes, self.world.getLinesWithoutBorders())
				if start != None and end != None:
					# print len(self.pathnetwork)
					newnetwork = unobstructedNetwork(self.pathnetwork, self.world.getGates())
					# print len(newnetwork)
					closedlist = []
					path, closedlist = astar(start, end, newnetwork)
					if path is not None and len(path) > 0:
						path = shortcutPath(source, dest, path, self.world, self.agent)
						self.setPath(path)
						if self.path is not None and len(self.path) > 0:
							first = self.path.pop(0)
							self.agent.moveToTarget(first)
		return None
		
	### Called when the agent gets to a node in the path.
	### self: the navigator object
	def checkpoint(self):
		myCheckpoint(self)
		return None

	### This function gets called by the agent to figure out if some shortcuts can be taken when traversing the path.
	### This function should update the path and return True if the path was updated.
	def smooth(self):
		return mySmooth(self)

	def update(self, delta):
		myUpdate(self, delta)


def unobstructedNetwork(network, worldLines):
	newnetwork = []
	for l in network:
		hit = rayTraceWorld(l[0], l[1], worldLines)
		if hit == None:
			newnetwork.append(l)
	return newnetwork


def generateSucessors(node, network):
	sucs = []
	for edge in network:
		if node == edge[0]:
			if edge[1] not in sucs:
				sucs.append(edge[1])
		elif node == edge[1]:
			if edge[0] not in sucs:
				sucs.append(edge[0])
	return sucs

def contains(nextNode, openList):
	for node in openList:
		if node[1] == nextNode:
			return True
	return False

def get(nextNode, openList):
	for node in openList:
		if node[1] == nextNode:
			return node[0]
	return -1

def getPath(nextNode, openList):
	for node in openList:
		if node[1] == nextNode:
			return node[2]
	return []

def astar(init, goal, network):
	path = []
	openList = []
	closedList = []
	parentTracker = {}
	gDict = {}
	### YOUR CODE GOES BELOW HERE ###
	#cost function is distance(p1, p2)
	heapq.heappush(openList, (0, init))
	gDict[init] = 0
	while len(openList) > 0:
		print(openList)
		#get current node
		info = heapq.heappop(openList)
		currentDist, currentNode = info
		closedList.append(currentNode)

		if currentNode == goal:
			path = []
			current = currentNode
			while current is not None:
				path.append(current)
				current = parentTracker[current] if current in parentTracker.keys() else None
			return path[::-1], closedList

		children = generateSucessors(currentNode, network)

		for child in children:
			if child in closedList:
				continue
			# f = currentNode.g + h
			g = gDict[currentNode] + distance(currentNode, child) 
			if contains(child, openList):
				if g > gDict[child]:
					continue
			parentTracker[child] = currentNode
			gDict[child] = g
			h = distance(child, goal)
			f = gDict[child] + h
			heapq.heappush(openList, (f, child))

	### YOUR CODE GOES ABOVE HERE ###
	return path, closedList

def myUpdate(nav, delta):
	### YOUR CODE GOES BELOW HERE ###
	obstacles = nav.world.getGates()
	#print(obstacles)
	goal = nav.getDestination()
	#print(goal)
	#print(nav.agent.getLocation())
	#print(nav.agent.moveTarget)
	agent = nav.agent

	if not clearShot(agent.getLocation(), agent.getMoveTarget(), nav.world.getLines(), [], agent):
		nav.world.getAgent().stopMoving()
		nav.setPath(None)
		return None	
	### YOUR CODE GOES ABOVE HERE ###
	return None

def myCheckpoint(nav):
	### YOUR CODE GOES BELOW HERE ###
	obstacles = nav.world.getGates()
	#print(obstacles)
	goal = nav.getDestination()
	#print(goal)
	#print(nav.agent.getLocation())
	#print(nav.agent.moveTarget)
	agent = nav.agent
	for obstacle in obstacles:
		#Agent should not hit gate (Raytrace)
		if rayTrace(agent.getLocation(), agent.moveTarget, obstacle) is not None:
			nav.world.getAgent().stopMoving()
			nav.setPath(None)
			return None			
		#Agent should not be too close to gate while moving
		if minimumDistance(obstacle, agent.getLocation()) <= agent.getMaxRadius():
			nav.world.getAgent().stopMoving()
			nav.setPath(None)
			return None
		#Destination should be valid
		if goal is None:
			nav.world.getAgent().stopMoving()
			nav.setPath(None) #must recompute using astar
			return None
	### YOUR CODE GOES ABOVE HERE ###
	return None

### Returns true if the agent can get from p1 to p2 directly without running into an obstacle.
### p1: the current location of the agent
### p2: the destination of the agent
### worldLines: all the lines in the world
### agent: the Agent object
def clearShot(p1, p2, worldLines, worldPoints, agent):
	### YOUR CODE GOES BELOW HERE ###
	if rayTraceWorld(p1, p2, worldLines) is not None:
		return False

	for obPoint in worldPoints:
		if minimumDistance((p1, p2), obPoint) <= agent.getMaxRadius():
			return False

	#for obpoint in worldPoints:
	#	if agent.getMaxRadius() > minimumDistance((p1, p2), obpoint):
	#		return False
	
	### YOUR CODE GOES ABOVE HERE ###
	return True
