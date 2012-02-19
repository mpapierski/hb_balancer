# hb_balancer

High performnance load balancer for Helbreath servers.

This tool is designed to be working as a frontend for several servers
hosted on local, or non local addresses.
Traffic from players are redirected to a specified servers based on a World Name.

There is possibility to define more than one address for a server, then
traffic will be balanced between them.

There is an ability to reload configuration on the fly, so there is no need
to shut down to make changes work.

## Installing

Create file hb_balancer.cfg with example configuration:

	{
		"WS1": [
			{
				"world": "WS1", 
				"port": 2849, 
				"address": "localhost"
				
			}
		], 
		"WS2": [
			{
				"world": "WS1",
				"port": 2850,
				"address": "localhost"
			}
		]
	}

Note that each configured World could be single dictionary with connection
data. If world is configured with a list of servers, then random one will
be selected.

## Writing

TODO

## Licensing

GNU AGPL. See LICENSE

## Copyright

Helbreath is a registered trademark of Siementech Co.
