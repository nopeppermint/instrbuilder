import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import rcParams
from databroker import Broker
from scipy.interpolate import splev, splrep

figure_dir = '/Users/koer2434/Google Drive/UST/research/bluesky/manuscript/bluesky_manuscript/figures/'
params = {
   'axes.labelsize': 8,
   'font.size': 8,
   'legend.fontsize': 8,
   'xtick.labelsize': 10,
   'ytick.labelsize': 10,
   'text.usetex': True,
   'figure.figsize': [4.5, 4.5]
   }
rcParams.update(params)

db = Broker.named('local_file')  # a broker poses queries for saved data sets)
uid = 'e70932a0-7b44-44e1-96cf-b3f9971693a2'
uid = '19fb9f07-3edc-4082-b1c7-cfe1224e8865'
uid = 'aa1fb303-c62a-4518-9ea0-49cc9cd08837'
header = db[uid]  # db is a DataBroker instance
df = header.table()

plt.figure(dpi=300)
for fs in df['lockin_filt_slope'].unique():
    idx = (df['lockin_filt_slope'] == fs)
    plt.semilogy(df.loc[idx]['fgen_freq'][1:-1], df.loc[idx]['lockin_disp_val'][1:-1],
                 marker='*',
                 label='Filter = {}'.format(fs.replace('-', ' ')))
    # above remove the first measurement due to incomplete settling after stepping the filter slope
    #       also remove the last element [for symmetry]

plt.grid(True)
plt.legend()
plt.ylabel('R [V RMS]')
plt.xlabel('f [Hz]')
plt.savefig(os.path.join(figure_dir, 'freq_res_sr810_preamp.eps'))

# ----------- analyze the data ------

# get instrument parameters from the metadata! No need to refer to a lab notebook.
fref = header['start']['lia_config']['lockin_freq']['value']  # lock-in reference frequency
tau = header['start']['lia_config']['lockin_tau']['value']  # lock-in time-constant
fc = 1/(2*np.pi*tau)  # find the filter cutoff frequency

for fs in df['lockin_filt_slope'].unique():
    idx = (df['lockin_filt_slope'] == fs)
    x = df.loc[idx]['fgen_freq'][1:-1]
    y = df.loc[idx]['lockin_disp_val'][1:-1]

    # find peak amplitude and freq. of peak amplitude at frequency close to fref
    f_search = np.linspace(fref - 6, fref + 6, num=10000)

    spl = splrep(x, y)
    val_int = splev(f_search, spl)
    plt.plot(f_search, val_int, marker='o')

    amp_fref = np.max(val_int)
    max_f = f_search[np.where(val_int == amp_fref)][0]

    print('At filter-slope of {}; peak amplitude of {:.3f} at {:.3f} Hz'.format(fs, amp_fref, max_f))

    for octave in [0, 1, 2, 3]:
        # find amplitude at a number of octaves beyond cutoff frequency
        amp_fref_oct = np.asscalar(splev(max_f + 2**octave*fc, spl))
        # find amplitude 2 octaves beyond cutoff frequency
        # print result, 1 octave; 2 octaves
        print('{} octave past cutoff {:.3f}; attenuation = {:.3f} dB'.format(octave,
                                                                     amp_fref_oct, 20*np.log10(amp_fref_oct/amp_fref)))

# --------- metadata -----------------
header['start']
header['stop']

# view the baseline data (i.e. configuration values)
header.table('baseline')
