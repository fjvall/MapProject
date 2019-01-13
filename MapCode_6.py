# -*- coding: utf-8 -*-
"""
1- Seleccionar archivo_Ok
2- Seleccionar si quiere el mapa o no_Ok
3- Promedio del centro de los gps points._Ok
4- 
5- Try and catch
6- Limpiar código
7-
Created on Mon Aug 20 16:18:08 2018

@author: fjval
"""
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
    #message box using tkinter. Reminder to the user.
    messagebox.showinfo('Information','-Please remember to place the .csv data file'+ 
                        ' in the MapTheList folder first.\n'+
                        '-Also, the process may take some time depending on the quantity of addresses')

    # This is a tuple of the allowed files. In this case only .csv
    my_filetypes = [('csv files', '.csv')]
    
    # Ask the user to select a single file name.
    route = filedialog.askopenfilename(parent=application_window,
                                        initialdir=os.getcwd(),
                                        title="Please select a file:",
                                        filetypes=my_filetypes)
    
    name = os.path.basename(route) 
    ## function to get the gps coordinates and google address
    def getGPS(route):
                               #name of the fileMm
        keyAPI = 'XXXXXX'     #API key
        #Panda read the .csv file.
        df = pandas.read_csv(route, sep=',')
        #iterate in on the dataframe
        for index  in df.index:
            #parse the information and clean with no spaces and add +
            try:
               street =urllib.parse.quote_plus(df.at[index,'street'])
               municipality = urllib.parse.quote_plus(df.at[index,'municipality'])
               region = urllib.parse.quote_plus(df.at[index,'region'])
            except KeyError:
               messagebox.showinfo('Error','Please check the names of the columns in your file before running MapTheList again \n'+
                   'Column names should be: street; municipality; region')
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
            df.loc[index, 'newAddress'] = data['results'][0]['formatted_address']
            time.sleep(timeUnit)
        return(df,index)
           
    #run the getGPS function
    df, index = getGPS(route)       
     
     
    #get the mean of the latitude and longitude to center the map.
    df.loc[index, 'AverageLat']= df["lat"].mean()
    df.loc[index, 'AverageLng']= df["lng"].mean()
    #save to a new .csv file
    df.to_csv('GPS_Address.csv', sep=',')   
    #prompt the user if the map is needed.
    mapList = messagebox.askokcancel('Question','Do you want to map the list?'+ 
                                     '\n\n (Info: The New file GPS_Address contains'+
                                     ' the gps coordinates, is ready in the MapTheList folder)')
    
    #if the map is needed:
    if mapList == True:
    
        #import the webrowser
        
        import webbrowser
        #create hmtl file that will contain the map
        f = open('Map.html','w')
        
        message = """<html>
        <head></head>
        
        <style>
            /* Style of the map css code*/
            #map{
                height:550px;
                width:100%;
                }
       
        </style>
        
        <body>
          <p>
            <h1>Map The List</h1>
            <!--  div element that holds the map -->
            <div id="map"></div>   
            <script src='./src/js/jquery-2.1.4.js'></script>
            <script src="PapaParse-4.5.0/papaparse.min.js"></script>
            <script>
                
                // Parse the data and create the map and icons
                function initMap()
                {
               
                    //activates the process of generating each marker
                    parseData(createMap);
                    
                    // parse the data and use the createMap function
                    function parseData(creaMap) 
                    {     
                         Papa.parse("GPS_Address.csv", {
                         download: true,
                         complete: function(results){
                                   createMap(results.data);
                                                    }
                                                       }      
                                 );
                    }
            
                    
                    //Create the map and the icons
                    function createMap(data)  
                    {
                           
                           //get the center of the coordinates to be mapped 
                           var size = data.length
                           var x=Number(data[size-2][11]);
                           var y=Number(data[size-2][12]);
                            
                          
                            // Map options, zoom and centered
                            var options = {
                                    zoom:12,
                                    center:{lat:x,lng: y} 
                                          }
                            
                            //New map
                            var map = new google.maps.Map(document.getElementById('map'), options);
    
                            
                            //New infowindow to show the data of the coordinate
                            var infowindow = new google.maps.InfoWindow();
                            
                            
                            //generate each marker and icon.
                            createIcons(map,data);
                            
                            function createIcons(map,data)
                            {   var image;
                                for(var i = 1; i < size-1; i++)
                                {
                                        x = Number(data[i][8]);
                                        y = Number(data[i][9]);
                                        //change the image of the icon
                                        if(data[i][7] == 0)
                                            {image = 'http://maps.google.com/mapfiles/ms/icons/ylw-pushpin.png';}
                                        else if(data[i][7] == 1)
                                            {image = 'http://maps.google.com/mapfiles/ms/icons/rangerstation.png'; }
                                        else if(data[i][7] == 2)
                                            {image = 'http://maps.google.com/mapfiles/ms/icons/dollar.png';}
                                        else
                                            { image = 'http://maps.google.com/mapfiles/ms/icons/question.png';}
                                        
                                        var marker = new google.maps.Marker({
                                        position: new google.maps.LatLng(x, y),
                                            map: map,
                                            icon: image});
                                    
                                        //when the icon is clicked the infowindow will appear
                                        google.maps.event.addListener(marker, 'click', (function(marker, i) 
                                        {
                                        return function() {
                                        infowindow.setContent(  "Index:"+ data[i][0]+"<br>"+
                                                                "Name:"+ data[i][6]+"<br>"+
                                                                "Phone:"+ data[i][5]+"<br>"+
                                                                "Family Size:"+ data[i][4]+"<br>"+
                                                                "Address:"+ data[i][1]+"<br>"
                                                                );
                                        infowindow.open(map, marker);
                                                          }
                                        }                                              )
                                        (marker, i)                );
                                }
                            }
                                        
                    }
                
                }
                        

            </script>  
            <!--  Load the Maps JavaScript API -->
            <script src="https://maps.googleapis.com/maps/api/js?key=XXXXXXXXXKeyXXX&callback=initMap"
            async defer></script>
          
          </p>
        </body>
        </html>"""
        #Write the html webpage
        f.write(message)
        f.close()
        #Open a web browser tab.
        webbrowser.open_new_tab('Map.html')
    repeatNow = messagebox.askokcancel('Question','Do you want to process a diferent list?')
    #In case the person does not to process a new list the program ends.
    if repeatNow == False or mapList== False:
        messagebox.showinfo('Information','Thank you for using MapTheList')
        break
#Close the tkinter window
application_window.destroy()    
   
        