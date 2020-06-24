# CVT-CGA
Keeping track of code updates for Coronavirus Visualization Team in collaboration with Harvard Center for Graphical Analysis & George Mason University. 
___

### Description
Automating data processes with support for the following datasets provided by [NASA Earth GES](https://earthdata.nasa.gov/):
<ul>
  <li>MERRA2 - Temperature + Humidity</li>
  <li>IMERG - Precipitation</li>
  <li>OMI - NO2</li>
</ul>

Shapefiles from [STC COVID-19 Dataset](https://github.com/stccenter/COVID-19-Data) provided by aforementioned organizations. 

___
### Usage
Clone the repository and download requirements using the `requirements.txt` file. Using Anaconda is recommended as it installs packages more easily and doesn't require the installation of header files.

```
git clone https://github.com/Shubham-SK/CVT-CGA.git
cd CVT-CGA
while read requirement; do conda install --yes $requirement; done < requirements.txt
```

Ensure all dependencies are installed before proceeding.

--- 
### Modifications
File paths must be adjusted to be able to run on different machines.
