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

class Packets:
	''' Packet IDs '''
	
	# Client login request
	MSGID_REQUEST_LOGIN = 0x0FC94201
	
	# Client login response
	MSGID_RESPONSE_LOG = 0x0FC94203
	
	# Client login response details
	
	# OK
	DEF_LOGRESMSGTYPE_CONFIRM = 0x0F14
	
	# Failure
	DEF_LOGRESMSGTYPE_REJECT = 0x0F15 # Failure
	
	# Not existing world server
	DEF_LOGRESMSGTYPE_NOTEXISTINGWORLDSERVER = 0x0A02
	
	# Enter game request
	MSGID_REQUEST_ENTERGAME = 0x0FC94205
	
	# Enter game response
	MSGID_RESPONSE_ENTERGAME = 0x0FC94206
	
	# Enter game response types
	DEF_ENTERGAMERESTYPE_REJECT = 0x0F21
	
	# Enter game response reject types
	DEF_REJECTTYPE_CHARABOVETRIALLEVEL = 0x01
	DEF_REJECTTYPE_MAXREGISTEREDIPREACHED = 0x02
	DEF_REJECTTYPE_GAMESERVERNOTONLINE = 0x03
	DEF_REJECTTYPE_DATADIFFERENCE = 0x04
	DEF_REJECTTYPE_MAXSERVERUSERLIMITREACHED = 0x06
	DEF_REJECTTYPE_WORLDSERVERISFULL = 0x07
	DEF_REJECTTYPE_LOGINERROR = 0x08
