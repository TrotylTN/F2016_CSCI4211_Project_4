# CSCI4211_Project_4

Members:
- Nan Qin (qinxx232)
- Tianhao Liu (liux3271)
- Tiannan Zhou (zhou0745)

Contributions:
- Most of the works are finished by we three sitting together, it is hard to seperate.
- Part1: Nan Qin
- Part2: Tiannan Zhou
- Part3: Tianhao Liu

Program design:
	Our controller will listen to three events, ConnectionUp, PacketIn and PortStatus.
	Since the topology is fixed, we generate the forwarding tables for each switch in each status at the beginning of our program, where status refers to the status of two spine switches. When a switch connects in, the controller will tell all roles to the switch. When all 5 switches connect in, network can run on itself without the controller except ARP request. To be specific, for each leaf switch, it has 4 roles. For example, when all link is up, l1 have:
		1. Src = h1, send_to: port 1, priority = 100
		2. Src = h2, send_to: port 2, priority = 100
		3. Dest = h1, send_to: port 3, priority = 200
		4. Dest = h2, send_to: port 4, priority = 200
	When h1 want to send packet to h2, both 1 and 4 will match. Since we set a higher priority for 4 so the it will be chose, which would not confuse the switch.
	Two spine switches have the same table in all status:
		1. Dest = h1, send_to: port 1
		2. Dest = h2, send_to: port 1
		3. Dest = h3, send_to: port 2
		4. Dest = h4, send_to: port 2
		5. Dest = h5, send_to: port 3
		6. Dest = h6, send_to: port 4
	Now the only issue that the PacketIn need to handle is that the ARP request. When the packet comes in, the controller will check its (IP:MAC) table and let the switch to send back an ARP response directly.
	When the link up/down happens, the PortStatus event will be triggered. Once a link of a spine switch is off, we will consider this spine switch is off and all of its traffic should be send to another spine switch. We turn a spine switch back on only if all its three links is up.
	Please checkout the comments in the code for more details.