# scripts  by Roy Haggerty for WW2100 data vis
# modified by Owen Haggerty summer 2014
# 
# Cascade plots 
#
# February, 2014 - February, 2015
#
# Python 2.7
# Dependencies & libraries that need to be installed:
#    numpy
#    matplotlib
#    xlrd
#

########################################################################################
########################################################################################
########################################################################################

def cascade(
            AltScenario,
            file_model_csv,             #the name of the reference file
            file_stats,                 #the name of the stats file (if available)
            stats_list,                 #a list of the stats files
            title,                      #the title of the graph to be generated
            flood_Q,                    #the level of the flood line
            file_name_list,             #list of file names
            data_type_list,             #list of data_types associated with file names
            breadth_str,                #scenarios to gray-shade on top of main scenario
            breadth_str_2nd,            #second set of scenarios, to be red-shaaded
            breadth_str_3rd,            #third set of scenarios, to be green-shaaded
            data_type = 'stream',       #the type of data
            flood_Q_available = False,  #whether the flood level is available
            Display = False,            #whether the graph is to be displayed(True) or saved as a PNG file(False)
            stats_available = False,    #whether there is an associated stats file
            SI = True                   #Whether the units are American Standard(True) or Metric(False)
            ):

    """
    Make a cascade plot and associated side & bottom graphs to show time series
    of discharge.  Shade some of the lines with range of possible values for
    alternative scenarios.
    """
    
    
    import numpy as np
    import matplotlib.pyplot as plt
    import datetime
    import time as timetool, os.path
    import matplotlib as mpl
    import constants_cp as cst   # constants.py contains constants used here
    import matplotlib.gridspec as gridspec
    from   mpl_toolkits.axes_grid1 import make_axes_locatable
    import metadata as md
    import collections
    from movingaverage import movingaverage
    
    np.set_printoptions(precision=3) 
    
    # This checks to see if there is anything in the second & third breadth columns:
    if isinstance(breadth_str_2nd, unicode):
         request_2nd = True
    else:
        request_2nd = False
    if isinstance(breadth_str_3rd, unicode):
        request_3rd = True
    else:
        request_3rd = False
        
    # Generate list of model runs to be gray-shaded, and place comparitor into
    # first slot in that list.
    model_run, primary = md.define_model_run(file_model_csv)  #primary is comparitor
    breadth_str = breadth_str.replace(" ","")
    breadth_str = breadth_str.replace(primary+",","").replace(","+primary,"") #remove primary
    breadth_str = primary + ',' + breadth_str #place primary in first slot
    breadth = breadth_str.split(",")  # breadth is list of model runs that will be grey-shaded.
    breadth_collection = collections.Counter(breadth)
    breadth_all_collection = breadth_collection

    if request_2nd:
        breadth_str_2nd = breadth_str_2nd.replace(" ","")
        breadth_str_2nd = breadth_str_2nd.replace(primary+",","").replace(","+primary,"") #remove primary
        breadth_str_2nd = primary + ',' + breadth_str_2nd #place primary in first slot
        breadth_2nd = breadth_str_2nd.split(",")  # breadth_2nd is list of model runs that will be red-shaded.
        breadth_2nd_collection = collections.Counter(breadth_2nd)
        breadth_all_collection = (breadth_collection - breadth_2nd_collection) +\
            breadth_2nd_collection
    
    if request_3rd:
        breadth_str_3rd = breadth_str_3rd.replace(" ","")
        breadth_str_3rd = breadth_str_3rd.replace(primary+",","").replace(","+primary,"") #remove primary
        breadth_str_3rd = primary + ',' + breadth_str_3rd #place primary in first slot
        breadth_3rd = breadth_str_3rd.split(",")  # breadth_2nd is list of model runs that will be red-shaded.
        breadth_3rd_collection = collections.Counter(breadth_3rd)
        breadth_all_collection = (breadth_collection - breadth_2nd_collection - breadth_3rd_collection) +\
            breadth_2nd_collection + breadth_3rd_collection
    
    file_model_csv_list = [file_model_csv.replace(primary, Case) for Case in breadth_all_collection]
    file_model_csv_w_path_list = [cst.path_data + file_model_csv.replace(primary, Case) for Case in breadth_all_collection]
    
    file_stats_w_path = cst.path_auxilliary_files + file_stats
    
    inum = 0
    for Case in breadth_all_collection:
        
        file_model_csv = file_model_csv_list[inum]
        file_model_csv_w_path = file_model_csv_w_path_list[inum]
        file_breadth_list = []
        for file_name in file_name_list:
            file_breadth_list.append(file_name.replace(AltScenario,Case))
    
#       Collect data for plotting from csv file:
        data_2D, data_2D_clipped, data_yr, time, data_length, num_water_yrs, \
            start_year, end_year, graph_name_tmp, plot_structure, error_check, \
            mass_balance_err_str, mean_Q \
            \
            = collect_data(
                file_model_csv, file_model_csv_w_path, file_stats_w_path, \
                data_type, data_type_list, file_breadth_list, \
                stats_list, stats_available, SI \
                )
            
        data_set_rhs_1, data_set_rhs_2, data_set_rhs_3 \
            = process_data(
                data_2D, data_yr, num_water_yrs, data_length, \
                data_type, data_type_list, SI,\
                start_year, end_year
                )
        
        data_early, data_mid, data_late, window, averaging_window \
            = process_bottom_strip(
                data_2D, data_yr, num_water_yrs, data_length, \
                data_type, data_type_list, SI,\
                start_year, end_year
                )
                
        if Case in breadth_collection:
            try:
              data_set_rhs_3_gray
            except NameError:
                data_set_rhs_3_gray = np.expand_dims(data_set_rhs_3,axis=1)
                data_bottom_gray = np.expand_dims(data_late,axis=1)
            else:
                data_set_rhs_3_gray = np.concatenate((data_set_rhs_3_gray, \
                                    np.expand_dims(data_set_rhs_3,axis=1)),axis=1)
                data_bottom_gray = np.concatenate((data_bottom_gray, \
                                    np.expand_dims(data_late,axis=1)),axis=1)
        if request_2nd and Case in breadth_2nd_collection:
            try:
                 data_set_rhs_3_red
            except NameError:
                data_set_rhs_3_red = np.expand_dims(data_set_rhs_3,axis=1)
                data_bottom_red_late = np.expand_dims(data_late,axis=1)
            else:
                data_set_rhs_3_red = np.concatenate((data_set_rhs_3_red, \
                                    np.expand_dims(data_set_rhs_3,axis=1)),axis=1)
                data_bottom_red_late = np.concatenate((data_bottom_red_late, \
                                    np.expand_dims(data_late,axis=1)),axis=1)
           
        if request_3rd and Case in breadth_3rd_collection:
            try:
                 data_set_rhs_3_green
            except NameError:
                data_set_rhs_3_green = np.expand_dims(data_set_rhs_3,axis=1)
                data_bottom_green_late = np.expand_dims(data_late,axis=1)
            else:
                data_set_rhs_3_green = np.concatenate((data_set_rhs_3_green, \
                                    np.expand_dims(data_set_rhs_3,axis=1)),axis=1)
                data_bottom_green_late = np.concatenate((data_bottom_green_late, \
                                    np.expand_dims(data_late,axis=1)),axis=1)
           
        if Case == primary: 
            graph_name = graph_name_tmp
            graph_title = cst.metadata.define_model_run(file_model_csv)[0]
            file_title = file_model_csv

            # Save comparitor data in variables beginning with s
            sdata_set_rhs_1, sdata_set_rhs_2, sdata_set_rhs_3, \
                sdata_early, sdata_mid, sdata_late, \
                sdata_2D, sdata_2D_clipped \
            = data_set_rhs_1, data_set_rhs_2, data_set_rhs_3, \
                data_early, data_mid, data_late, \
                data_2D, data_2D_clipped 
            pass
                
        inum += 1
             
    data_set_rhs_3_min_gray = np.amin(data_set_rhs_3_gray,1)
    data_set_rhs_3_max_gray = np.amax(data_set_rhs_3_gray,1)
    data_bottom_min_gray = np.amin(data_bottom_gray,1)
    data_bottom_max_gray = np.amax(data_bottom_gray,1)

    if request_2nd:
        data_set_rhs_3_min_red = np.amin(data_set_rhs_3_red,1)
        data_set_rhs_3_max_red = np.amax(data_set_rhs_3_red,1)
#1        data_bottom_min_red_early = np.amin(data_bottom_red_early,1)
#1        data_bottom_max_red_early = np.amax(data_bottom_red_early,1)
#1        data_bottom_min_red_mid = np.amin(data_bottom_red_mid,1)
#1        data_bottom_max_red_mid = np.amax(data_bottom_red_mid,1)
        data_bottom_min_red_late = np.amin(data_bottom_red_late,1)
        data_bottom_max_red_late = np.amax(data_bottom_red_late,1)
 
    if request_3rd:
        data_set_rhs_3_min_green = np.amin(data_set_rhs_3_green,1)
        data_set_rhs_3_max_green = np.amax(data_set_rhs_3_green,1)
        data_bottom_min_green_late = np.amin(data_bottom_green_late,1)
        data_bottom_max_green_late = np.amax(data_bottom_green_late,1)
 
    data_set_rhs_1, data_set_rhs_2, data_set_rhs_3, \
        data_early, data_mid, data_late, \
        data_2D, data_2D_clipped \
    = sdata_set_rhs_1, sdata_set_rhs_2, sdata_set_rhs_3, \
        sdata_early, sdata_mid, sdata_late, \
        sdata_2D, sdata_2D_clipped, 
          
    ylabel2, ylabel4 \
        = get_labels(
            data_2D, data_yr, num_water_yrs, data_length, \
            data_type, data_type_list, SI,\
            start_year, end_year
            )

      
    ##########################################################
    #   Prepare the figure "canvas"                          #
    ##########################################################

    if data_type != 'temperature' and data_type != 'aridity' and\
                    'water_deficit' not in data_type and\
                    data_type != 'h_drought' and\
                    data_type != 'CWDtoD' and\
                    data_type != 'ratio_min_to_discharge':
        cmap1 = mpl.colors.LinearSegmentedColormap.from_list('my_cmap',['white','blue'],256)
    else:
        cmap1 = mpl.colors.LinearSegmentedColormap.from_list('my_cmap',['white',(0.9,0.1,0.1)],256)
        
    fig = plt.figure(1, figsize=(10,7.5))
#    fig = plt.figure(1, figsize=(12,8))
    width_ratios=[3.5, 1.1, 1.1, 2.]
    height_ratios = [4., 1.5]
    wspace = 0.1     # horizontal space btwn figs
    hspace = 0.08     # vertical space btwn figs
    
    ###### Figure canvas left side
    if plot_structure == '4 by 2':
        gs1 = gridspec.GridSpec(2, 4, width_ratios=width_ratios,
                                height_ratios=height_ratios,
                                wspace = wspace)
    elif plot_structure == '3 by 2':
        gs1 = gridspec.GridSpec(2, 3, width_ratios=width_ratios,
                                height_ratios=height_ratios, 
                                wspace = wspace)
    gs1.update(left=0.1, right = 1.1, wspace=wspace, hspace = hspace)  
    
    ##########################################################
    #   Prep the first plot (cascade)                        #
    ##########################################################

    ax = fig.add_subplot(gs1[0,0])
    p = plt.imshow(data_2D_clipped, origin='lower', cmap = cmap1, aspect='auto',                     # with revised color ramp
                  extent=[cst.day_of_year_oct1, 365 + cst.day_of_year_oct1 - 1 , start_year, end_year]) 
    month_labels(ax)
    ax.set_ylabel('$Water \, Year$', fontsize=14)
    ticks=np.arange(2020,2100,10)
    ticklabels = ['%i'%w for w in np.arange(2020,2100,10)]
    plt.ticklabel_format(axis='y',style='plain',useOffset=False)
    plt.yticks(ticks, ticklabels, fontsize=14)
    plt.title(graph_title,fontsize=12)
    plt.suptitle(title, fontsize = 18)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.85, lw=0)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.04, aspect=20)
    plt.colorbar(p,cax=cax).set_label(ylabel2)

    ##########################################################
    #   Prep the fourth plot (bottom strip)                  #
    ##########################################################
    
    ax4 = fig.add_subplot(gs1[1,0], aspect = 'auto', sharex=ax)
    ax4.plot(range(cst.day_of_year_oct1, 365 + cst.day_of_year_oct1),
             data_early,  '--', color="0.0", lw=1.5)
    ax4.plot(range(cst.day_of_year_oct1, 365 + cst.day_of_year_oct1),
             data_mid, color="0.32", lw=1.)
    ax4.plot(range(cst.day_of_year_oct1, 365 + cst.day_of_year_oct1),
             data_late, color="0.", lw=2.)
    ax4.fill_between(range(cst.day_of_year_oct1, 365 + cst.day_of_year_oct1),
             data_bottom_min_gray, data_bottom_max_gray, color="blue", alpha = 0.3)
    if request_2nd: 
