
def gen_pair():
    l = [[]]
    for f in range(3):
        l.append([])
        l[f + 1].append(dict())
        for i in range(1, 7):
            if i < f * 2 + 1 or i > f * 2 + 2:
                l[f + 1][0][('00:00:00:00:00:0' + str(f * 2 + 1), '00:00:00:00:00:0' + str(i))] = 1
                l[f + 1][0][('00:00:00:00:00:0' + str(f * 2 + 2), '00:00:00:00:00:0' + str(i))] = 2
            else:
                l[f + 1][0]['00:00:00:00:00:0' + str(i)] = 3 + (i + 1) % 2
    for f in range (4, 6):
        l.append([])
        l[f].append(dict())
        for i in range(1, 7):
            l[f][0]['00:00:00:00:00:0' + str(i)] = (i - 1) // 2 + 1
    for f in range(3):
        l[f + 1].append(dict())
        for i in range(1, 7):
            if i < f * 2 + 1 or i > f * 2 + 2:
                l[f + 1][1][('00:00:00:00:00:0' + str(f * 2 + 1), '00:00:00:00:00:0' + str(i))] = 2
                l[f + 1][1][('00:00:00:00:00:0' + str(f * 2 + 2), '00:00:00:00:00:0' + str(i))] = 2
            else:
                l[f + 1][1]['00:00:00:00:00:0' + str(i)] = 3 + (i + 1) % 2
    for f in range(3):
        l[f + 1].append(dict())
        for i in range(1, 7):
            if i < f * 2 + 1 or i > f * 2 + 2:
                l[f + 1][2][('00:00:00:00:00:0' + str(f * 2 + 1), '00:00:00:00:00:0' + str(i))] = 1
                l[f + 1][2][('00:00:00:00:00:0' + str(f * 2 + 2), '00:00:00:00:00:0' + str(i))] = 1
            else:
                l[f + 1][2]['00:00:00:00:00:0' + str(i)] = 3 + (i + 1) % 2
    return l

a = (gen_pair())
for x in range(1, 6):
    for j in range(len(a[x])):
        print 'Switch', x, 'State:', j // 2, j % 2, "// 0 means connected, 1 means down"
        k= sorted(a[x][j].keys())
        for t in k:
            print t, ':', a[x][j][t]
        print ''
