import matplotlib.pyplot as plt

import config as cg
import functions as fn



def plot_drift(ss_dict, ss_tpc, ssr_dict, ssr_tpc):
    ''' assess any drift between two datasets'''

    ss_ave, ss_std = fn.calc_ave_std(ss_dict, ss_tpc)
    ssr_ave, ssr_std = fn.calc_ave_std(ssr_dict, ssr_tpc)

    # create en in a list
    ens = [float(e) for e in cg.pro_en]

    ssmssr = {}
    pssmssr = {}
    for en in cg.pro_en:
        d = ss_ave[en] - ssr_ave[en]

        # append ss_dict
        p = 100*d/ss_ave[en]
        ssmssr.update({en:d})
        pssmssr.update({en:p})

    fig, axes = plt.subplots(nrows =1, ncols =2, sharex = True, figsize = (12,4))

    axes[0].plot(ens, list(ssmssr.values()), 'k^', fillstyle = 'none')
    axes[0].axhline(y=0, color='gray',linestyle='--', linewidth=0.7)
    axes[0].set_ylabel('difference (nC)')
    axes[0].set_title('TPC corrected, ss-ssr', fontsize = 8)
    axes[0].set_xlim(60, 250)
    axes[0].set_xticks(range(60, 251, 30))

    axes[1].plot(ens, list(pssmssr.values()), 'ks', fillstyle='none')
    axes[1].axhline(y=0, color='gray',linestyle='--', linewidth=0.7)
    axes[1].set_ylabel('percentage diff. (%)')
    axes[1].set_title('TPC corrected nC, 100*(ss-ssr)/ss', fontsize = 8)
    axes[1].set_xlim(60, 250)
    axes[1].set_xticks(range(60, 251, 30))

    fig.supxlabel('proton energy (MeV)')
    plt.tight_layout()
    plt.savefig('ss_drift.PNG')
    # plt.show()
    return

def plot_fndws(values):
    ''' plot f_ndw as a function of proton energy'''

    f = fn.Chamber('f', values)

    ens = list(f.fndws.keys())
    vals = list(f.fndws.values()) # with TPC

    ave_ndw = sum(vals)/len(vals)
    std = fn.calc_sample_std(vals)

    fig, axe = plt.subplots(nrows =1, ncols =1, sharex = True, figsize = (6, 4))

    axe.plot(ens, vals, 'ko', fillstyle = 'none' )
    axe.axhline(y = ave_ndw, color='black',linestyle='-', linewidth=1)
    axe.axhline(y = ave_ndw + 2 * std, color='#AAA662',linestyle='--', linewidth=1)
    axe.axhline(y = ave_ndw - 2 * std, color='#AAA662',linestyle='--', linewidth=1)
    axe.set_xlim(60, 250)
    axe.set_xticks(range(60, 251, 30))

    axe.set_xlabel('proton energy (MeV)')
    axe.set_ylabel('field chamber NDW (Gy/nC)')
    plt.tight_layout()
    plt.savefig('fndws.PNG')

    return
