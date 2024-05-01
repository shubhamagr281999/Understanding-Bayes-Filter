#!/usr/bin/env python3
import random
import sys
from time import sleep

import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class BayesFilterVisualizer(QWidget):
    def __init__(self):
        super().__init__()

        ### State variables ###
        self.len_x = 50
        self.door_locations = np.zeros([self.len_x, 1])
        self.door_locations[[9, 18, 29, 45], 0] = 1
        self.bel_x = np.zeros([self.len_x, 1])
        self.bel_x[0, 0] = 1
        self.current_pos = 0
        self.p_z_x = np.zeros([self.len_x, 2])

        ### INIT graph UI ####
        self.setWindowTitle("Bayes Filter Visualization")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        # Add sliders
        self.label1 = QLabel("Probability of true positive | DOOR SENSOR")
        layout.addWidget(self.label1)
        self.true_positive_prob_slider = QSlider()
        self.true_positive_prob_slider.setOrientation(1)
        self.true_positive_prob_slider.setMinimum(1)
        self.true_positive_prob_slider.setMaximum(99)
        layout.addWidget(self.true_positive_prob_slider)

        self.label2 = QLabel("Probability of true negative | DOOR SENSOR")
        layout.addWidget(self.label2)
        self.true_negative_prob_slider = QSlider()
        self.true_negative_prob_slider.setOrientation(1)
        self.true_negative_prob_slider.setMinimum(1)
        self.true_negative_prob_slider.setMaximum(99)
        layout.addWidget(self.true_negative_prob_slider)

        self.label3 = QLabel("Probability of correct action | INPUT")
        layout.addWidget(self.label3)
        self.correct_action_prob_slider = QSlider()
        self.correct_action_prob_slider.setOrientation(1)
        self.correct_action_prob_slider.setMinimum(1)
        self.correct_action_prob_slider.setMaximum(99)
        layout.addWidget(self.correct_action_prob_slider)

        self.label4 = QLabel("Current position | STATE")
        layout.addWidget(self.label4)
        self.pos_slider = QSlider()
        self.pos_slider.setOrientation(1)
        self.pos_slider.setMinimum(0)
        self.pos_slider.setMaximum(self.len_x - 1)
        layout.addWidget(self.pos_slider)

        # Add buttons
        self.button1 = QPushButton("Go forward")
        self.button1.clicked.connect(self.goForward)
        layout.addWidget(self.button1)

        self.button2 = QPushButton("Go Back")
        self.button2.clicked.connect(self.goBack)
        layout.addWidget(self.button2)

        self.button3 = QPushButton("Reset")
        self.button3.clicked.connect(self.reset)
        layout.addWidget(self.button3)

        # Add plot
        self.plotWidget = pg.PlotWidget()
        layout.addWidget(self.plotWidget)
        self.setLayout(layout)

        # Set up initial plot
        self.updatePlot()

        self.pos_slider.valueChanged.connect(self.updatePos)
        self.true_positive_prob_slider.valueChanged.connect(
            self.updateInverseSensorModel
        )
        self.true_negative_prob_slider.valueChanged.connect(
            self.updateInverseSensorModel
        )
        self.flg_state_initialized = True

    def updateBelief(self, u, z):
        print("Current Pose:", self.current_pos, " action:", u, " Sensor:", z)

        # prediction
        prior_x = np.zeros([self.len_x, 1])
        for x in range(0, self.len_x):
            if self.bel_x[x, 0] > 0:
                p_x_u = np.zeros([self.len_x, 1])
                if u > 0 and x == (self.len_x - 1):
                    p_x_u[x, 0] = 1
                elif u < 0 and x == 0:
                    p_x_u[x, 0] = 1
                else:
                    p_x_u[x, 0] = 1 - self.correct_action_prob_slider.value() * 0.01
                    p_x_u[x + u, 0] = self.correct_action_prob_slider.value() * 0.01
                prior_x += p_x_u * self.bel_x[x, 0]

        # update
        normalizing_coeff = 0
        for x in range(0, self.len_x):
            self.bel_x[x, 0] = self.p_z_x[x, z] * prior_x[x, 0]
            normalizing_coeff += self.bel_x[x, 0]
        self.bel_x = self.bel_x / normalizing_coeff

    def updateInverseSensorModel(self):
        self.p_z_x = np.zeros([self.len_x, 2])

        # probability of z==1
        for x in range(0, self.len_x):
            if self.door_locations[x, 0] > 0:
                self.p_z_x[x, 1] = self.true_positive_prob_slider.value() * 0.01
            else:
                self.p_z_x[x, 1] = 1 - self.true_negative_prob_slider.value() * 0.01

        # probability of z==0
        for x in range(0, self.len_x):
            if self.door_locations[x, 0] > 0:
                self.p_z_x[x, 0] = 1 - self.true_positive_prob_slider.value() * 0.01
            else:
                self.p_z_x[x, 0] = self.true_negative_prob_slider.value() * 0.01

    def goForward(self):
        pass
        if random.random() <= self.correct_action_prob_slider.value() * 0.01:
            if (self.current_pos + 1) < self.len_x:
                self.current_pos += 1

        self.updateBelief(1, self.sensorValue())
        self.updatePlot()
        self.flg_state_initialized = False

    def goBack(self):
        pass
        if random.random() <= self.correct_action_prob_slider.value() * 0.01:
            if (self.current_pos) > 0:
                self.current_pos -= 1

        self.updateBelief(-1, self.sensorValue())
        self.updatePlot()
        self.flg_state_initialized = False

    def sensorValue(self):
        if self.door_locations[self.current_pos, 0] > 0:
            if random.random() <= self.true_positive_prob_slider.value() * 0.01:
                return 1
            else:
                return 0
        else:
            if random.random() <= self.true_negative_prob_slider.value() * 0.01:
                return 0
            else:
                return 1

    def reset(self):
        pass
        if not self.flg_state_initialized:
            self.bel_x = np.zeros([self.len_x, 1])
            self.bel_x[self.current_pos] = 1
        else:
            self.bel_x = np.zeros([self.len_x, 1]) + 1 / self.len_x

        self.updatePlot()
        self.flg_state_initialized = not (self.flg_state_initialized)

    def updatePlot(self):
        self.plotWidget.clear()
        self.plotWidget.plot()

        ## Door locations
        for i in range(0, self.len_x):
            if self.door_locations[i, 0] > 0:
                self.plotWidget.plot([i, i], [0, 1], pen="r")

        ## belief
        x = np.linspace(0, self.len_x)
        self.plotWidget.plot(
            np.reshape(x, self.len_x), np.reshape(self.bel_x, self.len_x), pen="b"
        )
        self.plotWidget.setLabel("bottom", "x")
        self.plotWidget.setLabel("left", "bel_x")
        self.plotWidget.setYRange(0, 1)
        self.plotWidget.setXRange(-0.5, self.len_x + 0.5)

        # Current Pos
        triangle = pg.PlotCurveItem(
            [
                self.current_pos,
                self.current_pos + 0.5,
                self.current_pos - 0.5,
                self.current_pos,
            ],
            [0, 0.1, 0.1, 0],
            fillLevel=0,
            brush="g",
        )
        self.plotWidget.addItem(triangle)

        self.show()

    def updatePos(self):
        self.current_pos = int(self.pos_slider.value())
        self.flg_state_initialized = False
        self.updatePlot()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = BayesFilterVisualizer()
    sys.exit(app.exec_())
