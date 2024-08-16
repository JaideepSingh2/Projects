import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import scipy.signal
import matplotlib.pyplot as plt

def freq_peak(sig,freq):
    low = 40/60
    high = 180/60

    sig = sig-np.mean(sig)
    sig = np.hstack((sig,np.zeros(500)))
    
    ft = np.fft.fft(sig)
    a = np.abs(ft)
    freq_axis = freq*np.arange(len(sig))/(len(sig))

    band = freq_axis[(freq_axis>low)*(freq_axis<high)]
    mag = a[(freq_axis>low)*(freq_axis<high)]
    
    ind = np.argmax(mag)
    hbs = band[ind]
    hb = hbs*60
    return np.max(mag),hb
