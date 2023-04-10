# FondeCyT-DataBase
These are the codes to create and manage the MySQL database of my Master's Thesis.

##OpenSees and STKO
Currently, I'm working Domain Reduction Method to study the response of reinforced concrete buildings located near the San Ramon Fault, in Santiago de Chile. I'm using Fixed-Base and Soil-Structure Interaction Models developed with OpenSees and the software of ASDEA's STKO (Scientific Toolkit for OpenSees). 

<p align="center">
  <img src="https://i.imgur.com/8A7zQsV.png" width="400" />
  <img src="https://i.imgur.com/aFduibC.png" width="400" /> 
</p>
<div style="display: inline-block;">
  <img src="https://i.imgur.com/a96kylX.png" >
</div>

##ShakerMaker
I'm using the ShakerMakers framework to create a simulation of the seismic wave propagation into the buildings, and then using it as an input to create a DRM Box that I use in my soil structure models.

<p align="center">
    <img width="500" src="https://i.imgur.com/WTYuZ2U.png" alt="San Ramón's Failure simulated in ShakerMaker">
</p>

In this work, I will use 10 stations located in different areas across the city of Santiago to evaluate the seismic performance of the buildings in various earthquake scenarios resulting from the San Ramon Fault.

<p align="center">
  <img width="500" src= "https://i.imgur.com/KNoeWVr.png">
</p>

#MySQL
All input and output data will be stored in a MySQL database that I designed according to the needs of the FondeCyT investigation led by José Antonio Abell. I will run approximately 4000 cases of different scenarios.

<div style="display: inline-block;">
  <img src="https://i.imgur.com/Jc7UpO5.png" >
</div>

In the final steps, I will perform statistical analysis on the results to identify potential issues and use machine learning techniques to predict the results of interest.
