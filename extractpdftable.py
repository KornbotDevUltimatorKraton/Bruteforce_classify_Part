from inspect import getfullargspec
import os 
import json
from zipfile import Path 
import camelot 
import difflib 
import subprocess
import pandas as pd
import psycopg2 # postgres database 
from PyPDF2 import PdfFileWriter, PdfFileReader

username = str(subprocess.check_output("uname -a",shell=True)) # Get the the username of the computer reading from the client computer 
Getusername = username.split("-")[0].split(" ")[1]  #Get the username
HOME_PATH = "/home/"+str(Getusername)+"/Automaticsoftware/"
EXTRACT  = "/home/"+str(Getusername)+"/Automaticsoftware/tempolarydocextract" #Tempolary read the file extraction from the pdf specification function
PATHMAIN = "/home/"+str(Getusername)+"/Automaticsoftware/ComponentDoc"   # Getting the document page 
CONFIG   = "/home/"+str(Getusername)+"/Automaticsoftware/Configuresearch" # Config file
TI_product  = "/home/"+str(Getusername)+"/Automaticsoftware/TI_product"
NXP_product = "/home/"+str(Getusername)+"/Automaticsoftware/NXP_product"
ST_product = "/home/"+str(Getusername)+"/Automaticsoftware/ST_product"

TI_motor_drive  = "/home/"+str(Getusername)+"/Automaticsoftware/TIpro/TI_motordriver"
TI_bms  = "/home/"+str(Getusername)+"/Automaticsoftware/TIpro/TI_BMS"
TI_sensor  = "/home/"+str(Getusername)+"/Automaticsoftware/TIpro/TI_sensor"

NXP_interfaces = "/home/"+str(Getusername)+"/Automaticsoftware/NXPpro/NXP_interface"
NXP_multiplexer = "/home/"+str(Getusername)+"/Automaticsoftware/NXPpro/NXP_multiplexer"

ST_motordriver = "/home/"+str(Getusername)+"/Automaticsoftware/STpro/ST_motordriver"
ST_sensor =  "/home/"+str(Getusername)+"/Automaticsoftware/STpro/ST_sensor"
ST_microcontroller  =  "/home/"+str(Getusername)+"/Automaticsoftware/STpro/ST_mcus"

directcreate = ['tempolarydocextract','ComponentDoc','Configuresearch','TI_product','NXP_product','ST_product'] #list of the directory to create file
print("Create directory and give permission.....")
mode = 0o777
listdir_data = os.listdir(EXTRACT)
print(listdir_data)
listConfig = os.listdir(CONFIG)
cluster_class = {}
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 
PinsNamepack = []
PinsNumpack  = []
IONamepack = [] # Getting the io name pack 
Packagingdata = {} 
PackagewithIO = {} 
completepack = {} 
completeioname = {} 
check_datatype = {}
Check_Packagename = []  # Checking the list of the package name inside the list 
Generate_Pinspack = []
Generate_Numpack = [] 
Generate_iopack = [] 
completeNumpack = {} # Getting the new pins name append into the dictionary 
completePinspack = {} #Getting the complete pins pack data
check_pack_order = {}   
check_pins_table = {} #Getting the pins table inside the list 
Pack_data = {}

Pins_page_intersec = [] 
Pins_subpage_intersec = []
Order_page_internsec = []
Pins_Page_regroup  = {} 
Order_page_regroup = {} 
#Static parameters 
n = 1
n1 = 0
n2 = 2
n3 = 3

Classified_package = {'Multipackage':['NAME', 'NO.', 'nan', 'nan', 'nan'],'Singlepackage':['NAME', 'NO.', 'nan', 'nan']}
False_package_check = {'True':'Singlepackage','False':'Multiplepackage'} # Getting the True Single package data ad false multipackage
listConfig = os.listdir(CONFIG)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#Writing the json file into the cloud database 
#using the roboreactorpart database cloud   
DATABASE_URL = "postgres://deblnijnzpwins:0b338cb6d067f909fa72de09359f40e8a3089c76a216192a3ae1355c58d71f5e@ec2-3-229-127-203.compute-1.amazonaws.com:5432/d43p77fjhmtuf2"
Host = "ec2-3-229-127-203.compute-1.amazonaws.com"
Database = "d43p77fjhmtuf2"
Password = "0b338cb6d067f909fa72de09359f40e8a3089c76a216192a3ae1355c58d71f5e"
Port = "5432"