#1        ax4.fill_between(range(cst.day_of_year_oct1, 365 + cst.day_of_year_oct1),
#1             data_bottom_min_red_early, data_bottom_max_red_early, color="red", alpha = 0.3)
#1        ax4.fill_between(range(cst.day_of_year_oct1, 365 + cst.day_of_year_oct1),
#1             data_bottom_min_red_mid, data_bottom_max_red_mid, color="red", alpha = 0.3)
        ax4.fill_between(range(cst.day_of_year_oct1, 365 + cst.day_of_year_oct1),
             data_bottom_min_red_late, data_bottom_max_red_late, color="red", alpha = 0.3)
    if request_3rd: 
        ax4.fill_between(range(cst.day_of_year_oct1, 365 + cst.day_of_year_oct1),
             data_bottom_min_green_late, data_bottom_max_green_late, color="green", alpha = 0.3)
    if stats_available:
        ax4.plot(range(cst.day_of_year_oct1, 365 + cst.day_of_year_oct1),
             movingaverage(
                 [mean_Q[i] for i in range(365-averaging_window/2, 364)] +\
                 [mean_Q[i] for i in range(365)] +\
                 [mean_Q[i] for i in range(averaging_window/2)],
                 window)[averaging_window/2 : 365+averaging_window/2]
                 , 'k--', lw=1.5)
    month_labels(ax4)
    ax4.set_xlabel('$Month \, of \, Year$', fontsize=14)
    ax4.set_ylabel(ylabel4, fontsize=14)
    if stats_available:
        ax4.legend(('Early century', 'Mid century', 'Late century','20$^{\t{th}}$ century'),
               loc='best',frameon=False, fontsize=12)
    else:
        ax4.legend(('Early century', 'Mid century', 'Late century'),
                   loc='best',frameon=False, fontsize=12)

