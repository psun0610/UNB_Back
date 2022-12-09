daylist = [8, 9, 10, 11, 2, 3, 19]

if len(daylist) == 1:
    consecutive = 1
else:
    cnt = 1
    daymax1 = []
    daymax2 = []
    for i in daylist:
        daymax1.append(i)
    daymax1.append(0)
    for i in range(len(daylist)):
        if daymax1[i + 1] - daymax1[i] == 1:
            cnt += 1
        else:
            daymax2.append(cnt)

            cnt = 1
    print(daymax2)
