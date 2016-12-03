
def gen_pair():
    l = [dict()]
    for f in range(3):
        l.append(dict())
        for i in range(1, 7):
            if f + 1 > 3:
                raise Error
            if i < f * 2 + 1 or i > f * 2 + 2:
                l[f + 1][('00:00:00:00:00:0' + str(f * 2 + 1), '00:00:00:00:00:0' + str(i))] = 1
                l[f + 1][('00:00:00:00:00:0' + str(f * 2 + 2), '00:00:00:00:00:0' + str(i))] = 2
            else:
                l[f + 1][('00:00:00:00:00:0' + str(f * 2 + 1), '00:00:00:00:00:0' + str(i))] = 3 + (i + 1) % 2
                l[f + 1][('00:00:00:00:00:0' + str(f * 2 + 2), '00:00:00:00:00:0' + str(i))] = 3 + (i + 1) % 2
    for f in range (4, 6):
        l.append(dict())
        for i in range(1, 7):
            l[f]['00:00:00:00:00:0' + str(i)] = (i - 1) // 2 + 1
    return l

a = (gen_pair())
for x in range(1, 6):
    print 'Switch', x
    k= sorted(a[x].keys())
    for t in k:
        print t, ':', a[x][t]
    print ''
