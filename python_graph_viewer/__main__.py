# -*- coding: utf-8 -*-
import time
import numpy as np
import matplotlib.pyplot as plt
import serial
import time


class RealtimePlot1D():
    def __init__(
        self,
        x_tick,
        length,
        xlabel="Time",
        title="RealtimePlot1D",
        label=None,
        color="c",
        marker='-o',
        alpha=1.0,
        ylim=None
    ):
        self.x_tick = x_tick
        self.length = length
        self.color = color
        self.marker = marker
        self.alpha = 1.0
        self.ylim = ylim
        self.label = label
        self.xlabel = xlabel
        self.title = title
        self.line = None

        # プロット初期化
        self.init_plot()

    def init_plot(self):
        self.x_vec = np.arange(0, self.length) * self.x_tick \
            - self.length * self.x_tick
        self.y_vec = np.zeros(self.length)

        plt.ion()
        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111)

        self.line = ax.plot(self.x_vec, self.y_vec,
                            self.marker, color=self.color,
                            alpha=self.alpha)

        if self.ylim is not None:
            plt.ylim(self.ylim[0], self.ylim[1])
        plt.xlabel(self.xlabel)
        plt.title(self.title)
        plt.grid()
        plt.show()

        self.index = 0
        self.x_data = -self.x_tick
        self.pretime = 0.0
        self.fps = 0.0

    def update_index(self):
        self.index = self.index + 1 if self.index < self.length - 1 else 0

    def update_ylim(self, y_data):
        ylim = self.line[0].axes.get_ylim()
        if y_data < ylim[0]:
            plt.ylim(y_data * 1.1, ylim[1])
        elif y_data > ylim[1]:
            plt.ylim(ylim[0], y_data * 1.1)

    def compute_fps(self):
        curtime = time.time()
        time_diff = curtime - self.pretime
        self.fps = 1.0 / (time_diff + 1e-16)
        self.pretime = curtime

    def update_empty(self):
        plt.pause(0.001)

    def update(self, y_data):
        # プロットする配列の更新
        self.x_data += self.x_tick
        self.y_vec[self.index] = y_data

        y_pos = self.index + 1 if self.index < self.length else 0
        tmp_y_vec = np.r_[self.y_vec[y_pos:self.length], self.y_vec[0:y_pos]]
        self.line[0].set_ydata(tmp_y_vec)
        if self.ylim is None:
            self.update_ylim(y_data)

        plt.title(f"fps: {self.fps:0.1f} Hz")
        plt.pause(0.001)

        # 次のプロット更新のための処理
        self.update_index()
        self.compute_fps()


if __name__ == "__main__":
    x_tick = 0.1  # 時間方向の間隔
    length = 50  # プロットする配列の要素数
    realtime_plot1d = RealtimePlot1D(x_tick, length)
    COM = "COM3"
    bitRate = 115200

    ser = serial.Serial(COM, bitRate, timeout=0.1)

    while True:
        time.sleep(0.001)
        result = ser.readline()
        if result:
            read_str = result.decode("utf-8").strip()
            value = int(read_str.split(": ")[1][:-2])
            print(value)
            realtime_plot1d.update(value)
        else:
            realtime_plot1d.update_empty()

        if result == b'\r':  # <Enter>で終了
            break

    print('program end')

    ser.close()
