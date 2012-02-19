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

class BaseHelbreathProtocol(StatefulProtocol):
	''' Basic Helbreath Protocol '''
	
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
		
		# Pass decoded data
		self.raw_data(data)
		
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

	def raw_data(self, data):
		''' Got packet '''
		pass
		
class ProxyHelbreathProtocol(BaseHelbreathProtocol):
	''' Proxy Helbreath protocol used for proxying packets '''
	def connectionMade(self):
		self.factory.success(self)
		
	def login(self, account_name, account_password, world_name):
		''' Request a login '''
		
		# Casting to str is made for sure
		# world_name could be either str or unicode.
		self.send_message(struct.pack('<IH10s10s30s',
			Packets.MSGID_REQUEST_LOGIN, # MsgID
			0, # MsgType
			str(account_name),
			str(account_password),
			str(world_name)))
			
	def raw_data(self, data):
		self.factory.receiver(data)
		self.transport.loseConnection()
		
class HelbreathProtocol(BaseHelbreathProtocol):
	def raw_data(self, data):
		# Header
		msg_id, msg_type = struct.unpack('<IH', data[:6])
		
		# Process packet data
		if msg_id == Packets.MSGID_REQUEST_LOGIN:
			# Client is requesting login
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
		elif msg_id == Packets.MSGID_REQUEST_ENTERGAME:
			# Client is trying to enter game
			packet_format = '<10s10s10s10si30s120s'
			player_name, map_name, account_name, account_password, \
				level, world_name, cmd_line = struct.unpack(
					packet_format,
					data[6:])
					
			self.request_entergame(
				msg_type,
				player_name.rstrip('\x00'),
				map_name.rstrip('\x00'),
				account_name.rstrip('\x00'),
				account_password.rstrip('\x00'),
				level,
				world_name.rstrip('\x00'),
				cmd_line.rstrip('\x00'))
			
		else:
			# Abort if a packet is not (yet) known
			self.transport.loseConnection()
			
	def request_login(self, account_name, account_password, world_name):
		''' Request client login
		
		account_name -- Account name
		account_password -- Account password
		world_name -- World server name
		'''
		
		def world_is_down(failure = None):
			''' The requested world is offline '''
			self.send_message(struct.pack('<IH',
				 Packets.MSGID_RESPONSE_LOG,
				 Packets.DEF_LOGRESMSGTYPE_NOTEXISTINGWORLDSERVER))
			reactor.callLater(10, self.transport.loseConnection)
		
		def handle_response(data):
			''' Pass data and close the connection nicely '''
			self.send_message(data)
			reactor.callLater(10, self.transport.loseConnection)
		
		def connection_made(remote):
			''' Connection is made. Request a login. '''
			log.msg('Remote connection made!')
			remote.login(
				account_name,
				account_password,
				remote.factory.world_name
			)
			
		# Request connection to a world by its name, pass some callbacks
		self.factory.connect_to_world(
			world_name = world_name,
			receiver = handle_response,
			success = connection_made,
			failure = world_is_down)
		
		log.msg('Request world %s' % (world_name, ))

	def request_entergame(self, msg_type, player_name, map_name, account_name,
		account_password, level, world_name, cmd_line):
		''' Client wants to enter game. '''
		log.msg('Request entergame player(%s) map(%s) account(%s) world(%s)' % (
			player_name, map_name, account_name, world_name))
			
		def connection_made(remote):
			''' Request enter game, construct exacly the same data.
			TODO: Parse the msg_type. '''
			log.msg('Requesting enter game...')
			remote.send_message(struct.pack('<IH10s10s10s10si30s120s',
				Packets.MSGID_REQUEST_ENTERGAME,
				msg_type,
				player_name,
				map_name,
				account_name,
				account_password,
				level,
				str(remote.factory.world_name),
				cmd_line))
				
		def error_handler(failure = None):
			''' Unable to connect to destination world '''
			log.err('Enter game error for account(%s) at world(%s)' % (
				account_name,
				world_name))
			self.send_message(struct.pack('<IHB',
				Packets.MSGID_RESPONSE_ENTERGAME,
				Packets.DEF_ENTERGAMERESTYPE_REJECT,
				Packets.DEF_REJECTTYPE_DATADIFFERENCE))
			reactor.callLater(10, self.transport.loseConnection)
			
		def response_handler(data):
			''' Pass the (modified) data '''
			self.send_message(data)
			
		self.factory.connect_to_world(
			world_name = world_name,
			receiver = response_handler,
			success = connection_made,
			failure = error_handler
		)
