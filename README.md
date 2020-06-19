# Imaging Radio Interferometeric data via brute force (IRIBF)

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
