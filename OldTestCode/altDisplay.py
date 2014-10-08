from music21 import *

notes = open('data.txt', 'r').read().split()

#RUN ALGORITHMS BEFORE PUTTING IN STREAM
s = stream.Stream()
for name in notes:
  if name == 'Rest':
    f = note.Rest()
  else:
    f = note.Note(name)
    print(f.frequency)

  print(f.name)
  f.duration.type = "half"
  f.duration.quarterLength
  s.append(f)
#After building thing, print score!
s.show('lily')