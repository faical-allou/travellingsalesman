import time
import numpy as np
import random
import warnings
from collections import defaultdict

dev = True
start = time.time()

def rollback(steps=1, apply_bl=True):
    global blacklist, itinerary, visited, current_airport, current_zone, day
    initial_length = len(itinerary)
    if initial_length > 0 and apply_bl: blacklist = np.vstack([blacklist,itinerary[-1]])
    if initial_length <= steps+2:
        current_airport = dep_apt
        current_zone = dep_zone
        itinerary = []
        visited = [dep_zone]
        day = '1'
    else: 
        for k in range(0,steps):
            del itinerary[-1]
            current_airport = itinerary[-1][1]
            current_zone = itinerary[-1][4]

    visited = [dep_zone]
    visited.extend(list([itin[5] for itin in itinerary]))

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
zones = {}
zones_name = []
flights_from_apt = {}
zones_prio = {}
zone_prices = {}

if dev:
    #when ran locally
    file = open('input.txt', mode = 'r')
    line = file.readline()
    first_line = line.rstrip().split(' ')
    size = int(first_line[0])
    dep_apt = first_line[1]

    for i in range(0, size):
        line = next(file)
        zone_name = line.rstrip().split(' ')
        line = next(file)
        zone_list =  line.rstrip().split(' ')
        for apt in zone_list:
            zones[apt] = zone_name[0]
        zones_name.append(zone_name[0])  
    try: 
        measure('before flights input')
        while line is not None:
            flight = next(file).split(' ')                                                       
            flight.extend([zones[flight[0]],zones[flight[1]]])      
            flights_from_apt.setdefault(flight[0],{})    \
                            .setdefault(flight[2],[])   \
                            .append(flight)
            zones_prio[flight[5]] = zones_prio.setdefault(flight[5],0)+1
            zone_prices.setdefault(flight[4],{})    \
                        .setdefault(flight[5],[])   \
                        .append(flight[3])              
    except StopIteration:
        pass

else:
    warnings.filterwarnings("ignore")
    #on the test platform
    line = raw_input()
    first_line = line.rstrip().split(' ')
    size = int(first_line[0])
    dep_apt = first_line[1]
    for i in range(0, size):
        line = raw_input()
        zone_name = line.rstrip().split(' ')
        line = raw_input()
        zone_list =  line.rstrip().split(' ')
        for apt in zone_list:
            zones[apt] = zone_name[0]
        zones_name.append(zone_name[0])  
    try: 
        while line is not None:
            flight = raw_input().split(' ')                                                       
            flight.extend([zones[flight[0]],zones[flight[1]]])      
            flights_from_apt.setdefault(flight[0],{})    \
                            .setdefault(flight[2],[])   \
                            .append(flight)
            zones_prio[flight[5]] = zones_prio.setdefault(flight[5],0)+1
            zone_prices.setdefault(flight[4],{})    \
                        .setdefault(flight[5],[])   \
                        .append(flight[3])    
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

time_to_solve = 0.08*time_limit

sum_prices = 0

first_time = True

#####--- zones with less flights get higher priority
avg_prio = sum(int(value) for key, value in zones_prio.iteritems()) / len(zones_prio)
for zone in zones_name:
    zones_prio[zone] = float(zones_prio[zone])/ float(avg_prio)

#####--- zones to zones avg price is compared to price available each day to know if you should wait
for key_from in zone_prices:
    for key_to in zone_prices[key_from]:
        listprices = zone_prices[key_from][key_to]
        zone_prices[key_from][key_to] = sum(int(value) for value in listprices) / len(listprices)

