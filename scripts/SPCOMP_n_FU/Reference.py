#-------------------------------------------------------------------------------
# Name:        Reference
# Purpose:     This stores constant variables and functions that applies to all plans.
#
# Author:      kimdan
#
# Created:     24/02/2017
# Copyright:   (c) kimdan 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, datetime, time

static_db = {
#           fmu                     code        plan start years    region
        'Abitibi_River':        [   '110',      [2012, 2022],       'NE'    ],
        'Algoma':               [   '615',      [2010, 2020],       'NE'    ],
        'Algonquin_Park':       [   '451',      [2010, 2020],       'S'     ],
        'Armstrong':            [   '444',      [2005],             ''      ], #outdated?
        'Bancroft_Minden':      [   '220',      [2011, 2021],       'S'     ],
        'Big_Pic':              [   '067',      [2007, 2017],       'NE'    ], # will be a part of Pic_Forest in 2019
        'Black_River':          [   '370',      [2006],             ''      ], #outdated?
        'Black_Spruce':         [   '035',      [2011, 2021],       'NW'    ],
        'Caribou':              [   '175',      [2008, 2018],       'NW'    ],
        'Crossroute':           [   '405',      [2007, 2017],       'NW'    ],
        'Dog_River_Matawin':    [   '177',      [2009, 2019],       'NW'    ],
        'Dryden':               [   '535',      [2011, 2021],       'NW'    ],
        'English_River':        [   '230',      [2009, 2019],       'NW'    ],
        'French_Severn':        [   '360',      [2009, 2019],       'S'     ],
        'Gordon_Cosens':        [   '438',      [2010, 2020],       'NE'    ],
        'Hearst':               [   '601',      [2007, 2017],       'NE'    ],
        'Kenogami':             [   '350',      [2011, 2021],       'NW'    ],
        'Kenora':               [   '644',      [2012, 2022],       'NW'    ],
        'Lac_Seul':             [   '702',      [2011, 2021],       'NW'    ],
        'Lake_Nipigon':         [   '815',      [2011, 2021],       'NW'    ],
        'Lakehead':             [   '796',      [2007, 2017],       'NW'    ],
        'Magpie':               [   '565',      [2009, 2019],       'NE'    ],
        'Martel':               [   '509',      [2011, 2021],       'NE'    ],
        'Mazinaw_Lanark':       [   '140',      [2011, 2021],       'S'     ],
        'Nagagami':             [   '390',      [2011, 2021],       'NE'    ],
        'Nipissing':            [   '754',      [2009, 2019],       'NE'    ],
        'Northshore':           [   '680',      [2010, 2020],       'NE'    ],
        'Ogoki':                [   '415',      [2008, 2018],       'NW'    ],
        'Ottawa_Valley':        [   '780',      [2011, 2021],       'S'     ],
        'Pic_Forest':           [   '966',      [2019],             'NE'    ], # Amalgamation of Big_Pic and Pic_River as of 2019 plan
        'Pic_River':            [   '965',      [2006, 2013],       'NE'    ], # will be a part of Pic_Forest in 2019
        'Pineland':             [   '421',      [2011, 2021],       'NW'    ],
        'Red_Lake':             [   '840',      [2008, 2018],       'NW'    ],
        'Romeo_Malette':        [   '930',      [2009, 2019],       'NE'    ],
        'Sapawe':               [   '853',      [2010, 2020],       'NW'    ],
        'Spanish':              [   '210',      [2010, 2020],       'NE'    ],
        'Sudbury':              [   '889',      [2010, 2020],       'NE'    ],
        'Temagami':             [   '898',      [2009, 2019],       'NE'    ],
        'Timiskaming':          [   '280',      [2011, 2021],       'NE'    ],
        'Trout_Lake':           [   '210',      [2009, 2019],       'NW'    ],
        'Wabigoon':             [   '130',      [2008, 2018],       'NW'    ],
        'Whiskey_Jack':         [   '490',      [2012, 2022],       'NW'    ],
        'White_River':          [   '060',      [2008, 2018],       'NE'    ],
        'Whitefeather':         [   '994',      [2012, 2022],       'NW'    ]
        }

# spcomp list in 2017 FIM FRI tech spec
##spcList2017 = ['AX', 'AB', 'AW', 'PL', 'PT', 'BD', 'BE', 'BW', 'BY', 'BN', 'CE', 'CR', 'CH', 'CB', 'OC', 'EX', 'EW', 'BF', 'OH', 'HE', 'HI', 'IW', 'LA', 'MH', 'MR', 'MS', 'MR', 'MH', 'OB', 'OR', 'OW', 'PN', 'PJ', 'PR', 'PS', 'PW', 'PO', 'PB', 'SX', 'SB', 'SR', 'SW']

