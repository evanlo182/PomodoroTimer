"""
Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['Pomodoro Timer.py']
DATA_FILES = [('', ['chime.mp3'])]
OPTIONS = {
           'iconfile': '/Users/evanlonczak/PomodoroApp/Designer.icns',
           'includes': 'customtkinter, requests, pygame, json, tkinter, re'
           }

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
