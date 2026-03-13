import numpy as np
import matplotlib.pyplot as plt
import scipy.signal

fs = sample_rate = 100000.

times = np.arange(0, 100., 1./sample_rate, dtype='float64')
sigsize = times.size
sigs = np.random.randn(times.size, 2) * 3.
#~ sigs = np.zeros((times.size, 2))
#~ sigs[:, 0] += np.sin(times * 2 * np.pi *5000.) * 1.5
print(sigs)
#~ sigs[:, 1] += np.sin(times * 2 * np.pi *20000.) * 0.5

sig = sigs[:, 0]

#create 2 moving sinus
f1 = 1000.
f2 = 25000.
freqs1 = np.concatenate([np.linspace(0,.5,sigsize*3//8) *  (f2-f1) + f1, np.ones(sigsize//4)*(f1+f2)/2 , np.linspace(0,.5,sigsize*3//8) *  (f2-f1) + (f1+f2)/2], axis=0)
phase1 = np.cumsum(freqs1/fs)*2*np.pi
# sig += np.sin(phase1)
sig = np.sin(phase1)



nperseg = int(sample_rate)
print(nperseg)

fig, ax = plt.subplots()
Sxx, feqs, t, im = ax.specgram(sig, Fs=fs, NFFT=nperseg, scale='dB')
fig.colorbar(im)






freqs, times, Sxx = scipy.signal.spectrogram(sig, fs=sample_rate,nperseg=nperseg, detrend='constant', scaling='spectrum')

print(Sxx)

fig, ax = plt.subplots()
ax.plot(freqs, Sxx)




fig, ax = plt.subplots()

extent = (times[0], times[-1], 0., sample_rate / 2.)

print(np.min(Sxx), np.max(Sxx))

im = ax.imshow(10* np.log10(Sxx), interpolation='none', 
                origin ='lower', aspect = 'auto', extent = extent, cmap='viridis')
fig.colorbar(im)
#~ im.set_clim(0, np.max(Sxx) / 1000.)


plt.show()
