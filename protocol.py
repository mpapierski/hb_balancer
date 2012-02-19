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

import struct
import random
import logging

from twisted.internet import reactor
from twisted.protocols.stateful import StatefulProtocol
from twisted.python import log

from packets import Packets

class HelbreathProtocol(StatefulProtocol):
	def __init__(self, config):
		''' Worlds configuration file passed from the factory '''
		self.config = config
		
	def connectionMade(self):
		''' Partial protocol data '''
		self.key = self.data_size = None
		
	def getInitialState(self):
		'''
			Protocol overview:
			[Key unsigned byte] [Size unsigned short] [Data Size-bytes]
		'''
		return (self.get_key, 1)
				
	def get_key(self, data):
		''' Get key '''
		self.key, = struct.unpack('<B', data)
		return (self.get_data_size, 2)
		
	def get_data_size(self, data):
		''' Read data size '''
		self.data_size, = struct.unpack('<H', data)
		return (self.get_data, self.data_size - 3)
		
	def get_data(self, data):
		''' Read encoded data and decode it '''
		if self.key > 0:
			# Decode
			data = list(data)
			for i in range(len(data)):
				data[i] = chr(((ord(data[i]) ^ (self.key ^ (self.data_size - 3 - i))) - (i ^ self.key)) % 256)
			data = ''.join(data)
		
		# Get the main header
		msg_id, msg_type = struct.unpack('<IH', data[:6])
		
		# Process packet data
		if msg_id == Packets.MSGID_REQUEST_LOGIN:
			packet_format = '<10s10s30s'
			account_name, account_password, world_name = struct.unpack(
				packet_format,
				data[6:]
			)
			
			self.request_login(
				account_name.rstrip('\x00'),
				account_password.rstrip('\x00'),
				world_name.rstrip('\x00')
			)
			
		return (self.get_key, 1)
	
	def send_message(self, data):
		''' Send a Helbreath Packet data '''
		key = random.randint(0, 255)
		if key > 0:
			# Encode
			data = list(data)
			for i in range(len(data)):
				data[i] = chr(((ord(data[i]) + (i ^ key)) ^ (key ^ (len(data) - i))) % 256)
			data = ''.join(data)
		self.transport.write(struct.pack('<BH', key, len(data) + 3) + data)
		
	def request_login(self, account_name, account_password, world_name):
		''' Request client login
		
		account_name -- Account name
		account_password -- Account password
		'''
		
		def world_is_down(failure = None):
			''' The requested world is offline '''
			self.send_message(struct.pack('<IH',
				 Packets.MSGID_RESPONSE_LOG,
				 Packets.DEF_LOGRESMSGTYPE_NOTEXISTINGWORLDSERVER))
				
		if world_name not in self.config:
			''' World is not found in the configuration '''
			log.msg('World not found')
			world_is_down()
			# Gracefully disconnect a person.
			reactor.callLater(10, self.transport.abortConnection)
			return
			
		log.msg('Request login %s %s' % (account_name, account_password))
		log.msg('WS: "%r"' % (world_name, ))
		log.msg('Found: %d' % (world_name in self.config, ))
