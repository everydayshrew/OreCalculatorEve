'''
This program will poll Eve-central once every 24 hours to fetch the
latest market data from Jita/Hek, and then parse it.  It uses the follow
API xml fetch request:
http://api.eve-central.com/api/marketstat?usesystem=30000142&typeid=34&typeid=35&typeid=36&typeid=37&typeid=38&typeid=39&typeid=40&typeid=11399&typeid=1230&typeid=1228&typeid=1224&typeid=18&typeid=1227&typeid=20&typeid=1226&typeid=1231&typeid=21&typeid=1229&typeid=1232&typeid=1225&typeid=19&typeid=1223&typeid=22&typeid=11396&typeid=16274&typeid=17887&typeid=17888&typeid=17889&typeid=16273&typeid=16272&typeid=16275&typeid=16267&typeid=16263&typeid=16266&typeid=16265&typeid=16264&typeid=16262&typeid=16268&typeid=16269

For future reference, here are the ids:
Tritanium - 34   Pyrite - 35   Mexallon - 36
Isogen - 37      Nocxium - 38  Zydrine - 39
Megacyte - 40    Morphite - 11399

Scordite - 1228     Vedlspar - 1230      Pyroxeres - 1224
Plagioclase - 18    Omber - 1227         Kernite - 20
Jaspet - 1226       Hemorphite - 1231    Hedbergite - 21
Gneiss - 1229       Dark Ochre - 1232    Crokite - 1225
Spodmain - 19       Bistot - 1223        Arkonor - 22
Mercoxit - 1136
'''

from bs4 import BeautifulSoup
import os
import datetime
import urllib2

#-----------------------------------------------------
# First Intilization
try:
    with open('pulledvals.txt'): pass
except IOError:
    dataFile = open('pulledvals.txt', 'w')
    dataFile.writelines("0 0 0 0 0")
    dataFile.close()

# Mineral Names.
Mnames = ("Tritanium", "Pyerite", "Mexallon", "Isogen", "Nocxium", "Zydrine", 
          "Megacyte", "Morphite")
# Ore names
Onames = ('Veldspar','Scordite', 'Pyroxeres', 'Plagioclase', 'Omber', 'Kernite', 'Jaspet', 'Hemorphite', 
          'Hedbergite', 'Gneiss', 'Dark Ochre', 'Crokite', 'Spodumain', 'Bistot', 'Arkonor', 'Mercoxit')
# Ice Names
Inames = ("Dark Glitter", "Glacial Mass", "Glare Crust", "White Glaze", "Blue Ice", "Clear Icicle", "Gelidus",
          "Krystallos")
# IceProduct Names
Cnames = ("Helium Isotopes", "Oxygen Isotopes", "Nitrogen Isotopes", "Hydrogen Isotopes", "Liquid Ozone",
          "Heavy Water", "Strontium Clathrates")

# Check date function.  Compare last pull from database to current time
def checkDate(day, month, year, hour):
    now = datetime.datetime.now()
    if now.year > year or now.month > month or now.day > day:
        return False
    else:
        return True

def fetchDate():
    dataFile = open("pulledvals.txt", "r")
    date = dataFile.readline()
    dataFile.close()
    parsedDate = date.split(" ")
    parsedDate[4] = parsedDate[4].replace("\n","")
    return parsedDate

