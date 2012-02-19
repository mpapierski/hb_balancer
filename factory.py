#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#	hb_balancer
#	High performance load balancer between Helbreath World Servers.
#
#	Copyright (C) 2012 Michał Papierski <michal@papierski.net>

#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.

#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.

#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import json
import random

from twisted.internet import protocol, reactor
from twisted.python import log

from protocol import HelbreathProtocol, ProxyHelbreathProtocol

class ServerFactory(protocol.Factory):
	''' Main server factory '''
	def __init__(self):
		self.config = {}
		self.load_config()
		
	def load_config(self):
		''' Load configuration file '''
		try:
			self.config = json.load(open('hb_balancer.cfg', 'r'))
		except IOError:
			log.err('Configuration file hb_balancer.cfg not found!')
		
	def buildProtocol(self, addr):
		p = HelbreathProtocol()
		p.factory = self
		return p

	def connect_to_world(self, world_name, success, failure, receiver):
		''' Select a destination server and make a connection '''
		try:
			world = self.config[world_name]
		except KeyError:
			# World is not found in the configuration
			log.err('World %s is not found in the configuration!' % (world_name, ))
			failure()
			return
		
		if isinstance(world, (list, tuple)):
			world = random.choice(world)
		
		# Start the new connection
		proxy = ProxyHelbreathFactory(
			world_name = world['world'],
			success = success,
			failure = failure,
			receiver = receiver
		)
		
		reactor.connectTCP(world['address'], world['port'], proxy, timeout = 5)
		
class ProxyHelbreathFactory(protocol.ClientFactory):
	''' Factory for remote server connections '''
	
	def __init__(self, world_name, success, failure, receiver):
		''' Create proxy factory with callbacks
		
		world_name -- Dictionary with world info
		success -- Connection is made
		failure -- Connection failed.
		receiver -- Is bound to a HB protocol, it is the raw packet	receiver
		'''
		self.success, self.failure, self.receiver = (
			success, failure, receiver)
		
		self.world_name = world_name
		
	def clientConnectionFailed(self, connector, reason):
		log.msg('Remote connection failed: %s' % (reason.getErrorMessage(), ))
		self.failure()
		
	def buildProtocol(self, addr):
		p = ProxyHelbreathProtocol()
		p.factory = self
		return p
