import os 
import json 
import pandas as pd 
import difflib
import subprocess 
import camelot
username = str(subprocess.check_output("uname -a",shell=True)) # Get the the username of the computer reading from the client computer 
Getusername = username.split("-")[0].split(" ")[1]  #Get the username
EXTRACT  = "/home/"+str(Getusername)+"/Automaticsoftware/tempolarydocextract" #Tempolary read the file extraction from the pdf specification function
PATHMAIN = "/home/"+str(Getusername)+"/Automaticsoftware/ComponentDoc"   # Getting the document page 
CONFIG   = "/home/"+str(Getusername)+"/Automaticsoftware/Configuresearch" # Config file
listdir_data = os.listdir(EXTRACT)
print(listdir_data)
listConfig = os.listdir(CONFIG)
cluster_class = {} 
def Configure(configfile): 
     try: 
       data = open(CONFIG+"/"+str(configfile),'r') #Open the configuretion file for the path 
       datas = data.readline()
       transfer = json.loads(datas)
       return transfer
     except:
        print("Not found the configure file please check again")
def max_index_cal(dictdatakeys,dictdatavav):
         cal_max = list(dictdatavav)
         keys_cal_max = list(dictdatakeys)
         max_index = max(cal_max)
         print(max_index,'Choosing',keys_cal_max[cal_max.index(max_index)])
         return max_index,keys_cal_max[cal_max.index(max_index)] 
def Matchingdata_cal(checkpackage,listheader): 
                percent=difflib.SequenceMatcher(None,checkpackage,listheader)
                #print("Match found:"+str(percent.ratio()*100)+"%") #Getting the percent matching 
                prob = percent.ratio()*100 # Calculate the percentage inside the list to find the max value in possibility detection 
                return  prob
configdata = Configure(listConfig[0])
Pinstable = configdata.get("Specific_pins").get("Pins_header") 
for sub_data in range(0,len(listdir_data)):
            list_subdata = os.listdir(EXTRACT+"/"+listdir_data[sub_data]) 
            #print(list_subdata)
            #Classified detected dataset of the pins table from the list of the dataframe 
            for w in range(0,len(list_subdata)):
                           #print(list_subdata[w])
                           if len(list_subdata[w].split(".")) >1:
                               # print(listdir_data[sub_data],list_subdata[w],list_subdata[w].split(".")[1])
                               if list_subdata[w].split(".")[1] == 'csv':
                                   df = pd.read_csv(EXTRACT+"/"+listdir_data[sub_data]+"/"+list_subdata[w].split(".")[0]+".csv")
                                   percent = Matchingdata_cal(Pinstable,df.columns)
                                   if percent >=40 and percent < 100:
                                      #print("Matching percentage ",percent)
                                      print(listdir_data[sub_data],df.values.tolist()[0],list_subdata[w])
                                      cluster_class[listdir_data[sub_data]]  = df.values.tolist()[0]
print(cluster_class)
for r in list(cluster_class): 
        print(r,cluster_class.get(r))          
