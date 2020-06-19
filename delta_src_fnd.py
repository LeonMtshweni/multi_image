import bdsf
import sys, os


# get pwd
cwd = os.getcwd()

# grab params that I ran this script with
isl = sys.argv[2] # check these numbers remember you removed the -c parameter
pix = sys.argv[3]

# ms name
myms = sys.argv[1]

# dummy mask file
img_name = sys.argv[4]

# save file
save_file = img_name[:-6]

# fit the image
img = bdsf.process_image(img_name, thresh_isl= isl, thresh_pix = pix, adaptive_rms_box = True, \
      advanced_opts = True, stop_at = 'isl')


# export the image
img.export_image(outfile = cwd + '/bdsf/' + myms + '_bdsf_mask.fits', img_type = 'island_mask')
