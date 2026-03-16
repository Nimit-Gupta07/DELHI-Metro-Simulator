# DATA EXTRACTION**************************************************
with open ("metro_data.txt","r") as f:
    lines=list(f.readlines())
lines_list=[[],[],[],[]]
time_list=[[],[],[],[]]
stations_list=[[],[],[],[]]
counter=0# counting when does metro line change in the list named "lines"
for i in lines:
    
    if i.count(",")==3: # made a unique way to pick out the just the metro stations from the list
        i=i.strip().split(",")
        list_with_good_values=[]
        for j in i:# visiting each element in the list i
            list_with_good_values.append(j.strip())
        

        time=int(list_with_good_values[2])#taking time from the list
        list_with_good_values[1]=list_with_good_values[1].casefold()
        station=list_with_good_values[1]#taking stations from the list
        
        lines_list[counter].append(list_with_good_values)#adding value to respective lists
        stations_list[counter].append(station)
        time_list[counter].append(time)
    elif i.count(",")==0:# when the metro line changes I have put no comma in text file in that line
        counter+=1
reversed_station_list=[i[::-1] for i in stations_list]
reversed_time_list=[i[::-1][1:]+[0] for i in time_list]
all_station_list=[j for i in stations_list for j in i]


# arranging and numbering metro line

num_line_internal={"blue1":0,"blue2":1,"magenta":2,"pink":3}#for internal calc
existing_lines=["blue1","blue2","magenta","pink"]# blue1 blue2 as diff line

# getting interchanges

dict_line_station_list={existing_lines[i]:stations_list[i] for i in range(4)}

interchanges={}
interchange_station=[]
for line in lines_list:
    for i in line:
        if len(i[3])>2:#ie something longer than "no" is written there that is yes|interchange line 
            if i[1] not in interchange_station:
                interchange_station.append(i[1])
                interchanges[i[1]]=(i[0],i[3][4:])

#****************************************************************
#ADVANCED STATION MATCHING (developing a function to give user closest match to his station if he misspells)
def name_checker(station):
    re_ask=False

    if station in all_station_list:
        return re_ask # if re ask is false we move ahead and take his position on the line
    
    possible_station=[]
    re_ask=True
    station_space_free="".join(station.split())
    for correct_station_name in all_station_list:
        match_score=0   
        correct_station_name_space_free="".join(correct_station_name.split())#the space free correct station name

        # matching letter in forward direction
        for idx,letter in enumerate(station_space_free[0:min(len(correct_station_name_space_free),len(station_space_free))]):#checking just on basis of letters and preventing index errors
                if letter==correct_station_name_space_free[idx]:
                    match_score+=1
        match_ratio=match_score/len(station_space_free) 

        # using reverse match score beacuse if a person makes mistake in the starting it gets caught as well
        reverse_match_score=0
        reversed_Station_space_free="".join(station[::-1].split())
        for idx,letter in enumerate(reversed_Station_space_free[0:min(len(correct_station_name_space_free),len(station_space_free))],start=1):#checking just on basis of letters in reversed state
                if letter==correct_station_name_space_free[-idx]:
                    reverse_match_score+=1
        reverse_match_ratio=reverse_match_score/len(reversed_Station_space_free)  

        #a thershold of 0.6 and 0.5 similarity is used        
        if match_ratio>=0.5 or reverse_match_ratio>0.6:
            possible_station.append((correct_station_name,max(match_ratio,reverse_match_ratio)))
    if len(possible_station)>0:
        print("did you mean")
        possible_station=list(set(possible_station))#avoiding duplicates
        possible_station.sort(key= lambda x:x[1],reverse=True)# showing best result first
        for i in range(min(4,len(possible_station))) : # showing not more than 4 stations 
            print(possible_station[i][0])
        return re_ask
    else :
        print("not found")
        return re_ask
   