SpcListInterp = ['AX', 'AB', 'AW', 'PL', 'PT', 'BD', 'BE', 'BG', 'BW', 'BY', 'BN', 'CE', 'CR', 'CW', 'CH', 'CB', 'CD', 'OC', 'PD', 'EX', 'EW', 'BF', 'OH', 'HE', 'HI', 'IW', 'LO', 'MX', 'MH', 'MR', 'MS', 'OX', 'OR', 'OW', 'PX', 'PJ', 'PR', 'PS', 'PW', 'PO', 'PB', 'SX', 'SB', 'SW', 'LA', 'WB', 'WI']

SpcListOther = ['AL', 'AQ', 'AP', 'AG', 'BC', 'BP', 'GB', 'BB', 'CAT', 'CC', 'CM', 'CP', 'CS', 'CT', 'ER', 'EU', 'HK', 'HL', 'HB', 'HM', 'HP', 'HS', 'HC', 'KK', 'LE', 'LJ', 'BL', 'LL', 'LB', 'GT', 'MB', 'MF', 'MM', 'MT', 'MN', 'MP', 'AM', 'EMA', 'MO', 'OBL', 'OB', 'OCH', 'OP', 'OS', 'OSW', 'PA', 'PN', 'PP', 'PC', 'PH', 'PE', 'RED', 'SC', 'SS', 'SK', 'SN', 'SR', 'SY', 'TP', 'HAZ']

def spcVal(data, fieldname, version = 2017): #sample data: 'Cw  70La  20Sb  10'
    #assuming the data is not None or empty string
    try:
        if len(data)%6 == 0:
            n = int(len(data)/6)
            spcList = [data[6*i:6*i+3].strip().upper() for i in range(n)]
            percentList = [int(data[6*i+3:6*i+6].strip()) for i in range(n)]
            # build species to percent dictionary
            spcPercentDict = dict(zip(spcList,percentList)) # this should look like {'AX':60,'CW':40}

            if sum(percentList) == 100:
                if len(set(spcList)) == len(spcList):

                    correctList = list(set(spcList)&set(SpcListInterp))
                    # To save processing time, check the spc code with the most common spc list (SpcListInterp) first, if not found, check the other possible spc code
                    if len(correctList) != len(spcList):
                        correctList = list(set(spcList)&set(SpcListInterp + SpcListOther))

                    if len(correctList) == len(spcList):
                        return ['Pass',spcPercentDict]
                    else:
                        wrongList = list(set(spcList) - set(correctList))
                        return ["Error","%s has invalid species code(s): %s"%(fieldname,wrongList)]
                else:
                    return ["Error","%s has duplicate species codes"%fieldname]
            else:
                return ["Error","%s does not add up to 100"%fieldname]
        else:
            return ["Error", "%s does not follow the SSSPPPSSSPPP patern"%fieldname]
    except:
        return ["Error", "%s does not follow the SSSPPPSSSPPP patern"%fieldname]


#    ------------       Checker for PRI_ECO and SEC_ECO     --------------------

# Geographic Range
ecoG = ['A','B','G','S','U']
# Vegetative Modifier
ecoV = ['Tt','Tl','S','N','X','']
# Substrate Depth Modifier
ecoD = ['R','VS','S','M','MD','D','']
# Substrate moisture modifier
ecoM = ['d','f','h','m','s','v','w','x']
# Substrate Chemistry Modifier
ecoC = ['a','b','k','n','z']
# Vegetative cover clss modifier
ecoS = ['cTt','oTt','sTt','Tt ','Tl ','sTl','St ','sSt','Sl ','sSl','H  ','sH ','Nv ','X  ']

def ecoVal(data, fieldname, version = 2017):
    # assuming the data is not blank or null
    if len(data) >= 4:
        if len(data.strip()) <= 13:
            if data[0] in ecoG:
                try:
                    if int(data[1:4]) < 225 or int(data[1:4]) > 996:
                        if len(data) > 4:
                            if data[4:6].strip() in ecoV:
                                if len(data)>6:
                                    if data[6:8].strip() in ecoD:
                                        return None
                                    else:
                                        return ["Error","%s has invalid substrate depth modifier."%fieldname]
                            else:
                                return ["Error","%s has invalid vegetative modifier."%fieldname]
                    else:
                        return ["Error","%s has invalid ecosite number."%fieldname]
                except:
                    return ["Error","%s has invalid ecosite number."%fieldname]
            else:
                return ["Error","%s has incorrect geographic range code"%fieldname]
        else:
            return ["Error","%s has over 13 characters"%fieldname]
    else:
        return ["Error","%s is too short or does not follow the coding scheme."%fieldname]





