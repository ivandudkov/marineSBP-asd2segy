import numpy as np

import matplotlib.pyplot as plt
import segyio


def plot_rawtraces(raw_traces):
    clip = 1e+3
    vmin, vmax = -clip, clip

    # Figure
    figsize=(20, 20)
    fig, axs = plt.subplots(nrows=1, ncols=1, figsize=figsize, facecolor='w', edgecolor='k',
                        squeeze=False,
                        sharex=True)
    axs = axs.ravel()
    im = axs[0].imshow(raw_traces.T, cmap=plt.cm.seismic, vmin=vmin, vmax=vmax)
    plt.show()


path = r'D:\aa_yandexcloud\InspectingP70Data\P70_data\Profile-0_W1_SLF2109171103_LL_car.sgy'


with segyio.open(filename=path, mode="r", iline = 189,
                             xline = 193,
                             strict = False,
                             ignore_geometry = True,
                             endian = 'big') as f:
    print(np.shape(f.trace.raw[:]))
    plot_rawtraces(f.trace.raw[:])

file_spec = segyio.spec()

print(file_spec.iline)