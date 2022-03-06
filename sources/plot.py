import wave
import matplotlib.pyplot as pl
import numpy as np

f = wave.open(r"../database/test/audio/open/20211028-202112-580788.wav", "rb")
params = f.getparams()
nchannels, sampwidth, framerate, nframes = params[:4]
print(nframes)
# 读取波形数据
str_data = f.readframes(nframes)
f.close()
wave_data = np.frombuffer(str_data, dtype=np.short)
time = np.arange(0, nframes) * (1.0 / framerate)
# 绘制波形
pl.figure(figsize=(10, 4))
pl.plot(time, wave_data)
pl.show()
