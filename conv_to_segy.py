import numpy as np

import matplotlib.pyplot as plt
import segyio


class MySpec(object):
    def __init__(self):
        self.iline = 189  # default value for segyio
        self.xline = 193  # default value for segyio
        self.tracecount = 0
        self.samples = []  # sample times, a list
        self.ext_headers = 0
        self.format = 5  # 4-byte IEEE float
        self.endian = 'big'

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


with segyio.open(filename=path, mode="r",
                            strict = False,
                            ignore_geometry = True,
                            endian = 'big') as f:
    # print(np.shape(f.trace.raw[:]))
    # plot_rawtraces(f.trace.raw[:])
    
    print('\n_____SEG-Y FILE____\n')
    
    print(f'Sample format: {f.format}')
    print(f'Sample count: {len(f.samples)}')
    print(f'Trace count: {f.tracecount}')
    
    print(f'{f.bin}')
    # print(f.text[0])
    print(f.header)
    print(f.trace)
    

print('\n_____SPEC____\n')
spec = MySpec()

# Mandatory
# print(spec.iline)
# print(spec.xline)
# print(spec.samples)  # times
# print(spec.format)
# Exclusive
# spec.tracecount
# Optional


# print(spec.xlines)
# print(spec.sorting)
# print(spec.ext_headers)
# print(spec.endian)
# print(spec.ext_headers)