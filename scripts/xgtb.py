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
        self.name = name + '_transaction'
        self.field = [field]

    def addField(self, field):
        self.field.append(field)

class Agent:
        def __init__(self, name, instance, interface, transaction, driver_policy, monitor_policy, type, refmod, comp):
            self.name = name
            self.instance = instance
            self.interface = interface
            self.transaction = transaction
            self.driver_policy = driver_policy
            self.monitor_policy = monitor_policy
            self.type = type
            self.refmod = refmod
            self.comp = comp

        def setInterface(self, Interface):
            self.interface = Interface

        def setTransaction(self, transaction):
            self.transaction = transaction

        def setDriverPolicy(self, diver_policy):
            self.diver_policy = diver_policy

        def setMonitorPolicy(self, monitor_policy):
            self.monitor_policy = monitor_policy

        def setMonitorType(self, type):
            self.type = type

        def setRefmodConn(self, refmod):
            self.refmod = refmod

        def setCompConn(self, comp):
            self.comp = comp

        def writeInterface(self):

            with open('../src/templates/general_agent/general_interface.tb', 'r') as file:
                tbInterface=file.read()

            tbInterface = tbInterface.replace('|-AGENT-|', self.interface.name)

            tbInterface = tbInterface.replace('|-CLOCK-|', self.interface.clock)

            tbInterface = tbInterface.replace('|-RESET-|', self.interface.reset)

            # SIGNALS

            for uSignal in self.interface.signal:
                tbInterface = tbInterface.replace('|-SIGNAL_NAME-|', uSignal.type + ' ' + uSignal.name + ';\n\t|-SIGNAL_NAME-|')

            # Cleaning residual tags
            tbInterface = tbInterface.replace('|-SIGNAL_NAME-|', '')

            interface_file = open( self.name + "_interface.sv", "wt")
            n = interface_file.write(tbInterface)
            interface_file.close()

        def writeTransaction(self):

            with open('../src/templates/general_agent/general_transaction.tb', 'r') as file:
                tbTransaction=file.read()

            tbTransaction = tbTransaction.replace('|-TRANSACTION-|', self.name)

            # FIELDS

            for uField in self.transaction.field:
                tbTransaction = tbTransaction.replace('|-FIELD_NAME-|', uField.type + ' ' + uField.name + ';\n\t|-FIELD_NAME-|') # INPUT DECLARATION
                tbTransaction = tbTransaction.replace('|-FIELD_MACRO-|','`uvm_field_int(' + uField.name + ', UVM_ALL_ON|UVM_HEX)\n\t\t|-FIELD_MACRO-|') #MACRO DECLARATION
                tbTransaction = tbTransaction.replace('|-FIELD_NAME_S-| = %h,', uField.name + ' |-FIELD_NAME_S-| = %h,') # convert2string DECLARATION
                tbTransaction = tbTransaction.replace('|-FIELD_NAME_S-|,', uField.name + ' |-FIELD_NAME_S-|,') # convert2string DECLARATION

            # Cleaning residual tags
            tbTransaction = tbTransaction.replace('|-FIELD_NAME-|;', '')
            tbTransaction = tbTransaction.replace('|-FIELD_MACRO-|', '')
            tbTransaction.replace('|-FIELD_NAME_S-| = %h,', '')
            tbTransaction.replace(' |-FIELD_NAME_S-|,', '')


            transaction_file = open( self.name + "_transaction.sv", "wt")
            n = transaction_file.write(tbTransaction)
            transaction_file.close()

        def writeAgent(self):

            with open('../src/templates/general_agent/general_agent.tb', 'r') as file:
                tbAgent=file.read()

            tbAgent = tbAgent.replace('|-AGENT-|', self.name)
            tbAgent = tbAgent.replace('|-TRANSACTION-|', self.transaction.name)
            

            agent_file = open( self.name + "_agent.sv", "wt")
            n = agent_file.write(tbAgent)
            agent_file.close()

        def writeDriver(self):
            with open('../src/templates/general_agent/general_driver.tb', 'r') as file:
                tbDriver=file.read()

            tbDriver = tbDriver.replace('|-AGENT-|', self.name)
            tbDriver = tbDriver.replace('|-TRANSACTION-|', self.transaction.name)

            tbDriver = tbDriver.replace('|-DRIVER_POLICY-|', self.driver_policy.replace('\n','\n\t'))

            driver_file = open( self.name + "_driver.sv", "wt")
            n = driver_file.write(tbDriver)
            driver_file.close()

        def writeMonitor(self):
            with open('../src/templates/general_agent/general_monitor.tb', 'r') as file:
                tbMonitor=file.read()

            tbMonitor = tbMonitor.replace('|-AGENT-|', self.name)
            tbMonitor = tbMonitor.replace('|-TRANSACTION-|', self.transaction.name)

            tbMonitor = tbMonitor.replace('|-MONITOR_POLICY-|', self.monitor_policy.replace('\n','\n\t\t'))

            if (self.type == 'input'):
                tbMonitor = tbMonitor.replace('this.resp.write(transCollected);', '')
            elif (self.type == 'output'):
                tbMonitor = tbMonitor.replace('this.req.write(transCollected);', '')
            else:
                pass

            monitor_file = open( self.name + "_monitor.sv", "wt")
            n = monitor_file.write(tbMonitor)
            monitor_file.close()

        def writeCoverage(self):

            with open('../src/templates/general_agent/general_agent.tb', 'r') as file:
                tbCoverage=file.read()

            tbCoverage = tbCoverage.replace('|-AGENT-|', self.name)
            tbCoverage = tbCoverage.replace('|-TRANSACTION-|', self.transaction.name)

            coverage_file = open( self.name + "_coverage.sv", "wt")
            n = coverage_file.write(tbCoverage)
            coverage_file.close()
        
        def writeAgentAll(Self):
            writeInterface()
            writeTransaction()
            writeAgent()
            writeDriver()
            writeMonitor()
            writeCoverage()
            writeAgent()

