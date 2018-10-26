import time
import numpy as np
import random
import warnings
import itertools

dev = True
start = time.time()

def rollback(steps=1, apply_bl=True):
    global blacklist, itinerary, visited, current_airport, current_zone, day
    initial_length = len(itinerary)
    for k in range(0,steps):
        if initial_length > 0 and apply_bl: blacklist = np.vstack([blacklist,itinerary[-1]])
        if initial_length <= steps+2:
            current_airport = dep_apt
            current_zone = dep_zone
            itinerary = []
            visited = [dep_zone]
            day = '1'
            break
        else: 
            del itinerary[-1]
            current_airport = itinerary[-1][1]
            current_zone = itinerary[-1][4]
            visited = [dep_zone]
            for itin in itinerary:
                visited.append(itin[5])
    day = str(len(itinerary)) # need to set up for the following day to start computing

def measure(tag=''):
    global day, tries, start, flight_list_iter, choices, dev
    if dev:
        endi = time.time()
        print("timestamp "+tag+": ", endi - start)

def flag(tag=''):
    global day, tries, start, flight_list_iter, choices, dev, first_time
    if dev:
        print(str(tries)+" "+str(day)+" "+str(len(flight_list_iter))+" "+
            str(len(choices))+" "+str(current_airport))+" "+str(round(time.time()-start,0))


#---------------------------- read data ---------------------------------------------------#
if dev:
    #when ran locally
    file = open('input.txt', mode = 'r')
    line = file.readline()
    first_line = line.rstrip().split(' ')
    size = int(first_line[0])
    dep_apt = first_line[1]
    zones = {}
    zones_name = []
    zone_compo = {}
    flights_from_apt = {}

    for i in range(0, size):
        line = next(file)
        zone_name = line.rstrip().split(' ')
        line = next(file)
        zone_list =  line.rstrip().split(' ')
        for apt in zone_list:
            zones[apt] = zone_name[0]
        zones_name.append(zone_name[0])
        zone_compo.setdefault(zone_name[0],[]).extend(zone_list)   
    try: 
        measure('before flights input')
        while line is not None:
            flight = next(file).split(' ')                                                        # 2.5s
            flight.extend([zones[flight[0]],zones[flight[1]]])      
            flights_from_apt.setdefault(flight[0],{})   \
                            .setdefault(flight[1],{})    \
                            .setdefault(flight[2],[])   \
                            .append(flight)                          
    except StopIteration:
        pass

else:
    warnings.filterwarnings("ignore")
    #on the test platform
    line = raw_input()
    first_line = line.rstrip().split(' ')
    size = int(first_line[0])
    dep_apt = first_line[1]
    zones = {}
    zones_name = []
    zone_compo = {}
    flights_from_apt = {}
    for i in range(0, size):
        line = raw_input()
        zone_name = line.rstrip().split(' ')
        line = raw_input()
        zone_list =  line.rstrip().split(' ')
        for apt in zone_list:
            zones[apt] = zone_name[0]
        zones_name.append(zone_name[0])
        zone_compo.setdefault(zone_name[0],[]).extend(zone_list)  
    try: 
        while line is not None:
            flight = raw_input().split(' ')                                                        # 2.5s
            flight.extend([zones[flight[0]],zones[flight[1]]])      
            flights_from_apt.setdefault(flight[0],{})   \
                            .setdefault(flight[1],{})    \
                            .setdefault(flight[2],[])   \
                            .append(flight)  
    except EOFError:
        pass

#---------------------------- end of read data ---------------------------------------------------#
measure('end of read')
itinerary = []
winner =[]
rerun = 0
one_off = 0

current_airport = dep_apt
dep_zone = zones[dep_apt]
current_day = 1
current_zone = dep_zone
choice=[]
visited = [dep_zone]
blacklist = np.array([[None,None, None, None, None, None]])
blank_flight = [[None,None, None, None, None, None]]

day = '0'
tries = 1

if size <= 20: 
    time_limit = 3
else: 
    if size <= 100:
        time_limit = 5
    else: 
        time_limit = 15

time_to_solve = 0.8*time_limit

sum_prices = 0

first_time = True

bign = 10000
sum_prices = bign*size


zones_to_shuffle = [x for x in zones_name if x!= dep_zone]


for j in range(1,10000):
    random.shuffle(zones_to_shuffle)
    zones_to_use = zones_to_shuffle[:]
    zones_to_use.insert(0,dep_zone)
    zones_to_use.extend([dep_zone])
    itinerary = 
    for i in range(1,size):
        itinerary.append( [zone_compo[zones_to_use[i]][0],zone_compo[zones_to_use[i+1]][0],i+1])
        price_list = flights_from_apt[itinerary[i][0]].setdefault(itinerary[i][1],{}).setdefault(str(i),[])                      
        try:
            min_price = min([int(row[3].rstrip()) for row in price_list])
        except ValueError:
            min_price = bign
        itinerary[i].extend([min_price])

    new_price = sum(int(line[3]) for line in itinerary) 
    if (sum_prices == 0 or new_price < sum_prices) and len(itinerary) == size : 
        winner = itinerary[:]
        sum_prices = new_price
    itinerary = []

measure('end of loop')
sum_prices = sum(int(line[3]) for line in itinerary) 
    
if np.all(winner[0]==0) : del winner[0]      
sum_prices = sum(int(line[3]) for line in winner) 
print(sum_prices)

for i in range(0,size):
    print(str(winner[i][0])+" "+str(winner[i][1])+" "+str(winner[i][2])+" "+str(winner[i][3]))

if dev:
    for row in winner:
       row[3]= row[3]
    measure('finished')
    print('final_price: ', sum_prices)
    print('reruns: ', rerun)
    np.savetxt("itinerary.csv", winner, delimiter=",", fmt='%s')