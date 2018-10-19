import time
import numpy as np
import random
import gc
dev = True

def apt_to_zone(apt, zones):
    for check in zones:
        if apt in check[1]:
            return check[0][0]

#---------------------------- read data ---------------------------------------------------#
if dev:
    #when ran locally
    start = time.time() 
    file = open('input.txt', mode = 'r')
    line = file.readline()
    first_line = line.rstrip().split(' ')
    size = int(first_line[0])
    dep_apt = first_line[1]
    zones = []
    zones_name = []
    for i in range(0, size):
        line = next(file)
        zone_name = line.rstrip().split(' ')
        line = next(file)
        zone_list =  line.rstrip().split(' ')
        zones.append([zone_name, zone_list])
        zones_name.append(zone_name[0])
    flight_list = []
    try: 
        while line is not None:
            line = next(file)
            flight = line.rstrip().split(' ')
            flight.append(apt_to_zone(flight[0], zones))
            flight.append(apt_to_zone(flight[1], zones))
            flight_list.append(flight)
    except StopIteration:
        pass

else:
    #on the test platform
    line = input()
    first_line = line.rstrip().split(' ')
    size = int(first_line[0])
    dep_apt = first_line[1]
    zones = []
    zones_name = []
    for i in range(0, size):
        line = input()
        zone_name = line.rstrip().split(' ')
        line = input()
        zone_list =  line.rstrip().split(' ')
        zones.append([zone_name, zone_list])
        zones_name.append(zone_name[0])
    flight_list = []
    try: 
        while line is not None:
            line = input()
            flight = line.rstrip().split(' ')
            flight.append(apt_to_zone(flight[0], zones))
            flight.append(apt_to_zone(flight[1], zones))
            flight_list.append(flight)
    except EOFError:
        pass

#---------------------------- end of read data ---------------------------------------------------#

itinerary = []
itinerary.append(0)

price = 0
current_airport = dep_apt
dep_zone = apt_to_zone(dep_apt, zones)
current_day = 1
current_zone = dep_zone
choice=[]

flight_list_iter = np.array( flight_list)

next_list = flight_list_iter[flight_list_iter[:,5] != dep_zone]

i = 1
j = 1
while j != 0:
    i = 1
    while i < size:
        current_day = i
        flight_list_iter = next_list

        choices = flight_list_iter[np.logical_and(flight_list_iter[:,0] == current_airport, 
                    np.logical_or(flight_list_iter[:,2] =='0', 
                        flight_list_iter[:,2] ==str(current_day))) ]

        print(str(j)+" "+str(i)+" "+str(len(flight_list_iter))+" "+str(len(choices)))

        if len(choices) > 0:
            choice = choices[random.randint(0,len(choices)-1)]
            #choice = choices[0]
            choice[2] = i
            new_airport = choice[1]
            new_zone = choice[4]
    
            itinerary.append(choice)

            price = price + int(choice[3])

            next_list = flight_list_iter[np.logical_and(flight_list_iter[:,4] != current_zone,
                                        flight_list_iter[:,5] != new_zone)]

            current_zone = new_zone
            current_airport = new_airport
            i = i +1

        else:
            gc.collect()
            flight_list_iter = np.array( flight_list)
            next_list = []
            next_list = flight_list_iter[flight_list_iter[:,5] != dep_zone]
            i = 1
            itinerary = []
            itinerary.append(0)
            price = 0
            current_airport = dep_apt
            current_zone = dep_zone
            choice=[]
            j = j+1
    
    flight_list_iter = np.array( flight_list)
    choices = flight_list_iter[np.logical_and(flight_list_iter[:,0] == current_airport, 
                flight_list_iter[:,5] == dep_zone, 
                np.logical_or(flight_list_iter[:,2] =='0', 
                flight_list_iter[:,2] ==str(size))) ]
    if len(choices) > 0:
        choice = choices[0]
        choice[2] = size
        itinerary.append(choice)
        price = price + int(choice[3])
        j = 0

itinerary[0] = price
print(itinerary[0])
for i in range(1,size+1):
    print(str(itinerary[i][0])+" "+str(itinerary[i][1])+" "+str(itinerary[i][2])+" "+str(itinerary[i][3]))

if dev:
    end = time.time()
    print(end - start)