class Port:
    def __init__(self, name, direction, origin, transaction, endComp):
        self.name = name
        self.direction = direction
        self.origin = origin
        self.transaction = transaction
        self.endComp = endComp

class Refmod:
    def __init__(self, name, instance, policy, port_out, destination):
        self.name = name + '_refmod'
        self.instance = instance + '_rfm'

        self.port_in = []
        self.port_out = [port_out]

        self.policy = policy

        self.destination = [destination]


    def addPortIn (self, port):
        self.port_in.append(port)

    def addPortOut (self, port):
        self.port_out.append(port)

    def addDestination (self, destination):
        self.destination.append(destination)

    def writeRefmod(self):
        with open('../src/templates/scoreboard/refmod.tb', 'r') as file:
            tbRefmod=file.read()

        tbRefmod = tbRefmod.replace('|-REFMOD-|', self.name)

        for idx, uPort in enumerate(self.port_in):
            tbRefmod = tbRefmod.replace('|-INPUT_TRANSA-|', uPort.transaction.name + ' ' +  'req_' + str(idx) + ';\n\t|-INPUT_TRANSA-|')

        for idx, uPort in enumerate(self.port_out):
            tbRefmod = tbRefmod.replace('|-OUTPUT_TRANSA-|', uPort.transaction.name + ' ' +  'resp_' + str(idx) + ';\n\t|-OUTPUT_TRANSA-|')

        for idx, uPort in enumerate(self.port_in):
            tbRefmod = tbRefmod.replace('|-TRANSA_CREATION-|', 'req_'+ str(idx) + ' = new("req_' + str(idx) + '", this)' + ';\n\t\t|-TRANSA_CREATION-|')

        for idx, uPort in enumerate(self.port_out):
            tbRefmod = tbRefmod.replace('|-TRANSA_CREATION-|', 'resp_'+ str(idx) + ' = new("resp_' + str(idx) + '", this)' + ';\n\t\t|-TRANSA_CREATION-|')

        for idx, uPort in enumerate(self.port_in):
            tbRefmod = tbRefmod.replace('|-INPUT_PORT-|', 'uvm_analysis_fifo #(' + uPort.transaction + ') ' + 'from_' + uPort.origin + ';\n\t|-INPUT_PORT-|')

        for idx, uPort in enumerate(self.port_out):
            tbRefmod = tbRefmod.replace('|-OUTPUT_PORT-|', 'uvm_analysis_export #(' + uPort.transaction.name + ') ' + uPort.origin + '_to_'+ uPort.direction + ';\n\t|-OUTPUT_PORT-|')

        for idx, uPort in enumerate(self.port_in):
            tbRefmod = tbRefmod.replace('|-PORT_CREATION-|', 'from_' + uPort.origin + ' = new("' + 'from_' + uPort.origin + '", this)' + ';\n\t|-TRANSA_CREATION-|')

        for idx, uPort in enumerate(self.port_out):
            tbRefmod = tbRefmod.replace('|-PORT_CREATION-|', uPort.origin + '_to_'+ uPort.direction + ' = new("' + uPort.origin + '_to_'+ uPort.direction + '", this)' + ';\n\t|-TRANSA_CREATION-|')

        tbRefmod = tbRefmod.replace('|-REFMOD_POLICY-|', self.policy.replace('\n','\n\t\t'))

        # Cleanup
        tbRefmod = tbRefmod.replace('|-INPUT_TRANSA-|', '')
        tbRefmod = tbRefmod.replace('|-OUTPUT_TRANSA-|', '')
        tbRefmod = tbRefmod.replace('|-TRANSA_CREATION-|', '')
        tbRefmod = tbRefmod.replace('|-INPUT_PORT-|', '')
        tbRefmod = tbRefmod.replace('|-OUTPUT_PORT-|', '')
        tbRefmod = tbRefmod.replace('|-PORT_CREATION-|', '')

        refmod_file = open( self.name + ".sv", "wt")
        n = refmod_file.write(tbRefmod)
        refmod_file.close()

