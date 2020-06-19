#!/usr/bin/env python3
import os, sys
from os import path
import pickle
import beta_setup as gen # imports setup file
import glob
import shutil

#---------------------------------------------------------------------------------------
# path to remember
cwd = os.getcwd()
# crease essential directories to keep products
gen.create_dirs()
IDIA_CONTAINER_PATH = '/software/astro/caracal/STIMELA_IMAGES_1.6.1/'
STIMELA_CONTAINER_PATH = '/software/astro/caracal/STIMELA_IMAGES_1.6.1/'
#wsclean container
WSCLEAN_CONTAINER = STIMELA_CONTAINER_PATH +'stimela_wsclean_1.6.0.sif'
# casa container
CASA_CONTAINER = '/idia/software/containers/casa-stable-4.7.2.simg'
# python container
PYTHON_CONTAINER = '/idia/software/containers/python3/python3-2020-01-28.simg'
# source finding container
SOURCE_FINDING_CONTAINER = '/idia/software/containers/sourcefinding-dev-2019-09-23.simg'
# directory where data is fetched
MS_BAK_DIR = '/scratch/users/mtshweni/masters/msback_up/'
# mask directory
MASK_DIR = '/scratch/users/mtshweni/masters/masks/'

# Essential directories
LOGS      = cwd + '/logs'
MAPS      = cwd + '/maps'
SCRIPTS   = cwd + '/scripts'
MS_DIR    = cwd + '/ms_files'
BDSF      = cwd + '/bdsf' 
IMG_STATS = cwd + '/image_stats'
#---------------------------------------------------------------------------------------

