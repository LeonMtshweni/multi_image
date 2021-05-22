import glob
import datetime
import time
import os
import sys

# create directories to keep products
def create_dirs():

    cwd = os.getcwd() # get current working directory
    path_list = ['logs','maps','ms_files','scripts','bdsf','casa_junk'] # essential directories
    for path in path_list:
        try:
            os.mkdir(cwd + '/' + path) #make this directory
        except OSError:
            print("The directories %s already exist " % path)


# this function makes an existing file executable
def make_executable(infile):

    mode = os.stat(infile).st_mode
    mode |= (mode & 0o444) >> 2
    os.chmod(infile, mode)

# this function write the to contain the image data
def write_table(opfile):
    t = open(opfile,'w')
    t.writelines(['img_name  rms  dynamic_range  flux\n'])
    t.close()

def selfcal_cubical():
    syscall  = 'gocubical '
    syscall += '--sol-jones G 
    syscall += --data-ms /stimela_mount/msdir/8sec_ch3_ch7_removed_lo.ms 
    syscall += --data-column DATA 
    syscall += --data-time-chunk 1 
    syscall += --data-freq-chunk 0 
    syscall += --model-list MODEL_DATA 
    syscall += --model-ddes auto 
    syscall += --model-pa-rotate 0 
    syscall += --model-feed-rotate 0 
    syscall += --weight-column WEIGHT_SPECTRUM 
    syscall += --flags-auto-init legacy 
    syscall += --flags-reinit-bitflags 0 
    syscall += --madmax-enable 1 
    syscall += --madmax-estimate corr 
    syscall += --madmax-plot 1 
    syscall += --madmax-threshold 10,12 
    syscall += --sol-term-iters 30 
    syscall += --sol-min-bl 300 
    syscall += --dist-ncpu 4 
    syscall += --dist-max-chunks 4 
    syscall += --out-name /stimela_mount/output/delayself_0 
    syscall += --out-overwrite 1 
    syscall += --out-mode sc 
    syscall += --out-column CORRECTED_DATA 
    syscall += --out-casa-gaintables 1 
    syscall += --log-verbose solver=2 
    syscall += --g-time-int 15 
    syscall += --g-freq-int 0 
    syscall += --g-clip-low 0.5 
    syscall += --g-clip-high 2.5 
    syscall += --g-solvable 1 
    syscall += --g-type f-slope 
    syscall += --g-save-to /stimela_mount/output/phase-0-0.parmdb
    
# this function writes the slurm/bash script 
def write_slurm(opfile,
                jobname,
                logfile,
                syscall,
                mail_ad,
                time='72:00:00',  
                partition='Main',
                ntasks='1',
                nodes='1',
                cpus='4',
                mem='32GB'):

    f = open(opfile,'w')
    f.writelines(['#!/bin/bash\n',
        '#file: '+opfile+':\n',
        '#SBATCH --job-name='+jobname+'\n',
        '#SBATCH --time='+time+'\n',
        '#SBATCH --partition='+partition+'\n'
        '#SBATCH --ntasks='+ntasks+'\n',
        '#SBATCH --nodes='+nodes+'\n',
        '#SBATCH --cpus-per-task='+cpus+'\n',
        '#SBATCH --mem='+mem+'\n',
        '#SBATCH --mail-user='+mail_ad+'\n',
        '#SBATCH --mail-type=END,FAIL,TIME_LIMIT\n',
        '#SBATCH --output='+logfile+'\n',
        '#SBATCH --error=./logs/'+jobname+'_std_err.log\n',
        syscall+'\n',
#        'singularity exec '+container+' '+syscall+'\n',
        'sleep 10\n'])
    f.close()

    make_executable(opfile)


# this function sets up the command for wsclean_blind
def generate_syscall_wsclean(mslist,
                          imgname,
                          datacol,
                          minuvw_range,
                          briggs,
                          mask,
                          size_auto_mask,
                          threshold_auto,
                          multiscale,
                          scales,
                          taper_uv,
                          beam_size,
                          startchan=-1,
                          endchan=-1,
                          chanout=8,
                          imsize=5096,
                          cellsize='1.3asec',
                          niter=120000,
                          sourcelist=True,
                          bda=False,
                          nomodel=True,
                          fitspectralpol=2):

    # Generate system call to run wsclean
 

    syscall = 'wsclean '
    syscall += '-log-time '
    if sourcelist and fitspectralpol != 0:
        syscall += '-save-source-list '
    syscall += '-size '+str(imsize)+' '+str(imsize)+' '
    syscall += '-scale '+cellsize+' '
    if bda:
        syscall += '-baseline-averaging 24 '
        syscall += '-no-update-model-required '
    elif not bda and nomodel:
        syscall += '-no-update-model-required '
    if multiscale == 'True':
        # replace the semicolon separators with commas
        scales = scales.replace(";",",")
        syscall += '-multiscale '
        syscall += '-multiscale-scales '+scales+' '
        syscall += '-multiscale-scale-bias 0.6 '
    syscall += '-niter '+str(niter)+' '
    syscall += '-gain 0.1 '
    syscall += '-mgain 0.9 '
    syscall += '-nmiter 20 '
    syscall += '-weight briggs '+str(briggs)+' '
    if taper_uv == 'True':
        syscall += '-taper-gaussian ' + str(beam_size) + ' '
    syscall += '-data-column '+datacol+' '
    syscall += '-auto-threshold ' +str(threshold_auto)+' '
    if minuvw_range != 'nill':
        syscall += '-minuvw-m ' + minuvw_range + ' '
    if startchan != -1 and endchan != -1:
        syscall += '-channel-range '+str(startchan)+' '+str(endchan)+' '
    if mask.lower() != 'auto':
        syscall += '-fits-mask ' + mask + ' '
    elif mask.lower() == 'none':
        syscall += ''
    elif mask.lower() == 'auto':
        syscall += '-auto-mask '+str(size_auto_mask)+' '
    syscall += '-no-small-inversion '
    syscall += '-pol I '
    syscall += '-no-negative '
    syscall += '-name '+imgname+' '
    syscall += '-channels-out '+str(chanout)+' '
    if fitspectralpol != 0:
        syscall += '-fit-spectral-pol '+str(fitspectralpol)+' '
    syscall += '-join-channels '
    syscall += '-padding 1.3 '
    #syscall += '-abs-mem 8 '
    syscall += '-weighting-rank-filter-size 16 '
    syscall += '-grid-mode kb '
    syscall += '-kernel-size 7 ' 
    syscall += '-fit-beam '


    for myms in mslist:
        syscall += myms+' '

    return syscall

# this function sets up the command for wsclean_predict
def generate_syscall_predict(msname,
                            imgbase,
                            channelsout=8,
                            imsize=5096,
                            cellsize='1.3asec',
                            predictchannels=64):

    # Generate system call to run wsclean in predict mode

    syscall = 'wsclean '
    syscall += '-log-time '
    syscall += '-predict '
    syscall += '-channels-out '+str(channelsout)+' '
    syscall += ' -size '+str(imsize)+' '+str(imsize)+' '
    syscall += '-scale '+cellsize+' '
    syscall += '-name '+imgbase+' '
    syscall += '-absmem 8 '
    syscall += '-predict-channels '+str(predictchannels)+' '
    syscall += msname

    return syscall