def FMUCodeConverter(x):
    '''if the input x is fmu name, the output is the code and vice versa.
        Note that the input should be String format.'''
    try:
        return static_db[x][0]
    except:
        try:
            fmu = next(key for key, value in static_db.items() if value[0] == x)
            return fmu
        except Exception:
            print ("ERROR: " + x + " is neither fmu name nor the code.")
            return None

def pathFinder(basePaths,fmu,plan,year):
    # concatenates the poth and folder names. for example, it returns "\\lrcpsoprfp00001\GIS-DATA\WORK-DATA\FMPDS\Abitibi_River\AWS\2017\_data\FMP_Schema.gdb"
    for b in basePaths:
        path = os.path.join(b,fmu,plan,str(year),'_data','FMP_Schema.gdb')
        if os.path.exists(path):
            gdbfilename = path
            break
    try:
        return gdbfilename
    except:
        print ("ERROR: %s does not exist!" %path)
        print ("Check if you have spelled the FMU correctly.")
        return "ERROR!! Could not find the geodatabase with the submission files!!!"


def fimdate(Fimdatecode):
    # input the fimdate such as 2010MAR29). Will return date format such as 2010-03-29
    Fimdateformat = "%Y%b%d"
    try:
        v= time.strptime(Fimdatecode,Fimdateformat)
        return datetime.date(v[0],v[1],v[2])
    except TypeError:
        return None
    except ValueError:
        return None

def findSubID(mainfolder):
    # input = \\lrcpsoprfp00001\GIS-DATA\WORK-DATA\FMPDS\Abitibi_River\AWS\2017, output = submission id number.
    files = os.listdir(mainfolder)
    try:
        fitxt = [s for s in files if "fi_Submission" in s] #list of files that has "fi_Submission" in its filename.
        return int(fitxt[0].split('.')[0].split('_')[-1]) #returning submission number
    except:
        try:
            lyrfile = [s for s in files if ".lyr" in s] #list of layer files (there should be just one).
            return int(lyrfile[0].split('.')[0].split('_')[-1]) # returning submission number at the end of layer filename.
        except Exception:
            return ''

