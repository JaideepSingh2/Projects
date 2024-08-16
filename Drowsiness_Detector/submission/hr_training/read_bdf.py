import pyedflib
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import sys

if len(sys.argv) != 2:
    print("You must specify a bdf file!")
    quit()

f = pyedflib.EdfReader(sys.argv[1])

#print(f.file_duration)
for i in [32,33,34]:
    sig = f.readSignal(i)
    freq = f.getSampleFrequency(i)

    print(freq)
    print("samples in file: %i" % f.getNSamples()[i])
    
    #consider lowpass filtering
    
    sig = sig-np.mean(sig)
    peaks, _ = find_peaks(-sig,height=0,distance=150)
    #peaks, _ = find_peaks(-sig)
    plt.plot(sig)
    plt.plot(peaks,sig[peaks],"x")
    plt.show()

    sig = 0*sig
    sig[peaks] = 1
    sig = sig-np.mean(sig)
    ft = np.fft.fft(sig)
    a = np.abs(ft)

    plt.plot(sig)
    plt.show()
    
    low = 30/60
    high = 200/60
    
    freq_axis = freq*np.arange(len(a))/len(a)

    band = freq_axis[(freq_axis>low)*(freq_axis<high)]

    mag = a[(freq_axis>low)*(freq_axis<high)]

    ind = np.argmax(mag)
    hbs = band[ind]
    hb = hbs*60
    print(hb)
