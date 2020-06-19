import sys, os
import numpy as np


# current working dir
cwd = os.getcwd()
# directory to dump the dat file
IMG_STATS = cwd + '/image_stats/'

image_name = sys.argv[3]
data_name  = sys.argv[4]
print(data_name)
log_file   = 'imstat_log_' + image_name[:-6] + '.log'

# casa task imstat
fits_data = imstat( imagename = image_name,
                    logfile   = log_file,
                    append    = True)

# get the rms value from the fits_data
img_rms = fits_data['rms'][0]
# get max pixel
max_pix = fits_data['max'][0]
# get min pixel
min_pix = fits_data['min'][0]
# calculate image dynamic range
dynamic_range = np.abs(max_pix/min_pix)
# get std dev
img_sigma = fits_data['sigma'][0]
# get image flux
flux = fits_data['flux'][0] 

# write these values to file
file_name = data_name +'_img_dat1.txt'
t = open(file_name,'a')
#t.writelines([str(image_name) + ' ' + str(img_rms) + ' ' + str(max_pix) + ' ' + str(min_pix) + ' ' + str(flux) + '\n'])
t.writelines([str(image_name) + ' ' + str(img_rms) + ' ' + str(dynamic_range) + ' ' + str(flux) + '\n'])
t.close()
 