while (time.time()-start) < time_to_solve or first_time : #----------while you still have time
    tries = 1
    
    while tries != 0: #------------- while not back at home       
        overpaid = defaultdict(dict)
        
        while  int(day) < size-1: #----------- loop for every day
            if (time.time()-start) > time_to_solve and not first_time : break
            day = str(len(itinerary)+1)
            
            #------------------ make up list of choices for the day
            choices = np.vstack(
                [flights_from_apt.setdefault(current_airport,{}).setdefault(day,blank_flight),
                flights_from_apt.setdefault(current_airport,{}).setdefault('0',blank_flight)] )
            
            if choices.size > 0:
                checks = np.array([(item not in visited and item is not None )for item in choices[:,5]])
                choices = choices[checks]    

            if choices.size > 0:
                choices[:,2]= day
                blacklist_flights = blacklist[:,[0,1,2]].tolist()
                choices_flights = choices[:,[0,1,2]].tolist()
                check_bl = np.array([item not in blacklist_flights for item in choices_flights])
                choices = choices[check_bl]
            
            #--------------------- choose a flight to take
            if choices.size > 0:
                deals = []
                overpaid_later = []
                for choix in choices:
                    deal_quality = int(choix[3].rstrip()) - zone_prices[choix[4]][choix[5]] 
                    deals.extend([deal_quality])
                    overpaid_later.extend([overpaid.setdefault(choix[4],{}).setdefault(choix[5],0)])
                overpaid_later = np.array(overpaid_later) 
                deals = np.array(deals)
                min_price = np.amin(deals)

                # normalizing with min to avoid negative values; 
                # and using (1-day/size) because prob of finding cheaper goes down
                # using size/300 to use more for big problems where prios are more important
                rank = (choices[:,3].astype('float') +
                        (deals[:] - min_price - overpaid_later)*(1-int(day)/size) ) * \
                        ( np.vectorize(zones_prio.get)(choices[:,5])**(size/300) ) 
                        
                choices = choices[rank.argsort()]                 # sort by score
                choice = choices[min(random.randint(one_off,one_off*4), len(choices)-1)]    # take one of the cheapest once
                one_off = 0                                                           

                new_airport = choice[1]
                new_zone = choice[5]
        
                itinerary.append(choice)
                visited.append(new_zone)
                current_zone = new_zone
                current_airport = new_airport
                
            else: # if no choice left for the day -> rollback
                rollback(1)
                choice=[]
                tries = tries+1
                if not first_time and tries > size: break
        #------------------final flight back to departing zone
        if not first_time and tries > size: break
        day = str(len(itinerary)+1)

        flight_list_iter = np.vstack(
            [flights_from_apt.setdefault(current_airport,{}).setdefault(day,blank_flight),
            flights_from_apt.setdefault(current_airport,{}).setdefault('0',blank_flight)] )

        
        indeces = [np.logical_and(flight_list_iter[:,5] == dep_zone, 
                    flight_list_iter[:,0] == current_airport)]

        choices = flight_list_iter[tuple(indeces)]

        if choices.size > 0:
            choice = choices[np.argmin(choices[:, 3])]
            choice[2] = size
            itinerary.append(choice)
            tries = 0       # meaning I arrived stop iteration
            first_time = False
        else:
            rollback(1)
            choice = []
            tries = tries + 1
    
    #------- check if better than champion
    new_price = sum(int(line[3]) for line in itinerary) 
    if first_time: sum_price = new_price
    if (sum_prices == 0 or new_price < sum_prices) and len(itinerary) == size : 
        winner = itinerary[:]
        sum_prices = new_price
        blacklist_saved = blacklist[:]

        for itin in winner:
            overpaid[itin[4]][itin[5]] = int(itin[3]) - zone_prices[itin[4]][itin[5]]
    else:
        blacklist = blacklist_saved[:]
        

    rerun = rerun+1
    one_off = 1
    
    #------------- if you have time, go back to a random point and solve it differently
    random_rewind = random.randint(1,size)
    if dev: print('new price: ', new_price, 'random rewind: ', random_rewind, 'time: '+str(round(time.time()-start,0)), len(itinerary))
    itinerary = winner[:]
    rollback(random_rewind, False)
    
    tries = tries + 1
    
if (sum_prices == 0 or new_price < sum_prices) and len(itinerary) == size : 
        winner = itinerary[:]
        sum_prices = sum(int(line[3]) for line in itinerary) 
    
if np.all(winner[0]==0) : del winner[0]      
sum_prices = sum(int(line[3]) for line in winner) 
print(sum_prices)

for i in range(0,size):
    print(str(winner[i][0])+" "+str(winner[i][1])+" "+str(winner[i][2])+" "+str(winner[i][3].rstrip()))

if dev:
    for row in winner:
       row[3]= row[3].rstrip()
    measure('finished')
    print('final_price: ', sum_prices)
    print('reruns: ', rerun)
    np.savetxt("itinerary.csv", winner, delimiter=",", fmt='%s')