#Specific function to classify data of the clusterring
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
         try: 
           max_index = max(cal_max)
           print(max_index,'Choosing',keys_cal_max[cal_max.index(max_index)])
           return max_index,keys_cal_max[cal_max.index(max_index)] 

         except:
             pass
def Matchingdata_cal(checkpackage,listheader): 
                percent=difflib.SequenceMatcher(None,checkpackage,listheader)
                #print("Match found:"+str(percent.ratio()*100)+"%") #Getting the percent matching 
                prob = percent.ratio()*100 # Calculate the percentage inside the list to find the max value in possibility detection 
                return  prob

def Get_fullPinpage_cal(configdata,pathselec,inputcomp):
                       
                                  Orderableoackage = configdata.get("Orderablepackage").get("Orderable") #Getting the package data from the search intersection                  
                                  Pinstable = configdata.get("Specific_pins").get("Pins_header")
                                  print("Getting the file path ",pathselec+inputcomp)  # file path           
                                  
                                  df = pd.read_csv(pathselec+inputcomp+".csv") 
                                  print("Header files",df.columns)
                                  probpinsdata = Matchingdata_cal(Pinstable,df.columns) # checking the columns matching data of the pins table inside the list 
                                  print("Matching prob",probpinsdata) # Checking the matching prob of the pins datatable   
                                  if probpinsdata >=40 and probpinsdata <= 100: # Checking if the data pins correct 100 percent inside the list
                                                check_pins_table[inputcomp] = probpinsdata # Getting the data of the page to calculate the right page to extract all pins to concatinate data together
                                                #Checking the orderlist
                                                probdata = Matchingdata_cal(Orderableoackage,df.columns)  
                                                print("Matching prob ",probdata)
                                                check_pack_order[inputcomp] = probdata # Getting the data of the page to calculate the right page matching probability 
                                                

def Pageclassification_cal(): 

        pass 

for directr in range(0,len(directcreate)):
      try:
           os.mkdir(directcreate[directr],mode)
      except: 
          pass
for directr in directcreate:
          print("Give permission to directory =====> ",directr)
          os.system("echo 'Rkl3548123#' | sudo -S "+"sudo chmod -R 777 "+str(directr))  
list_path = ['TI_product','NXP_product','ST_product']
list_subpath = ['TI_motor_drive','TI_bms','TI_sensor','NXP_interfaces','NXP_multiplexer','ST_motordriver','ST_sensor','ST_microcontroller']
dict_manufacture = {'TI':'TI_product','NXP':'NXP_product','ST':'ST_product'}
dict_menudoct = {'TI_product':'TI_comdoc','NXP_product':'NXP_comdoc','ST_product':'ST_comdoc'} #component doct
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
#Select PATH here ]
#example 
Comp_directory =  list(dict_manufacture)[0]
PATH_SELECT = HOME_PATH+dict_manufacture.get(list(dict_manufacture)[0]) + "/"+ list_subpath[0]+"/"
print("Path selected for manufacturer ",PATH_SELECT)
PATH_SUBSELECT =  HOME_PATH+dict_manufacture.get(list(dict_manufacture)[0]) + "/" 
print("Path sub select for components generated ",PATH_SUBSELECT) # Getting the path sub select file 
getdoct = dict_manufacture.get(list(dict_manufacture)[0])
create_comdoc = PATH_SUBSELECT+dict_menudoct.get(getdoct)+"/"
print("Create component_doct ", create_comdoc)
config_data = Configure(listConfig[0])
try: 
     print("Creating .....===>",create_comdoc)
     os.mkdir(create_comdoc,mode)
except: 
    pass
for ret in range(0,len(list_path)): 
     try:
         os.mkdir(list_path[ret],mode)
     except: 
         pass

for ret in range(0,len(list_subpath)): 
    try:
       verify = list_subpath[ret].split("_")[0]
         
       os.mkdir(dict_manufacture.get(verify)+"/"+list_subpath[ret],mode)
       
    except: 
        pass
