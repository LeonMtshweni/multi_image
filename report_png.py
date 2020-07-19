import numpy as np
from astropy.io import fits # handling fits file with astropy
from astropy.wcs import WCS
import glob
import os, sys
from os import path
import matplotlib as mpl
mpl.use('Agg') # plotting without X-forwarding
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable # for having multiple colorbars

# get current working directory
cwd = os.getcwd()
# create the directory for reports and ignore if it exists
try:
    os.mkdir(cwd + '/reports')
except FileExistsError:
    pass

# fetch myms value from perminal
myms = sys.argv[1]
prefix = sys.argv[2]
prefix = prefix.replace('_','_'+myms+'_')

print('The measuremnt set in use is ', myms)


#all_images = glob.glob("*data-MFS-image.fits")
single_image = prefix + "-MFS-image.fits"
single_resid = prefix + "-MFS-residual.fits"
single_model = prefix + "-MFS-model.fits"
single_psf   = prefix + "-MFS-psf.fits"


#Get the largest of these values
image_v_max = 0.036894241798892016 # max(image_upper_prcntl)
image_v_min = -0.004267486473207599 # min(image_lower_prcntl)
model_v_max = 0.0013412037407349725 # max(model_upper_prcntl)
model_v_min = -0.000038622914834380434 # min(model_lower_prcntl)
resid_v_max = 0.02 # max(resid_upper_prcntl)
resid_v_min = -0.02 # min(resid_lower_prcntl)
psf_v_max = 0.0012494441676839524 # max(psf_upper_prcntl)
psf_v_min = -0.0012300854677079892 # min(psf_lower_prcntl)



print(" -------------------------------------------------\n           creating figures and subplots\n -------------------------------------------------\n")

    
# open the fits files as image data
fits_image = fits.open(single_image)[0]
fits_resid = fits.open(single_resid)[0]
fits_model = fits.open(single_model)[0]
fits_psf   = fits.open(single_psf)[0]

#open fits header
header = fits_image.header
# get the wcs from header
wcs = WCS(header, naxis = 2)

# zero out the first two dimensions
image  = fits_image.data[0,0,:,:]
resid  = fits_resid.data[0,0,:,:]
model  = fits_model.data[0,0,:,:]
psf    = fits_psf.data[0,0,:,:]

# there are two ways to make these plots with wcs (which has it's own problems, but is the prefered method for now) and the pixel coord methon
fig, ax = plt.subplots(nrows = 2, ncols = 2, figsize=(20,20), subplot_kw={'projection': wcs}) # create figure and axes
#fig, ax = plt.subplots(nrows = 2, ncols = 2, figsize=(20,20))

#-----------------------------------------------------------------------------------------------
# Point SPread Function settings
print(" -------------------------------------------------\ncreating PSF subplots\n -------------------------------------------------\n")
ax00 = ax[0,0].imshow(psf, vmax = psf_v_max, vmin = psf_v_min, cmap='inferno', origin = 'lower')
ax[0,0].set_xlabel('Right Ascension (J2000)')
ax[0,0].set_ylabel('Declination (J2000)')
ax[0,0].set_title('PSF')
    
# Tick marks settings
ax[0,0].tick_params(axis='y', which='both', direction = 'in', right = False)
ax[0,0].tick_params(axis='y', which='major', direction = 'in', left = True)
ax[0,0].tick_params(axis='x', which='both', direction = 'in', top = False)
ax[0,0].tick_params(axis='x', which='major', direction = 'in', bottom = True)
    
# colorbar settings
divider = make_axes_locatable(ax[0,0])
cax = divider.append_axes('right', size='5%', pad = 0.05)
cax.xaxis.set_ticks_position("none")
fig.colorbar(ax00, cax=cax, orientation='vertical')

#-----------------------------------------------------------------------------------------------------
# Model settings
print(" -------------------------------------------------\ncreating MODEL subplots\n -------------------------------------------------\n")
ax01 = ax[0,1].imshow(model, vmax = model_v_max, vmin = model_v_min, cmap='inferno', origin = 'lower')
ax[0,1].set_xlabel('Right Ascension (J2000)')
ax[0,1].set_ylabel('Declination (J2000)')
ax[0,1].set_title('Model')

# Tick mark settings
ax[0,1].tick_params(axis='y', which='both', direction = 'in', right = False)
ax[0,1].tick_params(axis='y', which='major', direction = 'in', left = True)
ax[0,1].tick_params(axis='x', which='both', direction = 'in', top = False)
ax[0,1].tick_params(axis='x', which='major', direction = 'in', bottom = True)

# colorbar settings
divider = make_axes_locatable(ax[0,1])
cax = divider.append_axes('right', size='5%', pad=0.05)
fig.colorbar(ax01, cax=cax, orientation='vertical')

#-----------------------------------------------------------------------------------------------------
# Residual settings
print(" -------------------------------------------------\ncreating RESIDUAL subplots\n -------------------------------------------------\n")
ax10 = ax[1,0].imshow(resid, vmax = resid_v_max, vmin = resid_v_min, cmap='inferno', origin = 'lower')
ax[1,0].set_xlabel('Right Ascension (J2000)')
ax[1,0].set_ylabel('Declination (J2000)')
ax[1,0].set_title('Residual')

# Tick mark settings
ax[1,0].tick_params(axis='y', which='major', direction = 'in', right = True)
ax[1,0].tick_params(axis='y', which='major', direction = 'in', left = True)
ax[1,0].tick_params(axis='x', which='both', direction = 'in', top = False)
ax[1,0].tick_params(axis='x', which='major', direction = 'in', bottom = True)

# colorbar settings
divider = make_axes_locatable(ax[1,0])
cax = divider.append_axes('right', size='5%', pad=0.05)
fig.colorbar(ax10, cax=cax, orientation='vertical')

#-----------------------------------------------------------------------------------------------------
# Image settings
print(" -------------------------------------------------\ncreating IMAGE subplots\n -------------------------------------------------\n")
ax11 = ax[1,1].imshow(image, vmax = image_v_max, vmin = image_v_min, cmap='inferno', origin = 'lower')
ax[1,1].set_xlabel('Right Ascension (J2000)')
ax[1,1].set_ylabel('Declination (J2000)')
ax[1,1].set_title('Image')

# Tick mark settings
ax[1,1].tick_params(axis='y', which='both', direction = 'in', right = True, color = "white")
ax[1,1].tick_params(axis='y', which='major', direction = 'in', left = False)
ax[1,1].tick_params(axis='x', which='both', direction = 'in', top = False)
ax[1,1].tick_params(axis='x', which='major', direction = 'in', bottom = True, color = "white")


# colorbar settings
divider = make_axes_locatable(ax[1,1])
cax = divider.append_axes('right', size='5%', pad=0.05)
fig.colorbar(ax11, cax=cax, orientation='vertical')
# gets rid of the ticks


#-----------------------------------------------------------------------------------------------------
print(" -------------------------------------------------\nSaving Figure\n -------------------------------------------------\n")
report_name = prefix + '.png'
#fig.tight_layout() # for improved spacing between plots
fig.savefig(cwd + '/reports/' + report_name, bbox_inches="tight") # saved png name
#----------------------------------------------------------------------------------------------------
