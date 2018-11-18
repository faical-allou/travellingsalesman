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


input_list = ['input_small.txt', 'input_medium.txt', 'input_large.txt', 'input_xlarge.txt']
for one_off_it in range(0,3):
    for deal_weight_it in range(0,3):
        for over_weight_it in range(0,3): 
            for recom_weight_it in range(0,3):
                for rerun_divider in range(1,4): 
                    for text_input in input_list:
                        start = time.time()
                        one_off_steps = one_off_it
                        deal_weight = 0.5*deal_weight_it
                        over_weight = 0.5*over_weight_it
                        recom_weight = recom_weight_it
                        #---------------------------- read data ---------------------------------------------------#
                        zones = {}
                        zones_name = []
                        flights_from_apt = {}
                        zone_prices_to = {}

                        if dev:
                            #when ran locally
                            file = open(text_input, mode = 'r')
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
                                #measure('before flights input')
                                while line is not None:
                                    flight = next(file).split(' ')                                                       
                                    flight.extend([zones[flight[0]],zones[flight[1]]])      
                                    flights_from_apt.setdefault(flight[0],{})    \
                                                    .setdefault(flight[2],[])   \
                                                    .append(flight)
                                    zone_prices_to.setdefault(flight[5],{}).setdefault(flight[2],[]).append(flight[3])    
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
                                    zone_prices_to.setdefault(flight[5],{}).setdefault(flight[2],[]).append(flight[3])    
                            except EOFError:
                                pass

                        #---------------------------- end of read data ---------------------------------------------------#

                    
                        #--------------------hyper parameters------------------
                        #one_off_steps = 1
                        #deal_weight = 1
                        #over_weight = 0.5
                        #recom_weight = 3


                        #---------------------------------------------------------------------------------------
                        #measure('end of read')
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

                        time_to_solve = 2*time_limit

                        sum_prices = 0

                        first_time = True

                        ######### preprocessing the flight data

                        zone_prices_to_avg = defaultdict()
                        zone_prices_to_avg_day = defaultdict(dict)
                        zones_prices_trend = defaultdict()

                        #####--- avg price to go to a zone is compared to price available each day to know if you're getting a good deal
                        #####-- avg pice is also compared to the best itinerary to check if you overpaid at the end and prioritize
                        for key_to in zone_prices_to:
                            for day_ops, value in zone_prices_to[key_to].iteritems():
                                list_prices = map(float, value)
                                zone_prices_to_avg_day[key_to][int(day_ops)] = sum(list_prices) / len(list_prices)

                        for key_to, value in zone_prices_to_avg_day.iteritems():
                            zone_prices_to_avg[key_to] = sum(v for v in value.itervalues()) / len(value)

                        #####--- the trend is used to check if you should wait
                        for key_to, value in zone_prices_to_avg_day.iteritems():
                            keys = np.fromiter(value.iterkeys(), dtype=float)
                            vals = np.fromiter(value.itervalues(), dtype=float)
                            A = np.polyfit(keys, vals, 1)
                            zones_prices_trend[key_to] = A[0]

                        #measure('end of preprocess')

                        ################ Start of the "Greed"

                        while (time.time()-start) < time_to_solve : #----------while you still have time
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
                                        price_recom = []


                                        for choix in choices: 
                                            deals.extend( [int(choix[3]) - zone_prices_to_avg.setdefault(choix[5],0) ]  )
                                            overpaid_later.extend([overpaid.setdefault(choix[5],0)])
                                            price_recom.extend([zones_prices_trend.setdefault(choix[5],0) ])
                                        overpaid_later = np.array(overpaid_later) 
                                        deals = np.array(deals)
                                        price_recom = np.array(price_recom)

                                        # using (1-day/size) because probability of finding cheaper goes down
                                        # deals is checking if the price I see is good compared to average
                                        # overpaid_later checks if the price goes up later if I stay "greedy" today
                                        rank = choices[:,3].astype('float') + \
                                                deals*deal_weight - overpaid_later*over_weight + \
                                                - price_recom*recom_weight
                                                
                                        choices = choices[rank.argsort()]
                                        choice = choices[min(random.randint(one_off,one_off*10),len(choices)-1)]
                                        one_off = max(0,one_off-1)                        # make sure we "tilt" only once per rerun                                   

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
                                        if tries > size/rerun_divider: break
                                
                                #------------------final flight back to departing zone
                                if tries > size/rerun_divider : break
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

                                for itin in winner: # -- check how much I overpaid
                                    overpaid[itin[5]] = int(itin[3]) - zone_prices_to_avg[itin[5]]
                            else:
                                blacklist = blacklist_saved[:]

                            rerun = rerun+1
                            one_off = one_off_steps
                            
                            #------------- if you have time, go back to a random point and solve it differently
                            random_rewind = random.randint(1,size)
                            #if dev: print('new price: ', new_price, 'random rewind: ', random_rewind, 'time: '+str(round(time.time()-start,0)), len(itinerary))
                            itinerary = winner[:]
                            rollback(random_rewind, False)
                            
                            tries = tries + 1
                            
                        if (sum_prices == 0 or new_price < sum_prices) and len(itinerary) == size : 
                                winner = itinerary[:]
                                sum_prices = sum(int(line[3]) for line in itinerary) 
                            
                        sum_prices = sum(int(line[3]) for line in winner) 
                        #print(sum_prices)

                        #for i in range(0,size):
                        #    print(str(winner[i][0])+" "+str(winner[i][1])+" "+str(winner[i][2])+" "+str(winner[i][3].rstrip()))

                        if dev:
                            for row in winner:
                                row[3]= row[3].rstrip()
                            #measure('finished')
                            text = text_input+', final_price: '+ str(sum_prices)+', reruns: '+ str(rerun)+', parameters: '+str(one_off_steps)+" "+str(deal_weight)+" "+str(over_weight)+" "+str(recom_weight)+" "+str(rerun_divider)
                            
                            print(text)
                            #np.savetxt("./output/itinerary_"+str(time.time())+".csv", winner, delimiter=",", fmt='%s')
                            with open("test.csv", "a") as myfile:
                                myfile.write(text+"\n")