class Comparator:

    def __init__(self, name, instance, transaction):
        self.name = name
        self.transaction = transaction
        self.instance = instance
        self.name = 'uvm_in_order_class_comparator #('+ self.transaction.name + ')'

class Scoreboard:

    def __init__(self, name, instance, comp, refmod):
        self.name = name
        self.instance = instance
        self.port = []
        self.refmod = [refmod]
        self.comp = [comp]

    def addPort(self, port):
        self.port.append(port)

    def addComp(self, comp):
        self.comp.append(comp)

    def addRefmod(self, refmod):
        self.refmod.append(refmod)

    def writeScoreboard(self):

        with open('../src/templates/scoreboard/scoreboard.tb', 'r') as file:
            tbScoreboard=file.read()

        tbScoreboard = tbScoreboard.replace('|-SCOREBOARD-|', self.name)

        for idx,uRefmod in enumerate(self.refmod):
            tbScoreboard = tbScoreboard.replace('|-REFMOD-|', uRefmod.name + ' ' +  uRefmod.instance + ';\n\t|-REFMOD-|')

        for idx,uComp in enumerate(self.comp):
            tbScoreboard = tbScoreboard.replace('|-COMP-|', uComp.name + ' ' +  uComp.instance  + ';\n\t|-COMP-|')
        
        for idx,uPort in enumerate(self.port):
            tbScoreboard = tbScoreboard.replace('|-PORTS-|', 'uvm_analysis_port #(' + uPort.transaction.name + ') ' + uPort.origin + '_to_' + uPort.direction + ';\n\t|-PORTS-|')

        for idx,uRefmod in enumerate(self.refmod):
            tbScoreboard = tbScoreboard.replace('|-REFMOD_CREATION-|', uRefmod.instance + ' = ' + uRefmod.name + '::create("' + uRefmod.instance + '", this)' +  ';\n\t\t|-REFMOD_CREATION-|')

        for idx,uComp in enumerate(self.comp):
            tbScoreboard = tbScoreboard.replace('|-COMPARATOR_CREATION-|', uComp.instance + ' = ' + uComp.name + '::create("' + uComp.instance + '", this)' +  ';\n\t\t|-COMPARATOR_CREATION-|')

        for idx,uPort in enumerate(self.port):
            tbScoreboard = tbScoreboard.replace('|-PORTS_CREATION-|', uPort.origin + '_to_' + uPort.direction + '= new("' + uPort.origin + '_to_' + uPort.direction + '", this)' + ';\n\t\t|-PORTS_CREATION-|')

        for idx,uPort in enumerate(self.port):
            if uPort.endComp == 0:
                tbScoreboard = tbScoreboard.replace('|-CONNECTIONS-|', uPort.origin + '_to_' + uPort.direction + '.connect(' + uPort.direction + '.' 'from_' + uPort.origin + ');\n\t\t|-CONNECTIONS-|')
            else:
                tbScoreboard = tbScoreboard.replace('|-CONNECTIONS-|', uPort.origin + '_to_' + uPort.direction + '.connect(' + uPort.direction + '.' 'before_export' + ');\n\t\t|-CONNECTIONS-|')

        # Refmod Port Creation
        for idx,uPort in enumerate(self.port):
                for idy,uRefmod in enumerate(self.refmod):
                    if uPort.direction == uRefmod.instance:
                        port_aux = Port('rfm_in', uPort.direction, uPort.origin , uPort.transaction)
                        self.refmod[idy].addPortIn(port_aux)

        # Refmod -> Comp connection
        for idy,uRefmod in enumerate(self.refmod):
            for idx,uPort in enumerate(uRefmod.port_out):
                if idx == 0:
                    tbScoreboard = tbScoreboard.replace('|-CONNECTIONS-|', uRefmod.instance + '.' + uPort.origin + '_to_'+ uPort.direction + '.connect(' + uPort.direction + '.' 'after_export' + ');\n\t\t|-CONNECTIONS-|')
                else:
                    tbScoreboard = tbScoreboard.replace('|-CONNECTIONS-|', uRefmod.instance + '.' + uPort.origin + '_to_'+ uPort.direction + '.connect(' + uPort.direction + '.' + 'from_' + uPort.origin + ');\n\t\t|-CONNECTIONS-|')

        # CLEANUP
        tbScoreboard = tbScoreboard.replace('|-REFMOD-|', '')
        tbScoreboard = tbScoreboard.replace('|-COMP-|', '')
        tbScoreboard = tbScoreboard.replace('|-PORTS-|', '')
        tbScoreboard = tbScoreboard.replace('|-REFMOD_CREATION-|', '')
        tbScoreboard = tbScoreboard.replace('|-COMPARATOR_CREATION-|', '')
        tbScoreboard = tbScoreboard.replace('|-PORTS_CREATION-|', '')
        tbScoreboard = tbScoreboard.replace('|-CONNECTIONS-|', '')

        scoreboard_file = open( self.name + "_scoreboard.sv", "wt")
        n = scoreboard_file.write(tbScoreboard)
        scoreboard_file.close()

