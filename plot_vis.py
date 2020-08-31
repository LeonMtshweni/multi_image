import os,sys


myms = sys.argv[1]
data_column = sys.argv[2]

#---------------------------------------------------------------------------------------------------------------------
# create sub dirs for all plots for each ms run
path = cwd + '/visplots/' + myms[:-3]
# create fir for the plots
if not os.path.exists(path):
    os.makedirs(path)

#----------------------------------------------------------------------------------------------------------------------
# List of antennas

antennas = 'm000,m002,m003,m004,m005,m007,m008,m009,m010,m011,m012,m013,m014,m015,m016\
,m017,m018,m019,m020,m021,m022,m023,m024,m025,m026,m027,m028,m029,m030,m031,m032,m033\
,m034,m035,m036,m037,m038,m040,m041,m042,m043,m044,m045,m046,m047,m048,m049,m050,m051\
,m052,m053,m054,m055,m056,m057,m058,m059,m060,m061,m062,m063'
#---------------------------------------------------------------------------------------------------------------------
# SHADEMS command

commander = ['--xaxis TIME,CHAN,UV --yaxis '+data_column+':amp,'+data_column+':amp,'+data_column+':amp --corr ', # amplitude plots
        '--xaxis TIME,CHAN,UV --yaxis '+data_column+':phase,'+data_column+':phase,'+data_column+':phase --corr '] # phase plots

for command in commander:
    os.system('shadems ' + command + ' --dir ' + path + ' ' + myms)
