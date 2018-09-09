# -*- coding: utf-8 -*-


import sys
import pandas                      #Pandas to read csv file and process dataframe
import json                        #Work with the json file
import urllib.parse
import urllib.request
import time
import tkinter as tk
from tkinter import messagebox     #Messages and yes no questions
from tkinter import filedialog
import os


timeUnit=0.5                          #time unit to alow time between API requests  
application_window = tk.Tk()        #tkinter object
application_window.withdraw()
#Loop to repeat the map process.
while True: 
    # This is a tuple of the allowed files. In this case only .csv
    my_filetypes = [('csv files', '.csv')]
    
    # Ask the user to select a single file name.
    route = filedialog.askopenfilename(parent=application_window,
                                        initialdir=os.getcwd(),
                                        title="Seleccionar archivo:",
                                        filetypes=my_filetypes)
    
    name = os.path.basename(route) 
    ## function to get the gps coordinates and google address
    
    def getGPS(route):
                               #name of the fileMm
        keyAPI = ''     #API KEY??????????????????????????????????????????????????????????????????????????????????????
        #Panda read the .csv file.
        df = pandas.read_csv(route, sep=';')
        #iterate in on the dataframe
       
        for index  in df.index:
            #parse the information and clean with no spaces and add +
            try:
                street = df.at[index,'street']
                municipality = df.at[index,'municipality']
                region = df.at[index,'region']
                
                if isinstance(street, str) and isinstance(municipality, str) and isinstance(region, str):
                    try:
                       street =urllib.parse.quote_plus(street)
                       municipality = urllib.parse.quote_plus(municipality)
                       region = urllib.parse.quote_plus(region)
                    except KeyError:
                       messagebox.showinfo('Error','Please confirm the correct name of the columns\n'+
                           'Column names should be:street; municipality; region')
                       sys.exit(1)
                       #create the address to be search
                    addressNow= street+','+municipality+','+region
                    #get the response from google's Map API and load into a json file
                    urlgps = 'https://maps.googleapis.com/maps/api/geocode/json?address='+addressNow+'&key='+keyAPI
                    u=urllib.request.urlopen(urlgps)
                    X = u.read().decode()
                    data = json.loads(X)
                    
                      
                       #get the information needed from the json file
                    df.loc[index, 'lat'] = data['results'][0]['geometry']['location']['lat']
                    df.loc[index, 'lng'] = data['results'][0]['geometry']['location']['lng']
                    df.loc[index, 'direcGoogle'] = data['results'][0]['formatted_address']
                    time.sleep(timeUnit)
                    
                else:
                    
                    df.loc[index, 'lat'] = ''
                    df.loc[index, 'lng'] = ''
                    df.loc[index, 'newAddress'] = ''
            
                if index == 250:
                    df.to_csv('Respaldo250_'+name, sep=';') 
                if index == 500:
                    df.to_csv('Respaldo500_'+name, sep=';') 
                if index == 1000:
                    df.to_csv('Respaldo1000_'+name, sep=';')   
                print(index) 
            except:
                df.to_csv(+'Error_'+index+name, sep=';')
                  
        return(df,index)
           
    #run the getGPS function
   
    df, index = getGPS(route)       
     
    
       
    #save to a new .csv file
    df.to_csv('Coordinates_'+name, sep=';')   
    #prompt the user if the map is needed.
    messagebox.showinfo('Information',' The new file Coordinates_'+name+
                                     ' is ready')
    
  
    repeatNow = messagebox.askokcancel('Question','Do you want to process another list?')
    #In case the person does not to process a new list the program ends.
    if repeatNow == False:
        messagebox.showinfo('Information','Ok, program finished')
        break
#Close the tkinter window
application_window.destroy()    
   
        