#   Uncomment this to set a limit on y axis:
#    ax4.set_ylim(0, 50)
        
    divider2 = make_axes_locatable(ax4)
    cax2 = divider2.append_axes("right", size="5%", pad=0.01)
    cax2.axis('off')
    cax2.set_visible(False)
    max_yticks = 5
    yloc = plt.MaxNLocator(max_yticks)
    ax4.yaxis.set_major_locator(yloc)
    plt.colorbar(cax=cax2)
    
    ##########################################################
    #   Prep the right side figure canvas                    #
    #   Generate parameters common to one or both plots      #
    ##########################################################
    
    if plot_structure == '4 by 2':
        gs2 = gridspec.GridSpec(2, 4, width_ratios=width_ratios,
                                height_ratios=height_ratios)
    elif plot_structure == '3 by 2':
        gs2 = gridspec.GridSpec(2, 3, width_ratios=[width_ratios[i] for i in [0,1,3]],
                                height_ratios=height_ratios)
        
    gs2.update(left=0.35, right = 0.94, wspace=wspace, hspace = hspace)
    
    max_xticks = 2
    y = range(start_year,end_year)
    
    ##########################################################
    #   Prep the second plot (strip chart, right)            #
    ##########################################################
 
    ax2 = fig.add_subplot(gs2[0,1], aspect = 'auto', sharey=ax)
    BoxPlot(ax2, data_set_rhs_1)
    xloc = plt.MaxNLocator(max_xticks)
    ax2.xaxis.set_major_locator(xloc)
    plt.yticks(ticks, fontsize=14)
    plt.ylim(start_year,end_year)
    if data_type == 'stream' or \
       data_type == 'daminWdup' or \
       data_type == 'damoutWdup' or \
       data_type == 'damin' or \
       data_type == 'damout' or \
       data_type == 'tot_damin' or \
       data_type == 'tot_damout' or\
       data_type == 'tot_damdiff' or\
       data_type == 'creek_sums':

        plt.xlabel('$Min \, Q$', fontsize = 14)
        if data_type == 'tot_damdiff':
            plt.xlabel('$Min \, \Delta Q$', fontsize = 14)
        
    elif data_type == 'pool' or data_type == 'pool_indiv':
        plt.xlabel('$Min \, \Delta Ht$', fontsize = 14)
        
    elif data_type == 'snow':
        plt.xlabel('$Apr \, 1\, SWE$', fontsize = 14)
        
    elif data_type == 'precipitation':
        plt.xlabel('$Ann \, Precip$', fontsize = 14)
    
    elif data_type == 'irrigation':
        plt.xlabel('$Tot \, Ann \, Irrig\,$', fontsize = 14)

    elif data_type == 'tot_extract' or \
       data_type == 'aridity' or\
       data_type == 'tot_consumed':
        plt.xlabel('$Min\,$', fontsize = 14)
    elif data_type == 'ratio_min_to_discharge':
            plt.xlabel('$Max\, Ratio$', fontsize = 14)        
    elif data_type == 'ratio_avail_to_consum' :
            plt.xlabel('$Min\, Ratio$', fontsize = 14)        
    elif data_type == 'instream' or \
        data_type == 'CWDtoD':
            plt.xlabel('$Max\,$', fontsize = 14)

    elif data_type == 'swe_pre' or data_type == 'aridity':
        plt.xlabel('$Apr \, 1\, SWE:Pre$', fontsize = 14)

    elif data_type == 'municipal' or data_type == 'muni_alloc_big4' or \
        data_type == 'muni_less_disch' or data_type == 'muni_less_disch_big4':
        plt.xlabel('$Tot \, Ann \, Mncpl\,$', fontsize = 14)

    elif data_type == 'water_rights':
        plt.xlabel('$Tot \, Unxczd \, Wtr\, Rt\,$', fontsize = 14)

    elif data_type == 'temperature':
        plt.xlabel('$Min\,T\,$', fontsize = 14)            

    elif data_type == 'et' or\
         data_type == 'for_et' or\
         data_type == 'ag_et':
        plt.xlabel('$Tot \, ET$', fontsize = 14)

    elif data_type == 'potet' or\
         data_type == 'for_potet' or\
         data_type == 'ag_potet':
        plt.xlabel('$Tot \, PET$', fontsize = 14)
            
    elif data_type == 'water_deficit':
        plt.xlabel('$Max \, WD$', fontsize = 14)

    elif data_type == 'h_drought':
        plt.xlabel('$Tot \, DD$', fontsize = 14)

    ax2.yaxis.set_visible(False)

    ##########################################################
    #   Prep the third plot (2nd strip chart, right)         #
    ##########################################################

    if plot_structure == '4 by 2':
        ax3 = fig.add_subplot(gs2[0,2], aspect = 'auto', sharey=ax)
        if flood_Q_available:
            if not SI: flood_Q = flood_Q / cst.cfs_to_m3
            flood_Q_line = np.ones(90) * flood_Q
            plt.plot(flood_Q_line, np.append(np.array(y),2100), 'r-', lw=1.)
            textstr2 = 'Flood stage'
            props2 = dict(boxstyle='round', facecolor='w', alpha=0.3, lw=0)
            ax3.text(0.45, 0.31, textstr2, color='r', transform=ax3.transAxes,
                     fontsize=12, verticalalignment='top', bbox=props2, rotation = 'vertical')
            
        BoxPlot(ax3, data_set_rhs_2)
        xloc = plt.MaxNLocator(max_xticks)
        ax3.xaxis.set_major_locator(xloc)
        plt.ylim(start_year,end_year)
        ax3.yaxis.set_visible(False)
        if data_type == 'stream' or \
           data_type == 'daminWdup' or \
           data_type == 'damoutWdup' or \
           data_type == 'damin' or \
           data_type == 'damout' or \
           data_type == 'tot_damin' or \
           data_type == 'tot_damout' or\
           data_type == 'tot_damdiff' or\
           data_type == 'creek_sums':

            plt.xlabel('$Max \, Q$', fontsize = 14)
            if data_type == 'tot_damdiff':
                plt.xlabel('$Max \, \Delta Q$', fontsize = 14)
            
        elif data_type == 'pool' or data_type == 'pool_indiv':
            plt.xlabel('$Max$', fontsize = 14)
        elif data_type == 'temperature':
            plt.xlabel('$Max \, T$', fontsize = 14)
        elif data_type == 'tot_extract' or\
             data_type == 'aridity' or\
             data_type == 'tot_consumed':
            plt.xlabel('$Max \,$', fontsize = 14)

    ##########################################################
    #   Prep the fifth plot (3nd strip chart, right)         #
    ##########################################################

    line_shade = "0.1"

    if plot_structure == '4 by 2':
        ax5 = fig.add_subplot(gs2[0,3], aspect = 'auto', sharey=ax)
    else:
        ax5 = fig.add_subplot(gs2[0,2], aspect = 'auto', sharey=ax)

        xloc = plt.MaxNLocator(max_xticks)
        ax5.xaxis.set_major_locator(xloc)
        plt.ylim(start_year,end_year)
        ax5.yaxis.tick_right()
        plt.yticks(ticks, fontsize=14)
    if data_type == 'stream' or \
       data_type == 'daminWdup' or \
       data_type == 'damoutWdup' or \
       data_type == 'damin' or \
       data_type == 'damout' or \
       data_type == 'tot_damin' or \
       data_type == 'tot_damout' or\
       data_type == 'tot_damdiff' or\
       data_type == 'creek_sums':
        
        ax5.plot(data_set_rhs_3, range(start_year,end_year), color=line_shade, lw=1.5)
        if data_type != 'tot_damdiff':
            if SI:
                plt.xlabel('$Avg \, Q$ [m$^{\t{3}}$/s]', fontsize = 14)
            else:
                plt.xlabel('$Avg \, Q$ [cfs]', fontsize = 14)
        else:
            if SI:
                plt.xlabel('$Avg \, \Delta Q$ [m$^{\t{3}}$/s]', fontsize = 14)
            else:
                plt.xlabel('$Avg \, \Delta Q$ [cfs]', fontsize = 14)
        
    elif data_type == 'pool' or data_type == 'pool_indiv':
        
        ax5.plot(data_set_rhs_3, range(start_year,end_year), color=line_shade, lw=1.5)
        if SI:
            plt.xlabel('$Avg \, \Delta \, Pool \, Ht$ [m]', fontsize = 14)
        else:
            plt.xlabel('$Avg \, \Delta \, Pool \, Ht$ [ft]', fontsize = 14)
            
    elif data_type == 'temperature':
        
        ax5.plot(data_set_rhs_3, range(start_year,end_year), color=line_shade, lw=1.5)
        if SI:
            plt.xlabel('$Avg \, T$ [$^{\circ}\mathrm{C}$]', fontsize = 14)
        else:
            plt.xlabel('$Avg \, T$ [$^{\circ}\mathrm{F}$]', fontsize = 14)
            
    elif data_type == 'snow':
        
        ax5.plot(data_set_rhs_3, range(start_year,end_year), color=line_shade, lw=1.5)
        if SI:
            plt.xlabel('$Ann$ [mm]', fontsize = 14)
        else:
            plt.xlabel('$Ann$ [in]', fontsize = 14)
        
    elif data_type == 'swe_pre':
        
        ax5.plot(data_set_rhs_3, range(start_year,end_year), color=line_shade, lw=1.5)
        plt.xlabel('\n$Max\,Late-season \,SWE/Precip$ [-]', fontsize = 14)
        
    elif data_type == 'precipitation':

        ax5.plot(data_set_rhs_3*365., range(start_year,end_year), color=line_shade, lw=1.5)
        data_set_rhs_3_min_gray = data_set_rhs_3_min_gray*365.
        data_set_rhs_3_max_gray = data_set_rhs_3_max_gray*365.
        if request_2nd:
            data_set_rhs_3_min_red = data_set_rhs_3_min_red*365.
            data_set_rhs_3_max_red = data_set_rhs_3_max_red*365.
        if request_3rd:
            data_set_rhs_3_min_green = data_set_rhs_3_min_green*365.
            data_set_rhs_3_max_green = data_set_rhs_3_max_green*365.

        if SI:
            plt.xlabel('$Precip$ [mm]', fontsize = 14)
        else:
            plt.xlabel('$Precip$ [in]', fontsize = 14)
    
    elif data_type == 'irrigation':
        if SI:
            plt.xlabel('$Tot \, Ann \, Irrig\,$\n[million m$^3$]', fontsize = 14)
            ax5.plot(data_set_rhs_3*cst.million_peryr_factor, range(start_year,end_year), color=line_shade, lw=1.5)
            data_set_rhs_3_min_gray = data_set_rhs_3_min_gray*cst.million_peryr_factor
            data_set_rhs_3_max_gray = data_set_rhs_3_max_gray*cst.million_peryr_factor
            if request_2nd:
                data_set_rhs_3_min_red = data_set_rhs_3_min_red*cst.million_peryr_factor
                data_set_rhs_3_max_red = data_set_rhs_3_max_red*cst.million_peryr_factor
            if request_3rd:
                data_set_rhs_3_min_green = data_set_rhs_3_min_green*cst.million_peryr_factor
                data_set_rhs_3_max_green = data_set_rhs_3_max_green*cst.million_peryr_factor
            
        else:
            plt.xlabel('$Tot \, Ann \, Irrig\,$\n[thousand ac-ft]', fontsize = 14)
            ax5.plot(data_set_rhs_3, range(start_year,end_year), color=line_shade, lw=1.5)
            data_set_rhs_3_min_gray = data_set_rhs_3_min_gray
            data_set_rhs_3_max_gray = data_set_rhs_3_max_gray
            if request_2nd:
                data_set_rhs_3_min_red = data_set_rhs_3_min_red
                data_set_rhs_3_max_red = data_set_rhs_3_max_red
            if request_3rd:
                data_set_rhs_3_min_green = data_set_rhs_3_min_green
                data_set_rhs_3_max_green = data_set_rhs_3_max_green

    elif data_type == 'tot_extract' or\
         data_type == 'tot_consumed':

        ax5.plot(data_set_rhs_3, range(start_year,end_year), color=line_shade, lw=1.5)
        if SI:
            plt.xlabel('$Avg \, Extract\,$\n[m$^3$/s]', fontsize = 14)
        else:
            plt.xlabel('$Avg \, Extract\,$\n[thousand ac-ft]', fontsize = 14)

    elif data_type == 'CWDtoD':

        ax5.plot(data_set_rhs_3, range(start_year,end_year), color=line_shade, lw=1.5)
        plt.xlabel('$Avg\, Fraction$\n[-]', fontsize = 14)

    elif data_type == 'ratio_min_to_discharge':
        ax5.plot(data_set_rhs_3, range(start_year,end_year), color=line_shade, lw=1.5)
        plt.xlabel('$Max\, Ratio\,$ [-]', fontsize = 14)
        
    elif data_type == 'ratio_avail_to_consum' :
        ax5.plot(data_set_rhs_3, range(start_year,end_year), color=line_shade, lw=1.5)
        plt.xlabel('$Min\, Ratio\,$ [-]', fontsize = 14)
        
    elif data_type == 'instream':
        
        if SI:
            ax5.plot(data_set_rhs_3, range(start_year,end_year), color=line_shade, lw=1.5)
            plt.xlabel('$Avg \, Right\,$\n[m$^3$/d]', fontsize = 14)
        else:
            ax5.plot(data_set_rhs_3/1000., range(start_year,end_year), color=line_shade, lw=1.5)
            plt.xlabel('$Avg \, Right\,$\n[thousand ac-ft/d]', fontsize = 14)

    elif data_type == 'aridity':

        ax5.plot(data_set_rhs_3, range(start_year,end_year), color=line_shade, lw=1.5)
        if SI:
            plt.xlabel('$Aridity \,Idx$\n[-]', fontsize = 14)
        else:
            plt.xlabel('$Aridity \,Idx$\n[thousand ac-ft]', fontsize = 14)

    elif data_type == 'municipal' or data_type == 'muni_alloc_big4' or \
        data_type == 'muni_less_disch' or data_type == 'muni_less_disch_big4':

        if SI:
            plt.xlabel('$Tot \, Ann \, Mncpl\,$\n[million m$^3$]', fontsize = 14)
            ax5.plot(data_set_rhs_3*cst.million_peryr_factor, range(start_year,end_year), color=line_shade, lw=1.5)
            data_set_rhs_3_min_gray = data_set_rhs_3_min_gray*cst.million_peryr_factor
            data_set_rhs_3_max_gray = data_set_rhs_3_max_gray*cst.million_peryr_factor
            if request_2nd:
                data_set_rhs_3_min_red = data_set_rhs_3_min_red*cst.million_peryr_factor
                data_set_rhs_3_max_red = data_set_rhs_3_max_red*cst.million_peryr_factor
            if request_3rd:
                data_set_rhs_3_min_green = data_set_rhs_3_min_green*cst.million_peryr_factor
                data_set_rhs_3_max_green = data_set_rhs_3_max_green*cst.million_peryr_factor
            
        else:
            plt.xlabel('$Tot \, Ann \, Mncpl\,$\n[thousand ac-ft]', fontsize = 14)
            ax5.plot(data_set_rhs_3, range(start_year,end_year), color=line_shade, lw=1.5)
            data_set_rhs_3_min_gray = data_set_rhs_3_min_gray
            data_set_rhs_3_max_gray = data_set_rhs_3_max_gray
            if request_2nd:
                data_set_rhs_3_min_red = data_set_rhs_3_min_red
                data_set_rhs_3_max_red = data_set_rhs_3_max_red
            if request_3rd:
                data_set_rhs_3_min_green = data_set_rhs_3_min_green
                data_set_rhs_3_max_green = data_set_rhs_3_max_green

    elif data_type == 'water_rights':

        ax5.plot(data_set_rhs_3*cst.million_peryr_factor, range(start_year,end_year), color=line_shade, lw=1.5)
        data_set_rhs_3_min_gray = data_set_rhs_3_min_gray*cst.million_peryr_factor
        data_set_rhs_3_max_gray = data_set_rhs_3_max_gray*cst.million_peryr_factor
        if request_2nd:
            data_set_rhs_3_min_red = data_set_rhs_3_min_red*cst.million_peryr_factor
            data_set_rhs_3_max_red = data_set_rhs_3_max_red*cst.million_peryr_factor
        if request_3rd:
            data_set_rhs_3_min_green = data_set_rhs_3_min_green*cst.million_peryr_factor
            data_set_rhs_3_max_green = data_set_rhs_3_max_green*cst.million_peryr_factor
            
        if SI:
            plt.xlabel('$Tot \, Unxczd \, Wtr\, Rt\,$\n[million m$^3$]', fontsize = 14)
        else:
            plt.xlabel('$Tot \, Unxczd \, Wtr\, Rt\,$\n[thousand ac-ft]', fontsize = 14)

    elif data_type == 'et' or\
         data_type == 'for_et' or\
         data_type == 'ag_et':

        ax5.plot(data_set_rhs_3*365., range(start_year,end_year), color=line_shade, lw=1.5)
        data_set_rhs_3_min_gray = data_set_rhs_3_min_gray*365.
        data_set_rhs_3_max_gray = data_set_rhs_3_max_gray*365.
        if request_2nd:
            data_set_rhs_3_min_red = data_set_rhs_3_min_red*365.
            data_set_rhs_3_max_red = data_set_rhs_3_max_red*365.
        if request_3rd:
            data_set_rhs_3_min_green = data_set_rhs_3_min_green*365.
            data_set_rhs_3_max_green = data_set_rhs_3_max_green*365.
            
        if SI:
            plt.xlabel('$Tot \, ET$ [mm]', fontsize = 14)
        else:
            plt.xlabel('$Tot \, ET$ [in]', fontsize = 14)

    elif data_type == 'potet' or\
         data_type == 'for_potet' or\
         data_type == 'ag_potet':

        ax5.plot(data_set_rhs_3*365., range(start_year,end_year), color=line_shade, lw=1.5)
        data_set_rhs_3_min_gray = data_set_rhs_3_min_gray*365.
        data_set_rhs_3_max_gray = data_set_rhs_3_max_gray*365.
        if request_2nd:
            data_set_rhs_3_min_red = data_set_rhs_3_min_red*365.
            data_set_rhs_3_max_red = data_set_rhs_3_max_red*365.
        if request_3rd:
            data_set_rhs_3_min_green = data_set_rhs_3_min_green*365.
            data_set_rhs_3_max_green = data_set_rhs_3_max_green*365.
            
        if SI:
            plt.xlabel('$Tot \, PET$ [mm]', fontsize = 14)
        else:
            plt.xlabel('$Tot \, PET$ [in]', fontsize = 14)

    elif data_type == 'water_deficit':

        ax5.plot(data_set_rhs_3, range(start_year,end_year), color=line_shade, lw=1.5)
        if SI:
            plt.xlabel('$Tot \, WD$ [mm]', fontsize = 14)
        else:
            plt.xlabel('$Tot \, WD$ [in]', fontsize = 14)
    
    elif data_type == 'h_drought':

        ax5.plot(data_set_rhs_3, range(start_year,end_year), color=line_shade, lw=1.5)
        plt.xlabel('$Tot \, DD$ [d/y]', fontsize = 14)
    
    ax5.fill_betweenx(range(start_year,end_year), data_set_rhs_3_min_gray, 
                      data_set_rhs_3_max_gray, color="blue", alpha = 0.3)
    if request_2nd:
        ax5.fill_betweenx(range(start_year,end_year), data_set_rhs_3_min_red, 
                      data_set_rhs_3_max_red, color="red", alpha = 0.5)
    if request_3rd:
        ax5.fill_betweenx(range(start_year,end_year), data_set_rhs_3_min_green, 
                      data_set_rhs_3_max_green, color="green", alpha = 0.3)
        
    xloc = plt.MaxNLocator(max_xticks)
    ax5.xaxis.set_major_locator(xloc)
    plt.ylim(start_year,end_year)
#    plt.ticklabel_format(axis='y',style='plain',useOffset=False)
    ax5.yaxis.tick_right()
    plt.yticks(ticks, ticklabels, fontsize=14)

    ###################################################################
    #   Add metadata text box in lower right, citing figure details   #
    ###################################################################
    textstr = 'Willamette Water 2100\n'+cst.metadata.model_run + \
              '\n\n' + ' Graph generated on ' + str(datetime.date.today()) +\
              '\n\n' + ' File: ' + file_title +\
              '\n\n' + ' Data downloaded on ' + timetool.ctime(os.path.getctime(file_model_csv_w_path))