def main():

    # name of the submit file
    submit_file = 'submit_jobs.sh'

    # Open file for writing
    f = open(submit_file,'w')

    # write header information
    f.write('#!/bin/bash\n')

    # load the list of data to be copied
    mslist = sys.argv[1].split(',')

    # list of uvrange values
    uvlist = sys.argv[2].split(',')

    # list of fits masks
    masklist = sys.argv[3].split(',')

    # list of minivw
    wsclean_uv_range = sys.argv[4].split(',')
    
    #pybdsf selection parameters
    isl_pix_input = sys.argv[5].split(',') 

    # this is the data to be copied
    og_dat = sys.argv[6]

    # ms_file to be copied
    ms_path = MS_BAK_DIR + og_dat
    
    # this loop simultaneously iterates through the lists provided
    for (myms,uv_range,fitsmask,min_uvw,isl_pix) in zip(mslist,uvlist,masklist,wsclean_uv_range,isl_pix_input):

         #image names 
         blind_prefix = MAPS  + '/' + 'img_'+myms+'_data'
         pcal_prefix  = MAPS  + '/' + 'img_'+myms+'_pcal' 

         # job kill file for each of the datasets
         kill_file = SCRIPTS  + '/' + 'kill_jobs_'+ myms +'.sh'
         
         #-------------------------------------------------------------------------------
         # Make Copies of Data

         # name of slurm and the campanying log file to be executed
         slurmfile = SCRIPTS  + '/' + myms+'_cp.sh' # name of the slurm file # loop
         logfile   = LOGS     + '/' + myms+'_cp.log'  # name of log file # loop


         # check existence of data in msback directory
         if path.exists(ms_path):
           # get the path to the file in the current directory
           src = path.realpath(ms_path) # store the file path in the variable 'src' if .txt file exists
         else:
           print("The data you're looking for is not stored in the directory: " + MS_BAK_DIR + '\n Please move data to ' + MS_BAK_DIR)
         
         # this part of the code isolate the file extension of the file being copied
         root, sep, extension = src.partition('.')
         
         # assigning myms an extension
         myms_ext = MS_DIR  + '/' + myms + '.' + extension

         # the name and path to copy the file to
         dst = MS_DIR  + '/' + myms + '.' + extension

         # checks if copy already exists in current dir
         if os.path.exists(dst):
           print("#------------------------------------\n")
           print("MS files already exists in the ms_files directory\n")
           print("#------------------------------------\n")
         else:
           
           # this variable constitutes the bash command that is gonna all the copying  
           bash_command = 'cp -r ' + src + ' ' + dst # + '.' + extension 

           # write the slurm file
           gen.write_slurm(opfile  = slurmfile,
                           jobname = myms+'_cp',
                           logfile = logfile,
                           syscall = bash_command) 
           
           # slurm job name
           job_id_copy = 'cp_' + myms 
           syscall     = job_id_copy + "=`sbatch "+slurmfile+" | awk '{print $4}'`"
           f.write(syscall+'\n')

         #-------------------------------------------------------------------------------
         # Flag Summary, First

         slurmfile = SCRIPTS  + '/' + myms+'_flag_sum1.sh' # name of the slurm file
         logfile   = LOGS     + '/' + myms+'_flag_sum1.log'  # name of log file

         syscall  = 'singularity exec '+CASA_CONTAINER+' '
         syscall += 'casa -c ' + cwd + '/gamma_flag_summary.py ' + myms_ext + ' --nologger --log2term --nogui\n'
         gen.write_slurm(opfile  = slurmfile,
                         jobname = myms + '_flag_sum1',
                         logfile = logfile,
                         syscall = syscall)

         job_id_flag_sum1 = 'FLAG_SUM1_' + myms
         syscall = job_id_flag_sum1 + "=`sbatch -d afterok:${"+job_id_copy+"} "+slurmfile+" | awk '{print $4}'`"
         f.write(syscall+'\n')

         #------------------------------------------------------------------------------
         # BDSF Island Mask Export

         if fitsmask == 'none':

             # split the isl and pix into their individual variables
             isl, pix = isl_pix.split(';')

             # fetch the mask from current directory
             img_name = glob.glob('masking_dummy.fits')[0]

             slurmfile = SCRIPTS  + '/' + myms + '_mask.sh' # name of the slurm file
             logfile   = LOGS     + '/' + myms + '_mask.log'  # name of log file

             syscall = 'singularity exec '+SOURCE_FINDING_CONTAINER+' '
             syscall += 'python ' + cwd + '/delta_src_fnd.py ' + myms + ' ' + str(isl) + ' ' + str(pix) + ' ' + img_name + '\n'
             gen.write_slurm(opfile  = slurmfile,
                             jobname = myms+'_bdsf',
                             logfile = logfile,
                             syscall = syscall)

             # set the newly created mask as the fitsmask
             fitsmask    = cwd + '/bdsf/' + myms + '_bdsf_mask.fits' 
             job_id_bdsf = 'BDSF_' +myms
             syscall     = job_id_bdsf + "=`sbatch -d afterok:${"+job_id_flag_sum1+"} "+slurmfile+" | awk '{print $4}'`"
             f.write(syscall+'\n')


         #------------------------------------------------------------------------------
         # Automask wsclean

         # make sure wsclean knows where to find the mask if fitsmask option is selected
         if fitsmask != 'auto':
              fitsmask = MASK_DIR + '/' + fitsmask          

         # This sets up the command for wsclean
         slurmfile = SCRIPTS + '/' + myms+'_wsclean_data.sh' # name of the slurm file # there needs to be one of these for all the ms files
         logfile   = LOGS    + '/' + myms+'_wsclean_data.log'  # name of log file # loop over this
         syscall   = 'singularity exec '+WSCLEAN_CONTAINER+' ' # loop over this
         syscall  += gen.generate_syscall_wsclean(mslist = [myms_ext], # loop over this
                                                 imgname = blind_prefix,
                                                 datacol = 'DATA',
                                            minuvw_range = min_uvw,
                                                    bda  = False,
                                                    mask = fitsmask)


         # This is what actually generates the command in a bash file
         gen.write_slurm(opfile = slurmfile,
                        jobname = myms + '_data',
                        logfile = logfile,
                        syscall = syscall)

         # To make sure that this job waits for the previous jobs accordingly,I'm lazily putting an if statement like I did above
         # dummy variable for the if statement below
         dummy_var = fitsmask
         if fitsmask == dummy_var:
             job_id_blind = 'DATA_' + myms 
             syscall = job_id_blind+"=`sbatch -d afterok:${"+job_id_bdsf+"} "+slurmfile+" | awk '{print $4}'`"
             f.write(syscall+'\n')
         else:
             job_id_blind = 'DATA_' + myms
             syscall = job_id_blind+"=`sbatch -d afterok:${"+job_id_flag_sum1+"} "+slurmfile+" | awk '{print $4}'`"
             f.write(syscall+'\n')

         # ------------------------------------------------------------------------------
         # Predict

         slurmfile = SCRIPTS + '/' + myms+'_predict.sh' # name of the slurm file
         logfile   = LOGS + '/' + myms+'_predict.log'   # name of log file
         syscall   = 'singularity exec ' + WSCLEAN_CONTAINER + ' '  # for each of the msfiles
         syscall  += gen.generate_syscall_predict(msname = myms_ext,
                                                imgbase = blind_prefix)


         # This is what actually generates the command in a bash file
         gen.write_slurm(opfile = slurmfile,
                        jobname = myms + '_predict',
                        logfile = logfile,
                        syscall = syscall)
 
         job_id_predict1 = 'PREDICT_' + myms
         syscall = job_id_predict1 + "=`sbatch -d afterok:${"+job_id_blind+"} "+slurmfile+" | awk '{print $4}'`"
         f.write(syscall+'\n') # loop

         # ------------------------------------------------------------------------------
         # Self-calibrate phases

         slurmfile = SCRIPTS + '/' + myms + '_phase_cal.sh' # name of the slurm file
         logfile   = LOGS + '/' + myms + '_phase_cal.log'  # name of log file

         syscall   = 'singularity exec '+CASA_CONTAINER+' '
         syscall  += 'casa -c ' + cwd + '/epsilon_selfcal_target_phases.py ' + myms_ext + ' ' + uv_range + ' --nologger --log2term --nogui\n'
         gen.write_slurm(opfile   = slurmfile,
                         jobname  = myms+'_phase_cal',
                         logfile  = logfile,
                         syscall  = syscall)

         job_id_phasecal1 = 'PHASECAL_' + myms
         syscall = job_id_phasecal1 + "=`sbatch -d afterok:${"+job_id_predict1+"} "+slurmfile+" | awk '{print $4}'`"
         f.write(syscall+'\n')
         
         # ------------------------------------------------------------------------------
         # Flag Summary, Second

         slurmfile = SCRIPTS + '/' + myms + '_flag_sum2.sh' # name of the slurm file
         logfile   = LOGS + '/' + myms + '_flag_sum2.log'  # name of log file

         syscall  = 'singularity exec '+CASA_CONTAINER+' '
         syscall += 'casa -c ' + cwd + '/gamma_flag_summary.py ' + myms_ext + ' --nologger --log2term --nogui\n'
         gen.write_slurm(opfile = slurmfile,
                        jobname = myms+'_flag_sum2',
                        logfile = logfile,
                        syscall = syscall)

         job_id_flag_sum2 = 'FLAG_SUM2_' + myms
         syscall = job_id_flag_sum2 + "=`sbatch -d afterok:${"+job_id_phasecal1+"} "+slurmfile+" | awk '{print $4}'`"
         f.write(syscall+'\n')

         # ------------------------------------------------------------------------------
         # WSCLEAN CORRECTED_DATA

         # makes sure wsclean knows where to find the mask if fitsmask option is selected
         if fitsmask != 'auto':
             fitsmask = MASK_DIR + '/' + fitsmask

         # This sets up the command for wsclean
         slurmfile = SCRIPTS + '/' + myms+'_wsclean_correct.sh' # name of the slurm file
         logfile   = LOGS + '/' + myms+'_wsclean_correct.log'  # name of log file

         syscall  = 'singularity exec '+WSCLEAN_CONTAINER+' '
         syscall += gen.generate_syscall_wsclean(mslist       = [myms_ext],
                                                 imgname      = pcal_prefix,
                                                 datacol      = 'CORRECTED_DATA',
                                                 minuvw_range = min_uvw,
                                                 bda          = False,
                                                 mask         = MASK_DIR + '/' + fitsmask)

         # call function that writes the header info of a bash script
         gen.write_slurm(opfile  = slurmfile,
                         jobname = myms + '_wcorr',
                         logfile = logfile,
                         syscall = syscall)


         job_id_PCAL1 = 'CORRECT_' + myms
         syscall = job_id_PCAL1 + "=`sbatch -d afterok:${"+job_id_flag_sum2+"} "+slurmfile+" | awk '{print $4}'`"
         #syscall = job_id_PCAL1 + "=`sbatch "+slurmfile+" | awk '{print $4}'`"
         f.write(syscall+'\n')

         # ------------------------------------------------------------------------------
         # Image statistics, First

         slurmfile = SCRIPTS + '/' + myms+'_img_stat.sh' # name of the slurm file
         logfile   = LOGS + '/' + myms+'_img_stat.log'  # name of log file

         # write headings to image data file
         image_data = IMG_STATS + '/' + myms + '_img_stat.dat'
         gen.write_table(opfile = image_data)

         #
         syscall = 'singularity exec '+CASA_CONTAINER+' '
         syscall += 'casa -c ' + cwd + '/zeta_image_stats.py ' + pcal_prefix + '-MFS-image.fits' + ' ' + myms + ' --nologger --log2term --nogui\n'
         gen.write_slurm(opfile  = slurmfile,
                         jobname = myms+'_img_stat',
                         logfile = logfile,
                         syscall = syscall)

         job_id_im_stat1 = 'IMG_STAT_' + myms
         syscall = job_id_im_stat1+"=`sbatch -d afterok:${"+job_id_PCAL1+"} "+slurmfile+" | awk '{print $4}'`"
         f.write(syscall+'\n')

         #-------------------------------------------------------------------------------
         # Clean Up Empty Logging Files

         slurmfile = SCRIPTS + '/' + myms+'_clean_up.sh' # name of the slurm file
         logfile   = LOGS + '/' + myms+'_clean_up.log'  # name of log file

         # this variable constitutes the bash command that is gonna all the copying  
         bash_command ='mv casa*.log ipython*.log ./casa_junk/ && mv *.py ./engine_scripts && find ./ -empty -delete -print &>removed_logs.txt' 

         # write the slurm file
         gen.write_slurm(opfile  = slurmfile,
                         jobname = myms + '_clean_up',
                         logfile = logfile,
                         syscall = bash_command)

         job_id_rem_log = 'CLEAN_UP_' + myms
         syscall = job_id_rem_log+"=`sbatch -d afterok:${"+job_id_im_stat1+"} "+slurmfile+" | awk '{print $4}'`"
         f.write(syscall+'\n')

         # ------------------------------------------------------------------------------

         #kill = 'echo "scancel "$'+job_id_copy+'" "$'+job_id_flag_sum1+'" "$'+job_id_blind+'" "$'+job_id_predict1+'" "$'+job_id_phasecal1+'" "$'+job_id_flag_sum2+'" "$'+job_id_PCAL1+'" "$'+job_id_im_stat1+' >> '+kill_file
         #f.write(kill+'\n')

    f.close() # close function

if __name__ == "__main__":


    main()