for directr in list_path:
          print("Give permission to directory =====> ",directr)
          os.system("echo 'Rkl3548123#' | sudo -S "+"sudo chmod -R 777 "+str(directr))        

#listdir_data = os.listdir(EXTRACT)
#print(listdir_data)
listConfig = os.listdir(CONFIG)
print(listConfig[0])
#list docfile 
list_pdfdoc = os.listdir(PATH_SELECT)
print("Check path document",list_pdfdoc) #Using the list of the doc on processing the data 
Orderableoackage = config_data.get("Orderablepackage").get("Orderable") #Getting the package data from the search intersection                  
print("Order config data ",Orderableoackage)
for et in range(0,len(list_pdfdoc)):
                            
         pdf_list = list_pdfdoc[et].split(".")
         pdf_class = list_pdfdoc[et].split(".")[1]
         list_check_com = os.listdir(create_comdoc)
         print("Check the list in",Comp_directory+" ",list_check_com)
         print("Document docfile",list_pdfdoc[et]) 
         if list_pdfdoc[et].split(".")[0] not in list_check_com:
            
            if pdf_class == 'pdf': 
                  print(list_pdfdoc[et].split(".")[0]) # Create the document 
                  component_path_csv = create_comdoc+pdf_list[0]
                  try: 
                      print("Create component_path ",create_comdoc+pdf_list[0])
                      os.mkdir(component_path_csv,mode)   # Create the directory name here
                    
                  except: 
                      pass
                  #Running the loop of the total pdf file classification function 
                  try:
                     input1 = PdfFileReader(open(PATH_SELECT+"/"+pdf_list[0]+".pdf", "rb"))  #using oslist dir readding the file and extract all the value in the loop 
                  except:
                     input1 = PdfFileReader(open(PATH_SELECT+"/"+pdf_list[0].split("/")[1]+".pdf", "rb"))
                  print(pdf_list[0]+".pdf has %d pages." % input1.getNumPages())  # Getting the total pins of th page component 
                  total_page = input1.getNumPages()
                  for pagess in range(0,total_page): 
                      tables = camelot.read_pdf(PATH_SELECT+"/"+str(list_pdfdoc[et].split(".")[0])+".pdf",pages=str(pagess)) # Getting the pdf doc
                      print(list_pdfdoc[et].split(".")[0],len(tables)) # Getting the pdf file name and len(tables)
                      
                      if len(tables) > 0: 
                          for table in range(0,len(tables)): 
                                 print("Tables "+list_pdfdoc[et].split(".")[0]+"_"+str(pagess)+"_"+str(len(tables))) # Getting the page of the file and number list 
                                 #Naming the file name of the data 
                                 file_extract_name = list_pdfdoc[et].split(".")[0]+"_"+str(pagess)+"_"+str(len(tables)) # Getting the file name 
                                 #Now clreate the directory to generate the file into the components directory 
                                 print("Check sub select ",component_path_csv+"/"+file_extract_name) # Getting the file extract
                                 print(tables[table].df)
                                 tables[table].to_csv(component_path_csv+"/"+file_extract_name+".csv")
                                 
                      #Checking if the file is already done created directory and complete extracted csv file 
                      # If all requirement are done then created the function for running the pins extraction here   
                      if pagess+1 == total_page: 
                                 print("End of data sheet beginning extraction process......",str(pagess)+" pages") 
                                 print("Preparing new process........")
                                 file_ext = open('listerase.py','r')
                                 datafile = file_ext.readlines()
                                 
                                 #clear_check = ['check_pins_table','check_pack_order']
                                 #for re in clear_check:
                                         #print("Clearing list ====> ",re.split("=")[0]) 
                                         #exec(str(re)+".clear()") 
                                 
                                 #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                                 #Doing the file extraction here 
                                 for table in range(0,len(tables)):
                                          try:
                                              Path_to_Expins = component_path_csv+"/" #+list_pdfdoc[et].split(".")[0]
                                              print("Extract Path",Path_to_Expins)
                                              list_expins = os.listdir(Path_to_Expins)
                                              #sorted_expins = sorted(list_expins,reverse=True) # reverse the list in the sort list to ordering the page data
                                              print("Sort list pages ",list_expins)
                                              for files_ex in range(0,len(list_expins)): 
                                                      print('Extract matching file data',list_expins[files_ex],list_expins[files_ex].split("_")[1]) 
                                                      Orderableoackage = config_data.get("Orderablepackage").get("Orderable") #Getting the package data from the search intersection                  
                                                      Pinstable = config_data.get("Specific_pins").get("Pins_header")
                                                      print("Getting the file path ",Path_to_Expins+list_expins[files_ex])  # file path           
                                                      df = pd.read_csv(Path_to_Expins+list_expins[files_ex].split(".")[0]+".csv")
                                                      print("Header",df.columns)
                                                      probpinsdata = Matchingdata_cal(Pinstable,df.columns) 
                                                      print("Matching probabilty: ",probpinsdata) 
                                                      if probpinsdata >=40 and probpinsdata <= 100: # Checking if the data pins correct 100 percent inside the list
                                                                   check_pins_table[list_expins[files_ex].split(".")[0]] = probpinsdata # Getting the data of the page to calculate the right page to extract all pins to concatinate data together
                                                                   #Checking the orderlist
                                                      probdata = Matchingdata_cal(Orderableoackage,df.columns)  
                                                      print("Matching prob ",probdata)
                                                      check_pack_order[list_expins[files_ex].split(".")[0]] = probdata # Getting the data of the page to calculate the right page matching probability 
                                                      #Get_fullPinpage_cal(config_data,Path_to_Expins,list_expins[files_ex]) # Getting the full pins page 
                                          except:
                                              pass
                                 #Pins page calculation percentage
                                 
                                 print("List Pins ",check_pins_table)
                                 print("List Order ",check_pack_order)
                                 #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
                                 '''     
                                 try:
                                    pins_keys = check_pins_table.keys() 
                                    pins_vavs = check_pack_order.values()           
                                    Pinspercentage,pinspage = max_index_cal(pins_keys,pins_vavs) #Getting the percentage pins page calculation
                                    print('Pins page ',pinspage,'Pins percentage ',Pinspercentage)
                                    print("Pins page data ",pins_keys)
                                    #Order page calculation percentage   
                                    order_keys = check_pack_order.keys() 
                                    order_vavs = check_pack_order.values() 
                                    Order_percentage,Order_page = max_index_cal(order_keys,order_vavs) # Getting the percantage order page and page calculation  
                                    print('Order page ',Order_percentage,'Order percentage ',Order_page) 
                                    
                                 except:
                                     pass
                                 '''  
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.
#Create the matching data after complete processing 

