# Automated script

Download MCD43D07, MCD43D08, MCD43D09, MCD43D31 and MYD06

## Parameter

**MODDIR**: directory where save MCD43D and MYD06_L2

```
├── MODIS (This is $MODDIR)
│   ├── Land_Water_Mask_7Classes_UMD.hdf
│   ├── MCD43D
│   └── MYD06_L2
```

## Usage

Arguments:

-s|--startdate

​	yymmdd;

-e|--enddate

​	yymmdd;

-t|--token

​	LAADS app key; You can generate [here](https://ladsweb.modaps.eosdis.nasa.gov/tools-and-services/data-download-scripts/#appkeys).

Example:

```
./get_all.sh -s 20120529 -e 20120530 -t ****************
```



