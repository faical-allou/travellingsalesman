import time
import numpy as np
import random
import warnings

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
    file = open('input_small.txt', mode = 'r')
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
        zones_name.append(zone_name[0])  
    try: 
        measure('before flights input')
        while line is not None:
            flight = next(file).split(' ')                                                        # 2.5s
            flight.extend([zones[flight[0]],zones[flight[1]]])      
            flights_from_apt.setdefault(flight[0],{})    \
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
    flights_from_apt = {}
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
            flight = raw_input().split(' ')                                                        # 2.5s
            flight.extend([zones[flight[0]],zones[flight[1]]])      
            flights_from_apt.setdefault(flight[0],{})    \
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
blacklist_saved = []

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

while (time.time()-start) < time_to_solve or first_time : #----------while you still have time
    tries = 1
    
    while tries != 0: #------------- while not back at home       
        if (time.time()-start) > time_to_solve and not first_time : break
        
        while  int(day) < size-1: #----------- loop for every day
            if (time.time()-start) > time_to_solve and not first_time : break
            day = str(len(itinerary)+1)
            current_day = day
            
            #------------------ make up list of choices for the day
            flight_list_iter = np.vstack(
                [flights_from_apt.setdefault(current_airport,{}).setdefault(current_day,blank_flight),
                flights_from_apt.setdefault(current_airport,{}).setdefault('0',blank_flight)] )

            choices = flight_list_iter
            
            if choices.size > 0:
                checks = np.array([item not in visited for item in choices[:,5]])
                choices = choices[checks]    

            if choices.size > 0:
                choices[:,2]= current_day
                blacklist_flights = blacklist[:,[0,1,2]].tolist()
                choices_flights = choices[:,[0,1,2]].tolist()
                check_bl = np.array([item not in blacklist_flights for item in choices_flights])
                choices = choices[check_bl]
            
            if choices.size > 0:
                indeces = np.array([item is not None for item in choices[:,1]])
                choices = choices[indeces]
            
            #--------------------- choose a flight to take
            if choices.size > 0:
                rank = choices[:,3].astype('int')
                choices = choices[rank.argsort()]                          #sort by price
                #choice = choices[0]                                       #take the cheapest
                choice = choices[min(one_off, len(choices)-1)]    #take one of the cheapest once, after rerun
                one_off = 0                                                           

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
        flight_list_iter = np.vstack(
            [flights_from_apt.setdefault(current_airport,{}).setdefault(current_day,blank_flight),
            flights_from_apt.setdefault(current_airport,{}).setdefault('0',blank_flight)] )

        
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
            rollback(1)
            choice = []
            tries = tries + 1
    
    #------------- if you have time go back and solve it differently
    if (time.time()-start) > time_to_solve and not first_time : break
    
    new_price = sum(int(line[3]) for line in itinerary) 
    if first_time: sum_price = new_price
    if (sum_prices == 0 or new_price < sum_prices) and len(itinerary) == size : 
        winner = itinerary[:]
        sum_prices = new_price
        deals = []
        for flight_itin in winner:
            flight_compare = []
            for i in range(0,size):
                flight_compare_day = [f for f in flights_from_apt[flight_itin[0]].setdefault(str(i),0) if f[1] == flight_itin[1]]
                flight_compare.extend(flight_compare_day)
            deal = float(flight_itin[3]) - (sum([float(f[3]) for f in flight_compare])  / float(len(flight_compare)))
            deals.append(deal)

        deals_array = np.array(deals)
        max_var = deals_array.argmax()
        balcklits_saved = blacklist[:]
        blacklist = np.vstack([blacklist,winner[max_var]])
        random_rewind =  size

    else:
        one_off = 1
        if len(blacklist_saved) > 0: blacklist = blacklist_saved
        itinerary_array = np.array(itinerary)
        max_index = itinerary_array[:,3].astype('int').argmax()
        random_rewind = (size - max_index) + random.randint(0,max_index)


    itinerary = winner[:]
    rerun = rerun+1
    
  
    rollback(random_rewind, False)
    
    if dev: print('npriz: ', new_price, 'randrw: ', random_rewind, 'randrollb?: '+str(one_off))
    tries = tries + 1
    
if (sum_prices == 0 or new_price < sum_prices) and len(itinerary) == size : 
        winner = itinerary[:]
        sum_prices = sum(int(line[3]) for line in itinerary) 
    
if np.all(winner[0][0]==0) : del winner[0]      
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