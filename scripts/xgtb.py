######################################################################
#  Project           : Automatic Testbench Ceator
#
#  File Name         : setup.py
#
#  Author            : Jose Iuri B. de Brito (XMEN LAB)
#
#  Purpose           : Main file of the application. Used to call the
# 					   Other files and functions.
######################################################################

import os
import sys
from colorama import Fore
import pathlib as path
# from generate import *
# from doc_generate import *
# from wrapper_generate import *

class Signal:
    def __init__(self, name, type, io):
        self.name = name
        self.type = type
        self.io = io

class Field:
    def __init__(self, name , type):
        self.name = name
        self.type = type

class Interface:
    def __init__(self, name, signal, clock, reset):
        self.name = name
        self.signal = [signal]
        self.clock = clock
        self.reset = reset

    def addSignal(self, signal):
        self.signal.append(signal)


class Transaction:
    def __init__(self, name, field):
        self.name = name
        self.field = [field]

    def addField(Field):
        self.Field.append(Field)

class Agent:
        def __init__(self, name, instance, interface, transaction):
            self.name = name
            self.instance = instance
            self.interface = interface
            self.transaction = transaction

        def setInterface(self, Interface):
            self.interface = Interface

        def setTransaction(self, transaction):
            self.transaction = transaction

        def writeInterface(self):

            with open('../src/templates/general_agent/general_interface.tb', 'r') as file:
                tbInterface=file.read()

            tbInterface = tbInterface.replace('|-AGENT-|', self.interface.name)

            tbInterface = tbInterface.replace('|-CLOCK-|', self.interface.clock)

            tbInterface = tbInterface.replace('|-RESET-|', self.interface.reset)

            # SIGNALS

            for uSignal in self.interface.signal:
                tbInterface = tbInterface.replace('|-SIGNAL_NAME-|', uSignal.type + ' ' + uSignal.name + ';\n\t|-SIGNAL_NAME-|')

            tbInterface = tbInterface.replace('|-SIGNAL_NAME-|', '')

            interface_file = open( self.name + "_interface.sv", "wt")
            n = interface_file.write(tbInterface)
            interface_file.close()



def display_title_bar():

	# Clears the terminal screen, and displays a title bar.
	os.system('clear')
	# print(Fore.BLUE + "\t#################################################")
	# print(Fore.BLUE + "\t#           ▀▄ ▄▀  █▀▄▀█  █▀▀▀  █▄  █           #")
	# print(Fore.BLUE + "\t#             █    █ █ █  █▀▀▀  █ █ █           #")
	# print(Fore.BLUE + "\t#           ▄▀ ▀▄  █   █  █▄▄▄  █  ▀█           #")
	# print(Fore.BLUE + "\t#                                               #")
	# print(Fore.BLUE + "\t#                █     █▀▀█  █▀▀█               #")
	# print(Fore.BLUE + "\t#                █     █▄▄█  █▀▀▄               #")
	# print(Fore.BLUE + "\t#                █▄▄█  █  █  █▄▄█               #")
	print(Fore.BLUE + "\t#################################################")
	print(Fore.WHITE + "\t#################################################")
	print(Fore.WHITE + "\t# This script is used to automate generation of #")
	print(Fore.WHITE + "\t# UVM Testbench Follow the steps to finish the  #")
	print(Fore.WHITE + "\t# generation.                                   #")
	print(Fore.WHITE + "\t#################################################")
	print("\t                                                 ")


def main():
    display_title_bar()

    uSignal1 = Signal('in_data', 'logic [8]', 'input')
    uSignal_add = Signal('out_data', 'logic [8]', 'output')

    uInterface = Interface('interfaceDummy', uSignal1, 'clock', 'reset')

    uInterface.addSignal(signal=uSignal_add)

    dummyField = Field('in-data', 'int')
    dummyTransac = Transaction('transactionDummy', dummyField)

    uAgent = Agent( 'agentDummy', 'instanceDummy', uInterface, dummyTransac)

    uAgent.writeInterface()


if __name__== "__main__" :
    main()
