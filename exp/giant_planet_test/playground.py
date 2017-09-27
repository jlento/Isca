import numpy as np
import os
import remove_certain_restart_and_data_files as rem

from gfdl.experiment import Experiment, DiagTable

baseexp = Experiment('giant_planet_test', overwrite_data=False)

diag = DiagTable()

diag.add_file('atmos_monthly', 30, 'days', time_units='days')

# Define diag table entries 
diag.add_field('dynamics', 'ps', time_avg=True)
diag.add_field('dynamics', 'bk', time_avg=True)
diag.add_field('dynamics', 'pk', time_avg=True)
diag.add_field('dynamics', 'vor', time_avg=True)
diag.add_field('dynamics', 'div', time_avg=True)
diag.add_field('dynamics', 'ucomp', time_avg=True)
diag.add_field('dynamics', 'vcomp', time_avg=True)
diag.add_field('dynamics', 'temp', time_avg=True)
diag.add_field('atmosphere', 'rh', time_avg=True)
diag.add_field('dynamics', 'sphum', time_avg=True)
diag.add_field('dynamics', 'omega', time_avg=True)
diag.add_field('dynamics', 'height', time_avg=True)
diag.add_field('dynamics', 'EKE', time_avg=True)
diag.add_field('two_stream', 'tdt_rad', time_avg=True)
diag.add_field('atmosphere', 'diss_heat_ray', time_avg=True)
diag.add_field('damping', 'diss_heat_rdamp', time_avg=True)

baseexp.disable_rrtm()

baseexp.use_diag_table(diag)

baseexp.compile()

baseexp.clear_rundir()

#s Namelist changes from default values
baseexp.namelist['main_nml'] = {
     'days'   : 30,	
     'hours'  : 0,
     'minutes': 0,
     'seconds': 0,			
     'dt_atmos':1800,
     'current_date' : [0001,1,1,0,0,0],
     'calendar' : 'no_calendar'
}

baseexp.namelist['fms_nml']['domains_stack_size'] = 620000
baseexp.namelist['idealized_moist_phys_nml']['two_stream_gray'] = True
baseexp.namelist['idealized_moist_phys_nml']['do_rrtm_radiation'] = False

baseexp.namelist['idealized_moist_phys_nml']['gp_surface'] = True
baseexp.namelist['idealized_moist_phys_nml']['mixed_layer_bc'] = False

baseexp.namelist['two_stream_gray_rad_nml']['rad_scheme'] = 'Schneider'
baseexp.namelist['two_stream_gray_rad_nml']['do_seasonal'] = False

baseexp.namelist['two_stream_gray_rad_nml']['solar_constant'] = 50.7
baseexp.namelist['two_stream_gray_rad_nml']['diabatic_acce'] = 1.0

baseexp.namelist['surface_flux_nml']['diabatic_acce'] = 1.0

baseexp.namelist['constants_nml']['radius'] = 69860.0e3
baseexp.namelist['constants_nml']['grav'] = 26.0
baseexp.namelist['constants_nml']['omega'] = 1.7587e-4
baseexp.namelist['constants_nml']['orbital_period'] = 4332.589*86400.
baseexp.namelist['constants_nml']['PSTD'] = 3.0E+06
baseexp.namelist['constants_nml']['PSTD_MKS'] = 3.0E+05
baseexp.namelist['constants_nml']['rdgas'] = 3605.38

baseexp.namelist['sat_vapor_pres_nml']['tcmin_simple'] = -223

baseexp.namelist['spectral_dynamics_nml']['reference_sea_level_press'] = 3.0e5
baseexp.namelist['spectral_dynamics_nml']['vert_coord_option'] = 'even_sigma'
baseexp.namelist['spectral_dynamics_nml']['surf_res'] = 0.1
baseexp.namelist['spectral_dynamics_nml']['exponent'] = 2.0
baseexp.namelist['spectral_dynamics_nml']['scale_heights'] = 5.0
baseexp.namelist['spectral_dynamics_nml']['valid_range_t'] =[50.,800.]

baseexp.namelist['spectral_dynamics_nml']['num_fourier'] = 213
baseexp.namelist['spectral_dynamics_nml']['num_spherical'] = 214
baseexp.namelist['spectral_dynamics_nml']['lon_max'] = 1024
baseexp.namelist['spectral_dynamics_nml']['lat_max'] = 320
baseexp.namelist['spectral_dynamics_nml']['num_levels'] = 30

baseexp.namelist['spectral_dynamics_nml']['do_water_correction'] = False

baseexp.namelist['spectral_dynamics_nml']['damping_option'] = 'exponential_cutoff'
baseexp.namelist['spectral_dynamics_nml']['damping_order'] = 4
baseexp.namelist['spectral_dynamics_nml']['damping_coeff'] = 1.3889e-04
baseexp.namelist['spectral_dynamics_nml']['cutoff_wn'] = 100
baseexp.namelist['spectral_dynamics_nml']['initial_sphum'] = 0.0
baseexp.namelist['spectral_init_cond_nml']['initial_temperature'] = 200.
baseexp.namelist['idealized_moist_phys_nml']['convection_scheme'] = 'dry'

baseexp.namelist['rayleigh_bottom_drag_nml']= {
	'kf_days':10.0,
	'do_drag_at_surface':True,
	'variable_drag': False
	}

baseexp.namelist['dry_convection_nml'] = {
    'tau': 21600.,
    'gamma': 1.0, # K/km
}


kf_days_array    =[5.]

start_month_array=[2]
end_month_array  =[1202]

for exp_number in [1]:
    exp = baseexp.derive('giant_drag_exp_chai_values_1_bar_damping_%d' % exp_number)
    exp.clear_rundir()

    exp.namelist['rayleigh_bottom_drag_nml']['kf_days'] = kf_days_array[exp_number-1]

    exp.runmonth(1,num_cores=16, use_restart=False)

    for i in range(start_month_array[exp_number-1], end_month_array[exp_number-1]):
        successful_run = exp.runmonth(i,num_cores=32)

        if successful_run:
            print 'cleaning'
            max_num_files_input = np.max([0, i-5])

            temp_obj = rem.create_exp_object(exp.name)
            rem.keep_only_certain_restart_files(temp_obj, max_num_files_input)
            rem.keep_only_certain_restart_files_data_dir(temp_obj, max_num_files_input)
            rem.keep_only_certain_daily_data_uninterp(temp_obj, max_num_files_input, file_name = 'fms_moist.x')
            rem.keep_only_certain_daily_data_uninterp(temp_obj, max_num_files_input, file_name = 'INPUT/spectral_dynamics.res.nc')
            rem.keep_only_certain_daily_data_uninterp(temp_obj, max_num_files_input, file_name = 'INPUT/atmosphere.res.nc')