# Pull loaded file
def fetchData(forced):
    datelist = fetchDate() 
    dataFile = open("pulledvals.txt", "r")
    vals = dataFile.readline()

    # If date is recent 24 hours, pull from file.
    if (checkDate(int(datelist[1]), int(datelist[0]), int(datelist[2]), \
                  int(datelist[3])) and not forced):
        print "Last Access was {}/{}/{} at {}:{}, using stored values.".format(\
            datelist[0],datelist[1],datelist[2],datelist[3],datelist[4])
        vals = dataFile.readline()
        dataFile.close()
        vals = vals.replace("[","")
        vals = vals.replace("]","")
        values = vals.split(",")
        for n in range(0,len(values)): values[n] = float(values[n])

    # If data is outdated.  Pull from site, store in file.
    else:
        print "Updating Values from Eve-Central"
        address = "http://api.eve-central.com/api/marketstat?usesystem=30000142&typeid=34&typeid=35&typeid=36&typeid=37&typeid=38&typeid=39&typeid=40&typeid=11399&typeid=1230&typeid=1228&typeid=1224&typeid=18&typeid=1227&typeid=20&typeid=1226&typeid=1231&typeid=21&typeid=1229&typeid=1232&typeid=1225&typeid=19&typeid=1223&typeid=22&typeid=11396&typeid=16274&typeid=17887&typeid=17888&typeid=17889&typeid=16273&typeid=16272&typeid=16275&typeid=16267&typeid=16263&typeid=16266&typeid=16265&typeid=16264&typeid=16262&typeid=16268&typeid=16269"
        htmlPage = urllib2.urlopen(address)
        htmlText = htmlPage.read()
        mySoup = BeautifulSoup(htmlText)

        dataFile = open("pulledvals.txt", "w")
        values = []
        temp = []
        values = mySoup.find_all("avg")
        for n in range(0,len(values)):
            values[n] = str(values[n]).replace("<avg>","")
            values[n] = str(values[n]).replace("</avg>","")
            values[n] = float(values[n])
        now = datetime.datetime.now()
        lines = [str(now.month)+" ", str(now.day)+" ", str(now.year)+" ", \
                 str(now.hour)+" ", str(now.minute), "\n", str(values)]
        dataFile.writelines(lines)
        dataFile.close()

    print "Market data has been loaded."

    # Now the file is loaded!  Now we use it!
    # Dictionary Holding all Ore Asteroid Information
    pricedata = {}
    rawpricedata = {}
    icepricedata = {}
    icerawpricedata = {}

    Asteroids = {"Veldspar": {"Tritanium": 1000, "Pyerite": 0, "Mexallon": 0, \
                              "Isogen": 0, "Nocxium": 0, "Zydrine": 0, \
                              "Megacyte": 0, "Morphite": 0, "Batch": 333, \
                              "Volume": 0.1},
                "Scordite": {"Tritanium": 833, "Pyerite": 416, "Mexallon": 0, \
                              "Isogen": 0, "Nocxium": 0, "Zydrine": 0, \
                              "Megacyte": 0, "Morphite": 0, "Batch": 333, \
                              "Volume": 0.15},
                  "Pyroxeres": {"Tritanium": 844, "Pyerite": 59, "Mexallon": 120, \
                              "Isogen": 0, "Nocxium": 11, "Zydrine": 0, \
                              "Megacyte": 0, "Morphite": 0, "Batch": 333, \
                              "Volume": 0.3},
                  "Plagioclase": {"Tritanium": 256, "Pyerite": 512, "Mexallon": 256, \
                              "Isogen": 0, "Nocxium": 0, "Zydrine": 0, \
                              "Megacyte": 0, "Morphite": 0, "Batch": 333, \
                              "Volume": 0.35},
                  "Omber": {"Tritanium": 307, "Pyerite": 123, "Mexallon": 0, \
                              "Isogen": 307, "Nocxium": 0, "Zydrine": 0, \
                              "Megacyte": 0, "Morphite": 0, "Batch": 500, \
                              "Volume": 0.6},
                  "Kernite": {"Tritanium": 386, "Pyerite": 0, "Mexallon": 773, \
                              "Isogen": 386, "Nocxium": 0, "Zydrine": 0, \
                              "Megacyte": 0, "Morphite": 0, "Batch": 400, \
                              "Volume": 1.2},
                  "Jaspet": {"Tritanium": 259, "Pyerite": 259, "Mexallon": 518, \
                              "Isogen": 0, "Nocxium": 259, "Zydrine": 0, \
                              "Megacyte": 0, "Morphite": 0, "Batch": 500, \
                              "Volume": 2.0},
                  "Hemorphite": {"Tritanium": 212, "Pyerite": 0, "Mexallon": 0, \
                              "Isogen": 212, "Nocxium": 424, "Zydrine": 28, \
                              "Megacyte": 0, "Morphite": 0, "Batch": 500, \
                              "Volume": 3.0},
                  "Hedbergite": {"Tritanium": 0, "Pyerite": 0, "Mexallon": 0, \
                              "Isogen": 708, "Nocxium": 354, "Zydrine": 32, \
                              "Megacyte": 0, "Morphite": 0, "Batch": 400, \
                              "Volume": 3.0},
                  "Gneiss": {"Tritanium": 3700, "Pyerite": 0, "Mexallon": 3700, \
                              "Isogen": 700, "Nocxium": 0, "Zydrine": 171, \
                              "Megacyte": 0, "Morphite": 0, "Batch": 400, \
                              "Volume": 5.0},
                  "Dark Ochre": {"Tritanium": 25500, "Pyerite": 0, "Mexallon": 0, \
                              "Isogen": 0, "Nocxium": 500, "Zydrine": 250, \
                              "Megacyte": 0, "Morphite": 0, "Batch": 400, \
                              "Volume": 8.0},
                  "Crokite": {"Tritanium": 38000, "Pyerite": 0, "Mexallon": 0, \
                              "Isogen": 0, "Nocxium": 331, "Zydrine": 663, \
                              "Megacyte": 0, "Morphite": 0, "Batch": 250, \
                              "Volume": 16.0},
                  "Spodumain": {"Tritanium": 71000, "Pyerite": 9000, "Mexallon": 0, \
                              "Isogen": 0, "Nocxium": 0, "Zydrine": 0, \
                              "Megacyte": 140, "Morphite": 0, "Batch": 250, \
                              "Volume": 16.0},
                  "Bistot": {"Tritanium": 0, "Pyerite": 170, "Mexallon": 0, \
                              "Isogen": 0, "Nocxium": 0, "Zydrine": 341, \
                              "Megacyte": 170, "Morphite": 0, "Batch": 200, \
                              "Volume": 16.0},
                  "Arkonor": {"Tritanium": 10000, "Pyerite": 0, "Mexallon": 0, \
                              "Isogen": 0, "Nocxium": 0, "Zydrine": 166, \
                              "Megacyte": 333, "Morphite": 0, "Batch": 200, \
                              "Volume": 16.0},
                  "Mercoxit": {"Tritanium": 0, "Pyerite": 0, "Mexallon": 0, \
                              "Isogen": 0, "Nocxium": 0, "Zydrine": 0, \
                              "Megacyte": 0, "Morphite": 530, "Batch": 250, \
                              "Volume": 40.0},
                  "Dark Glitter": {"Helium Isotopes": 0, "Hydrogen Isotopes": 0,
                                   "Oxygen Isotopes": 0, "Nitrogen Isotopes": 0,
                                   "Heavy Water": 500, "Liquid Ozone": 1000,
                                   "Strontium Clathrates": 50},
                  "Glacial Mass": {"Helium Isotopes": 0, "Hydrogen Isotopes": 300,
                                   "Oxygen Isotopes": 0, "Nitrogen Isotopes": 0,
                                   "Heavy Water": 50, "Liquid Ozone": 25,
                                   "Strontium Clathrates": 1},
                  "Glare Crust": {"Helium Isotopes": 0, "Hydrogen Isotopes": 0,
                                   "Oxygen Isotopes": 0, "Nitrogen Isotopes": 0,
                                   "Heavy Water": 1000, "Liquid Ozone": 500,
                                   "Strontium Clathrates": 25},
                  "White Glaze": {"Helium Isotopes": 0, "Hydrogen Isotopes": 0,
                                   "Oxygen Isotopes": 0, "Nitrogen Isotopes": 300,
                                   "Heavy Water": 50, "Liquid Ozone": 25,
                                   "Strontium Clathrates": 1},
                  "Blue Ice": {"Helium Isotopes": 0, "Hydrogen Isotopes": 0,
                                   "Oxygen Isotopes": 300, "Nitrogen Isotopes": 0,
                                   "Heavy Water": 50, "Liquid Ozone": 25,
                                   "Strontium Clathrates": 1},
                  "Clear Icicle": {"Helium Isotopes": 300, "Hydrogen Isotopes": 0,
                                   "Oxygen Isotopes": 0, "Nitrogen Isotopes": 0,
                                   "Heavy Water": 50, "Liquid Ozone": 25,
                                   "Strontium Clathrates": 1},
                  "Krystallos": {"Helium Isotopes": 0, "Hydrogen Isotopes": 0,
                                   "Oxygen Isotopes": 0, "Nitrogen Isotopes": 0,
                                   "Heavy Water": 125, "Liquid Ozone": 500,
                                   "Strontium Clathrates": 125},
                  "Gelidus": {"Helium Isotopes": 0, "Hydrogen Isotopes": 0,
                                   "Oxygen Isotopes": 0, "Nitrogen Isotopes": 0,
                                   "Heavy Water": 250, "Liquid Ozone": 500,
                                   "Strontium Clathrates": 75}
                }

    # Parse information
    x = 0
    marketvals = {"Ore": {}, "Ice": {}}

    # Check if there is already a saved custom value file
    custvals = True
    try:
        with open('customvals.txt'): pass
    except IOError:
        custvals = False

    # If it has information, pull from it.  Otherwise, create the new file with duplicated
    # Eve central data.  This way the main program can edit it with no problems
    cvalues = []
    if custvals:
        if os.path.getsize("customvals.txt") > 0:
            custvals = True
            dataFile = open("customvals.txt", "r")
            vals = dataFile.readline()
            dataFile.close()
            vals = vals.replace("[","")
            vals = vals.replace("]","")
            cvalues = vals.split(",")
            for n in range(0,len(cvalues)): cvalues[n] = float(cvalues[n])
        else:
            dataFile = open("customvals.txt", "w")
            dataFile.writelines(str(values))
            dataFile.close()
            cvalues = values[:]
    else:
        dataFile = open("customvals.txt", "w")
        dataFile.writelines(str(values))
        dataFile.close()
        cvalues = values[:]
            

    # Parse data to main dictionary
    # R - Raw, SS/FS- Slow/Fast Sell. C - Custom
    for keys in Asteroids:
        total = 0
        totalB = 0
        totalC = 0

        if keys in Onames:
            # Ore Calculation
            for i in range(0,len(Mnames)):
                pricedata[Mnames[i]] = {'SS': values[1+3*i],'FS': values[2+3*i], 'CS': cvalues[1+3*i]}

                total += float(Asteroids[keys][Mnames[i]] * pricedata[Mnames[i]]['FS'])
                totalB += float(Asteroids[keys][Mnames[i]] * pricedata[Mnames[i]]['SS'])
                totalC += float(Asteroids[keys][Mnames[i]] * pricedata[Mnames[i]]['CS'])
            for i in range(0,len(Onames)):
                rawpricedata[Onames[i]] = {'RSS': values[25+3*i], 'RFS': values[26+3*i], 'RCS': cvalues[25+3*i]}

            # Final Format, Ore
            weightmodifier = float(1 / Asteroids[keys]["Volume"])

            marketvals["Ore"][keys] = {'FS': round(weightmodifier * total / Asteroids[keys]["Batch"],2), 
                                    'SS': round(weightmodifier * totalB / Asteroids[keys]["Batch"],2), 
                                    'RFS': round(weightmodifier * rawpricedata[keys]['RFS'],2),
                                    'RSS': round(weightmodifier * rawpricedata[keys]['RSS'],2),
                                    'CS': round(weightmodifier * totalC / Asteroids[keys]["Batch"],2),
                                    'RCS': round(weightmodifier * rawpricedata[keys]['RCS'],2)}

        else:
        # Ice Calculation
            for i in range(0,len(Cnames)):
                icepricedata[Cnames[i]] = {'SS': values[73+3*i],'FS': values[74+3*i], 'CS': cvalues[73+3*i]}
                total += float(Asteroids[keys][Cnames[i]] * icepricedata[Cnames[i]]['FS'])
                totalB += float(Asteroids[keys][Cnames[i]] * icepricedata[Cnames[i]]['SS'])
                totalC += float(Asteroids[keys][Cnames[i]] * icepricedata[Cnames[i]]['CS'])
            for i in range(0,len(Inames)):
                icerawpricedata[Inames[i]] = {'RSS': values[94+3*i], 'RFS': values[95+3*i], 'RCS': cvalues[94+3*i]}

            marketvals["Ice"][keys] = {'FS': round(total,2), 'SS': round(totalB,2), 
                                    'RFS': round(icerawpricedata[keys]['RFS'],2),
                                    'RSS': round(icerawpricedata[keys]['RSS'],2),
                                    'CS': round(totalC,2),'RCS': round(icerawpricedata[keys]['RCS'],2)}
        x+=1

    return marketvals