for r in range(0,len(check_pins_table)): 
                    #print("Checking the percentage of the data in array")
                    #print(list(check_pins_table)[r], check_datatype.get(list(check_pins_table)[r]))
                    matching_pins_percent = check_pins_table.get(list(check_pins_table)[r])
                    if matching_pins_percent > 40 and matching_pins_percent <= 100:
                                print("List pins percentage ",list(check_pins_table)[r].split("_")[0],list(check_pins_table)[r]) # Getting the pins percentage of the of the data extraction                              
                                Pins_Page_regroup[list(check_pins_table)[r] ] = list(check_pins_table)[r].split("_")[0]
                               
for k in range(0,len(check_pack_order)):
                    #print("Checking the percentage of the data in array")
                    #print(list(check_pack_order)[k], check_pack_order.get(list(check_pack_order)[k]))
                    matching_order_percent = check_pack_order.get(list(check_pack_order)[k])
                    if matching_order_percent > 40 and matching_order_percent <= 100: 
                                      print("List order percentage ",list(check_pack_order)[k].split("_")[0],list(check_pack_order)[k]) # Getting the package order percentage of the data extraction 
                                      Order_page_regroup[list(check_pack_order)[k] ] = list(check_pack_order)[k].split("_")[0]
print("Pins page regroup ", Pins_Page_regroup)
print("Order page regroup ", Order_page_regroup)  
# Processing the table classification to select the type of the table classifiation management system 
for pins in range(0,len(Pins_Page_regroup)):
        print("Getting the component name from the page input") 
        print("Componentname and Page",list(Pins_Page_regroup)[pins],Pins_Page_regroup.get(list(Pins_Page_regroup)[pins]))
        
