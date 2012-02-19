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

from twisted.internet import protocol
from twisted.python import log

from protocol import HelbreathProtocol

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
		return HelbreathProtocol(self.config)