#    if error_check: textstr = textstr + '\n\n' + 'Mass balance error = ' + mass_balance_err_str
    if data_type == 'h_drought': textstr = textstr + '\n\n' +\
    'Hydrological drought as defined in $Prudhomme \, et \, al., \, PNAS$, 2013.'
    props = dict(boxstyle='round', facecolor='white', alpha=0.5, lw=0.)

    ax4.text(1.03, -0.2, textstr, transform=ax.transAxes, fontsize=6,
            verticalalignment='top', bbox=props)

    ##########################################################
    #   Save or display the plots                            #
    ##########################################################

    if Display:
        plt.show()
    else:
        file_graphics = graph_name + '.png'
        plt.savefig(cst.path_write + file_graphics, format="png", dpi=300)
    plt.close(1)

#   End of script for cascade plots


########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################
    
#  Supporting functions

def collect_data( \
    file_model_csv, file_model_csv_w_path, file_stats_w_path, \
    data_type, data_type_list, file_name_list, \
    stats_list, stats_available, SI):

    """
    Collect needed information from csv file and return it for plotting
    """
    
    import numpy as np
    import xlrd
    import constants_cp as cst   # constants.py contains constants used here
    from movingaverage import movingaverage
    from compare import compare_rows
    import rules
    
    ###############################
    # Read data in from csv files #
    # Modify arrays as needed     #
    ###############################
#    file_model_csv_w_path = cst.path_data + file_model_csv       # Add path to data & stats files
    
    data_v = np.array(np.genfromtxt(file_model_csv_w_path, delimiter=',',skip_header=1)) # Read csv file
    mean_Q = 0. # only needed for creek_sum, but must have a value
    if data_type == 'stream': # (default)
        time = data_v[:,0]
        data_yr = data_v[:,1]
        if not SI: data_yr = data_yr/cst.cfs_to_m3
        graph_name = file_model_csv[:-4]
        plot_structure = '4 by 2'
    elif data_type == 'damin':
        time = data_v[:,0]
        data_yr = data_v[:,3]
        if not SI: data_yr = data_yr/cst.cfs_to_m3
        graph_name = file_model_csv[:-4] + '_inflow'
        plot_structure = '4 by 2'
    elif data_type == 'tot_damin':
        time = data_v[:,0]
        data_yr = np.zeros_like(data_v[:,3])
        file_number = -1
        for data_type_check in data_type_list:
            file_number += 1
            if data_type_check == 'damin' and \
               're-regulating' not in file_name_list[file_number] and \
               'Foster' not in file_name_list[file_number] and \
               'Lookout' not in file_name_list[file_number]:
                data_tmp = np.array(np.genfromtxt(cst.path_data + 
                   file_name_list[file_number]
                   , delimiter=',',skip_header=1)) # Read csv file
                data_yr = np.add(data_yr, data_tmp[:,3])
        if not SI: data_yr = data_yr/cst.cfs_to_m3
        graph_name = AltScenName(file_model_csv)  # For this graph name, we will want to strip csv-specific parts of string.
        graph_name = graph_name + '_tot_reservoir_inflow'
        plot_structure = '4 by 2'
    elif data_type == 'pool':
        time = data_v[:,0]
        data_yr = np.zeros_like(data_v[:,1])
        file_number = -1
        for data_type_check in data_type_list:
            file_number += 1
            if data_type_check == 'damin' and \
               're-regulating' not in file_name_list[file_number]:
                data_tmp = np.array(np.genfromtxt(cst.path_data + 
                   file_name_list[file_number]
                   , delimiter=',',skip_header=1)) # Read csv file
                data_yr = np.add(data_yr, data_tmp[:,1])
        data_yr = np.subtract(data_yr,np.max(data_yr))
        if not SI: data_yr = data_yr/0.3048
        graph_name = AltScenName(file_model_csv)  # For this graph name, we will want to strip csv-specific parts of string.
        graph_name = graph_name + '_reservoir_pool'
        plot_structure = '4 by 2'
    elif data_type == 'pool_indiv':
        time = data_v[:,0]
        data_yr = data_v[:,1]
        #  max conservation pool values from USACE SOPs 
        if  'Lookout_Point'  in file_model_csv: max_cons_pool_SOP = 926.  *cst.ft_to_m
        elif 'Detroit'       in file_model_csv: max_cons_pool_SOP = 1563. *cst.ft_to_m
        elif 'Foster'        in file_model_csv: max_cons_pool_SOP = 637.  *cst.ft_to_m
        elif 'Green_Peter'   in file_model_csv: max_cons_pool_SOP = 1010. *cst.ft_to_m
        elif 'Blue_River'    in file_model_csv: max_cons_pool_SOP = 1350. *cst.ft_to_m
        elif 'Cougar'        in file_model_csv: max_cons_pool_SOP = 1690. *cst.ft_to_m
        elif 'Fern_Ridge'    in file_model_csv: max_cons_pool_SOP = 373.5 *cst.ft_to_m
        elif 'Cottage_Grove' in file_model_csv: max_cons_pool_SOP =  790. *cst.ft_to_m
        elif 'Dorena'        in file_model_csv: max_cons_pool_SOP =  832. *cst.ft_to_m
        elif 'Fall_Creek'    in file_model_csv: max_cons_pool_SOP =  830. *cst.ft_to_m
        elif 'Hills_Creek'   in file_model_csv: max_cons_pool_SOP = 1541. *cst.ft_to_m
        else: 
            print 'file name does not match reservoir programming for pool_indiv code'
            print file_model_csv
            assert False
        max_cons_pool_SOP = np.min([max_cons_pool_SOP,np.max(data_yr[366:])])  #Take maximum conservation pool as larger of v
        max_cons_pool = np.ones_like(data_yr)*max_cons_pool_SOP
        data_yr = data_yr - max_cons_pool
        if not SI: data_yr = data_yr/cst.ft_to_m
        graph_name = file_model_csv[:-4] + '_reservoir_pool'
        plot_structure = '4 by 2'
    elif data_type == 'tot_damdiff':
        time = data_v[:,0]
        data_yr = np.zeros_like(data_v[:,3])
        file_number = -1
        for data_type_check in data_type_list:
            file_number += 1
            if data_type_check == 'damin' and \
               're-regulating' not in file_name_list[file_number] and \
               'Foster' not in file_name_list[file_number] and \
               'Lookout' not in file_name_list[file_number]:
                data_tmp = np.array(np.genfromtxt(cst.path_data + 
                   file_name_list[file_number]
                   , delimiter=',',skip_header=1)) # Read csv file
                data_yr = np.add(data_yr, data_tmp[:,3])  #Inflows
        data_yr_tmp = np.zeros_like(data_v[:,4])
        file_number = -1
        for data_type_check in data_type_list:
            file_number += 1
            if data_type_check == 'damout' and \
               're-regulating' not in file_name_list[file_number] and \
               'Green Peter' not in file_name_list[file_number] and \
               'Hills' not in file_name_list[file_number]:
                data_tmp = np.array(np.genfromtxt(cst.path_data + 
                   file_name_list[file_number]
                   , delimiter=',',skip_header=1)) # Read csv file
                data_yr_tmp = np.add(data_yr_tmp, data_tmp[:,4])  #Outflows
        if not SI: data_yr = data_yr/cst.cfs_to_m3
        graph_name = AltScenName(file_model_csv)  # For this graph name, we will want to strip csv-specific parts of string.
        graph_name = graph_name + '_tot_res_outflow_minus_inflow'
        plot_structure = '4 by 2'
    elif data_type == 'damout':
        time = data_v[:,0]
        data_yr = data_v[:,4]
        if not SI: data_yr = data_yr/cst.cfs_to_m3
        graph_name = file_model_csv[:-4] + '_outflow'
        plot_structure = '4 by 2'
    elif data_type == 'tot_damout':
        time = data_v[:,0]
        data_yr = np.zeros_like(data_v[:,4])
        file_number = -1
        for data_type_check in data_type_list:
            file_number += 1
            if data_type_check == 'damin' and \
               're-regulating' not in file_name_list[file_number] and \
               'Green Peter' not in file_name_list[file_number] and \
               'Hills' not in file_name_list[file_number]:
                data_tmp = np.array(np.genfromtxt(cst.path_data + 
                   file_name_list[file_number]
                   , delimiter=',',skip_header=1)) # Read csv file
                data_yr = np.add(data_yr, data_tmp[:,4])
        if not SI: data_yr = data_yr*cst.cfs_to_m3
        graph_name = AltScenName(file_model_csv)  # For this graph name, we will want to strip csv-specific parts of string.
        graph_name = graph_name + '_total_reservoir_outflow'
        plot_structure = '4 by 2'
    elif data_type == 'creek_sums':
        time = data_v[:,0]
        data_yr = data_v[:,1]
        current_number = 0
        creek_stats = xlrd.open_workbook(file_stats_w_path)
        creek_stat_data = np.roll(np.array(creek_stats.sheet_by_index(0).col_values(1)[1:]),-cst.day_of_year_oct1)
        for file_name_check in file_name_list:
            if 'Luckiamute' in file_name_check\
            or 'Marys' in file_name_check\
            or 'Mckenzie_Belknap' in file_name_check\
            or 'Mohawk' in file_name_check\
            or 'Molalla_at_Canby' in file_name_check\
            or 'Pudding_at_Aurora' in file_name_check\
            or 'Silver_at_Silverton' in file_name_check\
            or 'Tualatin' in file_name_check\
            or 'Johnson' in file_name_check:
                data_tmp = np.array(np.genfromtxt(cst.path_data+file_name_check,delimiter=",",skip_header=1))   #read the file
                if not SI: data_tmp[:,1] = data_tmp[:,1]/cst.cfs_to_m3
                data_yr += data_tmp[:,1]
                stats_name_tmp = xlrd.open_workbook(cst.path_auxilliary_files + stats_list[current_number])
                stats_tmp = np.roll(np.array(stats_name_tmp.sheet_by_index(0).col_values(1)[1:]),-cst.day_of_year_oct1)
                stats_tmp = stats_tmp*cst.cfs_to_m3
                creek_stat_data += stats_tmp
            current_number += 1
        mean_Q = creek_stat_data
        graph_name = AltScenName(file_model_csv)  # For this graph name, we will want to strip csv-specific parts of string.
        graph_name = graph_name + '_total_Creeks_gauged_no_ReservoirInfluence'
        plot_structure = '4 by 2'
    elif data_type == 'precipitation' or\
         data_type == 'snow' or\
         data_type == 'et' or\
         data_type == 'for_et' or\
         data_type == 'ag_et': 
        time = data_v[:,0]
        if data_type == 'ag_et': 
            data_yr = data_v[:,3]
            print 'reading ag et data on column [3].  Is this right?' 
            print 'line 911 of Cascade-Plotsv1.01.py'
        elif data_type == 'precipitation': 
            data_yr = data_v[:,2]
        else: 
            data_yr = data_v[:,1]
        if not SI:
            data_yr = data_yr/cst.in_to_mm
        graph_name = file_model_csv[:-4] 
        if data_type == 'precipitation':
            graph_name = file_model_csv[:-4] + '_precipitation'
        if data_type == 'for_et':
            graph_name = file_model_csv[:-4] + '_forest_et'
        elif data_type == 'ag_et':
            graph_name = file_model_csv[:-4] + '_ag_et'
        plot_structure = '3 by 2'
    elif data_type == 'swe_pre':
        time = data_v[:,0]
        data_swe = data_v[:,1]
        data_tmp = np.array(np.genfromtxt(file_model_csv_w_path.replace(
            "HBV_Snow_(mm)_by_elev_0-500-1200", "HBV_Climate_by_elev_0-200-1200"
            ), delimiter=',',skip_header=1)) # Read csv file
        data_pre = data_tmp[:,1]
        
        data_yr = data_swe
        graph_name = file_model_csv[:-4] + '_SWE-PRE'
        plot_structure = '3 by 2'
        data_pre = data_pre[cst.day_of_year_oct1:-(365-cst.day_of_year_oct1)] # water year
        data_swe = data_swe[cst.day_of_year_oct1:-(365-cst.day_of_year_oct1)] # water year
    elif data_type == 'water_deficit':
        time = data_v[:,0]
        data_pet = data_v[:,2]
        data_et = data_v[:,1] # Read csv file
        
        data_yr = np.add(data_pet, -1.*data_et)
        graph_name = file_model_csv[:-4] + '_Water_Deficit_basinwide'
        plot_structure = '3 by 2'
    elif data_type == 'he_water_deficit':
        time = data_v[:,0]
        data_pet = data_v[:,6]
        data_et = data_v[:,5] # Read csv file
        
        data_yr = np.add(data_pet, -1.*data_et)
        graph_name = file_model_csv[:-4] + '_Water_Deficit_high'
        plot_structure = '3 by 2'
        data_type = 'water_deficit'  # from here on, treat as basin-wide water_deficit
    elif data_type == 'le_water_deficit':
        time = data_v[:,0]
        data_pet = data_v[:,4]
        data_et = data_v[:,3] # Read csv file
        
        data_yr = np.add(data_pet, -1.*data_et)
        graph_name = file_model_csv[:-4] + '_Water_Deficit_low'
        plot_structure = '3 by 2'
        data_type = 'water_deficit'  # from here on, treat as basin-wide water_deficit
    elif data_type == 'me_water_deficit':
        time = data_v[:,0]
        data_pet = data_v[:,8]
        data_et = data_v[:,7] # Read csv file
        
        data_yr = np.add(data_pet, -1.*data_et)
        graph_name = file_model_csv[:-4] + '_Water_Deficit_mid'
        plot_structure = '3 by 2'
        data_type = 'water_deficit'  # from here on, treat as basin-wide water_deficit
    elif data_type == 'irrigation': 
        time = data_v[:,0]
        data_yr = np.add(data_v[:,4], data_v[:,5])/86400.  #convert per day to per second
        if not SI:
            data_yr = data_yr/cst.acftperday_to_m3s
        graph_name = file_model_csv[:-4] + '_irrigation'
        plot_structure = '3 by 2'
    elif data_type == 'municipal' or data_type == 'muni_less_disch': 
        time = data_v[:,0]
        data_yr = np.add(data_v[:,4], data_v[:,5])
        if data_type == 'muni_less_disch':
            data_tmp = data_yr
            data_return = [np.mean(data_tmp[365*i+2:365*i+33]) for i in range(len(data_yr)/365)]  #from Jan 3 to Feb 3
            data_return = np.repeat(data_return,365) #repeat each element of data_return 365 times.  I.e., fill each row with same number
            data_yr -= data_return
        if not SI:
            data_yr = data_yr/cst.acftperday_to_m3s
        if data_type == 'municipal':
            graph_name = file_model_csv[:-4] + '_municipal'
        elif data_type == 'muni_less_disch':
            graph_name = file_model_csv[:-4] + '_municipal less muni discharge'            
        plot_structure = '3 by 2'
    elif data_type == 'muni_alloc_big4'  or data_type == 'muni_less_disch_big4': 
        time = data_v[:,0]
        data_yr = data_v[:,1:5].sum(axis=1)
        if data_type == 'muni_less_disch_big4':
            data_tmp = data_yr
            data_return = [np.mean(data_tmp[365*i+2:365*i+33]) for i in range(len(data_yr)/365)]  #from Jan 3 to Feb 3
            data_return = np.repeat(data_return,365) #repeat each element of data_return 365 times.  I.e., fill each row with same number
            data_yr -= data_return
        if not SI:
            data_yr = data_yr/cst.acftperday_to_m3s
        if data_type == 'muni_alloc_big4': 
            graph_name = file_model_csv[:-4] + '_municipal_Big4'
        elif data_type == 'muni_less_disch_big4':
            graph_name = file_model_csv[:-4] + '_municipal_less_disch_Big4'
        plot_structure = '3 by 2'
    elif data_type == 'water_rights':
        time = data_v[:,0]
        data_yr = np.add(data_v[:,8], data_v[:,9])
        if not SI:
            data_yr = data_yr/cst.acftperday_to_m3s
        graph_name = file_model_csv[:-4] + '_unexercized_water_rights'
        plot_structure = '3 by 2'
    elif data_type == 'tot_extract':
        time = data_v[:,0]
        data_yr = np.add( np.add(data_v[:,2], data_v[:,3]), \
                          np.add(data_v[:,4],data_v[:,5])   )
        if not SI:
            data_yr = data_yr/cst.acftperday_to_m3s
        graph_name = file_model_csv[:-4] + '_total water use by people'
        plot_structure = '4 by 2'
    elif data_type == 'instream': 
        time = data_v[:,0]
        data_yr = data_v[:,1]
        if not SI:
            data_yr = data_yr/cst.acftperday_to_m3s
        graph_name = file_model_csv[:-4] + '_instream rights'
        plot_structure = '3 by 2'
    elif data_type == 'ratio_min_to_discharge':
        time = data_v[:,0]
        data_yr = data_v[:,1]
        graph_name = 'ratio min_to_discharge at Salem'
        plot_structure = '3 by 2'
    elif data_type == 'ratio_avail_to_consum':
        time = data_v[:,0]
        data_yr = data_v[:,1]
        data_v2 = np.array(np.genfromtxt(file_model_csv_w_path.replace(
            "Willamette_at_Salem_(m3_s)", "ALTWM_Daily_Metrics"
            ), delimiter=',',skip_header=1)) # Read 2nd csv file
        data2_yr = np.add( np.add(data_v2[:,2], data_v2[:,3]), \
                          np.add(data_v2[:,4],data_v2[:,5])   )
        data_tmp = np.add(data_v2[:,4], data_v2[:,5])
