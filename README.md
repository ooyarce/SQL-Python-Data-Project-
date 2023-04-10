# FondeCyT-DataBase
This are de codes to create and manage the MySQL DataBase of my Master's Thesis.

I'm currently working with Soil-Structure Models to see the behaviour of the reinforced concrete buildings near the San Ramon's Failure, in Santiago de Chile. 
<p align="center">
| Structure | Foundations |
| -------- | -------- |
|<div style="display: inline-block;"> <img src="https://i.imgur.com/8A7zQsV.png" width="400"></div>|<div style="display: inline-block;"><img src="https://i.imgur.com/aFduibC.png" width="400"></div>|

I'm using ShakerMakers framework to build up the simulation of the seismic wave propagation to the building and the using it as an input to create a DRM Box and using in my soil structure models.


    <img width="500" src="https://i.imgur.com/WTYuZ2U.png" alt="San Ramón's Failure simulated in ShakerMaker">
</p>

The soil structure models are build up with OpenSees and the software of ASDEA STKO (scientific toolkit for OpenSees). 

In this work I'll use 10 stations located in different places along the city of Santiago to the the seismic perfomance of the buildings in different scenarios of an earthquake due the San Ramon's Failure.

All the input and output data will be sorted in a MySQL DataBase that I designed acording the needs of the FondeCyT investigation leaded by José Antonio Abell. I'll run near 4000 cases of different scenarios.

In the final steps I'll do a Statistical analysis to the results to identify problems and use Machine Learning to predict the results of interest.

