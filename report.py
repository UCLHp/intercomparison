import json
# import datetime
import pandas as pd
import os

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, TableStyle, Table, PageBreak, Frame
from  reportlab.platypus.flowables import Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import pdfencrypt

from reportlab.lib import utils

import functions as fn
import config as cg

width, height = letter

def instrument_summary(values, tp):
    ''' make a summary table of ss and f instrument
        Report = object '''


    # calculate the field ndw from all energies
    # f_ndw_ave = fn.calc_fndws(values)
    f = fn.Chamber('f', values)
    fndws = f.fndws

    f_ndw_ave = sum(list(fndws.values()))/len(list(fndws.values()))
    f_ndw_std = fn.calc_sample_std(list(fndws.values()))


    f_ndw_str ='{:.5f}'.format(f_ndw_ave)
    std_str = '{:.5f}'.format(f_ndw_std)

    top_row = [' ', 'secondary standard (ss)', 'field (f)']
    chambers = ['Chambers: ', values['-SSCH-'], values['-FCH-']]
    electrometer = ['Electrometer: ',values['-SS_ELE-'], values['-F_ELE-']]
    ele_voltage = ['Voltage: ', values['-SS_ELE_VOLT-'], values['-F_ELE_VOLT-']]
    ele_range = ['Ele. range: ', values['-SS_ELE_RANGE-'], values['-F_ELE_RANGE-']]
    calc_f_ndw = [Paragraph('calc. N<sub>D,W</sub> (Gy/nC)', tp), '-', f_ndw_str + ' ± ' + std_str]

    if values['-PREV-fNDW-'] == "":
        # if no previous ndw record for f chamber, this could be a new chamber. display '-'

        ndw = [Paragraph('N<sub>D,W</sub> (Gy/nC) in database:', tp), values['-NDW-'], '-' ]
        # calc_f_ndw = [Paragraph('calc. N<sub>D,W</sub> (Gy/nC): ', tp), '-', str(f_ndw_ave)+ '%' ]
        percent_diff = ['% diff (%): ', '-',  '-']
    else:
        # if we have previous ndw in the database, calculate the percentage difference
        ndw = [Paragraph('N<sub>D,W</sub> (Gy/nC) in database', tp), values['-NDW-'], values['-PREV-fNDW-'] ]
        # calc_f_ndw = [Paragraph('calc. N<sub>D,W</sub> (Gy/nC)', tp), '-', f_ndw_str + ' ± ' + std_str]
        percent_diff = ['% diff (%): ', '-', str(fn.calc_percent_diff(float(values['-PREV-fNDW-']), f_ndw_ave)) + '%']

    rows = [top_row, chambers, electrometer, ele_voltage, ele_range, ndw, calc_f_ndw, percent_diff]

    return rows

def tabulate_data(values, np):
    ''' make a table to store the data'''

    prefix = ['ss', 'ssr', 'f', 'f_ndw']

    data = [['Energy (MeV)', Paragraph('mR<sub>ss</sub>', np),  Paragraph('mR<sub>ssr</sub>', np), Paragraph('mR<sub>f</sub>', np), Paragraph("N<sub>D,W</sub>(f)", np)]]

    ss = fn.Chamber('ss', values)
    f = fn.Chamber('f', values)
    ssr = fn.Chamber('ssr', values)

    ss_tot = []
    # f_ndws = []
    for en in cg.pro_en:
        ss_tot = []
        row = []
        row.append(en)
        # put all ss tpc corrected nRs in the same list
        ss_tot.extend(ss.tpc_nRs[en])
        ss_tot.extend(ssr.tpc_nRs[en])

        # calc ss ave (TPC corrected)
        ss_ave = '{:.3f}'.format(sum(ss.tpc_nRs[en])/len(ss.tpc_nRs[en]))
        ss_std = '{:.3f}'.format(fn.calc_sample_std(ss.tpc_nRs[en]))
        v = r"{} ± {}".format(ss_ave, ss_std)
        row.append(v)
        # calc ssr ave
        ssr_ave = '{:.3f}'.format(sum(ssr.tpc_nRs[en])/len(ssr.tpc_nRs[en]))
        ssr_std = '{:.3f}'.format(fn.calc_sample_std(ssr.tpc_nRs[en]))
        v = r"{} ± {}".format(ssr_ave, ssr_std)
        row.append(v)
        # calc f ave
        f_ave = '{:.3f}'.format(sum(f.tpc_nRs[en])/len(f.tpc_nRs[en]))
        f_std = '{:.3f}'.format(fn.calc_sample_std(f.tpc_nRs[en]))
        v = r"{} ± {}".format(f_ave, f_std)
        row.append(v)

        # calc f_N<sub>D,W</sub>
        sst_ave = sum(ss_tot)/len(ss_tot)
        f_ndw =  (ss.ssndw)*(sst_ave)/(sum(f.tpc_nRs[en])/len(f.tpc_nRs[en]))
        f_ndw = '{:.5f}'.format(f_ndw)

        v = r"{} ".format(f_ndw)
        row.append(v)

        # add to the data
        data.append(row)

    return data