class Env:
    def __init__(self, name, instance, port, agent, scoreboard):
        self.name = name + '_env'
        self.instance = instance
        self.port = [port]
        self.scoreboard = scoreboard
        self.agent = [agent]

    def addPort(self, port):
        self.port.append(port)

    def setScoreboard (self, scoreboard):
        self.scoreboard = scoreboard

    def addAgent(self, agent):
        self.agent.append(agent)

    def writeEnv(self):

        with open('../src/templates/env.tb', 'r') as file:
            tbEnv=file.read()

        tbEnv = tbEnv.replace('|-ENV-|', self.name)

        for idx,agent in enumerate(self.agent):
            tbEnv = tbEnv.replace('|-AGENT-|', agent.name + '_agent ' +  agent.instance + ';\n\t|-REFMOD-|')

        tbEnv = tbEnv.replace('|-SCOREBOARD-|', self.scoreboard.name + '_scoreboard ' +  self.scoreboard.instance  + ';\n\t|-SCOREBOARD-|')

        for idx,agent in enumerate(self.agent):
            tbEnv = tbEnv.replace('|-AGENT_CREATION-|', agent.instance + ' = ' + agent.name + '_agent' + '::create("' + agent.instance + '", this)' +  ';\n\t\t|-AGENT_CREATION-|')

        tbEnv = tbEnv.replace('|-SCOREBOARD_CREATION-|', self.scoreboard.instance + ' = ' + self.scoreboard.name + '_agent' + '::create("' + self.scoreboard.instance + '", this)' +  ';\n\t\t|-SCOREBOARD_CREATION-|')

        for uAgent in (self.agent):
            if (uAgent.type == 'input'):
                envPortAgtRfm = Port(uAgent.instance + '_to_' + uAgent.refmod, uAgent.refmod, uAgent.instance, uAgent.transaction, 0)
                self.scoreboard.addPort(envPortAgtRfm)
                tbEnv = tbEnv.replace('|-CONNECTIONS-|', uAgent.instance + '.' + 'ap_req' + '.connect(' + self.scoreboard.instance + '.' + uAgent.instance + '_to_' + uAgent.refmod + ');\n\t\t|-CONNECTIONS-|')
            elif (uAgent.type == 'output'):
                envPortAgtComp = Port(uAgent.instance + '_to_' + uAgent.comp, uAgent.comp, uAgent.instance, uAgent.transaction, 1)
                self.scoreboard.addPort(envPortAgtComp)
                tbEnv = tbEnv.replace('|-CONNECTIONS-|', uAgent.instance + '.' + 'ap_resp' + '.connect(' + self.scoreboard.instance + '.' + uAgent.instance + '_to_' + uAgent.comp + ');\n\t\t|-CONNECTIONS-|')
            else:
                envPortAgtRfm = Port(uAgent.instance + '_to_' + uAgent.refmod, uAgent.refmod, uAgent.instance, uAgent.transaction, 0)
                self.scoreboard.addPort(envPortAgtRfm)
                tbEnv = tbEnv.replace('|-CONNECTIONS-|', uAgent.instance + '.' + 'ap_req' + '.connect(' + self.scoreboard.instance + '.' + uAgent.instance + '_to_' + uAgent.refmod + ');\n\t\t|-CONNECTIONS-|')
                envPortAgtComp = Port(uAgent.instance + '_to_' + uAgent.comp, uAgent.comp, uAgent.instance, uAgent.transaction, 1)
                self.scoreboard.addPort(envPortAgtComp)
                tbEnv = tbEnv.replace('|-CONNECTIONS-|', uAgent.instance + '.' + 'ap_resp' + '.connect(' + self.scoreboard.instance + '.' + uAgent.instance + '_to_' + uAgent.comp + ');\n\t\t|-CONNECTIONS-|')


        # CLEANUP
        tbEnv = tbEnv.replace('|-AGENT-|', '')
        tbEnv = tbEnv.replace('|-REFMOD-|', '')
        tbEnv = tbEnv.replace('|-SCOREBOARD-|', '')
        tbEnv = tbEnv.replace('|-SCOREBOARD_CREATION-|', '')
        tbEnv = tbEnv.replace('|-AGENT_CREATION-|', '')
        tbEnv = tbEnv.replace('|-SCOREBOARD_CREATION-|', '')
        tbEnv = tbEnv.replace('|-CONNECTIONS-|', '')


        env_file = open( self.name + ".sv", "wt")
        n = env_file.write(tbEnv)
        env_file.close()

