# Automated script

Download MCD43D07, MCD43D08, MCD43D09, MCD43D31, MYD06, OMNO2 ans OMPIXCOR

## Requirements

1. LAADS app key; 

   You can generate [here](https://ladsweb.modaps.eosdis.nasa.gov/tools-and-services/data-download-scripts/#appkeys) and save it as `~/.earthdata-app-key`

2. SOAPpy; 

   `pip install SOAPpy`

3. Directory structure:

   ```
   export MODDIR='xxxxxxxxxxx/MODIS/'
   export OMNO2DIR='xxxxxxxxxxx/OMNO2/version_3_3_0'
   export OMPIXCORDIR='xxxxxxxxxxx/OMPIXCOR/version_3_3_0'
   ```

   ```
   ├── MODIS
   │   ├── Land_Water_Mask_7Classes_UMD.hdf
   │   ├── MCD43D
   │   │   └── yyyy_1
   │   │   └── yyyy_2
   │   └── MYD06_L2
   │       └── yyyy_1
   │       └── yyyy_2
   ├── OMI
   │   ├── OMNO2
   │   │   └── version_3_3_0
   │   │       ├── yyyy_1
   │   │       │   └── mm_1
   │   └── OMPIXCOR
   │       └── version_003
   │           ├── yyyy_1
   │           │   └── mm_1
   ```

## Usage

**Arguments:**

-s|--startdate

​	yyyy-mm-dd;

-e|--enddate

​	yyyy-mm-dd;

**Parameters:**

You need to change `USERNAME` and `PASSWORD ` in `get_omi.py`

**Example:**

```
python get_modis.py -s 20140401 -e 20140430 -v
python get_omi.py -s 20140401 -e 20140430 -v
```
