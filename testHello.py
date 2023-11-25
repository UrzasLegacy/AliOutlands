def printPicnic(itemsDict, leftWidth, rightWidth):
    print('PICNIC ITEMS'.center(leftWidth + rightWidth, '-'))
    for k, v in itemsDict.items():
        print(k.ljust(leftWidth) + str(v).rjust(rightWidth))

picnicItems = {'research materials': 4, 'mastercraftingdiagram': 12, 'cups': 4, 'cookies': 8000}
printPicnic(picnicItems, 20,20)
printPicnic(picnicItems, 20, 40)