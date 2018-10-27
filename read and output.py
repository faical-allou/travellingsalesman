import numpy as np
import warnings

dev = True          #set to False to run on the test platform


#---------------------------- read data ---------------------------------------------------#
zones = {}
zones_name = []
flights_from_apt = {}
zone_prices_to = {}

if dev:
    #when ran locally
    file = open('input_medium.txt', mode = 'r')
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
        while line is not None:
            flight = next(file).split(' ')                                                       
            flight.extend([zones[flight[0]],zones[flight[1]]])      
            flights_from_apt.setdefault(flight[0],{})    \
                            .setdefault(flight[2],[])   \
                            .append(flight)
            zone_prices_to.setdefault(flight[5],[]).append(flight[3])              
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
            zone_prices_to.setdefault(flight[5],[]).append(flight[3])    
    except EOFError:
        pass

#---------------------------- end of read data ---------------------------------------------------#





#---------------------------- output winner ---------------------------------------------------#

if np.all(winner[0]==0) : del winner[0]      
sum_prices = sum(int(line[3]) for line in winner) 
print(sum_prices)

for i in range(0,size):
    print(str(winner[i][0])+" "+str(winner[i][1])+" "+str(winner[i][2])+" "+str(winner[i][3].rstrip()))
