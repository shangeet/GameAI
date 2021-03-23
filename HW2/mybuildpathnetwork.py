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
from pygame.locals import *

from constants import *
from utils import *
from core import *

# Creates the path network as a list of lines between all path nodes that are traversable by the agent.
def myBuildPathNetwork(pathnodes, world, agent = None):
	lines = []
	### YOUR CODE GOES BELOW HERE ###
	obstacles = world.getObstacles()
	agentSize = agent.getMaxRadius()
	#for node in nodes
	#check if obstacle exists in path between nodes
	#check if agent's size doesn't cause it to crash into obstacles
	#return valid line if exists (append to lines)
	for nodeSrc in pathnodes:
		for nodeDest in pathnodes:
			if nodeSrc != nodeDest:
				line = (nodeSrc, nodeDest)
				#check for obstacle or agent collision
				obstaclesBetween = False
				agentCollision = False
				for obstacle in obstacles:
					obstaclesBetween = obstaclesBetween or checkCollision(nodeSrc, nodeDest, obstacle)
					agentCollision = agentCollision or checkAgentCollision(line, obstacle, agentSize)
				#check for agent collision
				if not (obstaclesBetween or agentCollision): 
					#accept the line
					lines.append(line)

	### YOUR CODE GOES ABOVE HERE ###
	return lines

def checkAgentCollision(line, obstacle, agentSize):
	for point in obstacle.getPoints():
		if minimumDistance(line, point) <= agentSize:
			return True
	return False

def checkCollision(pointA, pointB, obstacle):
	lines = obstacle.getLines()
	for line in lines:
		if rayTrace(pointA, pointB, line) is not None:
			return True 
	return False