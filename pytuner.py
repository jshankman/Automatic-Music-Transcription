#!/usr/bin/python

#-----------------------------------------------
#pytuner.py - Python Guitar Tuner
#Copyright (c) 2007, Imri Goldberg
#All rights reserved.
#
#Redistribution and use in source and binary forms,
#with or without modification, are permitted provided
#that the following conditions are met:
#
#    * Redistributions of source code must retain the
#       above copyright notice, this list of conditions
#       and the following disclaimer.
#    * Redistributions in binary form must reproduce the
#       above copyright notice, this list of conditions
#       and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#    * Neither the name of the Algorithm.co.il nor the names of
#       its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#-----------------------------------------------

import time
#import pymedia.audio.sound as sound
import pyaudio
import fft_utils
from base_tools import *
import numpy
import struct
import pickle
import sys
import math

NUM_NOTES = 12
HALF_TONE_STEP = 2**(1.0/NUM_NOTES)
NOTE_NAMES = "A A# B C C# D D# E F F# G G#".split()
BASE_FREQ = 110.0


DEFAULT_FFT_SIZE = 2**13
DEFAULT_SAMPLE_RATE=14000
DEFAULT_ERROR_TOLERANCE = 2**(1.0/36)

def round(f):
    return int(math.floor(f+0.5))

class Tuner(object):
    def __init__(self, sample_rate, fft_size, error_tolerance, notes):
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.notes = notes
        self.error_tolerance = error_tolerance

    def convert_buffer(self, buf, max_items):
        buf = "".join(buf)[:max_items*2]
        return struct.unpack("%dh" % max_items, buf)

    def compute_freq(self, sample):
        return float(sample)*2*self.sample_rate/self.fft_size

    def recognize_note(self, audio_data):
        """return the note played in the given audio data
        Params:
            audio_data - a buffer of samples
        Return value:
            The frequency of the playing note.
            If no playing note is found, None is returned.
        """
        mult = fft_utils.awindow(len(audio_data))
        final_fft = numpy.array(map(abs, numpy.fft.fft(audio_data*mult)[:self.fft_size/12]))

        signature = [peak for peak in fft_utils.find_peaks(final_fft,2) if peak[0]>10]

        if len(signature) == 0:
            return

        note = min([x[0] for x in signature])
        return self.compute_freq(note)

    def display_tuning(self, note_freq):
        """print a string containing the correct tuning of a given note"""
        note_tone = round(math.log((note_freq/BASE_FREQ),HALF_TONE_STEP))

        note_name = NOTE_NAMES[note_tone%12]

        if self.notes is None:
            desired_note_tone = note_tone
        else:

            tone_distances = [abs(note_tone-possible_note) for possible_note in self.notes]
            desired_note_tone = self.notes[arg_min(tone_distances)]

        desired_note_name = NOTE_NAMES[desired_note_tone%12]
        desired_note_freq = BASE_FREQ*((HALF_TONE_STEP)**desired_note_tone)

        evaluation_str = ""

        if max(desired_note_freq, note_freq) / min(desired_note_freq, note_freq) < self.error_tolerance:
            evaluation_str = "ok"
        else:
            if  note_freq < desired_note_freq:
                evaluation_str = "too low"
            else:
                evaluation_str = "too high"

        note_str = self.create_note_str(note_name, note_tone, note_freq)
        desired_note_str = self.create_note_str(desired_note_name, desired_note_tone, desired_note_freq)
        result_str = "%s -> %s, %s" % (note_str, desired_note_str, evaluation_str)

        print result_str


    def create_note_str(self, note_name, note_tone, note_freq):
        return "%s(%d) at %2.1fHz" % (note_name, note_tone, note_freq)

    def main_loop(self):
        max_freqs = []
        sample_buffer = []
        #recorder = sound.Input(self.sample_rate,1,sound.AFMT_S16_LE)
        #recorder.start()
        p = pyaudio.PyAudio()
        stream = p.open(format = pyaudio.paInt16,
                        channels = 1,
                        rate = self.sample_rate,
                        input = True,
                        frames_per_buffer = 1024)

        real_buffer = []
        real_buffer_len = 0
        total_time=0
        num_iters=0
        prev_len = 0
        try:
            while True:

                sample_buffer = stream.read(1024)
                if sample_buffer and len(sample_buffer) > 0:
                    real_buffer.append(sample_buffer)
                    real_buffer_len += len(sample_buffer)
                    if real_buffer_len < self.fft_size*2:
                        time.sleep(0.003)

                        continue
                    else:
                        to_fft = self.convert_buffer(real_buffer,self.fft_size)
                        real_buffer = []
                        real_buffer_len = 0
                else:
                    continue

                start_time = time.time()

                note_freq = self.recognize_note(to_fft)
                if note_freq is not None:
                    self.display_tuning(note_freq)


                end_time = time.time()
                loop_time = end_time-start_time
                total_time+=loop_time
                num_iters +=1
        finally:
            stream.close()
            p.terminate()
            if num_iters < 0:
                print total_time/num_iters

from optparse import OptionParser

def main():
    description_str = ("A tuner implemented in python. To tune your guitar use with -i guitar."
                       "To specify specific notes use -n. This is useful for tuning unsupported instruments.\n"
                       "Low A is considered to be 0, so the list 0,3,7 will tune you to (low) A,C and E.\n"
                       "Without arguments, the tuner will recognize any keyboard-note.\n")
    parser = OptionParser(usage="%prog [-i guitar]", version="PyTuner 1.1", description = description_str)


    parser.add_option("-f","--fft_size",dest="fft_size", default=DEFAULT_FFT_SIZE, type="int",
                      help="How many samples to include in the fft")
    parser.add_option("-s","--sample_rate",dest="sample_rate", default=DEFAULT_SAMPLE_RATE,
                      type="int", help="The sample rate of the recording")
    parser.add_option("-t","--tolerance",dest="error_tolerance", default=DEFAULT_ERROR_TOLERANCE,
                      type="float", help="The maximum ratio between freqs to be considered 'good tuning'")


    parser.add_option("-n","--notes",dest="notes", default=None,
                      help="Specify the target notes as a comma seperated list.\n"
                           "for example, 7,12,17,22,26,31 is the correct list for a guitar,\n"
                           "while 5,12,17,22,26,31 will yield a low-d tuning of a guitar.\n"
                           "Negative values are allowed.")
    parser.add_option("-i","--instrument",dest="instrument", default=None, type="string",
                      help="Specify the instrument to tune. Can't be used together with --notes.\n"
                           "currently only 'guitar' is supported")

    (options, args) = parser.parse_args()

    if (options.instrument is not None) and (options.notes is not None):
        parser.error("Can't use --notes together with --instrument")
    notes = options.notes
    if notes is not None:
        try:
            notes = [int(x) for x in notes.split(',')]
        except ValueError, e:
            parser.error("can't parse note string, should be a comma seperated list of ints")

    if options.instrument is not None:
        if options.instrument.lower() == "guitar":
            notes = [7,12,17,22,26,31]

    print "PyTuner - Python Guitar Tuner\nCopyright 2007 by Imri goldberg"
    print "Precision: %2.2fHz" % (float(options.sample_rate)/options.fft_size)
    print "Use ctrl-c to exit"
    tuner = Tuner(options.sample_rate, options.fft_size, options.error_tolerance, notes)
    try:
        tuner.main_loop()
    except KeyboardInterrupt, e:
        pass

if __name__ == "__main__":
    main()