#       get average metro water used for Jan 1 - Feb 28:
        data_return = [np.mean(data_tmp[365*i+2:365*i+33]) for i in range(len(data_yr)/365)]  #from Jan 3 to Feb 3
        data_return = np.repeat(data_return,365) #repeat each element of data_return 365 times.  I.e., fill each row with same number
        data2_yr -= data_return
        data2_yr = data2_yr.clip(1.e-5) #prevent negative numbers or zeros
        graph_name = 'ratio water_available_at_Salem to total_consumptive_use'
        plot_structure = '3 by 2'
    elif data_type == 'tot_consumed' or data_type == 'CWDtoD':
        time = data_v[:,0]
        data_yr = np.add( np.add(data_v[:,2], data_v[:,3]), \
                          np.add(data_v[:,4],data_v[:,5])   )
        data_tmp = np.add(data_v[:,4], data_v[:,5])
#       get average metro water used for Jan 1 - Feb 28:
        data_return = [np.mean(data_tmp[365*i+2:365*i+33]) for i in range(len(data_yr)/365)]  #from Jan 3 to Feb 3
        data_return = np.repeat(data_return,365) #repeat each element of data_return 365 times.  I.e., fill each row with same number
        data_yr -= data_return
        if not SI:
            data_yr = data_yr/cst.acftperday_to_m3s
        if data_type == 'tot_consumed':
            graph_name = file_model_csv[:-4] + '_total consumptive water use'
            plot_structure = '4 by 2'
        elif data_type == 'CWDtoD':
            data_tmp = np.array(np.genfromtxt(file_model_csv_w_path.replace(
                "ALTWM_Daily_Metrics", "Willamette_at_Portland_(m3_s)"
                ), delimiter=',',skip_header=1)) # Read csv file
            data_yr = data_yr/data_tmp[:,1]
            graph_name = file_model_csv[:-4] + '_tot consump use rel to Willamette'
            plot_structure = '3 by 2'
    elif data_type == 'aridity':
        time = data_v[:,0]
        data_pet = data_v[:,2]
#        data_tmp = np.array(np.genfromtxt(file_model_csv_w_path.replace(
#            "HBV_ET_(mm)_by_elev_0-200-1200_Ref_Run0", "Daily_WaterMaster_Metrics"
#            ), delimiter=',',skip_header=1)) # Read csv file
        data_tmp = np.array(np.genfromtxt(file_model_csv_w_path.replace(
            "HBV_ET_(mm)_by_elev_0-200-1200", "ALTWM_Daily_Metrics"
            ), delimiter=',',skip_header=1)) # Read csv file
        data_irrig = np.add(data_tmp[:,2], data_tmp[:,3])
        
        data_tmp = np.array(np.genfromtxt(file_model_csv_w_path.replace(
            "HBV_ET_(mm)_by_elev_0-200-1200", "HBV_Climate_by_elev_0-200-1200"
            ), delimiter=',',skip_header=1)) # Read csv file
        data_precip = data_tmp[:,2]
        
        data_yr = data_pet/np.add(data_irrig, data_precip)
        graph_name = file_model_csv[:-4] + '_Aridity_Index'
        plot_structure = '4 by 2'
    elif data_type == 'temperature':
        time = data_v[:,0]
        data_yr = data_v[:,1]
        if not SI: data_yr = (data_yr/cst.F_to_C) + 32.
        graph_name = file_model_csv[:-4] + '_temperature'
        plot_structure = '4 by 2'
    elif data_type == 'potet' or\
         data_type == 'for_potet' or\
         data_type == 'ag_potet':
        time = data_v[:,0]
        if data_type != 'ag_potet': data_yr = data_v[:,2]
        if data_type == 'ag_potet': data_yr = data_v[:,4]
        if not SI: data_yr = data_yr/cst.in_to_mm
        graph_name = file_model_csv[:-4] + '_pet'
        if data_type != 'potet': graph_name = file_model_csv[:-4] + data_type
        plot_structure = '3 by 2'
    elif data_type == 'h_drought':
        time = data_v[:,0]
        data_yr = movingaverage(data_v[:,1],np.ones(30)/30.) #30-day running avg
        ScenarioName = '_' + AltScenName(file_model_csv).split('_')[0] + '_'
        if ScenarioName is '_Ref_':
            data_hd1 = data_yr[:,1][0:(365*11)] #first 11 years
        else: 
            data_tmp = np.array(np.genfromtxt(file_model_csv_w_path.replace(
                ScenarioName, "_Ref_"
                ), delimiter=',',skip_header=1)) # Read csv file
            data_hd1 = data_tmp[:,1][0:(365*11)] #first 11 years
        data_smth_hd1 = movingaverage(data_hd1,np.ones(30)/30.)  #30-day running avg
        
        data_tmp = np.array(np.genfromtxt(file_model_csv_w_path.replace(
            ScenarioName, "_HighClim_"
            ), delimiter=',',skip_header=1)) # Read csv file
        data_hd2 = data_tmp[:,1][0:(365*11)] #first 11 years
        data_smth_hd2 = movingaverage(data_hd2,np.ones(30)/30.)  #30-day running avg
        
        data_tmp = np.array(np.genfromtxt(file_model_csv_w_path.replace(
            ScenarioName, "_LowClim_"
            ), delimiter=',',skip_header=1)) # Read csv file
        data_hd3 = data_tmp[:,1][0:(365*11)] #first 11 years
        data_smth_hd3 = movingaverage(data_hd3,np.ones(30)/30.) #30-day running avg
        
        graph_name = file_model_csv[:-4] + '_Hydrologic_Drought'
        plot_structure = '3 by 2'

  # Do Error checking if Willamette at Portland
    if "Willamette_at_Portland" in file_model_csv and data_type != 'h_drought':
        error_check = True
        data_spQ = data_yr / cst.Willamette_Basin_area_at_PDX * 86400.  #m in each day
        data_tmp = np.array(np.genfromtxt(file_model_csv_w_path.replace(
            "Willamette_at_Portland_(m3_s)", "HBV_ET_(mm)_by_elev_0-200-1200"
            ), delimiter=',',skip_header=1)) # Read csv file
        data_ET = data_tmp[:,1]/1000.
        
        data_tmp = np.array(np.genfromtxt(file_model_csv_w_path.replace(
            "Willamette_at_Portland_(m3_s)", "HBV_Climate_by_elev_0-200-1200"
            ), delimiter=',',skip_header=1)) # Read csv file
        data_precip = data_tmp[:,2]/1000.
        Basin_spQ_sum = np.sum(data_spQ)/len(data_spQ)*365.          # avg specific discharge each year
        Basin_ET_sum = np.sum(data_ET)/len(data_ET)*365.             # avg ET each year
        Basin_precip_sum = np.sum(data_precip)/len(data_precip)*365. # avg precip each year