class Sequence:

    def __init__(self, name, agent, transaction):
        self.name = name + '_sequence'
        self.agent = [agent]
        self.transaction = transaction

    def writeSequence(self):

            with open('../src/templates/sequence.tb', 'r') as file:
                tbSequence=file.read()

            tbSequence = tbSequence.replace('|-SEQUENCE-|', self.name)
            tbSequence = tbSequence.replace('|-TRANSACTION-|', self.transaction.name)

            sequence_file = open( self.name + ".sv", "wt")
            n = sequence_file.write(tbSequence)
            sequence_file.close()

class Test:
    def __init__(self, env, name):
        self.name = name + '_test'
        self.env = env
        self.sequence = []

    def addSequence(self, sequence):
        self.sequence.append(sequence)

    def writeTest(self):

        with open('../src/templates/test.tb', 'r') as file:
            tbTest=file.read()

        tbTest = tbTest.replace('|-TEST-|', self.name)

        tbTest = tbTest.replace('|-ENV-|', self.env.name + ' env_h;')

        for idx,sequence in enumerate(self.sequence):
            tbTest = tbTest.replace('|-SEQUENCE-|', sequence.name + ' seq_' + str(idx) + ';\n\t|-SEQUENCE-|')

        tbTest = tbTest.replace('|-ENV_CREATION-|', 'env_h' + ' = ' + self.env.name + '::create("env_h", this)' +  ';\n\t\t|-ENV_CREATION-|')
        for idx,sequence in enumerate(self.sequence):
            tbTest = tbTest.replace('|-SEQUENCE_CREATION-|', 'seq' + str(idx) + ' = ' + sequence.name + '::create("'+ 'seq' + str(idx) +'", this)' +  ';\n\t\t|-SEQUENCE_CREATION-|')
            for agent in sequence.agent:
                tbTest = tbTest.replace('|-SEQUENCE_START-|', 'seq' + str(idx) + '.start(env_h.' + agent.name + '.seqr)' + ';\n\t\t|-SEQUENCE_START-|')

        # CLEANUP
        tbTest = tbTest.replace('|-TEST-|', '')
        tbTest = tbTest.replace('|-ENV-|', '')
        tbTest = tbTest.replace('|-SEQUENCE-|', '')
        tbTest = tbTest.replace('|-ENV_CREATION-|', '')
        tbTest = tbTest.replace('|-SEQUENCE_CREATION-|', '')
        tbTest = tbTest.replace('|-SEQUENCE_START-|', '')


        test_file = open( self.name + ".sv", "wt")
        n = test_file.write(tbTest)
        test_file.close()

