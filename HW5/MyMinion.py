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
from moba import *

class MyMinion(Minion):
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
		self.states = [Idle]
		### Add your states to self.states (but don't remove Idle)
		### YOUR CODE GOES BELOW HERE ###
		self.states.append(Move)
		self.states.append(AttackTower)
		self.states.append(AttackBase)
		self.states.append(AttackMinion)
		self.states.append(AttackHero)
		### YOUR CODE GOES ABOVE HERE ###

	def start(self):
		Minion.start(self)
		self.changeState(Idle)





############################
### Idle
###
### This is the default state of MyMinion. The main purpose of the Idle state is to figure out what state to change to and do that immediately.

class Idle(State):
	
	def enter(self, oldstate):
		State.enter(self, oldstate)
		# stop moving
		self.agent.stopMoving()
	
	def execute(self, delta = 0):
		State.execute(self, delta)
		### YOUR CODE GOES BELOW HERE ###
		team = self.agent.getTeam()
		world = self.agent.world
		towers = world.getEnemyTowers(team) 
		bases = world.getEnemyBases(team)
		minions = world.getEnemyNPCs(team)
		#if tower and not within shoot range, go to tower
		if len(towers) != 0:
			targetTower = None
			targetDistance = None
			for tower in towers:
				agentPos = self.agent.getLocation()
				towerPos = tower.getLocation()
				curDistance = distance(agentPos, towerPos)
				if targetTower is None:
					targetDistance = curDistance
					targetTower = tower
				elif targetDistance > curDistance:
					targetDistance = curDistance
					targetTower = tower
			#move
			self.agent.changeState(Move, targetTower, 'Tower')				
		elif len(bases) != 0:
			targetBase = None
			targetDistance = None
			for base in bases:
				agentPos = self.agent.getLocation()
				basePos = base.getLocation()
				curDistance = distance(agentPos, basePos)
				if targetBase is None:
					targetDistance = curDistance
					targetBase = base
				elif targetDistance > curDistance:
					targetDistance = curDistance
					targetBase = base
			self.agent.changeState(Move, targetBase, 'Base')			
		elif len(minions) != 0:
			targetMinion = None
			targetDistance = None
			for minion in minions:
				agentPos = self.agent.getLocation()
				minionPos = minion.getLocation()
				curDistance = distance(agentPos, minionPos)
				if targetMinion is None:
					targetDistance = curDistance
					targetMinion = minion
				elif targetDistance > curDistance:
					targetDistance = curDistance
					targetMinion = minion
			self.agent.changeState(Move, targetMinion, 'Minion')
		

		### YOUR CODE GOES ABOVE HERE ###
		return None

##############################
### Taunt
###
### This is a state given as an example of how to pass arbitrary parameters into a State.
### To taunt someome, Agent.changeState(Taunt, enemyagent)

class Taunt(State):

	def parseArgs(self, args):
		self.victim = args[0]

	def execute(self, delta = 0):
		if self.victim is not None:
			print "Hey " + str(self.victim) + ", I don't like you!"
		self.agent.changeState(Idle)

##############################
### YOUR STATES GO HERE:
#State to move to a particular location
class Move(State):

	def parseArgs(self, args):
		self.goalLocation = args[0].getLocation()
		self.startLocation = self.agent.getLocation()
		self.goal = args[0]
		self.goalType = args[1]

	def enter(self, oldstate):
		self.agent.navigateTo(self.goalLocation)

	def execute(self, delta=0):
		if self.agent.moveTarget is None:
			self.agent.navigateTo(self.goalLocation)
		else:
			if self.goalType == 'Tower' and distance(self.goal.getLocation(), self.agent.getLocation()) <= BULLETRANGE and self.goal in self.agent.getVisible():
				self.agent.changeState(AttackTower, self.goal)
			elif self.goalType == 'Base' and distance(self.goal.getLocation(), self.agent.getLocation()) <= BULLETRANGE and self.goal in self.agent.getVisible():
				self.agent.changeState(AttackBase, self.goal)
			elif self.goalType == 'Minion' and distance(self.goal.getLocation(), self.agent.getLocation()) <= BULLETRANGE and self.goal in self.agent.getVisible():
				self.agent.changeState(AttackMinion, self.goal)
			elif self.goalType == 'Hero' and distance(self.goal.getLocation(), self.agent.getLocation()) <= BULLETRANGE and self.goal in self.agent.getVisible():
				self.agent.changeState(AttackHero, self.goal)

class AttackTower(State):
	#TODO
	def parseArgs(self, args):
		self.target = args[0]

	def enter(self, oldstate):
		self.targetPos = self.target.position

	def execute(self, delta=0):

		if distance(self.target.getLocation(), self.agent.getLocation()) <= BULLETRANGE and self.target in self.agent.getVisible():	
			self.agent.turnToFace(self.targetPos)
			self.agent.shoot()
		elif self.target.getHitpoints() == 0:
			self.target = None
			self.targetPos = None
			self.agent.changeState(Idle)
		else:
			#tower is out of range or already destroyed
			self.target = None
			self.targetPos = None
			#go back to idle state
			self.agent.changeState(Idle)

class AttackBase(State):
	#TODO
	def parseArgs(self, args):
		self.target = args[0]

	def enter(self, oldstate):
		self.targetPos = self.target.position

	def execute(self, delta=0):
		if distance(self.target.getLocation(), self.agent.getLocation()) <= BULLETRANGE and self.target in self.agent.getVisible():	
			self.agent.turnToFace(self.targetPos)
			self.agent.shoot()
			#self.agent.stopMoving()
		else:
			#tower is out of range or already destroyed
			self.target = None
			self.targetPos = None
			#go back to idle state
			self.agent.changeState(Idle)

class AttackMinion(State):
	#TODO
	def parseArgs(self, args):
		self.target = args[0]

	def enter(self, oldstate):
		self.targetPos = self.target.position

	def execute(self, delta=0):

		if distance(self.target.getLocation(), self.agent.getLocation()) <= BULLETRANGE and self.target in self.agent.getVisible():	
			self.agent.turnToFace(self.targetPos)
			self.agent.shoot()
		else:
			#tower is out of range or already destroyed
			self.target = None
			self.targetPos = None
			#go back to idle state
			self.agent.changeState(Idle)

class AttackHero(State):
	#TODO
	def parseArgs(self, args):
		self.target = args[0]

	def enter(self, oldstate):
		self.targetPos = self.target.position

	def execute(self, delta=0):

		if distance(self.target.getLocation(), self.agent.getLocation()) <= BULLETRANGE and self.target in self.agent.getVisible():	
			self.agent.turnToFace(self.targetPos)

			if self.target.getHitpoints() <= 0:
				self.exit()

			self.agent.shoot()
		else:
			#hero is out of range or already destroyed
			self.exit()

	def exit(self):
		self.target = None
		self.targetPos = None
		self.agent.changeState(Idle)
