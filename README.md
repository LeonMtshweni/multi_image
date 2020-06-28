# Imaging Radio Interferometeric data via brute force (IRIvBF)

The config file takes commas separated values
Config file Method
- OG_data: 
    bckup: 

This handles itself, for the most part, just remember to have the correct ms file name
- Duplicates:
    mslist: 
Give intuitive names to these ms files, names that’ll be reminiscent of the experiments in which they’re running.
Leave out the “.ms” bit of the name the code knows to attach it

- UV_range:
    uvrange: 
Should you not want to enable this feature give the value nill
 For specific uvrange give the appropriate minimum as follows \>1000,\>1km, etc


- Masking:
    Mask_list:
Leave these in the experiment’s parent directory, appropriately named
Give the value “auto” for auto-masking
Give the value “nill” to create a mask using BDSF/BDSM

- Wsclean_range:
    min_range:
Should you not want to enable this feature give the value nill
Specify value without units (takes meters only)

- BDSM:
    bdsf_par: 
Should you not want to enable this feature give the value nill
Leave these in the experiment’s parent directory, appropriately renamed to dummy_mask.fits
A single entry requires two numbers. Like all the other options are entered as a comma-separated list but a single entry will require two int values separated by a semicolon. 
For two ms file runs we’d have: ‘3;5’,’1;3’.if you wish not to specify this parameter use the command ‘none;none’ for each ms entry


- Imaging:
    robustness: -2.0,-1.0,0.0
    auto_threshold: 3,3,3
    automatic_mask_size: 5,5,5
    
#########################################
# everything below this text is depricated
##########################################
How to run the pipeline
`python <script_name> <ms_name> <uvrange> <mask_type/mask_list> <minuvw-m> <bdsdf_params> <og_data>`

`<script_name>`
Python script to run

`<ms_name>`
New files to be copied to current dir, the file name must not contain the .ms extension.

`<uvrange>`
If no uvrange is to be specified pass the string ‘none’, for specific uvrange give the appropriate minimum as follows \>1000,\>1km, etc

`<mask_type/mask_list>`
Kept in the /scratch/users/mtshweni/masters/masks/ directory and in fits format if not using auto mask

`<minuvw-m>`
If not needed leave whitespace as a string, otherwise specify without units (takes meters only)

`<bdsdf_params>`
To use this option you will need to have an existing image of field, rename it to masking_dummy.fits and leave it in the current directory. 
You will need to set mask_type/mask_list = ‘none’. That is, pass none for the mask_type/mask_list input param
A single entry requires two numbers. Like all the other options are entered as a comma-separated list but a single entry will require two int values separated by a semicolon. 
For two ms file runs we’d have: ‘3;5’,’1;3’.if you wish not to specify this parameter use the command ‘none;none’ for each ms entry

`<og_data>`
Kept in the dir /scratch/users/mtshweni/masters/msback_up. If data isn’t here then move it there 

Examples, suppose we cant to create a job for one ms file:
`python alpha_main.py 'tight' 'none' 'none' ' ' '150;750' 1561723022_sdp_l0.full_1284.full_pol_split_1024ch_3C274_64_chn_32s.ms`
`
