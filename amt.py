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
#Other
import fft_utils  #Copyright (c) 2007, Imri Goldberg

###
#Finds the closest note
###
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

###
#Sets up the peak finding
###
#THINGS TO TRY: loop over different noise values and take smaller chunks (like 2 seconds out of whole) from .wav input. Precut it and rename the file.
def getFreq(audio, rate):
  #Filter with Hanning Window
  window = hann(len(audio))
  audio = audio * window
  #run rfft
  spectrum = rfft(audio)
  #find peak of signal
  #This segment is Copyright (c) 2007, Imri Goldberg
  signature = [peak for peak in fft_utils.find_peaks(spectrum,2, 1e6) if peak[0]>10]
  print signature, " signature\n"
  if len(signature) == 0:
    #0 indicates REST. Returning none is faulty.
   return 0
  note = min([x[0] for x in signature])
  return float(note)*2*rate/(2**13)

#
  #return spectrum
#convert ms to sample
def conversion(time, rate):
  return int((time/50)*rate)


###
#
#This is the start of the code
#
###
wavFile = raw_input('Enter .wav file to read: ') 
input_data = read(wavFile)
print input_data, "\n"
audio = input_data[1]
rate = input_data[0]
n = len(audio)
print "3 Data Pieces: a, r, n"
print audio, rate, n, "\n"

i = 0
duration = n/rate
print duration *50, "\n"
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
time.sleep(5)
while (i < duration*50 - 1):
  start = conversion(i, rate)
  end = conversion(i + 1, rate)
  #end += 3*(end - start)
  #Caps off sliding
  if end > len(audio):
    end = len(audio) - 1
  #
  print start, end, "\n"
  chunk = audio[start:end]
  Hz.append(getFreq(chunk,rate))
  i = i + 1
print Hz, "\n"
print len(Hz), "\n"

###
#Note to self: Play around w/ rate manipulation and duration manipulation for sliding chunks. Also abs(rfft)!
###





###
#This is where the mapping occurs
#
###
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

print "\nGenerating your transcription...\n"
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