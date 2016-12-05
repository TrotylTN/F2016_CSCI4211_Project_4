forwardings = [[],
               [{}, {}, {}, {}, {}, {}],
               [{}, {}, {}, {}, {}, {}],
               [{}, {}, {}, {}, {}, {}]]

macbase = '00:00:00:00:00:0'
emptymac = "-1"
priority1 = 100
priority2 = 200
status = 3

def generator(status, sid):
    state = [status // 2 != 0, status % 2 != 0]
    if sid in [4, 5]:
        for i in range(1, 7):
            forwardings[status][sid][(emptymac, macbase+str(i))] = ((i + 1) // 2, priority1)
    elif sid in [1, 2, 3]:
        hosts = [sid * 2 - 1, sid * 2]
        for i in range(2):
            if i==0 and not state[i]:
                port = 2
            elif i==1 and not state[i]:
                port = 1
            else:
                port = i + 1
            forwardings[status][sid][(macbase+str(hosts[i]), emptymac)] = (port, priority1)
            forwardings[status][sid][(emptymac, macbase+str(hosts[i]))] = ((i + 3), priority2)

for s in range(1, 4):
    for switch in range(1, 6):
        generator(s, switch)

for s in range(1, 4):
    state = [s // 2 != 0, s % 2 != 0]
    print state
    for switch in range(1, 6):
        print "Switch:", switch
        for k in sorted(forwardings[s][switch].keys()):
            print k, ":", forwardings[s][switch][k]
    print "\n"