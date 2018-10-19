import time
import numpy as np

dev = True

def rollback(steps=1):
    global blacklist, itinerary, visited, current_airport, current_zone, day
    for k in range(0,steps):
        blacklist = np.vstack([blacklist,itinerary[-1]])
        if len(itinerary) < steps+2:
            current_airport = dep_apt
            current_zone = dep_zone
            itinerary = [0]
            visited = [dep_zone]
            break
        else: 
            del itinerary[-1]
            del visited[-1]
            current_airport = itinerary[-1][1]
            current_zone = itinerary[-1][4]
    day = max(1, day-steps)

def measure(tag=''):
    global day, tries, start, flight_list_iter, choices, dev
    if dev:
        endi = time.time()
        print("timestamp "+tag+": ", endi - start)

def flag(tag=''):
    global day, tries, start, flight_list_iter, choices, dev
    if dev:
        print(str(tries)+" "+str(day)+" "+str(len(flight_list_iter))+" "+str(len(choices))+" "+str(current_airport))


#---------------------------- read data ---------------------------------------------------#
if dev:
    #when ran locally
    start = time.time() 
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
            for i in range(0,size+1): 
                flights_from_apt[apt+str(i)] = {}
                flights_from_apt[apt+str(i)] = [[None,None, None, None, None, None]]
        zones_name.append(zone_name[0])  
    try: 
        i = 0
        while line is not None:
            i=i+1
            line = next(file)
            flight = line.rstrip().split(' ')
            apt_from = flight[0]
            flight=flight+[zones[apt_from],zones[flight[1]]]
            flights_from_apt[apt_from+str(int(flight[2]))].append(flight)
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
                flights_from_apt[apt][i] = [[None,None, None, None, None, None]]
        zones_name.append(zone_name[0])  
    try: 
        i = 0
        while line is not None:
            i=i+1
            line = raw_input()
            flight = line.rstrip().split(' ')
            apt_from = flight[0]
            flight=flight+[zones[apt_from],zones[flight[1]]]
            flights_from_apt[apt_from][int(flight[2])].append(flight)
    except EOFError:
        pass

#---------------------------- end of read data ---------------------------------------------------#
measure('end of read')
itinerary = [0]

current_airport = dep_apt
dep_zone = zones[dep_apt]
current_day = 1
current_zone = dep_zone
choice=[]
visited = [dep_zone]
blacklist = np.array([['---', '---', '1', '0','---','---']])

day = 1
tries = 1

while tries != 0: #--- while not back at home
    while day < size: #--- loop for every day
        current_day = day
        #------------------ make up list of choices for the day

        flight_list_iter = np.vstack([flights_from_apt[current_airport+str(current_day)],
                                            flights_from_apt[current_airport+str(0)]])
        
        choices = flight_list_iter

        if choices.size > 0:
            checks = list([item not in visited for item in choices[:,5]])
            choices = choices[checks]    

        if choices.size > 0:
            choices[:,2]= current_day
            blacklist_flights = blacklist[:,[0,1,2]]
            choices_flights = choices[:,[0,1,2]]
            check_bl = np.array([item not in blacklist_flights.tolist() for item in choices_flights.tolist()])
            choices = choices[check_bl]

            indeces = list([item is not None for item in choices[:,1]])
            choices = choices[indeces]

        #--------------------- choose a flight to take
        if choices.size > 0:
            #choice = choices[0]                                        #chose the first one you find
            #choice = choices[random.randint(0,len(choices)-1)]         #chose a random one
            
            rank = choices[:,3].astype('int')
            choices = choices[rank.argsort()]                           #sort by price
            choice = choices[0]                                         #take the cheapest
            #choice = choices[min(random.randint(0,1), len(choices)-1)] #take one of the X cheapest randomly

            choice[2] = day

            new_airport = choice[1]
            new_zone = choice[5]
    
            itinerary.append(choice)

            visited.append(new_zone)
            current_zone = new_zone
            current_airport = new_airport
            day = day +1

        else: # if no choice for the day -> reset
            rollback(1)
            choice=[]
            tries = tries+1
        
    #------------------final flight back to departing zone
    current_day = day

    flight_list_iter = np.vstack([flights_from_apt[current_airport+str(current_day)],
                                            flights_from_apt[current_airport+str(0)]])

    
    indeces = [np.logical_and(flight_list_iter[:,5] == dep_zone, 
                flight_list_iter[:,0] == current_airport)]
    choices = flight_list_iter[tuple(indeces)]

    if choices.size > 0:
        choice = choices[np.argmin(choices[:, 3])]
        choice[2] = size
        itinerary.append(choice)
        k = tries
        tries = 0
    else:
        rollback(2)
        choice=[]
        tries = tries + 1

if itinerary[0]==0 : del itinerary[0]      
prices = sum(int(line[3]) for line in itinerary) 
print(prices)

for i in range(0,size):
    print(str(itinerary[i][0])+" "+str(itinerary[i][1])+" "+str(itinerary[i][2])+" "+str(itinerary[i][3]))

if dev:
    measure('finished')
    print('rollbacks', k-1)
    np.savetxt("itinerary.csv", itinerary, delimiter=",", fmt='%s')