import time
import numpy as np
import random

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
    file = open('input_large2.txt', mode = 'r')
    line = file.readline()
    first_line = line.rstrip().split(' ')
    size = int(first_line[0])
    dep_apt = first_line[1]
    zones = {}
    zones_name = []
    flights_from_apt = {}

    for i in range(0, size):
        line = next(file)
        zone_name = line.rstrip().split(' ')
        line = next(file)
        zone_list =  line.rstrip().split(' ')
        for apt in zone_list:
            zones[apt] = zone_name[0]
            flights_from_apt[apt] = {}
            for i in range(0,size+1): 
                flights_from_apt[apt][str(i)] = [[None,None, None, None, None, None]]
        zones_name.append(zone_name[0])  
    try: 
        measure('before flights input')
        while line is not None:
            line = next(file)
            flight = line.split(' ')
            apt_from = flight[0]
            flight.extend([zones[apt_from],zones[flight[1]]])
            flights_from_apt.setdefault(apt_from).setdefault(flight[2]).append(flight)
    except StopIteration:
        pass

else:
    #on the test platform
    line = raw_input()
    first_line = line.rstrip().split(' ')
    size = int(first_line[0])
    dep_apt = first_line[1]
    zones = {}
    zones_name = []
    flights_from_apt = {}
    for i in range(0, size):
        line = raw_input()
        zone_name = line.rstrip().split(' ')
        line = raw_input()
        zone_list =  line.rstrip().split(' ')
        for apt in zone_list:
            zones[apt] = zone_name[0]
            flights_from_apt[apt] = {}
            for i in range(0,size+1): 
                flights_from_apt[apt][str(i)] = [[None,None, None, None, None, None]]
        zones_name.append(zone_name[0])  
    try: 
        while line is not None:
            line = raw_input()
            flight = line.split(' ')
            apt_from = flight[0]
            flight.extend([zones[apt_from],zones[flight[1]]])
            flights_from_apt.setdefault(apt_from).setdefault(flight[2]).append(flight)
    except EOFError:
        pass

#---------------------------- end of read data ---------------------------------------------------#
measure('end of read')
itinerary = []
winner =[]
rerun = 0
current_airport = dep_apt
dep_zone = zones[dep_apt]
current_day = 1
current_zone = dep_zone
choice=[]
visited = [dep_zone]
blacklist = np.array([[None,None, None, None, None, None]])

day = '0'
tries = 1

if size <= 20: 
    time_to_solve = 3
else: 
    if size <= 100:
        time_to_solve = 5
    else: 
        time_to_solve = 15

sum_prices = 0

first_time = True

while (time.time()-start) < 0.8*time_to_solve or first_time : #----------while you still have time
    tries = 1
    
    while tries != 0: #------------- while not back at home       
        if (time.time()-start) > 0.8*time_to_solve and not first_time : break
        
        while  int(day) < size-1: #----------- loop for every day
            if (time.time()-start) > 0.8*time_to_solve and not first_time : break
            day = str(len(itinerary)+1)
            current_day = day
            
            #------------------ make up list of choices for the day
            flight_list_iter = np.vstack([flights_from_apt[current_airport][current_day],
                                                flights_from_apt[current_airport]['0']])
            
            choices = flight_list_iter

            if choices.size > 0:
                checks = np.array([item not in visited for item in choices[:,5]])
                choices = choices[checks]    

            if choices.size > 0:
                choices[:,2]= current_day
                blacklist_flights = blacklist[:,[0,1,2]]
                choices_flights = choices[:,[0,1,2]]
                check_bl = np.array([item not in blacklist_flights.tolist() for item in choices_flights.tolist()])
                choices = choices[check_bl]

                indeces = np.array([item is not None for item in choices[:,1]])
                choices = choices[indeces]
            #--------------------- choose a flight to take
            if choices.size > 0:
                rank = choices[:,3].astype('int')
                choices = choices[rank.argsort()]                          #sort by price
                choice = choices[0]                                        #take the cheapest
                
                if not first_time and random.randint(0, 1) == 1:                                         #check also following day
                    potential_dest = choices[:,[1,3]]
                    day_plus = str(int(current_day)+1)
                    choices_plus = np.array([['---', '---', '1', '0','---','---']])
                    for x in potential_dest[:,0]:
                        choices_plus = np.vstack([choices_plus, flights_from_apt[x][day_plus],
                                                            flights_from_apt[x]['0']])
                    
                    checks = np.array([item not in visited for item in choices_plus[:,5]])
                    choices_plus = choices_plus[checks] 

                    rank = [0]*len(choices)
                    for x in range(0,len(choices)):
                        check_plus =np.array(choices_plus[:,0]==choices[x,1])
                        flights_plus = choices_plus[check_plus] 
                        
                        if flights_plus.size >0 : 
                            rank[x] = int(choices[x,3]) + int(min(flights_plus[:,3]))
                        else: 
                            rank[x] = int(choices[x,3])
                    choices = choices[np.array(rank).argsort()]                          #sort by score
                    choice = np.array(choices[0] )

                new_airport = choice[1]
                new_zone = choice[5]
        
                itinerary.append(choice)
                visited.append(new_zone)
                current_zone = new_zone
                current_airport = new_airport
                
            else: # if no choice for the day -> rollback
                rollback(1)
                choice=[]
                tries = tries+1

        #------------------final flight back to departing zone
        day = str(len(itinerary)+1)
        current_day = day
        flight_list_iter = np.vstack([flights_from_apt[current_airport][current_day],
                                            flights_from_apt[current_airport]['0']])

        
        indeces = [np.logical_and(flight_list_iter[:,5] == dep_zone, 
                    flight_list_iter[:,0] == current_airport)]
        choices = flight_list_iter[tuple(indeces)]

        if choices.size > 0:
            choice = choices[np.argmin(choices[:, 3])]
            choice[2] = size
            itinerary.append(choice)
            tries = 0
            first_time = False
        else:
            rollback(2)
            choice = []
            tries = tries + 1
    
    #------------- if you have time go back and solve it differently
    if (time.time()-start) > 0.8*time_to_solve and not first_time : break
    
    new_price = sum(int(line[3]) for line in itinerary) 
    if first_time: sum_price = new_price
    if (sum_prices == 0 or new_price < sum_prices) and len(itinerary) == size : 
        winner = itinerary[:]
        sum_prices = new_price
    
    itinerary = winner[:]
    rerun = rerun+1
    random_rewind = random.randint(2,size-1)
    if dev: print('new price: ', new_price, 'random rewind: ', random_rewind, 'time: '+str(round(time.time()-start,0)))
    rollback(random_rewind, False)
    tries = tries + 1
    
if (sum_prices == 0 or new_price < sum_prices) and len(itinerary) == size : 
        winner = itinerary[:]
        sum_prices = new_price
    
if np.all(winner[0]==0) : del winner[0]      
sum_prices = sum(int(line[3]) for line in winner) 
print(sum_prices)

for i in range(0,size):
    print(str(winner[i][0])+" "+str(winner[i][1])+" "+str(winner[i][2])+" "+str(winner[i][3].rstrip()))

if dev:
    measure('finished')
    print('final_price: ', sum_prices)
    print('reruns: ', rerun)
    np.savetxt("itinerary.csv", itinerary, delimiter=",", fmt='%s')