def display_title_bar():

    # Clears the terminal screen, and displays a title bar.
    print(Fore.BLUE + "################################################")
    print(Fore.BLUE + "           ▀▄ ▄▀  █▀▄▀█  █▀▀▀  █▄  █           ")
    print(Fore.BLUE + "             █    █ █ █  █▀▀▀  █ █ █           ")
    print(Fore.BLUE + "           ▄▀ ▀▄  █   █  █▄▄▄  █  ▀█           ")
    print(Fore.BLUE + "                                               ")
    print(Fore.BLUE + "                █     █▀▀█  █▀▀█               ")
    print(Fore.BLUE + "                █     █▄▄█  █▀▀▄               ")
    print(Fore.BLUE + "                █▄▄█  █  █  █▄▄█               ")
    print(Fore.BLUE + "################################################")
    print(Fore.BLUE + "################################################")
    print(Fore.BLUE + "# This script is used to automate generation of ")
    print(Fore.BLUE + "# UVM Testbench Follow the steps to finish the  ")
    print(Fore.BLUE + "# generation.                                   ")
    print(Fore.BLUE + "################################################")
    print(Fore.BLUE + "################################################")
    print(Fore.BLUE + "# Author: Jose Iuri Barbosa de Brito            ")
    print(Fore.BLUE + "# MIT License                                   ")
    print(Fore.BLUE + "# Copyright: Copyright (c) 2020, XGeneratorTB")
    print(Fore.BLUE + "# Credits: ")
    print(Fore.BLUE + "# Version: 0.0.0")
    print(Fore.BLUE + "# Maintainer: Jose Iuri Barbosa de Brio")
    print(Fore.BLUE + "# Email: jose.brito@embedded.ufcg.edu.br")
    print(Fore.BLUE + "# Status: In Progress")
    print(Fore.BLUE + "################################################\n\n")


def main():
    display_title_bar()

    uSignal1 = Signal('in_data', 'logic [8]', 'input')
    uSignal_add = Signal('out_data', 'logic [8]', 'output')

    uInterface = Interface('agentDummy', uSignal1, 'clock', 'reset')

    uInterface.addSignal(signal=uSignal_add)

    dummyField = Field('in_data', 'int')
    dummyField2 = Field('out_data', 'int')
    dummyTransac = Transaction('dummyTransa', dummyField)

    dummyTransac.addField(dummyField2)

    uAgent = Agent( 'agentDummy', 'instanceDummy', uInterface, dummyTransac, '', '', 'bidirectional', 'dummyRfm', 'dummyComp')
    
    output_port = Port('comp', 'dummyComp', 'dummyRfm', dummyTransac, 1)
    output_port_int = Port('rfm2', 'dummyRfm2', 'dummyRfm', dummyTransac, 0)
    output_port2 = Port('comp2', 'dummyComp2', 'dummyRfm2', dummyTransac, 1)

    comp = Comparator('comp', 'dummyComp', dummyTransac)
    
    refmod = Refmod ('dummyRefmod', 'dummyRfm', '', output_port, 'dummyComp')

    refmod.addPortOut(output_port_int)

    comp2 = Comparator('comp2', 'dummyComp2', dummyTransac)
    
    refmod2 = Refmod ('dummyRefmod2', 'dummyRfm2', '', output_port2, 'dummyComp2')

    scoreboard = Scoreboard('dummyScoreboard', 'dummyScb', comp, refmod)
    scoreboard.addComp(comp2)
    scoreboard.addRefmod(refmod2)

    env = Env('dummyEnv', 'env', [], uAgent, scoreboard)
    
    env.writeEnv()
    env.scoreboard.writeScoreboard()
    for refmod in env.scoreboard.refmod:
        refmod.writeRefmod()

    sequence = Sequence('dummy', uAgent, dummyTransac)
    test = Test(env, 'dummyT')

    test.addSequence(sequence)

    sequence.writeSequence()
    test.writeTest()
if __name__== "__main__" :
    main()
