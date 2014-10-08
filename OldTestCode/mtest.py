#ignore failure statement: go straight to ScoreOutput and .png
from __future__ import division
from music21 import *
import time
#Scipy imports
import scipy
from scipy.io.wavfile import read
from scipy.signal import hann
from scipy.fftpack import *
#Numpy imports
import numpy
from numpy import argmax, sqrt, mean, diff, log
# PyPlot imports
import matplotlib.pyplot as plt
#Other
from parabolic import parabolic
import fft_utils  #Copyright (c) 2007, Imri Goldberg

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

#
def getFreq(audio, rate):
  #Filter with Hanning Window
  window = hann(len(audio))
  audio = audio * window
  #run rfft
  spectrum = rfft(audio)
  hertz = 20*scipy.log10(abs(spectrum))
  frequency = rfftfreq(len(spectrum))
  #find peak of signal
  #try taking first peak  because peaks after give overtones...
  i = argmax(abs(spectrum))
  true_i = int(parabolic(log(abs(spectrum)), i)[0])
  
  #Convert to Frequency
  return rate * true_i / len(audio)
#
  #return spectrum
#convert ms to sample
def conversion(time, rate):
  return int((time/1000)*rate)
  
  
input_data = read("couchplayin2.wav")
print input_data, "\n"
audio = input_data[1]
rate = input_data[0]
n = len(audio)
print "3 Data Pieces: a, r, n"
print audio, rate, n, "\n"

i = 0
duration = n/rate
print duration *1000, "\n"
Hz = []
#conversion rate
#i in milliseconds
#rate is samples per second
#rate/1000 = samples per ms
#n = samples
#to get chunk, take n/(rate/1000)
#
#
# i /1000
#
while (i < duration*1000 - 1):
  start = conversion(i, rate)
  end = conversion(i + 1, rate)
  print start, end, "\n"
  chunk = audio[start:end]
  Hz.append(getFreq(chunk,rate))
  i = i + 1
print Hz, "\n"
print len(Hz), "\n"

#plt.plot(audio[0:len(audio) -1])
#plt.ylabel("Amplitude")
#plt.xlabel("Time (samples)")
#plt.title("Couch Playin Sample")
#plt.show()
#	Filter with Hanning Window
#window = hann(len(audio) - 1)
#audio = audio[0:len(audio) - 1] * window


time.sleep(5)
#gets all frequencies
key = {}
items = []
notes = open('frequency.txt', 'r').read().split()
i = 0
while i < len(notes):
  key[notes[i + 1]] = notes[i]
  i += 2
#Prints all frequencies  
for item in Hz:
  closest= closestNote(key, abs(item))
  print "Closest note: ", key[closest], "\tGiven frequency: ", abs(item)
  items.append(closest)

  
## Note TO SELF: CLEAR METADATA FIRST!!!!
## Also need to decide between fft and rfft


s = stream.Stream()
for n in items:
  if key[n] == 'Rest':
    f = note.Rest()
  else:
    f = note.Note(key[n])
    print(f.frequency)
#for n in key.values():
  #if n == 'Rest':
    #f = note.Rest()
  #else:
    #f = note.Note(n)
    #print(f.frequency)

  print(f.name)
  f.duration.type = "half"
  f.duration.quarterLength
  s.append(f)
#After building thing, print score!
s.show('lily')