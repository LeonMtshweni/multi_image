#!/usr/bin/env python3
import os, sys
from os import path
sys.path.insert(1,'./multi_image')
import beta_setup as beta
import glob
import shutil
# yaml
import yaml

#---------------------------------------------------------------------------------------
# current working path
cwd = os.getcwd()

# crease essential directories to keep products
beta.create_dirs()
print("#------------------------------------\n")
print("Creating the engine directories directory\n")
print("#------------------------------------\n")

# FOR CONTAINERS
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
# aimfast container
AIMFAST = '/idia/software/containers/STIMELA_IMAGES/stimela_aimfast_dev.sif'
# shadems container
SHADEMS = '/software/astro/caracal/STIMELA_IMAGES_1.6.1/stimela_shadems_1.7.0.sif'

# directory where data is fetched
MS_BAK_DIR = '/scratch/users/mtshweni/masters/msback_up/'
# mask directory
MASK_DIR = '/scratch/users/mtshweni/masters/masks/'

# Essential directories
LOGS      = cwd + '/logs'
MAPS      = './maps' #cwd + '/maps' # i used the shorthand method because of another script
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

    # yaml file name
    yaml_file = cwd + '/config.yaml'
    # Read in file
    yml_file = open(yaml_file,'r')
    
    # Read yaml file
    YAML = yaml.full_load(yml_file)
    
    # write header information
    f.write('#!/bin/bash\n')

    # this is the data to be copied
    #og_dat = sys.argv[6]
    og_dat = YAML[0]['OG_data']['bckup']
    print("Using the ms file %s" %og_dat)
    # load the list of data to be copied
    #mslist  = sys.argv[1].split(',')
    mslist = YAML[1]['Duplicates']['mslist'].split(',') 

    # list of uvrange values
    #uvlist = sys.argv[2].split(',')
    uvlist = YAML[2]['UV_range']['uvrange'].split(',')

    # list of fits masks
    #masklist = sys.argv[3].split(',')
    masklist = YAML[3]['Masking']['mask_list'].split(',')
    
    # list of minivw
    #wsclean_uv_range = sys.argv[4].split(',')
    wsclean_uv_range = YAML[4]['Wsclean_range']['min_range'].split(',')
    
    #pybdsf selection parameters
    #isl_pix_input = sys.argv[5].split(',') 
    isl_pix_input = YAML[5]['BDSM']['bdsf_par'].split(',')
       
    # imaging parameters
    robustness        = YAML[6]['Imaging']['robustness'].split(',')
    auto_threshld     = YAML[6]['Imaging']['auto_threshold'].split(',')
    auto_mask_size    = YAML[6]['Imaging']['automatic_mask_size'].split(',')
    multiscale_clean  = YAML[6]['Imaging']['multiscale_clean'].split(',')
    multiscale_scales = YAML[6]['Imaging']['multiscale_scales'].split(',')
    taper_UV          = YAML[6]['Imaging']['taper_UV'].split(',')
    uv_tapering       = YAML[6]['Imaging']['uv_tapering'].split(',')

    # ms_file to be copied
    ms_path = MS_BAK_DIR + og_dat
    
    # mailing service address
    address_mail = YAML[7]['EMAIL']['address']
    
    # this loop simultaneously iterates through the lists provided
    for (myms,uv_range,fitsmask,min_uvw,isl_pix,rbst,auto_thresh,auto_mask,mltscl_cln,mltscl_scls,taper_bool,uv_taper) in zip(mslist,uvlist,masklist,wsclean_uv_range,isl_pix_input,robustness,auto_threshld,auto_mask_size,multiscale_clean,multiscale_scales,taper_UV,uv_tapering):

         #image names 
         blind_prefix = MAPS  + '/' + 'img_'+myms+'_data'
         pcal_prefix  = MAPS  + '/' + 'img_'+myms+'_pcal' 

         # Write header information to the file
         #kill_file.writelines('echo "scancel "')
         
         #-------------------------------------------------------------------------------
         # Make Copies of Data

         # name of slurm and the campanying log file to be executed
         bash_script = SCRIPTS  + '/' + myms+'_cp.sh' # name of the slurm file # loop
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
           beta.write_slurm(opfile = bash_script,
                           jobname = 'cp_' + myms,
                           logfile = logfile,
                           mail_ad = address_mail,
                           syscall = bash_command) 
           
           # slurm job name
           job_id_copy = 'cp_' + myms 
           syscall     = job_id_copy + "=`sbatch "+bash_script+" | awk '{print $4}'`"
           # write the syscall command to the submit file
           f.write(syscall+'\n')

         #-------------------------------------------------------------------------------
         # Generating visibility plots, I

         bash_script = SCRIPTS + '/' + myms+'_shadems.sh' # name of the slurm file
         logfile   = LOGS + '/' + myms+'_shadems.log'  # name of log file

         syscall   = 'singularity exec '+SHADEMS+' '
         syscall  += 'python ' + cwd + '/plot_vis.py ' + myms_ext + ' DATA\n'
         # write the slurm file
         beta.write_slurm(opfile = bash_script,
                         jobname = 'shadems_' + myms,
                         logfile = logfile,
                         mail_ad = address_mail,
                         syscall = syscall)

         job_id_shadems = 'SHADE_MS_' + myms
         syscall = job_id_shadems+"=`sbatch -d afterok:${"+job_id_copy+"} "+bash_script+" | awk '{print $4}'`"
         # write the syscall command to the submit file
         f.write(syscall+'\n')

         #-------------------------------------------------------------------------------
         # Flag Summary, First

         bash_script = SCRIPTS  + '/' + myms+'_flag_sum1.sh' # name of the slurm file
         logfile   = LOGS     + '/' + myms+'_flag_sum1.log'  # name of log file

         syscall  = 'singularity exec '+CASA_CONTAINER+' '
         syscall += 'casa -c ' + cwd + '/multi_image/gamma_flag_summary.py ' + myms_ext + ' --nologger --log2term --nogui\n'
         beta.write_slurm(opfile  = bash_script,
                         jobname = 'flag_sum1_' + myms,
                         logfile = logfile,
                         mail_ad = address_mail,
                         syscall = syscall)

         job_id_flag_sum1 = 'FLAG_SUM1_' + myms
         syscall = job_id_flag_sum1 + "=`sbatch -d afterok:${"+job_id_shadems+"} "+bash_script+" | awk '{print $4}'`"
         # write the syscall command to the submit file
         f.write(syscall+'\n')
        
         #------------------------------------------------------------------------------
         # BDSF Island Mask Export

         if path.exists(cwd+ '/dummy_mask.fits'): #fitsmask == 'nill':

             # split the isl and pix into their individual variables
             isl, pix = isl_pix.split(';')

             # fetch the mask from current directory
             img_name = glob.glob('masking_dummy.fits')[0]

             bash_script = SCRIPTS  + '/' + myms + '_mask.sh' # name of the slurm file
             logfile   = LOGS     + '/' + myms + '_mask.log'  # name of log file

             syscall = 'singularity exec '+SOURCE_FINDING_CONTAINER+' '
             syscall += 'python ' + cwd + '/multi_image/delta_src_fnd.py ' + myms + ' ' + str(isl) + ' ' + str(pix) + ' ' + img_name + '\n'
             beta.write_slurm(opfile  = bash_script,
                             jobname = 'bdsf_' + myms,
                             logfile = logfile,
                             mail_ad = address_mail,
                             syscall = syscall)

             # set the newly created mask as the fitsmask
             fitsmask    = cwd + '/bdsf/' + myms + '_bdsf_mask.fits' 
             job_id_bdsf = 'BDSF_' +myms
             syscall     = job_id_bdsf + "=`sbatch -d afterok:${"+job_id_flag_sum1+"} "+bash_script+" | awk '{print $4}'`"
             # write the syscall command to the submit file
             f.write(syscall+'\n')

         #------------------------------------------------------------------------------
         # Automask wsclean

         # choose appropriate fitsmask for run
         if path.exists(fitsmask):
             fitsmask = fitsmask
         else:
             fitsmask  = 'auto'

         # This sets up the command for wsclean
         bash_script = SCRIPTS + '/' + myms+'_wsclean_data.sh' # name of the slurm file # there needs to be one of these for all the ms files
         logfile   = LOGS    + '/' + myms+'_wsclean_data.log'  # name of log file # loop over this
         syscall   = 'singularity exec '+WSCLEAN_CONTAINER+' ' # loop over this
         syscall  += beta.generate_syscall_wsclean(mslist  = [myms_ext], # loop over this
                                                   imgname = blind_prefix,
                                                   datacol = 'DATA',
                                              minuvw_range = min_uvw,
                                                    briggs = rbst,
                                            threshold_auto = auto_thresh,
                                            size_auto_mask = auto_mask,
                                                      bda  = False,
                                                      mask = fitsmask,
                                                multiscale = mltscl_cln,
                                                    scales = mltscl_scls,
                                                  taper_uv = taper_bool,
                                                 beam_size = uv_taper)


         # This is what actually generates the command in a bash file
         beta.write_slurm(opfile = bash_script,
                        jobname = 'data_' + myms,
                        logfile = logfile,
                        mail_ad = address_mail,
                        syscall = syscall)

         # To make sure that this job waits for the previous jobs accordingly,I'm lazily putting an if statement like I did above
         if path.exists(cwd + '/bdsf/' + myms + '_bdsf_mask.fits'):
             job_id_blind = 'DATA_' + myms 
             syscall = job_id_blind+"=`sbatch -d afterok:${"+job_id_bdsf+"} "+bash_script+" | awk '{print $4}'`"
             # write the syscall command to the submit file
             f.write(syscall+'\n')
             
         else:
             job_id_blind = 'DATA_' + myms
             syscall = job_id_blind+"=`sbatch -d afterok:${"+job_id_flag_sum1+"} "+bash_script+" | awk '{print $4}'`"
             # write the syscall command to the submit file
             f.write(syscall+'\n')
         
         # ------------------------------------------------------------------------------
         # Pre-selfcal Report
         bash_script = SCRIPTS+'/'+myms+'_report_pre.sh' # name of the slurm file
         logfile   = LOGS + '/' +myms+'_report_pre.log'  # name of log file

         # this variable constitutes the bash command that is gonna all the copying  
         bash_command  = 'singularity exec ' +  PYTHON_CONTAINER+ ' '
         bash_command += 'python multi_image/report_png.py ' + myms + ' img_data'
                 
         # write the slurm file
         beta.write_slurm(opfile  = bash_script,
                         jobname = 'report_pre_' + myms,
                         logfile = logfile,
                         mail_ad = address_mail,
                         syscall = bash_command)

         job_id_report_pre = myms + '_REPORT_PRE'
         syscall = job_id_report_pre+"=`sbatch -d afterok:${"+job_id_blind+"} "+bash_script+" | awk '{print $4}'`"
         f.write(syscall+'\n')

         # ------------------------------------------------------------------------------
         # Predict

         bash_script = SCRIPTS + '/' + myms+'_predict.sh' # name of the slurm file
         logfile   = LOGS + '/' + myms+'_predict.log'   # name of log file
         syscall   = 'singularity exec ' + WSCLEAN_CONTAINER + ' '  # for each of the msfiles
         syscall  += beta.generate_syscall_predict(msname = myms_ext,
                                                imgbase = blind_prefix)


         # This is what actually generates the command in a bash file
         beta.write_slurm(opfile = bash_script,
                        jobname = 'predict_' + myms,
                        logfile = logfile,
                        mail_ad = address_mail,
                        syscall = syscall)
 
         job_id_predict1 = 'PREDICT_' + myms
         syscall = job_id_predict1 + "=`sbatch -d afterok:${"+job_id_report_pre+"} "+bash_script+" | awk '{print $4}'`"
         # write the syscall command to the submit file
         f.write(syscall+'\n')

         # ------------------------------------------------------------------------------
         # Self-calibrate phases

         bash_script = SCRIPTS + '/' + myms + '_phase_cal.sh' # name of the slurm file
         logfile   = LOGS + '/' + myms + '_phase_cal.log'  # name of log file

         syscall   = 'singularity exec '+CASA_CONTAINER+' '
         syscall  += 'casa -c ' + cwd + '/multi_image/epsilon_selfcal_target_phases.py ' + myms_ext + ' ' + uv_range + ' --nologger --log2term --nogui\n'
         beta.write_slurm(opfile = bash_script,
                         jobname = 'phase_cal_' + myms,
                         logfile = logfile,
                         mail_ad = address_mail,
                         syscall = syscall)

         job_id_phasecal1 = 'PHASECAL_' + myms
         syscall = job_id_phasecal1 + "=`sbatch -d afterok:${"+job_id_predict1+"} "+bash_script+" | awk '{print $4}'`"
         # write the syscall command to the submit file
         f.write(syscall+'\n')
         
         #-------------------------------------------------------------------------------
         # Generating visibility plots, II
         # Creating vis plots after selfcal run

         bash_script = SCRIPTS + '/' + myms+'_shadems.sh' # name of the slurm file
         logfile   = LOGS + '/' + myms+'_shadems.log'  # name of log file

         syscall   = 'singularity exec '+SHADEMS+' '
         syscall  += 'python ' + cwd + '/plot_vis.py ' + myms_ext + ' CORRECTED_DATA\n'
         # write the slurm file
         beta.write_slurm(opfile = bash_script,
                         jobname = 'shadems_' + myms,
                         logfile = logfile,
                         mail_ad = address_mail,
                         syscall = syscall)

         job_id_shadems = 'SHADE_MS_' + myms
         syscall = job_id_shadems+"=`sbatch -d afterok:${"+job_id_phasecal1+"} "+bash_script+" | awk '{print $4}'`"
         # write the syscall command to the submit file
         f.write(syscall+'\n')
        
         # ------------------------------------------------------------------------------
         # Flag Summary, Second

         bash_script = SCRIPTS + '/' + myms + '_flag_sum2.sh' # name of the slurm file
         logfile   = LOGS + '/' + myms + '_flag_sum2.log'  # name of log file

         syscall  = 'singularity exec '+CASA_CONTAINER+' '
         syscall += 'casa -c ' + cwd + '/multi_image/gamma_flag_summary.py ' + myms_ext + ' --nologger --log2term --nogui\n'
         beta.write_slurm(opfile = bash_script,
                         jobname = 'flag_sum2_' + myms,
                         logfile = logfile,
                         mail_ad = address_mail,
                         syscall = syscall)

         job_id_flag_sum2 = 'FLAG_SUM2_' + myms
         syscall = job_id_flag_sum2 + "=`sbatch -d afterok:${"+job_id_shadems+"} "+bash_script+" | awk '{print $4}'`"
         # write the syscall command to the submit file
         f.write(syscall+'\n')

         # ------------------------------------------------------------------------------
         # WSCLEAN CORRECTED_DATA

         # choose appropriate fitsmask for run
         if path.exists(fitsmask):
             fitsmask = fitsmask
         else:
             fitsmask = 'auto'

         # This sets up the command for wsclean
         bash_script = SCRIPTS + '/' + myms+'_wsclean_correct.sh' # name of the slurm file
         logfile   = LOGS + '/' + myms+'_wsclean_correct.log'  # name of log file

         syscall  = 'singularity exec '+WSCLEAN_CONTAINER+' '
         syscall += beta.generate_syscall_wsclean(mslist         = [myms_ext],
                                                  imgname        = pcal_prefix,
                                                  datacol        = 'CORRECTED_DATA',
                                                  minuvw_range   = min_uvw,
                                                  briggs         = rbst,
                                                  threshold_auto = auto_thresh,
                                                  size_auto_mask = auto_mask,
                                                  bda            = False,
                                                  mask           = fitsmask,
                                                  multiscale     = mltscl_cln,
                                                  scales         = mltscl_scls,
                                                  taper_uv       = taper_bool,
                                                  beam_size      = uv_taper)

         # call function that writes the header info of a bash script
         beta.write_slurm(opfile  = bash_script,
                          jobname = 'wcorr_' + myms,
                          logfile = logfile,
                          mail_ad = address_mail,
                          syscall = syscall)


         job_id_PCAL1 = 'CORRECT_' + myms
         syscall = job_id_PCAL1 + "=`sbatch -d afterok:${"+job_id_flag_sum2+"} "+bash_script+" | awk '{print $4}'`"
         # write the syscall command to the submit file
         f.write(syscall+'\n')

         # ------------------------------------------------------------------------------
         # Post-selfcal I Report
         bash_script = SCRIPTS+'/'+myms+'_report_post.sh' # name of the slurm file
         logfile   = LOGS + '/' +myms+'_report_post.log'  # name of log file

         # this variable constitutes the bash command that is gonna all the copying  
         bash_command  = 'singularity exec ' +  PYTHON_CONTAINER+ ' '
         bash_command += 'python multi_image/report_png.py ' + myms + ' img_pcal'

         # write the slurm file
         beta.write_slurm(opfile  = bash_script,
                         jobname = 'report_post_' + myms,
                         logfile = logfile,
                         mail_ad = address_mail,
                         syscall = bash_command)

         job_id_report_post = myms + '_REPORT_POST'
         syscall = job_id_report_post+"=`sbatch -d afterok:${"+job_id_PCAL1+"} "+bash_script+" | awk '{print $4}'`"
         f.write(syscall+'\n')

         # ------------------------------------------------------------------------------
         # Aimfast , First

         bash_script = SCRIPTS + '/' + myms+'_aimfast.sh'
         logfile   = LOGS + '/' + myms+'_aimfast.log'  

         # this variable constitutes the bash command 
         bash_command  = 'singularity exec ' + AIMFAST + ' '
         bash_command += 'aimfast  --residual-image ' + pcal_prefix + '-MFS-residual.fits' 

         # write the bash command into a bash script 
         beta.write_slurm(opfile = bash_script,
                         jobname = 'aimfast_' + myms,
                         logfile = logfile,
                         mail_ad = address_mail,
                         syscall = bash_command)

         job_id_aimfast1 = 'AIMFAST_' + myms
         syscall = job_id_aimfast1+"=`sbatch -d afterok:${"+job_id_report_post+"} "+bash_script+" | awk '{print $4}'`"
         # write the syscall command to the submit file
         f.write(syscall+'\n')

         #-------------------------------------------------------------------------------
         # Clean Up Empty Logging Files

         bash_script = SCRIPTS + '/' + myms+'_clean_up.sh' # name of the slurm file
         logfile   = LOGS + '/' + myms+'_clean_up.log'  # name of log file

         # this variable constitutes the bash command that is gonna all the copying  
         bash_command ='mv casa*.log ipython* *.last ./casa_junk/ && find ./ -empty -delete -print &>removed_logs.txt' 

         # write the slurm file
         beta.write_slurm(opfile = bash_script,
                         jobname = 'clean_up_' + myms,
                         logfile = logfile,
                         mail_ad = address_mail,
                         syscall = bash_command)

         job_id_rem_log = 'CLEAN_UP_' + myms
         syscall = job_id_rem_log+"=`sbatch -d afterok:${"+job_id_aimfast1+"} "+bash_script+" | awk '{print $4}'`"
         # write the syscall command to the submit file
         f.write(syscall+'\n')

         # ------------------------------------------------------------------------------

    #-----------------------------------------------------------------------------------
    # This code exists outside of the main loop 
    #-----------------------------------------------------------------------------------
    # Generating gif

    # the name of the shell script that gets run
    bash_script = SCRIPTS + '/convert_gif.sh' # name of the slurm file
    # name of the log file for gif.sh std out dump
    logfile   = LOGS + '/convert_gif.log'  # name of log file
    
    bash_command  = 'singularity exec ' + IMAGE_MAGIC_CONTAINER + ' ' 
    bash_command += 'convert -delay 150 reports/*img*data.png loop 0 reports/data.gif'

    # write the slurm file
    beta.write_slurm(opfile  = bash_script,
                     jobname = 'cnvrt_gif', # this is the name that's displayed on squeue
                     logfile = logfile,
                     mail_ad = address_mail,
                     syscall = bash_command)


    # initialise the job Id with the base name of the job ID's
    job_all_report = '${REPORT_POST_' 
    # insterts the actual job id's into the base name given above
    for msfile in mslist: 
        job_all_report += msfile + "}:${REPORT_POST_"

    # remove the extra ":REPORT_POST_"
    job_all_report = job_all_report[:-15] 
    
    # name of job that generetes the gifs
    job_gif = "GIF_ALL"

    # writes to the submit file, information about queuing and dependencies
    syscall = job_gif+"=`sbatch -d afterok:"+job_all_report+" "+bash_script+" | awk '{print $4}'`"
    f.write(syscall+'\n')

    #-----------------------------------------------------------------------------------

    f.close()
    yml_file.close()
    
if __name__ == "__main__":


    main()