#        print Basin_spQ_sum, Basin_ET_sum, Basin_precip_sum
        mass_balance_err = 100 - (Basin_spQ_sum + Basin_ET_sum)/Basin_precip_sum*100.
        mass_balance_err_str = "{0:.3f}".format(mass_balance_err)+'%'
#        print mass_balance_err_str
    else:
        error_check = False     
        mass_balance_err_str = ''
  # End error check
        
    time = time[cst.day_of_year_oct1 - 1:] # water year    
    data_yr = data_yr[cst.day_of_year_oct1:-(365-cst.day_of_year_oct1)] # truncate data to water year
    if data_type == 'ratio_avail_to_consum':
        data2_yr = data2_yr[cst.day_of_year_oct1:-(365-cst.day_of_year_oct1)] # truncate data to water year
    elif data_type == 'tot_damdiff':
        data_yr_tmp = data_yr_tmp[cst.day_of_year_oct1:-(365-cst.day_of_year_oct1)] # water year
    data_length = len(time)
    num_water_yrs = len(time)/365
    start_year = 2011
    end_year = 2011 + num_water_yrs

    if  not data_type == 'temperature' and \
        not data_type == 'ratio_min_to_discharge' and \
        not data_type == 'ratio_avail_to_consum':          # If true, then replace max and min in cascade plot
        plot_lower_bound = np.percentile(data_yr,5)
        plot_upper_bound = np.percentile(data_yr,95)
    elif data_type == 'temperature':
        plot_lower_bound = np.percentile(data_yr,5)
        plot_upper_bound = np.percentile(data_yr,97.5)

    if stats_available and data_type != 'creek_sums':
        stats = xlrd.open_workbook(file_stats_w_path)
        mean_Q = np.roll(np.array(stats.sheet_by_index(0).col_values(1)[1:]),
                     -cst.day_of_year_oct1)
        if SI: mean_Q = mean_Q*cst.cfs_to_m3

    # Convert the data into a 2D array in numpy format, and clip it to +/- 1 sigma for vis.
    # For specialized data such as aridity index, swe-pre ratio, this requires 
    # a few extra steps.  For other data (else...), it only requires 
    # re-shaping the array 
    if data_type == 'aridity':
        data_2D_num = np.add.accumulate(np.reshape(np.array(data_pet), (-1,365)),1)
        data_2D_den = np.add.accumulate(np.reshape(np.array(np.add(data_irrig,data_precip)), (-1,365)),1)
        data_2D = np.divide(data_2D_num, data_2D_den)
    elif data_type == 'swe_pre':   # Calculate SWE/sum(Precip starting Nov 1)
        data_2D_num = np.reshape(np.array(data_swe), (-1,365)) #2D matrix of data in numpy format
        data_2D_den = np.reshape(np.array(data_pre), (-1,365)) #2D matrix of data in numpy format
        den_tmp_neg = np.multiply(data_2D_den,-1.)   # need a negative number to zero out some of the precip matrix
        data_2D_den[:,0:30] += den_tmp_neg[:,0:30]   # zero out precip from Oct. 1 through Oct. 31
        data_2D_den[:,cst.day_of_year_apr1+(365-cst.day_of_year_oct1):] += \
            den_tmp_neg[:,cst.day_of_year_apr1+(365-cst.day_of_year_oct1):]  # zero out precip after Apr 1
        data_2D_den = np.add.accumulate(data_2D_den,1)  # sum precip and make this the denominator
        np.place(data_2D_den,data_2D_den==0,[0.001])         # a fix of the divide by zero warning in the following line
        data_2D = np.divide(data_2D_num, data_2D_den)  # divide numerator by denominator
        data_2D[:,0:90] = 0.
        data_2D[:,cst.day_of_year_apr1+(365-cst.day_of_year_oct1):] = 0.
    elif data_type == 'tot_damdiff':
        data_2D     = np.reshape(np.array(data_yr    ), (-1,365)) #2D matrix of data in numpy format
        data_2D_tmp = np.reshape(np.array(data_yr_tmp), (-1,365)) #2D matrix of data in numpy format
        how_much_outflow_bigger_than_inflow = np.divide(np.sum(data_2D_tmp,1),np.sum(data_2D,1))
        data_2D = np.subtract(data_2D_tmp,np.multiply(data_2D, how_much_outflow_bigger_than_inflow[:,None]))
        plot_lower_bound = np.percentile(data_2D,5)
        plot_upper_bound = np.percentile(data_2D,97.5)
    elif data_type == 'ratio_avail_to_consum':     
        data_2D = np.reshape(np.array(data_yr), (-1,365)) #2D matrix of data in numpy format
        data_2D_denominator = np.reshape(np.array(data2_yr), (-1,365)) #2D matrix of data in numpy format
       
    else:     ## All cases other than above
        data_2D = np.reshape(np.array(data_yr), (-1,365)) #2D matrix of data in numpy format
        
    if data_type == 'h_drought':
        data_smth_hd1 = data_smth_hd1[cst.day_of_year_oct1:-(365-cst.day_of_year_oct1)] # truncate data to water year
        data_smth_hd2 = data_smth_hd2[cst.day_of_year_oct1:-(365-cst.day_of_year_oct1)] # truncate data to water year
        data_smth_hd3 = data_smth_hd3[cst.day_of_year_oct1:-(365-cst.day_of_year_oct1)] # truncate data to water year
        data_2D_hd1 = np.reshape(np.array(data_smth_hd1), (-1,365)) #2D matrix of data in numpy format
        data_2D_hd2 = np.reshape(np.array(data_smth_hd2), (-1,365)) #2D matrix of data in numpy format
        data_2D_hd3 = np.reshape(np.array(data_smth_hd3), (-1,365)) #2D matrix of data in numpy format
        data_2D_hd = np.vstack((data_2D_hd1, data_2D_hd2, data_2D_hd3))
        Q10 = np.percentile(data_2D_hd,10.,axis=0)
        data_2D = compare_rows(data_2D,Q10)
    elif data_type == 'ratio_min_to_discharge':
        min_flows = rules.get_min_flows('Salem','minQ',np.shape(data_2D)[0])
        data_2D = np.divide(min_flows,data_2D)
        plot_lower_bound = np.percentile(data_2D,5)
        plot_upper_bound = np.percentile(data_2D,95)
    elif data_type == 'ratio_avail_to_consum':
        min_flows = rules.get_min_flows('Salem','minQ',np.shape(data_2D)[0])
        data_2D_numerator = np.subtract(data_2D,min_flows)
        data_2D = np.divide(data_2D_numerator,data_2D_denominator)
        data_2D = data_2D.clip(-10.,2.)
        plot_lower_bound = np.percentile(data_2D,5)
        plot_upper_bound = np.percentile(data_2D,95)
        
    data_2D_clipped = np.empty_like(data_2D)
    data_2D_clipped = np.clip(data_2D, plot_lower_bound, plot_upper_bound)
    
    if data_type == 'h_drought': data_2D_clipped = data_2D
    
    return data_2D, data_2D_clipped, data_yr, time, data_length, num_water_yrs,\
       start_year, end_year, graph_name, plot_structure, error_check, \
       mass_balance_err_str, mean_Q



