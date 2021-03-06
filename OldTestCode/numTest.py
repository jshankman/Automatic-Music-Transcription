#Jake Shankman, 10/9/2012
#Computer Systems Research P1
#FFT Test

import scipy
from scipy.io.wavfile import read
#from scipy.signal import hann
from scipy.fftpack import rfft
from scipy.fftpack import rfftfreq
import matplotlib.pyplot as plt

#Finds the closest note
def closestNote(key, frequency):
  distance = abs(float(key.keys()[0]) - frequency)
  closest = key.keys()[0]
  i = 1
  while i < len(key.keys()):
    pitch = key.keys()[i]
    newDistance = abs(float(pitch) - frequency)
    if newDistance < distance:
      distance = newDistance
      closest = pitch
    i +=1
  return closest

input_data = read("click.wav")
print input_data
audio = input_data[1]
print audio

#plt.plot(audio[0:len(audio) -1])
#plt.ylabel("Amplitude")
#plt.xlabel("Time (samples)")
#plt.title("Couch Playin Sample")
#plt.show()

#	Filter with Hanning Window
#window = hann(len(audio) - 1)
#audioSample = audio[0:len(audio) - 1] * window

spectrum = abs(rfft(audio))
print spectrum
frequency = rfftfreq(len(spectrum))

print frequency

#gets all frequencies
key = {}
notes = open('frequency.txt', 'r').read().split()
i = 0
while i < len(notes):
  key[notes[i + 1]] = notes[i]
  i += 2
#Prints all frequencies  
for item in spectrum:
  closest= closestNote(key, abs(item)/1000)
  print "Closest note: ", key[closest], "\tGiven frequency: ", abs(item)/1000

  
## Note TO SELF: CLEAR METADATA FIRST!!!!
## Also need to decide between fft and rfft