#!/usr/bin/env python3.7.3
"""
Copyright © 2021 DUE TUL
@ crea  : Sunday February 14, 2021
@ modi  : Sunday February 14, 2021
@ desc  : This modules is used for audio
@ author: Bohao Chu
"""

import pyaudio
import matplotlib.pyplot as plt
import numpy as np
import time, wave, datetime, os, csv, sys
from tqdm import tqdm



CHUNK = 8000
SAMPRATE = 16000
PYADUIOFORMAT = pyaudio.paInt16
buffer_format = np.int16
CHANNELS = 1
record_length = 1


def device_check():
    audio = pyaudio.PyAudio()
    # print audio card
    for ii in range(0, audio.get_device_count()):
        print(audio.get_device_info_by_index(ii))


def audio_start():
    audio = pyaudio.PyAudio()
    stream = audio.open(format=PYADUIOFORMAT, rate=SAMPRATE, channels=CHANNELS, input=True, frames_per_buffer=CHUNK)
    stream.stop_stream()
    return stream, audio


def audio_end(stream, audio):
    stream.close()
    audio.terminate()


def data_grabber(stream, record_len):
    start_time = datetime.datetime.now()
    stream.start_stream()
    # stream.read(CHUNK,exception_on_overflow=False) # flush port first
    data, data_frames = [], []
    for frame in range(int((SAMPRATE * record_len) / CHUNK)):
        stream_data = stream.read(CHUNK, exception_on_overflow=False)
        data_frames.append(stream_data)
        data.append(np.frombuffer(stream_data, dtype=buffer_format))
    stream.stop_stream()
    return data, data_frames, start_time


def data_saver(audio, data_folder, data_frames, start_time, name):
    if os.path.isdir(data_folder) == False:
        os.mkdir(data_folder)
    filename = datetime.datetime.strftime(start_time, '%Y%m%d-%H%M%S-%f-')
    wf = wave.open(data_folder + filename + name+ '.wav', 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(PYADUIOFORMAT))
    wf.setframerate(SAMPRATE)
    wf.writeframes(b''.join(data_frames))
    wf.close()
    return filename


def data_analyzer(data_chunks):
    freq_array, fft_array = [], []
    spectrogram = []
    data_array = []
    t_ii = 0.0
    for frame in data_chunks:
        freq_frame, fft_frame = fft_process(frame)
        freq_array.append(freq_frame)
        fft_array.append(fft_frame)
        t_vec_ii = np.arange(0, len(frame)) / float(SAMPRATE)
        t_ii += t_vec_ii[-1]
        spectrogram.append(t_ii)
        data_array.extend(frame)
    time_array = np.arange(0, len(data_array)) / SAMPRATE
    freq_vec, fft_vec = fft_process(data_array)
    return time_array, data_array, freq_vec, fft_vec, freq_array, fft_array, spectrogram


def fft_process(data_frame):
    data_frame = data_frame * np.hanning(len(data_frame))
    N_fft = len(data_frame)
    freq_frame = (float(SAMPRATE) * np.arange(0, int(N_fft / 2))) / N_fft
    fft_data_raw = np.abs(np.fft.fft(data_frame))
    fft_data = fft_data_raw[0:int(N_fft / 2)] / float(N_fft)
    fft_data[1:] = 2.0 * fft_data[1:]
    return freq_frame, fft_data


# function for plotting data
def plotter():
    plt.style.use('ggplot')
    plt.rcParams.update({'font.size': 16})

    fig, axs = plt.subplots(3, 1, figsize=(12, 8))
    ax = axs[0]  # top axis: time series
    ax.plot(time_array, sound_array)  # time data

    ax2 = axs[1]
    ax2.plot(freq_vec, fft_data)
    max_indx = np.argmax(fft_data)  # FFT peak index
    ax2.annotate(r'$f_{max}$' + ' = {0:2.1f}Hz'.format(freq_vec[max_indx]),
                 xy=(freq_vec[max_indx], fft_data[max_indx]),
                 xytext=(2.0 * freq_vec[max_indx], (fft_data[max_indx] + np.mean(fft_data)) / 2.0),
                 arrowprops=dict(facecolor='black', shrink=0.1))  # peak label

    ax3 = axs[2]
    t_spec = np.reshape(np.repeat(spectrogram, np.shape(freq_array)[1]), np.shape(freq_array))
    y_plot = fft_array
    spect = ax3.pcolormesh(t_spec, freq_array, y_plot, shading='nearest')
    ax3.set_ylim([20.0, 20000.0])
    ax3.set_yscale('log')
    cbar = fig.colorbar(spect)
    cbar.ax.set_ylabel('Amplitude', fontsize=16)  # amplitude label
    # fig.savefig('A.png',dpi=300, bbox_inches='tight')
    plt.show()  # show plot


def sound_collect(data_floder, amount, name):
    stream, audio = audio_start()
    data_chunks, data_frames, start_time = data_grabber(stream, 2)
    for i in tqdm(range(amount)):
        data_chunks, data_frames, start_time = data_grabber(stream, 1)
        n = data_saver(audio, data_floder, data_frames, start_time, name)
    audio_end(stream, audio)


if __name__ == "__main__":
    # helllo
    sound_collect("../database/one-second/audio/close/", 400, "Close")