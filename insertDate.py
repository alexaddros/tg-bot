import re
import pymysql

textFile = open("fcat.txt", "r", encoding='utf-8')
lineCounter = 0
errorOn = False
errorNumberList = []
errorTextList = []
errorHowToList = []
errorThisList = []
for line in textFile:
    if errorOn:
        lineCounter = lineCounter - 1
    if re.match(r'0', line):
        #print(line)
        errorNumberList.append(line)
        lineCounter = 5
        errorOn = True
        continue
    if lineCounter == 1:
        errorOn = False
        lineCounter = 0
        #print(line)
        errorTextList.append(line)
textFile.close()
textFile = open("fcat.txt", "r", encoding='utf-8')
thisOn = False
for line in textFile:

    if re.match(r'――How', line):
        thisOn = True
    if re.match(r'──Error', line):
        thisOn = False
    if thisOn:
        #print(line)
        errorHowToList.append(line)

res = list()
for line in errorHowToList:
    res_t = str()
    for cymbal in line:
        if ord(cymbal) > 0 and ord(cymbal) < 150:
            res_t += cymbal
    res.append(res_t)
errorHowToList = res

indexes = list()
for number, line in enumerate(errorHowToList):
    if line == 'How                 \n' or line == 'How                \n':
        indexes.append(number)

parts = list()
for i in range(len(indexes) - 1):
    parts.append(errorHowToList[indexes[i]:indexes[i + 1]])

for part in parts:
    del part[0]

textFile.close()


con = pymysql.connect('localhost', 'root', 'Koordinator1414a', 'TestBase')

with con:
    cur = con.cursor()
    for i in range(76):
        cur.execute(f"INSERT INTO Errors (Number, Description, Correction) VALUES ({errorNumberList[i], errorTextList[i], parts[i]})")

    version = cur.fetchone()
con.close()
print('success')
# root
# Koordinator1414a
# TestBase
