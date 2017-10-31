import pyaudio
import numpy as np
from scipy import fft, arange, signal
import struct
import cv2


def plotSpectrum(y, Fs):
    """
    Plots a Single-Sided Amplitude Spectrum of y(t)
    """
    n = len(y)  # length of the signal
    k = arange(n)
    T = n / Fs
    frq = k / T  # two sides frequency range
    frq = frq[range(n / 2)]  # one side frequency range

    Y = np.fft.fft(y) / n  # fft computing and normalization
    Y = Y[range(n / 2)]

    return np.array(abs(Y)) * signal.gaussian(len(Y), 1024)


FORMAT = pyaudio.paInt16


def recordAudioSegments(BLOCKSIZE, Fs=44100):
    midTermBufferSize = int(Fs * BLOCKSIZE)

    print "Press Ctr+C to stop recording"

    pa = pyaudio.PyAudio()

    stream = pa.open(format=FORMAT,
                     channels=1,
                     rate=Fs,
                     input=True,
                     frames_per_buffer=midTermBufferSize,)

    while 1:
        try:
            block = stream.read(midTermBufferSize)


            countB = len(block) / 2
            format = "%dh" % (countB)
            shorts = struct.unpack(format, block)
            curWindow = list(shorts)

            #print "--", len(curWindow)
            spec = plotSpectrum(curWindow, Fs)
            np.exp(spec)
            plot = np.zeros((480, len(spec), 3))
            for i in range(0, len(spec)):
                n = int((spec[i] / 16384.) * 480)
                #print n
                for j in range(0, n):
                    plot[j, i] = (255, 255, 255)
            plot = cv2.resize(plot, (640, 480))
            cv2.imshow("ret", plot)
            if chr(cv2.waitKey(1) & 0xff) == "q":
                break
        except KeyboardInterrupt:
            break
        except Exception as e:
            print "something failed" + str(e)


if __name__ == "__main__":
    recordAudioSegments(0.01, 41000)