def process_data(data_2D, data_yr, num_water_yrs, data_length, \
        data_type, data_type_list, SI,\
        start_year, end_year):
    """
    Process dat needed for plotting
    """

    import numpy as np
    import constants_cp as cst   # constants.py contains constants used here
    from movingaverage import movingaverage, n_take_k

    ##########################################################
    # Assemble the data needed on the right-hand-side plots. #
    # This differs with data_type.                           #
    ##########################################################
    data_set_rhs_1 = np.empty([1])
    data_set_rhs_2 = np.empty([1])
    data_set_rhs_3 = np.empty([1])

    if data_type == 'stream' or \
       data_type == 'daminWdup' or \
       data_type == 'damoutWdup' or \
       data_type == 'damin' or \
       data_type == 'damout' or \
       data_type == 'tot_damin' or \
       data_type == 'tot_damout' or\
       data_type == 'tot_damdiff' or\
       data_type == 'pool' or\
       data_type == 'pool_indiv' or\
       data_type == 'creek_sums':

        Q_max = [np.amax(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        extra = np.median(Q_max[-9:])
        Q_max_decadal = np.reshape(np.append(Q_max, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_2 = Q_max_decadal
        
        Q_min = [np.amin(data_2D[i,:]) for i in range(num_water_yrs)]  # min discharge
        extra = np.median(Q_min[-9:])
        Q_min_decadal = np.reshape(np.append(Q_min, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = Q_min_decadal
                  
    elif data_type == 'snow':
        swe_apr1 = data_yr[cst.day_of_year_apr1+(365-cst.day_of_year_oct1):data_length:365]
        extra = np.median(swe_apr1[-9:])
        swe_apr1_decadal = np.reshape(np.append(swe_apr1, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = swe_apr1_decadal

    elif data_type == 'irrigation':
        irigation_data = np.array([np.sum(data_yr[i*365:(i+1)*365]) for i in range(num_water_yrs)])
        if SI: irigation_data = irigation_data*86400./1.e6  # convert from m3/s to millions of m3
        if not SI: irigation_data = irigation_data/1.e3  # convert to thousands of ac-ft
        extra = np.median(irigation_data[-9:])
        irigation_data_decadal = np.reshape(np.append(irigation_data, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = irigation_data_decadal
        
    elif data_type == 'tot_extract':

        Q_max = [np.amax(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        extra = np.median(Q_max[-9:])
        Q_max_decadal = np.reshape(np.append(Q_max, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_2 = Q_max_decadal
        
        Q_min = [np.amin(data_2D[i,:]) for i in range(num_water_yrs)]  # min discharge
        extra = np.median(Q_min[-9:])
        Q_min_decadal = np.reshape(np.append(Q_min, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = Q_min_decadal
                  
    elif data_type == 'tot_consumed':

        Q_max = [np.amax(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        extra = np.median(Q_max[-9:])
        Q_max_decadal = np.reshape(np.append(Q_max, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_2 = Q_max_decadal
        
        Q_min = [np.amin(data_2D[i,:]) for i in range(num_water_yrs)]  # min discharge
        extra = np.median(Q_min[-9:])
        Q_min_decadal = np.reshape(np.append(Q_min, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = Q_min_decadal
                  
    elif data_type == 'CWDtoD':

        Q_max = [np.amax(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        extra = np.median(Q_max[-9:])
        Q_max_decadal = np.reshape(np.append(Q_max, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = Q_max_decadal

    elif data_type == 'CWDtoD' or data_type == 'ratio_min_to_discharge':

        Q_max = [np.amax(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        extra = np.median(Q_max[-9:])
        Q_max_decadal = np.reshape(np.append(Q_max, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = Q_max_decadal

    elif data_type == 'ratio_avail_to_consum':

        Q_min = [np.amin(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        extra = np.median(Q_min[-9:])
        Q_min_decadal = np.reshape(np.append(Q_min, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = Q_min_decadal

    elif data_type == 'instream':

        if SI: Q_max = np.array([np.amax(data_2D[i,:]) for i in range(num_water_yrs)])  # max right
        if not SI: Q_max = np.array([np.amax(data_2D[i,:]/1000.) for i in range(num_water_yrs)])  # max right
        extra = np.median(Q_max[-9:])
        Q_max_decadal = np.reshape(np.append(Q_max, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = Q_max_decadal
                                 
    elif data_type == 'aridity':
        Q_max = [np.amax(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        extra = np.median(Q_max[-9:])
        Q_max_decadal = np.reshape(np.append(Q_max, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_2 = Q_max_decadal
        
        Q_min = [np.amin(data_2D[i,:]) for i in range(num_water_yrs)]  # min discharge
        extra = np.median(Q_min[-9:])
        Q_min_decadal = np.reshape(np.append(Q_min, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = Q_min_decadal
                    
    elif data_type == 'swe_pre':
        swe_apr1 = data_2D[:,cst.day_of_year_apr1+(365-cst.day_of_year_oct1)-1]
        extra = np.median(swe_apr1[-9:])
        swe_apr1_decadal = np.reshape(np.append(swe_apr1, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = swe_apr1_decadal
        yearly_max = [np.max(data_2D[i,61:150]) for i in range(num_water_yrs)]
                    
    elif data_type == 'municipal' or data_type == 'muni_alloc_big4' or \
        data_type == 'muni_less_disch' or data_type == 'muni_less_disch_big4':
        municipal_data = np.array([np.sum(data_yr[i*365:(i+1)*365]) for i in range(num_water_yrs)])
        if SI: municipal_data = municipal_data*86400./1.e6  # convert from m3/s to millions of m3
        if not SI: 
            municipal_data = municipal_data/1.e3  # convert to thousands of ac-ft
        extra = np.median(municipal_data[-9:])
        municipal_data_decadal = np.reshape(np.append(municipal_data, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = municipal_data_decadal
    elif data_type == 'water_rights':
        unusedWR_data = np.array([np.sum(data_yr[i*365:(i+1)*365]) for i in range(num_water_yrs)])
        if SI: unusedWR_data = unusedWR_data*86400./1.e6  # convert from m3/s to millions of m3
        if not SI: unusedWR_data = unusedWR_data/1.e3  # convert to thousands of ac-ft
        extra = np.median(unusedWR_data[-9:])
        unusedWR_data_decadal = np.reshape(np.append(unusedWR_data, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = unusedWR_data_decadal

    elif data_type == 'precipitation':
        precip_data = [np.sum(data_yr[i*365:(i+1)*365]) for i in range(num_water_yrs)]
        extra = np.median(precip_data[-9:])
        precip_data_decadal = np.reshape(np.append(precip_data, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = precip_data_decadal
                
    elif data_type == 'temperature':
        T_max = [np.amax(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        extra = np.median(T_max[-9:])
        T_max_decadal = np.reshape(np.append(T_max, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_2 = T_max_decadal
        
        T_min = [np.amin(data_2D[i,:]) for i in range(num_water_yrs)]  # min discharge
        extra = np.median(T_min[-9:])
        T_min_decadal = np.reshape(np.append(T_min, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = T_min_decadal
        
        yearly_avg = [np.mean(data_2D[i,:]) for i in range(num_water_yrs)]  
        averaging_window = 9
        window_raw = np.array([])
        window_raw = np.append(window_raw,[n_take_k(averaging_window-1,i) for i in range(averaging_window)])
        window = window_raw / np.sum(window_raw)  # normalized weights
        yearly_avg = movingaverage(
            yearly_avg[:averaging_window] + yearly_avg + yearly_avg[-averaging_window:],
            window)[averaging_window:-averaging_window]
        data_set_rhs_3 = yearly_avg
        
    elif data_type == 'et' or\
         data_type == 'ag_et' or\
         data_type == 'for_et':
        et_data = [np.sum(data_yr[i*365:(i+1)*365]) for i in range(num_water_yrs)]
        extra = np.median(et_data[-9:])
        et_data_decadal = np.reshape(np.append(et_data, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = et_data_decadal

    elif data_type == 'potet' or\
         data_type == 'ag_potet' or\
         data_type == 'for_potet':
        potet_data = [np.sum(data_yr[i*365:(i+1)*365]) for i in range(num_water_yrs)]
        extra = np.median(potet_data[-9:])
        et_data_decadal = np.reshape(np.append(potet_data, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = et_data_decadal

    elif 'water_deficit' in data_type:
        wd_data_max = [np.amax(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        extra = np.median(wd_data_max[-9:])
        wd_data_max_decadal = np.reshape(np.append(wd_data_max, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = wd_data_max_decadal
        wd_data = [np.sum(data_yr[i*365:(i+1)*365]) for i in range(num_water_yrs)]
        yearly_max = wd_data

    elif data_type == 'h_drought':
        d_data = np.sum(data_2D,axis=1) 
        extra = np.median(d_data[-9:])
        d_data_decadal = np.reshape(np.append(d_data, extra), (9,-1)) #2D matrix of decadal data
        data_set_rhs_1 = d_data_decadal

#   Calculate values for 3rd strip chart on right-hand-side (yearly avg)
    averaging_window = 9
    window_raw = np.array([])
    window_raw = np.append(window_raw,[n_take_k(averaging_window-1,i) for i in range(averaging_window)])
    window = window_raw / np.sum(window_raw)  # normalized weights
    if data_type == 'h_drought':
        yearly_avg = [np.mean(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        yearly_avg = movingaverage(
            yearly_avg[:averaging_window] + yearly_avg + yearly_avg[-averaging_window:],
            window)[averaging_window:-averaging_window]
        data_set_rhs_3 = yearly_avg*365.
    
    elif data_type == 'ratio_min_to_discharge':
#        Q_max = [np.amax(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        yearly_max = [np.amax(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        yearly_max = movingaverage(
            yearly_max[:averaging_window] + yearly_max + yearly_max[-averaging_window:],
            window)[averaging_window:-averaging_window]
        data_set_rhs_3 = yearly_max
        
    elif data_type == 'ratio_avail_to_consum':
        yearly_min = [np.amin(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        yearly_min = movingaverage(
            yearly_min[:averaging_window] + yearly_min + yearly_min[-averaging_window:],
            window)[averaging_window:-averaging_window]
        data_set_rhs_3 = yearly_min
        
    elif data_type != 'swe_pre' and data_type != 'water_deficit':   ###THIS IS MOST CASES ***
        yearly_avg = [np.mean(data_2D[i,:]) for i in range(num_water_yrs)]  # max discharge
        yearly_avg = movingaverage(
            yearly_avg[:averaging_window] + yearly_avg + yearly_avg[-averaging_window:],
            window)[averaging_window:-averaging_window]
        data_set_rhs_3 = yearly_avg
        if data_type == 'municipal' or data_type == 'muni_alloc_big4' or data_type == 'irrigation' or \
           data_type == 'muni_less_disch' or data_type == 'muni_less_disch_big4':        
            if not SI:
                data_set_rhs_3 = data_set_rhs_3*365/1000.
            else:
                data_set_rhs_3 = data_set_rhs_3 #*365/1.e6
        elif data_type == 'instream':
            if not SI:
                data_set_rhs_3 = data_set_rhs_3/1000.
    else:  
        yearly_max = movingaverage(
            yearly_max[:averaging_window] + yearly_max + yearly_max[-averaging_window:],
            window)[averaging_window:-averaging_window]
        data_set_rhs_3 = yearly_max
   
    return data_set_rhs_1, data_set_rhs_2, data_set_rhs_3
    

def get_labels(data_2D, data_yr, num_water_yrs, data_length, \
        data_type, data_type_list, SI,\
        start_year, end_year):
    """
    Provide labels and titles for plotting
    """
    
    ylabel2 = ''
    ylabel4 = ''

    if data_type == 'stream' or \
       data_type == 'daminWdup' or \
       data_type == 'damoutWdup' or \
       data_type == 'damin' or \
       data_type == 'damout' or \
       data_type == 'tot_damin' or \
       data_type == 'tot_damout' or\
       data_type == 'tot_damdiff' or\
       data_type == 'creek_sums':
        
        if SI:
            ylabel2 = '$Daily \, Q$ [m$^{\t{3}}$/s]'
            ylabel4 = '$Discharge\, (Q)\,$ [m$^{\t{3}}$/s]'
        else:
            ylabel2 = '$Daily \, Q$ [cfs]'
            ylabel4 = '$Discharge\, (Q)\,$ [cfs]'
        if data_type == 'tot_damdiff':
            if SI:
                ylabel2 = '$Daily \, \Delta Q$ [m$^{\t{3}}$/s]'
                ylabel4 = '$\Delta\, Discharge (\Delta Q)\,$ [m$^{\t{3}}$/s]'
            else:
                ylabel2 = '$Daily \, \Delta Q$ [cfs]'
                ylabel4 = '$Discharge\, (\Delta Q)\,$ [cfs]'
                  
    elif data_type == 'snow':
        if SI:
            ylabel2 = '$Snow \,Water \,Equivalent\,$ [mm]'
            ylabel4 = '$SWE\,$ [mm]'
        else:
            ylabel2 = '$Snow \,Water \,Equivalent\,$ [in]'
            ylabel4 = '$SWE\,$ [in]'
                
    elif data_type == 'irrigation':
        if SI:
            ylabel2 = '$Irrigation \,Rate\,$ [m$^3$/s]'
            ylabel4 = '$Irrig \,Rate\,$ [m$^3$/s]'
        else:
            ylabel2 = '$Irrigation \,Rate\,$ [ac-ft/d]'
            ylabel4 = '$Irrig \,Rate\,$ [ac-ft/d]'
        
    elif data_type == 'tot_extract':
        if SI:
            ylabel2 = '$Tot \,Extract \,$ [m$^{\t{3}}$/s]'
            ylabel4 = '$Extract\,$ [m$^{\t{3}}$/s]'
        else:
            ylabel2 = '$Tot \,Extract \,$ [cfs]'
            ylabel4 = '$Extract\,$ [cfs]'
                  
    elif data_type == 'tot_consumed':
        if SI:
            ylabel2 = '$Tot \,Consump\, Extract \,$ [m$^{\t{3}}$/s]'
            ylabel4 = '$Consump\,$ [m$^{\t{3}}$/s]'
        else:
            ylabel2 = '$Tot \,Consump\, Extract \,$ [cfs]'
            ylabel4 = '$Consump,$ [cfs]'
    
    elif data_type == 'ratio_min_to_discharge' or data_type == 'ratio_avail_to_consum':
        ylabel2 = '$Ratio\, Available/Consumptive$ [-]'
        ylabel4 = '$Ratio$ [-]'
           
    elif data_type == 'CWDtoD':
        ylabel2 = '$Frac\, Extract \,$ [-]'
        ylabel4 = '$Frac$ [-]'

    elif data_type == 'instream':
        if SI:
            ylabel2 = '$Instream\, Rights$ [m$^{\t{3}}$/s]'
            ylabel4 = '$Instream$ [m$^{\t{3}}$/s]'
        else:
            ylabel2 = '$Instream \,Rights$ [ac-ft/d]'
            ylabel4 = '$Instream$ [ac-ft/d]'
                                    
    elif data_type == 'aridity':
        ylabel2 = '$Aridity \,Index$ [-]'
        ylabel4 = '$Aridity$ [-]'
                    
    elif data_type == 'swe_pre':
        ylabel2 = '$SWE:Precip\, Ratio$ [-]'
        ylabel4 = '$SWE:Precip$ [-]'
                    
    elif data_type == 'municipal' or data_type == 'muni_alloc_big4' or \
        data_type == 'muni_less_disch' or data_type == 'muni_less_disch_big4':
        if SI:
            ylabel2 = '$Municipal\, Use\,$ [m$^3$/s]'
            ylabel4 = '$Mncpl\, Use\,$ [m$^3$/s]'
        else:
            ylabel2 = '$Municipal\, Use\,$ [ac-ft/d]'
            ylabel4 = '$Mncpl\, Use\,$ [ac-ft/d]'
        
    elif data_type == 'water_rights':
        if SI:
            ylabel2 = '$Unxczd \,Water \,Rights\,$ [m$^3$/s]'
            ylabel4 = '$Unxczd \,Wtr \,Rt\,$ [m$^3$/s]'
        else:
            ylabel2 = '$Unxczd \,Water \,Rights\,$ [ac-ft/d]'
            ylabel4 = '$Unxczd \,Wtr \,Rt\,$ [ac-ft/d]'

    elif data_type == 'precipitation':
        if SI:
            ylabel2 = '$Precipitation\,$ [mm/d]'
            ylabel4 = '$Precip\,$ [mm/d]'
        else:           
            ylabel2 = '$Precipitation\,$ [in/d]'
            ylabel4 = '$Precip\,$ [in/d]'
        
    elif data_type == 'temperature':
        if SI:
            ylabel2 = '$Temperature\,$ [$^{\circ}\mathrm{C}$]'
            ylabel4 = '$Temperature\,$ [$^{\circ}\mathrm{C}$]'
        else:
            ylabel2 = '$Temperature\,$ [$^{\circ}\mathrm{F}$]'
            ylabel4 = '$Temperature\,$ [$^{\circ}\mathrm{F}$]'            
        
    elif data_type == 'et' or\
         data_type == 'ag_et' or\
         data_type == 'for_et':
        if SI:
            ylabel2 = '$Evapotranspiration\,$ [mm/d]'
            ylabel4 = '$ET\,$ [mm/d]'
        else:
            ylabel2 = '$Evapotranspiration\,$ [in/d]'
            ylabel4 = '$ET\,$ [in/d]'

    elif data_type == 'potet' or\
         data_type == 'ag_potet' or\
         data_type == 'for_potet':
        if SI:
            ylabel2 = '$Potential Evapotranspiration\,$ [mm/d]'
            ylabel4 = '$ET\,$ [mm/d]'
        else:
            ylabel2 = '$Potential \,Evapotranspiration\,$ [in/d]'
            ylabel4 = '$ET\,$ [in/d]'

    elif 'water_deficit' in data_type:
        if SI:
            ylabel2 = '$Water \,Deficit\,$ [mm/d]'
            ylabel4 = '$WD\,$ [mm/d]'
        else:
            ylabel2 = '$Water \,Deficit\,$ [in/d]'
            ylabel4 = '$WD\,$ [in/d]'
    
    elif 'h_drought' in data_type:
        ylabel2 = '$Drought \,Day$ [yes/no]'
        ylabel4 = '$Frac \, DDs\,$ [-]'

    return ylabel2, ylabel4


def process_bottom_strip(data_2D, data_yr, num_water_yrs, data_length, \
            data_type, data_type_list, SI,\
            start_year, end_year):
    """Returns 3 data sets for plotting on bottom strip
    """
    
    import numpy as np
    from movingaverage import movingaverage, n_take_k
    
    ##########################################################
    #   Prep the fourth plot (bottom strip)                  #
    ##########################################################
    
    if data_type == 'swe_pre':
        averaging_window = 9
    else:
        averaging_window = 49
    window_raw = np.array([])
    window_raw = np.append(window_raw,[n_take_k(averaging_window-1,i) for i in range(averaging_window)])
    window = window_raw / np.sum(window_raw)  # normalized weights

    # Calculate moving averages (using binomial filter - in movingaverage).
    # Prepend and append half of averaging window to data window so that moving average at early
    #   and late time are correct.

    data_early = movingaverage([np.mean(data_2D[0:29,i]) for i in range(365-averaging_window/2 , 364)] +
                               [np.mean(data_2D[0:29,i]) for i in range(365)] +
                               [np.mean(data_2D[0:29,i]) for i in range(0 , averaging_window/2)],
                               window)[averaging_window/2 : 365+averaging_window/2]
    data_mid   = movingaverage([np.mean(data_2D[30:59,i]) for i in range(365-averaging_window/2 , 364)] +
                               [np.mean(data_2D[30:59,i]) for i in range(365)] +
                               [np.mean(data_2D[30:59,i]) for i in range(0 , averaging_window/2)],
                               window)[averaging_window/2 : 365+averaging_window/2]
    data_late  = movingaverage([np.mean(data_2D[60:89,i]) for i in range(365-averaging_window/2 , 364)] +
                               [np.mean(data_2D[60:89,i]) for i in range(365)] +
                               [np.mean(data_2D[60:89,i]) for i in range(0 , averaging_window/2)],
                               window)[averaging_window/2 : 365+averaging_window/2]
                               
    return data_early, data_mid, data_late, window, averaging_window        
    
def month_labels (axys):
    """
    Place month labels on horizontal axis.  This is a little tricky,
       so I found some code on the web and modified it.
    """
    from pylab import plot, ylim, xlim, show, xlabel, ylabel, grid
    import matplotlib.dates as dates
    import matplotlib.ticker as ticker

    axys.xaxis.set_major_locator(dates.MonthLocator())
    axys.xaxis.set_minor_locator(dates.MonthLocator(bymonthday=15))
    axys.xaxis.set_major_formatter(ticker.NullFormatter())
    axys.xaxis.set_minor_formatter(dates.DateFormatter('%b'))
    for tick in axys.xaxis.get_minor_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment('center')
    return

def BoxPlot(axys, variable):
    """
    Create and plot the boxes for the box-and-whisker plot
    """
    import matplotlib.pyplot as plt
#    import numpy as np
    variableT = variable.T
#    col = (0.6,0.6,1.)  # light blue in rgb
    col = (0.6, 0.6, 0.6) # light gray in rgb
    positions=range(2015,2096,10)
    box = axys.boxplot(variableT, vert=False,positions=positions,widths=9.2,
                       whis=50,sym=' ',patch_artist=True)
    plt.setp(box['boxes'], color=col)
    colors = [col]*9
    for patch, colors in zip(box['boxes'], colors):
        patch.set_facecolor(colors)
    for cap in box['caps']:
        cap.set(linewidth = 0)
    for whisker in box['whiskers']:
        whisker.set_linestyle('solid')
        whisker.set_linewidth(1)
        whisker.set_color('black')
    for medians in box['medians']:
        medians.set_color('black')
    return

def ct(water_yr_array):
    """
    Calculate center of timing for each water year in the water_yr_array
    Return CT for each year (vector)
    water_yr_array = array size 365 by water years containing values
    """
    import numpy as np
    num_water_yrs = water_yr_array.shape[0]
    CT = np.zeros_like(range(0, num_water_yrs))
    m0 = np.zeros_like(range(0, num_water_yrs))
    m1 = np.zeros_like(range(0, num_water_yrs))
    m0 = [np.trapz(water_yr_array[i,:], x=None, dx=1.0, axis=-1) for i in range(num_water_yrs)]
    m1 = [np.trapz(np.multiply(water_yr_array[i,:],range(365)), x=None, dx=1.0, axis=-1) for i in range(num_water_yrs)]
    CT = np.divide(m1,m0) #+ cst.day_of_year_oct1
    return CT

def metadata(fig,show,climates,files):
##  fig = the figure on which the metadata is drawn  ##
##  show = whether the plot will be show on the screen  ##
##  climates = what climate models are being used  ##
##  files = the data file names with paths  ##
    import time as timetool, os.path

    ax = fig.add_subplot(111,position=[0.125,0.165,0.001,0.001])
    textstr = 'Willamette Water 2100\n Graph generated on ' \
    + str(datetime.date.today()) +'\n\n'+ climates[0] \
    + ' data generated on ' + time.ctime(os.path.getctime(files[0])) \
    +'\n'+ climates[1] + ' data generated on ' \
    + time.ctime(os.path.getctime(files[1])) +'\n'+ climates[2] \
    + ' data generated on ' + time.ctime(os.path.getctime(files[2])) \
    +'\n'+ climates[3] + ' data generated on ' + time.ctime(os.path.getctime(files[3]))
#    if show:
#        props = dict(boxstyle='round', facecolor=(0.75,0.75,0.75), lw=0.)
#    else:
#        props = dict(boxstyle='round', facecolor='white', lw=0.)
#    plt.text(-100, 15, textstr, transform=ax.transAxes, fontsize=6,verticalalignment='top',bbox = props)
    return textstr

def AltScenName(file_model_csv):
##  file_model_csv = name of csv file  ##
##  return the Alternative Scenario name ##
    
    # First line gets second-last piece between "_" and "_".
    # Second line gets last piece after "_" but before "."
    Alternative_Scenario_Name = str(file_model_csv).split("_")[-2] + \
     "_" + str(file_model_csv).split("_")[-1].rpartition(".")[0]  # 
     
    return Alternative_Scenario_Name


########################################################################################
########################################################################################
########################################################################################

######################################################
#####   SCRIPT TO GENERATE THE PLOTS             #####
######################################################
"""
 This script generates a set of plots by first reading in the names of files
 and associated parameters from an xls file.  That file is called
 "cascade plot parameters.xls"
"""
# kwargs:
#   data_type = 'stream' (default), daminWdup, damin,
#               damoutWdup, damout                    damWdup means file has duplicate data
#   flood_Q_available = False (default), True
#   Display = False (default), True
#   stats_available = False (default), True
#   SI = True (default), False

import constants_cp as cst   # constants.py contains constants used here
import xlrd

# Read a parameter file in xls format.
cascade_plot_params = xlrd.open_workbook('cascade plot parameters.xls')

file_model_csv = cascade_plot_params.sheet_by_index(0).col_values(0)[1:]        # name of data file for plot
file_name_list = list(file_model_csv)
file_stats = cascade_plot_params.sheet_by_index(0).col_values(1)[1:]            # name of stats file for plot (if any)
title = cascade_plot_params.sheet_by_index(0).col_values(2)[1:]                 # title for plot
ToBePlotted = cascade_plot_params.sheet_by_index(0).col_values(3)[1:]           # make this plot? True or False
Display_v = cascade_plot_params.sheet_by_index(0).col_values(4)[1:]             # Display plot on screen (True) or as png file (False)
flood_Q = cascade_plot_params.sheet_by_index(0).col_values(5)[1:]               # Flood discharge in cfs, if known
flood_Q_available_v = cascade_plot_params.sheet_by_index(0).col_values(6)[1:]   # We know flood discharge (True/False)
data_type_v = cascade_plot_params.sheet_by_index(0).col_values(7)[1:]           # What type of data is this? Stream, Dam, etc.
stats_available_v = cascade_plot_params.sheet_by_index(0).col_values(8)[1:]     # The stats file is available (True/False)
SI_v = cascade_plot_params.sheet_by_index(0).col_values(9)[1:]                  # Metric or standard units
breadth_v = cascade_plot_params.sheet_by_index(0).col_values(10)[1:]            # Breadth of simulations to create gray-scale
breadth_2nd_v = cascade_plot_params.sheet_by_index(0).col_values(11)[1:]        # Breadth of simulations to create gray-scale
breadth_3rd_v = cascade_plot_params.sheet_by_index(0).col_values(12)[1:]        # Breadth of simulations to create gray-scale

flood_Q[:] = [element*cst.cfs_to_m3 for element in flood_Q]   # convert flood_Q from cfs to m3/s

total_number_of_plots = len(file_model_csv)

## DO NOT DELETE THE NEXT 6 LINES:
## If you want to plot all scenarios, uncomment this line:
#AltScenarioList = list(cst.metadata.AltScenarios[0:6])

## If you only want to plot the scenario indicated in the master file, 
##   uncomment this line:
AltScenarioList = [str(file_model_csv[0]).split("_")[-2]]  #List of length 1
## DO NOT DELETE THE TEXT ABOVE HERE ^^^^^

# Make the plots.
for AltScenario in AltScenarioList:
    file_list_ToBeUsed = []
    for file in file_name_list: 
        file_list_ToBeUsed.append(file.replace('Ref', AltScenario))
    for plot_number in range(total_number_of_plots):
        if ToBePlotted[plot_number]:
            file_name_ToBeUsed = file_list_ToBeUsed[plot_number]
            cascade(
                AltScenario,
                file_name_ToBeUsed,
                file_stats[plot_number],
                list(file_stats),
                title[plot_number],
                flood_Q[plot_number],
                file_name_list,
                list(data_type_v),
                breadth_str = breadth_v[plot_number],
                breadth_str_2nd = breadth_2nd_v[plot_number],
                breadth_str_3rd = breadth_3rd_v[plot_number],
                Display = Display_v[plot_number],
                data_type = data_type_v[plot_number],
                flood_Q_available = flood_Q_available_v[plot_number],
                stats_available = stats_available_v[plot_number],
                SI = SI_v[plot_number]
                )