# this function is used only if there is a watchfile generated to "describe" the coverages. (for NER only)
# also note that this function is slightly different from the original checkWatchFile function.
def checkWatchFile2(mainfolder):
    import webbrowser
    path = os.path.join(mainfolder,'E00')
    e00List = []
    watchFile = ''
    for file in os.listdir(path):
        if file.lower().endswith('.e00'):
            e00List.append(file[:-4].lower())
        elif file.endswith('.wat'):
            watchFile = file  # will be checking if the watchfile exists a few lines below...
    e00List = sorted(e00List)

    htmlstring = ''
    htmlstring += "This checks dangling nodes and label erros of coverages in this folder: %s<br>"%path
    htmlstring += "This summarizes the watchfile: %s<br><br>"%watchFile
    htmlstring += "<strong>List of coverages found:</strong><br><br>"
    htmlstring += str(e00List) + "<br>"

    # looking at the watch file...
    ePre = 0 # precision
    ePro = 0 # projection
    eNode = 0 # node errors
    eLabel = 0 # label errors

    if not os.path.isfile(os.path.join(path,watchFile)):
        print ("Watch file does not exist in " + path)
        return None
    else:
        print ("found the watch file: " + watchFile)
        f = open(os.path.join(path,watchFile))
        for line in f:
            if line.startswith("DESCRIBE  "):
                htmlstring += "<br><br><strong>" + line + '</strong><br>'
            if line.startswith("             Description of"):
                if "DOUBLE" in line:
                    htmlstring += line.strip() + '<br>'
                else:
                    htmlstring += '<span style="color: red">' + line.strip() + '</span><br>'
                    ePre += 1
            if line.startswith("Projection "):
                if line.strip() == "Projection":
                    htmlstring += '<span style="color: red">' + line.strip() + '</span><br>'
                    ePro += 1
                else:
                    htmlstring += line.strip() + '<br>'
            if line.startswith("Datum "):
                if line.strip() == "Datum":
                    htmlstring += '<span style="color: red">' + line.strip() + '</span><br>'
                    ePro += 1
                else:
                    htmlstring += line.strip() + '<br>'
            if line.startswith("Zone "):
                if line.strip() == "Zone":
                    htmlstring += '<span style="color: red">' + line.strip() + '</span><br>'
                    ePro += 1
                else:
                    htmlstring += line.strip() + '<br>'
            if line.startswith("Units "):
                htmlstring += line.strip() + '<br>'
            if line.startswith("Total number of Dangling Nodes:"):
                if line.strip().endswith('0'):
                    htmlstring += line.strip() + '<br>'
                else:
                    htmlstring += '<span style="color: red">' + line.strip() + '</span><br>'
                    eNode += 1
            if line.startswith("Total number of Polygons with No Labels:"):
                if line.strip().endswith('1'):
                    htmlstring += line.strip() + '<br>'
                else:
                    htmlstring += '<span style="color: red">' + line.strip() + '</span><br>'
                    eLabel += 1
            if line.startswith("Total number of Polygons with Multiple Labels:"):
                if line.strip().endswith('0'):
                    htmlstring += line.strip() + '<br>'
                else:
                    htmlstring += '<span style="color: red">' + line.strip() + '</span><br>'
                    eLabel += 1


        # writing the summary at the end
        htmlstring += "<br><br>***********************    SUMMARY    ***********************<br>"
        if ePre < 1:
            htmlstring += '<br><span style="color: green">All layers have precision set to DOUBLE: YES</span>'
        else:
            htmlstring += '<br><span style="color: red">All layers have precision set to DOUBLE: NO  &emsp;  Error Count: ' + str(ePre) + '</span>'
            print ("All layers have precision set to DOUBLE: NO    Error Count: " + str(ePre))
        if ePro < 1:
            htmlstring += '<br><span style="color: green">All layers have projection and datum defined: YES</span>'
        else:
            htmlstring += '<br><span style="color: red">All layers have projection and datum defined: NO  &emsp;  Error Count: ' + str(ePro) + '</span>'
            print ("All layers have projection and datum defined: NO    Error Count: " + str(ePro))
        if eNode < 1:
            htmlstring += '<br><span style="color: green">All layers have zero dangling nodes: YES</span>'
        else:
            htmlstring += '<br><span style="color: red">All layers have zero dangling nodes: NO  &emsp;  Error Count: ' + str(eNode) + '</span>'
            print ("All layers have zero dangling nodes: NO    Error Count: " + str(eNode))
        if eLabel < 1:
            htmlstring += '<br><span style="color: green">All layers have zero label error: YES</span>'
        else:
            htmlstring += '<br><span style="color: red">All layers have zero label error: NO  &emsp;  Error Count: ' + str(eLabel) + '</span>'
            print ("All layers have zero label error: NO    Error Count: " + str(eLabel))

    watSummary = path + '\\' + watchFile[:-4] + '_summary.html'
    f = open(watSummary,'w')
    f.write(htmlstring)
    f.close()
    webbrowser.open(watSummary,new=2)



def shortenList(lst):
    '''Input a long list and it will turn the list into a html string that you can toggle hide and show text.'''
    if len(lst) < 4:
        return str(lst)
    else:
        return """<details>
                  <summary>Click to view/hide</summary>
                  <p>""" + str(lst) + """</p>
                  </details>"""



def sortError(errorListList, maxnum):
    ''' input should be errorDetail[lyr] and an integer. This function will return reduced error list in case there are thousands of same error type'''
    newList = []
##        uniqueError = [i[0].split(":")[1] for i in errorListList]
##        print uniqueError

    for errorType in errorListList:
        if len(errorType) >= maxnum:
            newList.append(errorType[:maxnum] + ['... and more errors (warnings) like this.'])
        else:
            newList.append(errorType)

    return newList







##        newlist = []
##        uniqueError = set([i.split(":")[1] for i in errorList])
##        uniqueErrorDict = dict(zip(uniqueError,[[] for i in uniqueError])) ## e.g. {' DEVSTAGE should be LOWMGMT, LOWNAT, DEPHARV or DEPNAT if POLYTYPE = FOR and if UCCLO + OCCLO < 25.': [], ' FORMOD attribute should be PF when OSC equals 4.': []}
##
##        for statement in uniqueError:  # statements are like 'FORMOD attribute should be PF when OSC equals 4.'
##            for i in errorList:
##                if statement in i:
##                    uniqueErrorDict[statement].append(i)
##
##        for statement in uniqueError:
##            if len(uniqueErrorDict[statement]) > max:
##                newlist += uniqueErrorDict[statement][:max]
##            else:
##                newlist += uniqueErrorDict[statement]
##
##    return newlist






if __name__ == '__main__':
    spcomp = "CW  70SB  20LA  10"
    print (spcVal(spcomp,"SPCOMP"))


    completeSpList = SpcListInterp + SpcListOther # this is our complete species list.
    completeSpList.sort()
    print(completeSpList)