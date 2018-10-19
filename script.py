import time
dev = True

def apt_to_zone(apt, zones):
    for check in zones:
        if apt in check[1]:
            return check[0][0]

#---------------------------- read data ---------------------------------------------------#
if dev:
    #when ran locally
    start = time.time() 
    file = open('input.txt', mode = 'r', encoding = 'utf-8-sig')
    line = file.readline()
    first_line = line.rstrip().split(' ')
    size = int(first_line[0])
    dep_apt = first_line[1]
    zones = []
    for i in range(0, size):
        line = next(file)
        zone_name = line.rstrip().split(' ')
        line = next(file)
        zone_list =  line.rstrip().split(' ')
        zones.append([zone_name, zone_list])
    flight_list = []
    try: 
        while line is not None:
            line = next(file)
            flight = line.rstrip().split(' ')
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
    for i in range(0, size):
        line = input()
        zone_name = line.rstrip().split(' ')
        line = input()
        zone_list =  line.rstrip().split(' ')
        zones.append([zone_name, zone_list])
    flight_list = []
    try: 
        while line is not None:
            line = input()
            flight = line.rstrip().split(' ')
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
choice=[]
visited=[dep_zone]

flight_list_iter = flight_list.copy()
next_list = flight_list_iter.copy()
to_delete =[]

for i in range(1,size):
    j=0
    for flight in flight_list_iter:
        if flight[4] in visited:
            to_delete.append(j)
        else:
            if flight[0] == current_airport and flight[2] in ('0',str(i)):
                choice = [flight[0],flight[1],flight[2],flight[3]]
                choice[2] = i
                itinerary.append(choice)
                current_airport = flight[1]
                visited.append(flight[4])
                break
        j = j+1      
    price = price + int(choice[3])
    for k in sorted(to_delete, reverse=True): 
        del next_list[k]
        to_delete =[]
    flight_list_iter = next_list.copy()


for flight in flight_list:
    if flight[0] == current_airport and apt_to_zone(flight[1], zones) == dep_zone and flight[2] in ('0',str(size)):
        choice = [flight[0],flight[1],flight[2],flight[3]]
        choice[2] = size
        itinerary.append(choice)
        break
price = price + int(choice[3])

itinerary[0] = price
print(itinerary[0])
for i in range(1,size+1):
    print(str(itinerary[i][0])+" "+str(itinerary[i][1])+" "+str(itinerary[i][2])+" "+str(itinerary[i][3]))

if dev:
    end = time.time()
    print(end - start)