class Report:
    def __init__(self, values, ndw_fetch_msg, eqt_ndw_path, eqt_std_path, ss_drift_path, fndws_path):

        self.values = values
        self.ndw_fetch_msg = ndw_fetch_msg
        self.eqt_ndw_path = eqt_ndw_path
        self.eqt_std_path = eqt_std_path
        self.ss_drift_path = ss_drift_path
        self.fndws_path = fndws_path

        # date/ time
        date = values['-DATETIME-'].split()
        self.date = date[0]

        # operators
        op1 = values['-PERSON1-']
        op2 = values['-PERSON2-']

        if op2:
            self.operators = op1 + '_' + op2
        else:
            self.operators = op1

        # gantry angle
        gantry_angle = values['-GA-']
        gantry_no = self.values['-GANTRY-'].split(" ")[1]
        report_name = 'IC_%s_G%s_GA%s_%s.pdf' % (self.date, str(gantry_no), self.values['-GA-'], self.operators)
        self.report_name = report_name

        self.doc = SimpleDocTemplate(self.report_name,pagesize=letter,
                                rightMargin=60,leftMargin=60,
                                topMargin=20,bottomMargin=20)

        # define head paragraph style
        # styles = getSampleStyleSheet()
        self.hp = ParagraphStyle(
                                'CustomStyle',
                                textColor=colors.black,    # Text color
                                fontSize=15,               # Font size
                                fontName='Helvetica-Bold',      # Font name
                                spaceAfter=12,             # Space after the paragraph
                                leading=16,                # Line spacing
                                )

        # subtitle paragraph
        self.sp = ParagraphStyle(
                                'CustomStyle',
                                textColor = colors.black,    # Text color
                                fontSize = 11,               # Font size
                                fontName = 'Helvetica-Bold',      # Font name
                                spaceBefore = 3,             # Space before the paragraph
                                spaceAfter = 3,             # Space after the paragraph
                                leading = 16,                # Line spacing
                                underline = True,            # underline the font
                                underlineWidth = 10           # Underline weight
                                )

        # normal text
        self.np = ParagraphStyle(
                                'CustomStyle',
                                textColor = colors.black,    # Text color
                                fontSize = 11,               # Font size
                                fontName = 'Times-Roman',      # Font name
                                spaceBefore = 3,             # Space before the paragraph
                                spaceAfter = 3,             # Space after the paragraph
                                leading = 15,                # Line spacing
                                underlineWidth = 1           # Underline weight
                                )

        # text for center alignment (text in table)
        self.tp = ParagraphStyle(
                                 'CustomStyle',
                                 textColor = colors.black,    # Text color
                                 fontSize = 11,               # Font size
                                 fontName = 'Times-Roman',      # Font name
                                 spaceBefore = 3,             # Space before the paragraph
                                 spaceAfter = 3,             # Space after the paragraph
                                 leading = 15,                # Line spacing
                                 underlineWidth = 1,           # Underline weight
                                 alignment = 1               # 0 for left, 1 for center, 2 for right alignment
                                 )

        # checked but warning paragraph
        self.wp = ParagraphStyle(
                                'CustomStyle',
                                textColor = colors.red,    # Text color
                                fontSize = 11,               # Font size
                                fontName = 'Times-Roman',      # Font name
                                spaceBefore = 3,             # Space before the paragraph
                                spaceAfter = 3,             # Space after the paragraph
                                leading = 15                # Line spacing

                                )

        # checked but passed paragraph
        self.pp =ParagraphStyle(
                                'CustomStyle',
                                textColor = colors.blue,    # Text color
                                fontSize = 11,               # Font size
                                fontName = 'Times-Roman',      # Font name
                                spaceBefore = 3,             # Space before the paragraph
                                spaceAfter = 3,             # Space after the paragraph
                                leading = 15
                                )

    def write_report(self):
    # def write_report(self, values, ndw_fetch_msg, eqt_ndw_path, eqt_std_path ):
        ''' prepare the report
            values =  the input values from GUI
            ndw_fetch_msg = message to indicate whether fetching data from database is sucessfully or not
            eqt_ndw_path = path to eqt_ndw.PNG
            eqt_std_path = path to eqt_std.PNG '''


        story = []

        #  Report header
        report_title = ' %s intercomparison report' % self.values['-FCH-']
        story.append(Paragraph(report_title, self.hp))
        story.append(Paragraph('Date: ' + self.values['-DATETIME-'], self.np))
        story.append(Paragraph('Gantry: ' + self.values['-GANTRY-'], self.np))
        story.append(Paragraph('Gantry angle: ' + self.values['-GA-'], self.np))
        story.append(Paragraph('Operator(s): ' + self.operators, self.np))
        story.append(Paragraph('Material: ' + self.values['-MATERIAL-'], self.np))
        story.append(Paragraph('Humidity: ' + self.values['-HUMIDITY-'], self.np))
        story.append(Paragraph('Comment: ' + self.values['-COMMENT-'], self.np))

        # add an empty line
        story.append(Spacer(1, 5))

        story.append(Paragraph('Summary: ', self.sp))


        if "success" in self.ndw_fetch_msg:
            story.append(Paragraph('- ' + self.ndw_fetch_msg, self.pp))
        else:
            story.append(Paragraph('- ' + self.ndw_fetch_msg, self.wp))

        # tabulate the secondary standard and field chamber measuurement requirement
        story.append(Spacer(1, 5))
        # show NDW equation
        im_ndw = Image(self.eqt_ndw_path, width = 2.5*inch,  height = 0.5*inch,   hAlign = 'CENTER')
        story.append(im_ndw)

        story.append(Paragraph("Equation 1 calculates the field chamber N<sub>D,W</sub>, \
                                where N<sub>D,W</sub>(ss) is the secondary standard N<sub>D,W</sub>, \
                                mR<sub>ss</sub> and mR<sub>f</sub> are average nCs measured by a ss and f chambers, respectively.\
                                The former calculates from eight ss measurements,and the latter calculates from five measurements. \
                                TPC factors were applied to calculate mRs. ", self.np))
        story.append(Spacer(1, 5))



        summary_instrument = instrument_summary(self.values, self.tp)
        table_instrument = Table(summary_instrument)
        table_instrument.setStyle(TableStyle([('VALIGN', (0,0), (-1, -1), 'MIDDLE'), ('ALIGN', (0,0), (-1, -1), 'CENTER'), \
                               ('BACKGROUND', (0, 0), (-1, -1), colors.white), ('BOX', (0, 0), (-1, -1), 2, colors.black), \
                               ('BOX', (0, 0), (0, -1), 2, colors.black), ('BOX', (0, 0), (-1, 0), 2, colors.black)]))

        story.append(table_instrument)
        story.append(Paragraph('Table 1: Measurement parameters for the secondary standard and field chambers. The calc N<sub>D,W</sub>(f) presents as average N<sub>D,W</sub>(f) from all energies ± σ. ', self.np))

        # show fndws.png
        im_fndws = Image(self.fndws_path, width = 4*inch,  height = 2.8*inch,   hAlign = 'CENTER')
        story.append(im_fndws)
        story.append(Paragraph('Figure 1: The calculated N<sub>D,W</sub> as a function of proton energy. \
                                The mR are calculated from TPC corrected readings. \
                                The dotted lines indicate ±2σ regarding equation 2.', self.np))

        # add an empty line
        story.append(Spacer(1, 20))

        story.append(Paragraph('Measurement results: ', self.sp))

        data = tabulate_data(self.values, self.tp)
        table_data = Table(data)
        table_data.setStyle(TableStyle([('VALIGN', (0,0), (-1, -1), 'MIDDLE'), ('ALIGN', (0,0), (-1, -1), 'CENTER'), \
                               ('BACKGROUND', (0, 0), (-1, -1), colors.white), ('BOX', (0, 0), (-1, -1), 2, colors.black), \
                               ('BOX', (0, 0), (0, -1), 2, colors.black), ('BOX', (0, 0), (-1, 0), 2, colors.black)]))

        story.append(table_data)
        story.append(Paragraph('Table 2: The average (±σ, from equation 2) TPC corrected nC of secondary standard (ss), repeated secondary standard (ssr) and field (f) sections. ', self.np))

        # show stds equation
        im_std = Image(self.eqt_std_path, width = 1.7*inch,  height = 0.8*inch,   hAlign = 'CENTER')
        story.append(im_std)

        story.append(Paragraph("Equation 2 calculates standard deviation (σ) for TPC corrected mR<sub>ss</sub>, mR<sub>ssr</sub>, mR<sub>f</sub>, and N<sub>D,W</sub>(f). \
                                where σ is the sample standard deviation, N is the total number of observations, x<sub>i</sub> is the observed value of sample i and x is \
                                the mean value of all observations.", self.np))
        story.append(Spacer(1, 10))

        # show ss_drift.png
        im_ss_drift = Image(self.ss_drift_path, width = 8*inch,  height = 3*inch,   hAlign = 'CENTER')
        story.append(im_ss_drift)
        story.append(Paragraph('Figure 2: The SSR average mR difference from SS (Left) and the SSR percentage difference from SS (Right) as a function of proton energy ', self.np))





        self.doc.build(story)



        return
