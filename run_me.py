import pandas as pd
import numpy as np
import PySimpleGUI as sg

import pypyodbc
import config as cg
import os
from datetime import datetime
import shutil

import functions as fn
import figures as fg

import report as rp
import database as db




def main():

    # get current directory, std_eqt.PNG, eqt_ndw.PNG
    home_dir = os.getcwd()
    eqt_ndw_path = os.path.join(home_dir, 'eqt_ndw.PNG')
    eqt_std_path = os.path.join(home_dir, 'eqt_std.PNG')

    theme = 'DefaultNoMoreNagging'

    event, values, ndw_fetch_msg, window = fn.make_GUI(theme)

    if event == 'Submit':

        # --- trouble-shooting --

        # # for uclh
        # values = {'-DATETIME-': '2023-12-28 21:42:40', 'DATE + TIME': '', '-PERSON1-': 'KC', '-PERSON2-': '', '-GANTRY-': '3', '-GA-': '0', '-MATERIAL-': 'solid water (RW3)', '-HUMIDITY-': '50.2', '-SSCH-': '3126', '-SS_ELE-': '92580', '-SS_ELE_RANGE-': 'Medium', '-SS_ELE_VOLT-': '-200', '-FCH-': '3735', '-F_ELE-': '92581', '-F_ELE_RANGE-': 'Medium', '-F_ELE_VOLT-': '-200', '-COMMENT-': 'test', '-RESULT_LOC-': 'C:/Users/KAWCHUNG/Downloads', 'Browse': 'C:/Users/KAWCHUNG/Downloads', '-NDW-': '0.08470', '-PREV-fNDW-': '0.08320', '-CALC-fNDW-': '0.08323', '-ss_TEMP-': '22.8', '-ss_PRESSURE-': '998.6', '-ss_TPC-': '1.0244', '-ssR1_240-': '6.442', '-ssR1_210-': '6.414', '-ssR1_180-': '6.394', '-ssR1_170-': '6.396', '-ssR1_160-': '6.409', '-ssR1_110-': '6.683', '-ssR1_70-': '8.206', '-ssR2_240-': '6.452', '-ssR2_210-': '6.415', '-ssR2_180-': '6.396', '-ssR2_170-': '6.407', '-ssR2_160-': '6.407', '-ssR2_110-': '6.688', '-ssR2_70-': '8.216', '-ssR3_240-': '6.443', '-ssR3_210-': '6.416', '-ssR3_180-': '6.397', '-ssR3_170-': '6.404', '-ssR3_160-': '6.411', '-ssR3_110-': '6.693', '-ssR3_70-': '8.212', '-ssR4_240-': '6.458', '-ssR4_210-': '6.42', '-ssR4_180-': '6.402', '-ssR4_170-': '6.405', '-ssR4_160-': '6.415', '-ssR4_110-': '6.693', '-ssR4_70-': '8.217', '-ssR5_240-': '6.448', '-ssR5_210-': '6.415', '-ssR5_180-': '6.396', '-ssR5_170-': '6.401', '-ssR5_160-': '6.409', '-ssR5_110-': '6.682', '-ssR5_70-': '8.212', '-ssAVE_240-': '6.449', '-ssAVE_210-': '6.416', '-ssAVE_180-': '6.397', '-ssAVE_170-': '6.403', '-ssAVE_160-': '6.41', '-ssAVE_110-': '6.688', '-ssAVE_70-': '8.213', '-ssSTD_240-': '0.00662', '-ssSTD_210-': '0.00235', '-ssSTD_180-': '0.003', '-ssSTD_170-': '0.00428', '-ssSTD_160-': '0.00303', '-ssSTD_110-': '0.00526', '-ssSTD_70-': '0.00434', '-f_TEMP-': '22.9', '-f_PRESSURE-': '998.6', '-f_TPC-': '1.0247', '-fR1_240-': '6.551', '-fR1_210-': '6.523', '-fR1_180-': '6.504', '-fR1_170-': '6.508', '-fR1_160-': '6.521', '-fR1_110-': '6.805', '-fR1_70-': '8.349', '-fR2_240-': '6.563', '-fR2_210-': '6.525', '-fR2_180-': '6.507', '-fR2_170-': '6.52', '-fR2_160-': '6.526', '-fR2_110-': '6.81', '-fR2_70-': '8.356', '-fR3_240-': '6.56', '-fR3_210-': '6.525', '-fR3_180-': '6.513', '-fR3_170-': '6.519', '-fR3_160-': '6.524', '-fR3_110-': '6.806', '-fR3_70-': '8.36', '-fR4_240-': '6.554', '-fR4_210-': '6.519', '-fR4_180-': '6.507', '-fR4_170-': '6.513', '-fR4_160-': '6.521', '-fR4_110-': '6.801', '-fR4_70-': '8.35', '-fR5_240-': '6.566', '-fR5_210-': '6.527', '-fR5_180-': '6.509', '-fR5_170-': '6.516', '-fR5_160-': '6.525', '-fR5_110-': '6.808', '-fR5_70-': '8.358', '-fAVE_240-': '6.559', '-fAVE_210-': '6.524', '-fAVE_180-': '6.508', '-fAVE_170-': '6.515', '-fAVE_160-': '6.523', '-fAVE_110-': '6.806', '-fAVE_70-': '8.355', '-fSTD_240-': '0.00622', '-fSTD_210-': '0.00303', '-fSTD_180-': '0.00332', '-fSTD_170-': '0.00487', '-fSTD_160-': '0.0023', '-fSTD_110-': '0.00339', '-fSTD_70-': '0.00488', '-ssr_TEMP-': '22.8', '-ssr_PRESSURE-': '998.6', '-ssr_TPC-': '1.0244', '-ssrR1_240-': '6.453', '-ssrR1_210-': '6.41', '-ssrR1_180-': '6.4', '-ssrR1_170-': '6.402', '-ssrR1_160-': '6.407', '-ssrR1_110-': '6.684', '-ssrR1_70-': '8.211', '-ssrR2_240-': '6.452', '-ssrR2_210-': '6.415', '-ssrR2_180-': '6.394', '-ssrR2_170-': '6.401', '-ssrR2_160-': '6.414', '-ssrR2_110-': '6.687', '-ssrR2_70-': '8.216', '-ssrR3_240-': '6.452', '-ssrR3_210-': '6.414', '-ssrR3_180-': '6.395', '-ssrR3_170-': '6.405', '-ssrR3_160-': '6.41', '-ssrR3_110-': '6.684', '-ssrR3_70-': '8.212', '-ssrAVE_240-': '6.452', '-ssrAVE_210-': '6.413', '-ssrAVE_180-': '6.396', '-ssrAVE_170-': '6.403', '-ssrAVE_160-': '6.41', '-ssrAVE_110-': '6.685', '-ssrAVE_70-': '8.213', '-ssrSTD_240-': '0.00058', '-ssrSTD_210-': '0.00265', '-ssrSTD_180-': '0.00321', '-ssrSTD_170-': '0.00208', '-ssrSTD_160-': '0.00351', '-ssrSTD_110-': '0.00173', '-ssrSTD_70-': '0.00265', '-f_ndw_240-': '0.08327', '-f_ndw_210-': '0.08326', '-f_ndw_180-': '0.08323', '-f_ndw_170-': '0.08321', '-f_ndw_160-': '0.08321', '-f_ndw_110-': '0.08319', '-f_ndw_70-': '0.08324', '-CSV_LOC-': '', 'Browse0': ''}

        # # --- trouble-shooting --
        print(f'event: {event}')
        print(f'values: {values}')

        # make a folder to store the report
        mdate = str(datetime.strptime(values['-DATETIME-'], '%Y-%m-%d %H:%M:%S').date())
        mdate = mdate.replace('-', '_')

        ss_chamber = values['-SSCH-']
        f_chamber = values['-FCH-']

        folder_name = 'IC_' + mdate + '_SS_' + ss_chamber + '_F_' + f_chamber
        # move the csv to the report folder
        csv_fn = folder_name + '.csv'

        if values['-RESULT_LOC-']:

            os.chdir(values['-RESULT_LOC-'])
            csv_saving_dir = os.getcwd()
            # make a folder
            os.makedirs(folder_name, exist_ok = True)
            # data_dir = os.path.join(csv_saving_dir, folder_name)
            os.chdir(folder_name)
            report_dir = os.getcwd()

            # move csv
            shutil.move(os.path.join(csv_saving_dir, csv_fn), os.path.join(report_dir, csv_fn))
        else:
            # if the values['-RESULT_LOC-'] is empty
            user_home_dir = os.path.expanduser('~')
            csv_saving_dir = os.path.join(user_home_dir, 'Downloads')
            os.chdir(csv_saving_dir)

            # make a folder
            os.makedirs(folder_name, exist_ok = True)

            os.chdir(folder_name)
            report_dir = os.getcwd()
            print(f'csv_saving_dir: {csv_saving_dir}')
            shutil.move(os.path.join(csv_saving_dir , csv_fn), os.path.join(report_dir, csv_fn))


        # create an object for ssChamber
        ssChamber = fn.Chamber('ss', values)
        fChamber = fn.Chamber('f', values)
        ssrChamber = fn.Chamber('ssr', values)

        # preparing the report
        fg.plot_drift(ssChamber.nRs, ssChamber.tpc, ssrChamber.nRs, ssrChamber.tpc)
        ss_drift_path = os.path.join(report_dir, 'ss_drift.PNG')

        fg.plot_fndws(values)
        fndws_path = os.path.join(report_dir, 'fndws.PNG')

        Report = rp.Report(values, ndw_fetch_msg, eqt_ndw_path, eqt_std_path, ss_drift_path, fndws_path)
        Report.write_report()

        # second gui to prompt the operator to check the report before
        window2 = fn.make_window_after_reviewing_data(theme)
        event2, values2 = window2.read()

        window2.close()

        # put the comment from second gui box to values[-COMMENT-]
        if values2['-COMMENT2-']:
            values['-COMMENT-'] = values['-COMMENT-'] + ' ' + values2['-COMMENT2-']

        # re-print the report with all comments
        Report = rp.Report(values, ndw_fetch_msg, eqt_ndw_path, eqt_std_path, ss_drift_path, fndws_path)
        Report.write_report()

        if event2 == "Submit":
            # create session table
            session = db.make_session_data(values)
            push_session_data = db.push_session_data(cg.DATABASE_DIR, session,  PWD = cg.PWD )

            if push_session_data == True: # successfully pushed session data
                # make the session data
                all_data = db.make_measurement_data(values)
                push_measurement_data = db.push_measurement_data(cg.DATABASE_DIR, all_data,  PWD = cg.PWD)

                if push_measurement_data == True:
                    print(f'Data analysed and pushed to the database. Intercomparison is done.')


if __name__ == '__main__':

    main()