# METRO TIMING MODULE*******************************************
def metro_timing_module(line,station,time,stations_list,time_list):
    # for blue line we have made 2 lines dwarka to noida and dwarka to vaishali 
    #we keep metros at 20 min gap on the metro station at 6 in the morning so nobody gets late
   
    # we calculate user's position on the line in terms of time
    line_number=num_line_internal[line]
    time_from_beginning_of_user_on_line= sum(time_list[line_number][0:(stations_list[line_number].index(station))])
    hour=int(time[0:2])
    minutes=int(time[3:5]) 
    total_minutes_elapsed=hour*60+minutes

    hour_frequency={range(6,8):(4,8,20),range(8,10):(8,4,8),range(10,17):(4,8,4),range(17,19):(8,4,8),range(19,23):(0,8,4)}

    def metro_sub_module(hour1,hour2,frequency1,frequency2,frequency3,total_minutes_elapsed):
        # transition from frequency3 to 2 to 1 between before hour1 mid hour1 and hour2 and after hour 2

            time_after_frequency_switch=total_minutes_elapsed-hour1*60
            #time_after_frequency_switch , this is nothing but total time after the last frequency shift

            if (time_after_frequency_switch)>=time_from_beginning_of_user_on_line:# in this case frequency3 metro do not effact the use 
                minutes_diff=frequency2-(time_after_frequency_switch-time_from_beginning_of_user_on_line)%frequency2

                if minutes_diff==frequency2:
                    minutes_diff=0
                # doing so because if minutes diff=frequesncy2 then it is perfect sync
    
                metro_arrival=[]
                counter=3# we need to report 3 times only but we need to check for frequency change

            #IMP IMP #this is a uniques way of assuming that every metro's experiences time on basis of their posn from the start hence time
                #ellapse for them differently
                while time_after_frequency_switch-time_from_beginning_of_user_on_line<=(hour2-hour1)*60 and counter>0:
                    counter-=1
                    
                    metro_arrival.append(minutes_diff+time_after_frequency_switch)
                    total_minutes_elapsed+=frequency2 # a frequency 2 metro passes
                    time_after_frequency_switch=total_minutes_elapsed-hour1*60

                
                # adding frequency1 minutes metro if result is less
                while len(metro_arrival)<3:
                    metro_arrival.append(metro_arrival[-1]+frequency1)
            
            elif (time_after_frequency_switch)<time_from_beginning_of_user_on_line:# in this case frequency3 metro effact the user

                incoming_frequency3_metros=(((time_from_beginning_of_user_on_line)-(time_after_frequency_switch))//frequency3)

                time_for_next_metro=((time_from_beginning_of_user_on_line)-(time_after_frequency_switch))%frequency3

                metro_arrival=[time_after_frequency_switch+time_for_next_metro]
                
                while incoming_frequency3_metros>0 and len(metro_arrival)<3:
                        metro_arrival.append(metro_arrival[-1]+frequency3)
                        incoming_frequency3_metros-=1
                while len (metro_arrival)<3:
                    metro_arrival.append(metro_arrival[-1]+frequency2)
            return metro_arrival
            
    #end of sub module*************************
            
#finally presenting answer in a readable way that can be used further as well
    def time_converter(starting_hour,time):#converts time into required output
        return f"{((starting_hour*60+time)//60):02d}:{((time)%60):02d}"

#handling after 11 cases
    if hour>=23:
        if time_from_beginning_of_user_on_line>total_minutes_elapsed-23*60:
                final_timing_list=metro_sub_module(19,23,0,8,4,total_minutes_elapsed)
                x=final_timing_list[0]
                a,b,c=time_converter(19,x),time_converter(19,x+8),time_converter(19,x+16)

                if len(final_timing_list)==len(set(final_timing_list)) :# if time doesn't repeat we want this
                    final_list=[a,b,c]
                    final_output=f"next metro at {a}\nsubsequent metro at {b}, {c}"
                else :#subsequesntly according to our need we do them
                    if final_timing_list[0]==final_timing_list[1] :
                        final_list=[a,"nil","nil"]
                        final_output=f"next metro at {a}\nend of service"
                    elif final_timing_list[1]==final_timing_list[2]:
                        final_list=[a,b,"nil"]
                        final_output=f"next metro at {a}\nsubsequent metro at {b}, end of service"
               
                return final_output,final_list 
                       
        else:
            return "no metro service available", ["24:00","24:00","24:00"],
#handling normal cases
    else:
        for hour_range,freq in hour_frequency.items():

            if hour in hour_range:
                hour1,hour2=hour_range[0],hour_range[-1]
                final_timing_list=(metro_sub_module(hour1,hour2+1,freq[0],freq[1],freq[2],total_minutes_elapsed))
        final_list=[]
        
        for i in final_timing_list:
            final_list.append(time_converter(hour1,i))
        if len(final_list)==len(set(final_list)):
            final_output=f"next metro at {final_list[0]}\nsubsequent metros at {final_list[1]}, {final_list[2]}"
        elif len(final_list)==len(set(final_list))-1:
            final_output=f"next metro at {final_list[0]}\nsubsequent metros at {final_list[1]}, end of service"#considering if service ends on one side
        else:
            final_output = f"next metro at {final_list[0]}\nend of service"
        
        return final_output,final_list

# ****************************************************************
#JOURNEY PLANNER
# now we are making 2 lines blue1(noida to dwarka) and blue2 (vaishali to dwarka)

def journey_planner(initial_station,final_station,user_arrival_time):
    interchange_time=3
    train_speed=40 #taking a train speed of 40 kmph on all three lines for fare canculation since fare is calculated on the basis
    #of shortest distance between final and initial point and distance is not available any where on google or on the app
    def possible_path_calculator(initial_station,final_station):
        possible_paths=[] 
        
        def same_line_checker(station1,station2):
            for i in stations_list :
                if station1 in i and station2 in i:
                    return True
            return False

        def all_possible_connections(station1,station2):# all possible connection between stations on 1 line 
            l1=[]
            if same_line_checker(station1,station2) :
                for line,stations in dict_line_station_list.items():
                    if station2 in stations and station1 in stations:
                        l1.append(line)
            return l1
        
        #zero interchange paths       
        if same_line_checker(initial_station,final_station):
            l1=all_possible_connections(initial_station,final_station)
            for line in l1:
                possible_paths.append(((line,initial_station,final_station),))

        #1 interchange path
        for interchange_station,line_combo in interchanges.items():
            l1=all_possible_connections(initial_station,interchange_station)# checking all possibilities of connection between intial and interchange
            l2=all_possible_connections(interchange_station ,final_station)#checking all possibilities of connection between interchange and final
            if l1 and l2:
                for line1 in l1:
                    for line2 in l2:
                        if len(set([interchange_station,initial_station,final_station]))==3:
                            #although we compute all the useless loops costing time but we never store them saving memory
                            possible_paths.append(((line1,initial_station,interchange_station),(line2,interchange_station,final_station)))# we append all permutation possible

        #2 interchange path
        for interchange_station1,line_combo in interchanges.items():

            for interchange_station2,line_combo in interchanges.items():
                l1=all_possible_connections(initial_station,interchange_station1)  #saving computation even if one of them fails we exit
                if not l1:
                        continue
                
                l2=all_possible_connections(interchange_station1,interchange_station2)#saving computation even if one of them fail
                if not l2:
                        continue
                
                l3=all_possible_connections(interchange_station2,final_station)
                if not l3:
                        continue
                
                for line1 in l1:#we loop in lists to create every possible way with 1,2,0 interchange to reach point desitination 
                    for line2 in l2:
                        for line3 in l3:
                            if len(set([interchange_station1,initial_station,final_station,interchange_station2]))==4:
                            #although we compute all the useless loops costing time but we never store them saving memory
                                possible_paths.append(((line1,initial_station,interchange_station1),(line2,interchange_station1,interchange_station2),(line3,interchange_station2,final_station)))
        return possible_paths
    #end of path calculator***************************

    possible_paths=possible_path_calculator(initial_station,final_station)

    
#in the next few functions we jumble up with different values and all the work we have done till now to finally fetch some useful data       
    def helper(line_number,initial_station,stations_list,time_list,time_diff,user_arrival_time,interchange_time):
                  
            final_output,final_list=metro_timing_module(existing_lines[line_number],initial_station,user_arrival_time,stations_list,time_list )
            #checking_for_nil
            first_arrival=final_list[0]
            first_two_elem=first_arrival[0:2]#"23" in "23:10", or "ni" in "nil", as the function calculates many possibilities this prevents us from running into any sort of error
            if not first_two_elem.isdigit():
                return first_arrival,user_arrival_time,10**9# we set wait time too high so which taking min this gets eliminated
            
            hour=int(final_list[0][0:2])
            minutes=int(final_list[0][3:5])
            
            arrival_time_hours=int(user_arrival_time[0:2])
            arrival_time_minutes=int(user_arrival_time[3:5])

            # we fetch the wait time
            wait_time =(hour*60 +minutes)-(arrival_time_hours*60+arrival_time_minutes)

            final_time=f"{(hour*60+minutes+time_diff+interchange_time)//60:02d}:{(hour*60+minutes+time_diff+interchange_time)%60:02d}"#we calculate final time 
            return final_list[0],final_time,wait_time

   
#we have too many interchanges manually taking into account all of them is tedios hence we take canstant interchange time 
    def travel_on_1line(user_arrival_time,line_number,initial_station,final_station,interchange_time):

            posn1=stations_list[line_number].index(initial_station)#numeric posn of user on his line 
            posn2=stations_list[line_number].index(final_station)#numeric posn of destination on the line 
             
            if posn2>=posn1:
                time_diff=sum(time_list[line_number][posn1:posn2])#we check in the order stored in our txt file
                metro_arrival,final_time,wait_time=helper (line_number,initial_station,stations_list,time_list,time_diff,user_arrival_time,interchange_time)
                
                return metro_arrival,final_time,time_diff+wait_time+interchange_time,initial_station,final_station,stations_list[line_number][-1],existing_lines[line_number],time_diff#now we retrun next metro arrival,final time ,time elaplsed after metro move

            else:
                time_diff=sum(time_list[line_number][posn2:posn1]) #now we check if the reverse is true
                metro_arrival,final_time,wait_time = helper(line_number, initial_station, reversed_station_list, reversed_time_list, time_diff, user_arrival_time,interchange_time)
                return metro_arrival, final_time, time_diff+wait_time+interchange_time,initial_station,final_station,reversed_station_list[line_number][-1],existing_lines[line_number],time_diff
    final_list=[]
    time_list_of_path=[]
    for path in possible_paths:
        path_info_list=[]
        total_time=0
        path_info_list=[list(travel_on_1line(user_arrival_time,num_line_internal[path[0][0]],initial_station,path[0][2],interchange_time))]# adding first element manually rest of them non manually,
        total_time+=path_info_list[0][2]

        for i in range(1,len(path)):
            if i==len(path)-1:
                path_info_list.append(list(travel_on_1line(path_info_list[i-1][1],num_line_internal[path[i][0]],path[i][1],path[i][2],0)))#interchange time for last station needs to be 0,we take final time from previous item

            else:
                path_info_list.append(list(travel_on_1line(path_info_list[i-1][1],num_line_internal[path[i][0]],path[i][1],path[i][2],interchange_time)))#this time interchange time can be equal to 3
            total_time+=path_info_list[i][2]
        final_list.append(path_info_list)
        time_list_of_path.append(total_time)
    
    time_path_list=list(zip(final_list,time_list_of_path))
    required_result=min(time_path_list,key= lambda x:x[1])# fetching the minimum time path
    
    #synthesising desired output format
    info,min_time=required_result# info is the new min time path
    final_time=info[-1][1]
    hour=int(final_time[0:2])
    if hour>22:
        return "No service available"#we define a breaking condition no service after 11 as said in the
    
    #fetching the intital station before we change the list
    initial_line=info[0][6]
    if initial_line=="blue1" or initial_line=="blue2":
        initial_line="blue"
    
    # we now replace stations with interchange instruction
    for idx,journey in enumerate(info,start=-1):#to avoid last and use first I set enumerate to -1 and take +2 element of info
        if  idx ==len(info)-2:#to avoiding the last element we check everytime
            break
        if journey[4]=="yamuna bank":
            # if we see yamuna bank as an element we need to take some extra steps 
            
            next_line=info[idx+2][6]#this gives us the next element in info beacuse index starts from -1
            if next_line=="blue2":
                journey[6] = "change at yamuna bank towards vaishali"#taking blue2 line 
            elif next_line == "blue1":
                journey[6] = "change at yamuna bank towards noida electronic city"
            else:
                journey[6]=f"change at yamuna bank towards {info[idx+1][5]}"#this will never run as we have only 2 stations at yamuna bank but just keeping it anyways 
        
        elif "blue1" in info[idx+2] or "blue2" in info[idx+2] :
            journey[6]=f"transfer to blue line towards {info[idx+2][5]}"
        else :
            journey[6]=f"transfer to {info[idx+2][6] } line towards {info[idx+2][5]}"
        
    def time_subtractor(smaller_time,time):# in the above functions when we calculate reaching time we actually calculate time to the next station
        # +interchange_time ,but we need to report the time at which user reaches the station not the total time 
        hour=int(time[0:2])
        minutes=int(time[3:5])
        if minutes-smaller_time<0:
            return f"{(hour-1):02d}:{(60-smaller_time):02d}"
        
        return f"{(hour):02d}:{(minutes-smaller_time):02d}"
    # at last we calculate total fare
    run_time=0#wecalculate total dist travelled by runtime of metro
    
    for i in info:
        run_time+=i[-1]
#official data
    def fare_calculator():
        travel_dist=int((run_time/60)*train_speed)
        fare_dist_dict={
            range(0,2):11,
            range(2,5):21,
            range(5,12):32,
            range(12,21):43,
            range(21,32):54,
            range(32,10000):64# if answer is big
        }
        for dist_range in fare_dist_dict:
            if travel_dist in dist_range:
                return fare_dist_dict[dist_range]
         
    
    
    #next 2 lines are important to understand how we present the data
    #format of info list is like metro arrival time, metro reaching+interchange time, starting,station, final station
    #last station on the line , transfer instructions and at last time diff(not used here)


    final_output=f"\nstart at {initial_station} ({initial_line}) "
    for i in info:# over here we start adding up the final segments into the required answer
        if i==info[-1]:#if i is the last element
            hour=int(user_arrival_time[0:2])
            fare=fare_calculator()
            if 8<=hour<10 or 17<=hour<19:
                final_output+=f'''\nnext metro at {i[0]} towards {i[5]}\narrive at {i[4]} at {i[1]}\ntotal time is {min_time} minutes
                \nyour total fare is {fare} rupees\nif you use smart card you get peak time discount of 20% and fare is {fare*0.8:.02f} rupees'''
            else:
                final_output+=f'''\nnext metro at {i[0]} towards {i[5]}\narrive at {i[4]} at {i[1]}\ntotal time is {min_time} minutes
                \nyour total fare is {fare} rupees\nif you use smart card you get off peak time discount of 10% and fare is {fare*0.9:.02f} rupees'''
            return final_output
        else:
            final_output=final_output+f"\nnext metro at {i[0]} towards {i[5]}\narrive at {i[4]} at {time_subtractor(interchange_time,i[1])}\n{i[6]}\n"

    

#*****************************************************************
#I have design a function to take station as input as this task was repeated in metro timing module and journey planner
def station_input(command):
    station=input(command).strip().casefold()
    permission=True #this is a permission to continue
    reask=False
    while True:
        reask=name_checker(station)
        if reask==True:
            station=input("enter your station or enter press 1 to exit: ").casefold().strip()
        if station=="1":
            permission=False
            break
        elif reask==False:
            break
    return station,permission

# I have designed a function to take time input
def time_input(num):
    time=input("enter time in HH:MM 24 hour format or 1 to exit: ").strip()
    permission=True
    while True:
        if time=="1":
            permission=False
            break
        try:
            int(time[0:2])
            assert 6<=int(time[0:2])<=23 
            assert 0<=int(time[3:5])<=60
            if int(time[0:2])==23 :
                if int(time[3:5])>30:
                    1/0
            break
        except :
            if num==1:#we use same function for both test case 1 and 2 but need different output
                print(f"Timing should be between 6 and 23:30 and in correct format")
            elif num==2:
                print(f"Timing should be between 6 and 23:00 and in correct format")
        time=input("enter time in HH:MM 24 hour format or 1 to exit: ")
    return time,permission
#USER INTERACTION 

print("\n"+"*"*5+" (●'◡'●) Hi and Welcome To Delhi Metro Route and Schedule Simulator"+"*"*5+"\n")
try:
    user_input_1=int(input("Select from the following options \n\nMetro Timing Module     Press 1\nRide Journey Planner    Press 2\n"))
    match user_input_1:
            case 1:
                line=input("enter your line: ").strip().casefold()
                while True: 
                    
                    if line not in ["blue","pink","magenta"]:
                        line=input("available lines are blue, pink and magenta enter line or 1 to exit: ").strip().casefold()
                        if line=="1":
                            break
                    else:
                        break
                if line!="1": #user didn't oppt out
                    
                    initial_station,permission= station_input("enter your station: ")
                    if permission:#user didn't oppt out
                        try:
                            
                            time,permission=time_input(1)# last check at 30
                            if permission:
                                if line=="blue" and initial_station in stations_list[0]:
                                    line="blue1"
                                if line=="blue" and initial_station in stations_list[1]:
                                    line="blue2"
                            line_number=num_line_internal[line]             
                            if initial_station!=stations_list[line_number][-1]:
                                final_output,final_list=metro_timing_module(line,initial_station,time,stations_list,time_list)
                                
                                print("\n"+final_output, f"towards {stations_list[line_number][-1]}")
                            
                            if initial_station!=reversed_station_list[line_number][-1]:

                                final_output,final_list=metro_timing_module(line,initial_station,time,reversed_station_list,reversed_time_list)
                                print("\n"+final_output, f"towards {reversed_station_list[line_number][-1]}")
                                # now reversing the lines
                        except:
                                if time!="1":# we do not want this to printed every time user exits
                                    print("the station doesn't lie on the line")        
                            
         
            case 2:
                initial_station,permission=station_input("enter source station: ")
                if permission:
                    final_station,permission=station_input("enter destination station: ")
                    if permission:
                        time,permission=time_input(2)
                        if permission:
                            if initial_station==final_station:
                                print("station need to be different")
                            else:
                                print(journey_planner(initial_station,final_station,time))    
            case _:
                print("invalid input")
except:
    print("invalid input")# mostly when journey time reaches out of servicable time


