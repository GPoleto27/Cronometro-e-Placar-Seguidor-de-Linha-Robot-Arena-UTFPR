#! /usr/bin/env python3

import os
import serial
import threading
import time
import numpy as np
import serial.tools.list_ports   # import serial module
import math
from gi.repository import Gtk, GLib
import gi
gi.require_version('Gtk', '3.0')

#settings = Gtk.Settings.get_default()
#settings.set_property("gtk-application-prefer-dark-theme", True)


def list_ports():
    l = Gtk.ListStore(int, str)
    i = 1
    for s in serial.tools.list_ports.comports():
        l.append([i, "/dev/"+s.name])
        i += 1
    return l


scoreboard = []


class ButtonWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(
            self, title="Seguidor de Linha - Robot Arena 2020.2")
        self.set_border_width(10)

        self.__time_threshold = 2

        self.maing = Gtk.Grid()
        self.maing.set_column_spacing(50)
        self.maing.set_row_spacing(25)
        self.add(self.maing)

        # SENSOR ---------------------------------
        self.sensor = Gtk.Grid()
        self.sensor.set_column_spacing(10)
        self.sensor.set_row_spacing(10)
        self.maing.attach(self.sensor, 0, 1, 1, 1)

        self.label = Gtk.Label()
        self.label.set_markup("<big>Sensor</big>")
        self.label.set_justify(Gtk.Justification.CENTER)
        self.sensor.attach(self.label, 0, 0, 2, 1)

        self.conlabel = Gtk.Label()
        self.conlabel.set_markup(
            '<span foreground="red"><big><b>Desconectado</b></big></span>')
        self.conlabel.set_justify(Gtk.Justification.CENTER)
        self.sensor.attach(self.conlabel, 0, 1, 2, 1)

        self.comboBox = Gtk.ComboBox.new_with_model(list_ports())
        renderer = Gtk.CellRendererText()
        self.comboBox.set_active(0)
        self.comboBox.pack_start(renderer, True)
        self.comboBox.add_attribute(renderer, 'text', 1)
        self.sensor.attach(self.comboBox, 0, 2, 2, 1)

        self.button = Gtk.Button.new_with_mnemonic("Atualizar")
        self.button.connect("clicked", self.atualizarUSB)
        self.sensor.attach(self.button, 0, 3, 1, 1)

        self.button = Gtk.Button.new_with_mnemonic("Conectar")
        self.button.connect("clicked", self.conectarUSB)
        self.sensor.attach(self.button, 1, 3, 1, 1)

        # GRID ---------------------------------
        self.grid = Gtk.Grid()
        self.grid.set_column_spacing(2)
        self.grid.set_row_spacing(10)
        self.maing.attach(self.grid, 1, 1, 1, 1)

        img = Gtk.Image.new_from_file('./logo.png')
        self.grid.attach(img, 0, 1, 3, 1)

        self.nome = Gtk.Label()
        self.nome.set_markup(
            '<big><b><span foreground="red">Selecione um competidor</span></b></big>')
        self.nome.set_justify(Gtk.Justification.CENTER)
        self.grid.attach(self.nome, 0, 2, 5, 1)

        self.tempo1 = Gtk.Label()
        self.tempo1.set_markup("1ª Tentativa\n<big><b>- s</b></big>")
        self.tempo1.set_justify(Gtk.Justification.CENTER)
        self.grid.attach(self.tempo1, 0, 4, 1, 1)

        self.button = Gtk.Button.new_with_mnemonic("Autorizar")
        self.button.connect("clicked", self.autorizar, 1)
        self.grid.attach(self.button, 0, 5, 1, 1)

        self.button = Gtk.Button.new_with_mnemonic("Resetar")
        self.button.connect("clicked", self.resetar, 1)
        self.grid.attach(self.button, 0, 6, 1, 1)

        self.tempo2 = Gtk.Label()
        self.tempo2.set_markup("2ª Tentativa\n<big><b>- s</b></big>")
        self.tempo2.set_justify(Gtk.Justification.CENTER)
        self.grid.attach(self.tempo2, 1, 4, 1, 1)

        self.button = Gtk.Button.new_with_mnemonic("Autorizar")
        self.button.connect("clicked", self.autorizar, 2)
        self.grid.attach(self.button, 1, 5, 1, 1)

        self.button = Gtk.Button.new_with_mnemonic("Resetar")
        self.button.connect("clicked", self.resetar, 2)
        self.grid.attach(self.button, 1, 6, 1, 1)

        self.tempo3 = Gtk.Label()
        self.tempo3.set_markup("3ª Tentativa\n<big><b>- s</b></big>")
        self.tempo3.set_justify(Gtk.Justification.CENTER)
        self.grid.attach(self.tempo3, 2, 4, 1, 1)

        self.button = Gtk.Button.new_with_mnemonic("Autorizar")
        self.button.connect("clicked", self.autorizar, 3)
        self.grid.attach(self.button, 2, 5, 1, 1)

        self.button = Gtk.Button.new_with_mnemonic("Resetar")
        self.button.connect("clicked", self.resetar, 3)
        self.grid.attach(self.button, 2, 6, 1, 1)

        # SCORE ---------------------------------
        self.score = Gtk.Grid()
        self.score.set_column_spacing(2)
        self.score.set_row_spacing(10)
        self.maing.attach(self.score, 2, 1, 1, 1)

        self.label = Gtk.Label()
        self.label.set_markup("<big>Placar</big>")
        self.label.set_justify(Gtk.Justification.CENTER)
        self.score.attach(self.label, 0, 0, 3, 1)

        self.entry = Gtk.Entry()
        self.score.attach(self.entry, 0, 1, 2, 1)

        self.button = Gtk.Button.new_with_mnemonic("Adicionar")
        self.button.connect("clicked", self.addChallenger)
        self.score.attach(self.button, 2, 1, 1, 1)

        # SPONSORS ---------------------------------
        self.sponsors = Gtk.Grid()
        self.sponsors.set_column_spacing(2)
        self.sponsors.set_row_spacing(2)
        self.maing.attach(self.sponsors, 0, 2, 1, 3)

        self.label = Gtk.Label()
        self.label.set_markup("<big>Patrocinadores</big>")
        self.label.set_justify(Gtk.Justification.CENTER)
        self.sponsors.attach(self.label, 0, 1, 3, 1)

        # Variáveis
        self.tentativa = 0
        self.start = 0
        self.threadID = 0
        self.Trig = False
        self.selectedIndex = 0
        self.t = math.inf
        self.selected = []

    # Funções
    def conectarUSB(self, button):
        usb = self.comboBox.get_model()[
            self.comboBox.get_active_iter()][1]
        self.ser = serial.Serial(usb)
        self.conlabel.set_markup(
            '<span foreground="green"><big><b>Conectado</b></big></span>')

    def atualizarUSB(self, button):
        self.comboBox.destroy()
        self.comboBox = Gtk.ComboBox.new_with_model(list_ports())
        renderer = Gtk.CellRendererText()
        self.comboBox.set_active(0)
        self.comboBox.pack_start(renderer, True)
        self.comboBox.add_attribute(renderer, 'text', 1)
        self.sensor.attach(self.comboBox, 0, 2, 2, 1)
        win.show_all()

    def resetar(self, button, tentativa):
        if self.threadID != 0:
            GLib.source_remove(self.threadID)
            self.threadID = 0
            if tentativa == 1:
                self.tempo1.set_markup(
                    '1ª Tentativa\n<big><b><span foreground="red">Resetada</span></b></big>')
            if tentativa == 2:
                self.tempo2.set_markup(
                    '2ª Tentativa\n<big><b><span foreground="red">Resetada</span></b></big>')
            if tentativa == 3:
                self.tempo3.set_markup(
                    '3ª Tentativa\n<big><b><span foreground="red">Resetada</span></b></big>')

    def autorizar(self, button, tentativa):
        if self.threadID == 0:
            self.tentativa = tentativa
            if tentativa == 1:
                self.tempo1.set_markup(
                    '1ª Tentativa\n<big><b><span foreground="green">Autorizada</span></b></big>')
            if tentativa == 2:
                self.tempo2.set_markup(
                    '2ª Tentativa\n<big><b><span foreground="green">Autorizada</span></b></big>')
            if tentativa == 3:
                self.tempo3.set_markup(
                    '3ª Tentativa\n<big><b><span foreground="green">Autorizada</span></b></big>')

            while self.ser.in_waiting > 0:
                self.ser.read()
            self.Trig = True
            self.start = 0
            self.threadID = GLib.timeout_add(1, self.updateTime)

    def updateTime(self):
        if self.tentativa == 1:
            self.Trig = False
            if self.ser.in_waiting > 0:
                self.ser.read()
                if self.start != 0:
                    if time.time() - self.start > self.__time_threshold:
                        self.tentativa += 1
                        scoreboard[self.selectedIndex][2] = self.t
                        self.start = time.time()
                        if self.t < scoreboard[self.selectedIndex][1]:
                            scoreboard[self.selectedIndex][1] = self.t
                            self.updateScoreboard()
                        self.updateFile()
                else:
                    self.start = time.time()
            else:
                if self.start != 0:
                    self.t = round(time.time() - self.start, 4)
                    self.tempo1.set_markup(
                        "1ª Tentativa\n<big><b>" + str(self.t) + "s</b></big>")

        if self.tentativa == 2:
            if(self.Trig):
                if self.ser.in_waiting > 0:
                    self.ser.read()
                    self.start = time.time()
                    self.Trig = False
            else:
                if self.ser.in_waiting > 0:
                    self.ser.read()
                    if time.time() - self.start > self.__time_threshold:
                        self.start = time.time()
                        self.tentativa += 1
                        scoreboard[self.selectedIndex][3] = self.t
                        if self.t < scoreboard[self.selectedIndex][1]:
                            scoreboard[self.selectedIndex][1] = self.t
                            self.updateScoreboard()
                        self.updateFile()
                else:
                    if self.start != 0:
                        self.t = round(time.time() - self.start, 4)
                        self.tempo2.set_markup(
                            "2ª Tentativa\n<big><b>" + str(round(time.time() - self.start, 4)) + "s</b></big>")

        if self.tentativa == 3:
            if(self.Trig):
                if self.ser.in_waiting > 0:
                    self.ser.read()
                    self.start = time.time()
                    self.Trig = False
            else:
                if self.ser.in_waiting > 0:
                    self.ser.read()
                    if time.time() - self.start > self.__time_threshold:
                        self.start = 0
                        scoreboard[self.selectedIndex][4] = self.t
                        if self.t < scoreboard[self.selectedIndex][1]:
                            scoreboard[self.selectedIndex][1] = self.t
                            self.updateScoreboard()
                        self.updateFile()
                        GLib.source_remove(self.threadID)
                        self.threadID = 0
                else:
                    if self.start != 0:
                        self.t = round(time.time() - self.start, 4)
                        self.tempo3.set_markup(
                            "3ª Tentativa\n<big><b>" + str(round(time.time() - self.start, 4)) + "s</b></big>")

        return True

    def selecionar(self, button, index):
        self.selectedIndex = index
        print(index)
        self.selected = scoreboard[self.selectedIndex]
        self.nome.set_markup('<big><b>' + scoreboard[index][0] + '</b></big>')
        self.tempo1.set_markup(
            "1ª Tentativa\n<big><b>" + str(round(scoreboard[index][2], 4)) + "s</b></big>")
        self.tempo2.set_markup(
            "2ª Tentativa\n<big><b>" + str(round(scoreboard[index][3], 4)) + "s</b></big>")
        self.tempo3.set_markup(
            "3ª Tentativa\n<big><b>" + str(round(scoreboard[index][4], 4)) + "s</b></big>")

    def sortSecond(self, val):
        return val[1]

    def addChallenger(self, button):
        if self.entry.get_text() != "":
            newChallenger = [self.entry.get_text(), math.inf,
                             math.inf, math.inf, math.inf]
            scoreboard.append(newChallenger)
            if self.selected == []:
                self.selected = newChallenger
            self.updateScoreboard()

    def updateFile(self):
        with open('.robotarena', 'w') as filehandle:
            for competidor in scoreboard:
                for a in competidor:
                    filehandle.write('%s,' % a)
                filehandle.write('\n')

    def updateScoreboard(self):
        if len(scoreboard) > 0:
            self.selected = scoreboard[self.selectedIndex]
            scoreboard.sort(key=self.sortSecond)
            print(scoreboard)
            self.selectedIndex = scoreboard.index(self.selected)
            self.score.destroy()

            self.score = Gtk.Grid()
            self.score.set_column_spacing(2)
            self.score.set_row_spacing(10)
            self.maing.attach(self.score, 2, 1, 1, 1)

            self.label = Gtk.Label()
            self.label.set_markup("<big>Placar</big>")
            self.label.set_justify(Gtk.Justification.CENTER)
            self.score.attach(self.label, 0, 0, 3, 1)

            i = 1
            for challenger in scoreboard:
                self.label = Gtk.Label()
                self.label.set_markup("<b><big>" + str(i) + "º</big></b>")
                self.label.set_justify(Gtk.Justification.LEFT)
                self.score.attach(self.label, 0, i, 1, 1)
                self.label = Gtk.Label()
                self.label.set_markup(
                    "<b><big>" + challenger[0] + " </big></b>")
                self.label.set_justify(Gtk.Justification.LEFT)
                self.score.attach(self.label, 1, i, 1, 1)
                self.label = Gtk.Label()
                self.label.set_markup("<big>" + str(challenger[1]) + "s</big>")
                self.label.set_justify(Gtk.Justification.RIGHT)
                self.score.attach(self.label, 2, i, 1, 1)
                self.button = Gtk.Button.new_with_mnemonic("Selecionar")
                self.button.connect("clicked", self.selecionar, i-1)
                self.score.attach(self.button, 3, i, 1, 1)
                i += 1

            self.entry = Gtk.Entry()
            self.score.attach(self.entry, 0, i, 3, 1)

            self.button = Gtk.Button.new_with_mnemonic("Adicionar")
            self.button.connect("clicked", self.addChallenger)
            self.score.attach(self.button, 3, i, 1, 1)

            win.show_all()


with open('.robotarena', 'r') as filehandle:
    for line in filehandle:
        s = line.split(sep=",")
        s[4] = s[4][:-1]
        for i in range(1, 5):
            if s[i] == "inf" or s[i] == "in":
                s[i] = math.inf
        scoreboard.append(
            [s[0], float(s[1]), float(s[2]), float(s[3]), float(s[4])])

win = ButtonWindow()
win.set_icon_from_file("logo.png")
win.connect("destroy", Gtk.main_quit)
win.show_all()
win.updateScoreboard()
Gtk.main()
