######################################################################
#  Project           : Aurora Integrated Reference Flow Generation
#
#  File Name         : aurora.py
#
#  Author            : Jose Iuri B. de Brito (XMEN LAB)
#
#  Purpose           : Main file of the application. Used to call the
# 					   Other files and functions.
######################################################################

import os
import sys, getopt
import argparse
from colorama import Fore
from pathlib import Path
import copy

class Clock:
    def __init__(self, name, period):
        self.name = name
        self.period = period

class Reset:
    def __init__(self, name, period, duration):
        self.name = name
        self.period = period
        self.duration = duration

class Signal:
    def __init__(self, name, type, io):
        self.name = name
        self.type = type
        self.io = io
        self.connect = None

    def addConnection (self, connect):
        self.connect = connect

class Field:
    def __init__(self, name , type):
        self.name = name
        self.type = type

class Interface:
    def __init__(self, name, instance, clock, reset):
        self.name = name + '_interface'
        self.instance = instance
        self.signal = []
        self.clock = clock
        self.reset = reset

    def addSignal(self, signal):
        self.signal.append(signal)


class Transaction:
    def __init__(self, name):
        self.name = name + '_transaction'
        self.field = []

    def addField(self, field):
        self.field.append(field)

class Agent:
        def __init__(self, name, instance, interface, transaction, driver_policy, monitor_policy, type):
            self.name = name
            self.instance = instance
            self.interface = interface
            self.transaction = transaction
            self.driver_policy = driver_policy
            self.monitor_policy = monitor_policy
            self.type = type
            self.refmod = []
            self.comp = []

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

        def writeInterface(self, outputdir):

            with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/general_agent/general_interface.tb', 'r') as file:
                tbInterface=file.read()

            tbInterface = tbInterface.replace('|-INTERFACE-|', self.interface.name)

            tbInterface = tbInterface.replace('|-CLOCK-|', self.interface.clock.name)

            tbInterface = tbInterface.replace('|-RESET-|', self.interface.reset.name)

            # SIGNALS

            for uSignal in self.interface.signal:
                tbInterface = tbInterface.replace('|-SIGNAL_NAME-|', uSignal.type + ' ' + uSignal.name + ';\n\t|-SIGNAL_NAME-|')

            # Cleaning residual tags
            tbInterface = tbInterface.replace('|-SIGNAL_NAME-|', '')

            interface_file = open(outputdir + '/' + self.interface.name + ".sv", "wt")
            n = interface_file.write(tbInterface)
            interface_file.close()

        def writeTransaction(self, outputdir):

            with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/general_agent/general_transaction.tb', 'r') as file:
                tbTransaction=file.read()

            tbTransaction = tbTransaction.replace('|-TRANSACTION-|', self.transaction.name)

            # FIELDS

            for uField in self.transaction.field:
                tbTransaction = tbTransaction.replace('|-FIELD_NAME-|', uField.type + ' ' + uField.name + ';\n\t|-FIELD_NAME-|') # INPUT DECLARATION
                tbTransaction = tbTransaction.replace('|-FIELD_MACRO-|','`uvm_field_int(' + uField.name + ', UVM_ALL_ON|UVM_HEX)\n\t\t|-FIELD_MACRO-|') #MACRO DECLARATION
                tbTransaction = tbTransaction.replace('|-FIELD_NAME_S-| = %h,', uField.name + ', |-FIELD_NAME_S-| = %h,') # convert2string DECLARATION
                tbTransaction = tbTransaction.replace('|-FIELD_NAME_S-|,', uField.name + ', |-FIELD_NAME_S-|,') # convert2string DECLARATION

            # Cleaning residual tags
            tbTransaction = tbTransaction.replace('|-FIELD_NAME-|', '')
            tbTransaction = tbTransaction.replace('|-FIELD_MACRO-|', '')
            tbTransaction = tbTransaction.replace(', |-FIELD_NAME_S-| = %h,', '')
            tbTransaction = tbTransaction.replace(', |-FIELD_NAME_S-|,', '')


            transaction_file = open(outputdir + '/' + self.name + "_transaction.sv", "wt")
            n = transaction_file.write(tbTransaction)
            transaction_file.close()

        def writeAgent(self, outputdir):

            with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/general_agent/general_agent.tb', 'r') as file:
                tbAgent=file.read()

            tbAgent = tbAgent.replace('|-AGENT-|', self.name)
            tbAgent = tbAgent.replace('|-TRANSACTION-|', self.transaction.name)

            if (self.type == 'input'):
                tbAgent = tbAgent.replace('uvm_analysis_port #(|-TRANSACTION-|) ap_resp;', '')
                tbAgent = tbAgent.replace('ap_resp = new("ap_resp", this);', '')
                tbAgent = tbAgent.replace('mon.resp.connect(ap_resp);', '')
            elif (self.type == 'output'):
                tbAgent = tbAgent.replace('uvm_analysis_port #(|-TRANSACTION-|) ap_req;', '')
                tbAgent = tbAgent.replace('ap_req = new("ap_req", this);', '')
                tbAgent = tbAgent.replace('mon.req.connect(ap_req);', '')
                tbAgent = tbAgent.replace('mon.req.connect(cov.collected_port);', '//OUTPUT COVERAGE')
            else:
                pass


            agent_file = open(outputdir + '/' + self.name + "_agent.sv", "wt")
            n = agent_file.write(tbAgent)
            agent_file.close()

        def writeDriver(self, outputdir):
            with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/general_agent/general_driver.tb', 'r') as file:
                tbDriver=file.read()

            tbDriver = tbDriver.replace('|-AGENT-|', self.name)
            tbDriver = tbDriver.replace('|-TRANSACTION-|', self.transaction.name)
            tbDriver = tbDriver.replace('|-INTERFACE-|', self.interface.name)
            tbDriver = tbDriver.replace('|-INTERFACE_INSTANCE-|', self.interface.instance)

            tbDriver = tbDriver.replace('|-DRIVER_POLICY-|', self.driver_policy.replace('\n','\n\t'))

            driver_file = open(outputdir + '/' + self.name + "_driver.sv", "wt")
            n = driver_file.write(tbDriver)
            driver_file.close()

        def writeMonitor(self, outputdir):
            with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/general_agent/general_monitor.tb', 'r') as file:
                tbMonitor=file.read()

            tbMonitor = tbMonitor.replace('|-AGENT-|', self.name)
            tbMonitor = tbMonitor.replace('|-INTERFACE-|', self.interface.name)
            tbMonitor = tbMonitor.replace('|-INTERFACE_INSTANCE-|', self.interface.instance)

            tbMonitor = tbMonitor.replace('|-MONITOR_POLICY-|', self.monitor_policy.replace('\n','\n\t\t'))

            if (self.type == 'input'):
                tbMonitor = tbMonitor.replace('this.resp.write(transCollected);', '')
                tbMonitor = tbMonitor.replace('uvm_analysis_port #(|-TRANSACTION-|) resp;', '')
                tbMonitor = tbMonitor.replace('this.resp = new("resp", this);', '')
            elif (self.type == 'output'):
                tbMonitor = tbMonitor.replace('this.req.write(transCollected);', '')
                tbMonitor = tbMonitor.replace('uvm_analysis_port #(|-TRANSACTION-|) req;', '')
                tbMonitor = tbMonitor.replace('this.req = new("req", this);', '')
            else:
                pass

            tbMonitor = tbMonitor.replace('|-TRANSACTION-|', self.transaction.name)

            monitor_file = open(outputdir + '/' + self.name + "_monitor.sv", "wt")
            n = monitor_file.write(tbMonitor)
            monitor_file.close()

        def writeCoverage(self, outputdir):

            with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/general_agent/general_coverage.tb', 'r') as file:
                tbCoverage=file.read()

            tbCoverage = tbCoverage.replace('|-AGENT-|', self.name)
            tbCoverage = tbCoverage.replace('|-TRANSACTION-|', self.transaction.name)

            coverage_file = open(outputdir + '/' + self.name + "_coverage.sv", "wt")
            n = coverage_file.write(tbCoverage)
            coverage_file.close()

        def writeAgentAll(self, outputdir):
            self.writeInterface(outputdir)
            self.writeTransaction(outputdir)
            self.writeAgent(outputdir)
            self.writeDriver(outputdir)
            self.writeMonitor(outputdir)
            self.writeCoverage(outputdir)
            self.writeAgent(outputdir)

class Port:
    def __init__(self, name, direction, origin, transaction, endComp):
        self.name = name
        self.direction = direction
        self.origin = origin
        self.transaction = transaction
        self.endComp = endComp

    def setEndComp(self, endComp):
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

    def writeRefmod(self, outputdir):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/scoreboard/refmod.tb', 'r') as file:
            tbRefmod=file.read()

        tbRefmod = tbRefmod.replace('|-REFMOD-|', self.name)

        for idx, uPort in enumerate(self.port_in):
            tbRefmod = tbRefmod.replace('|-INPUT_TRANSA-|', uPort.transaction.name + ' ' +  'req_' + str(idx) + ';\n\t|-INPUT_TRANSA-|')

        for idx, uPort in enumerate(self.port_out):
            tbRefmod = tbRefmod.replace('|-OUTPUT_TRANSA-|', uPort.transaction.name + ' ' +  'resp_' + str(idx) + ';\n\t|-OUTPUT_TRANSA-|')

        for idx, uPort in enumerate(self.port_in):
            tbRefmod = tbRefmod.replace('|-TRANSA_CREATION-|', 'req_'+ str(idx) + ' = new("req_' + str(idx) + '")' + ';\n\t\t|-TRANSA_CREATION-|')

        for idx, uPort in enumerate(self.port_out):
            tbRefmod = tbRefmod.replace('|-TRANSA_CREATION-|', 'resp_'+ str(idx) + ' = new("resp_' + str(idx) + '")' + ';\n\t\t|-TRANSA_CREATION-|')

        for idx, uPort in enumerate(self.port_in):
            tbRefmod = tbRefmod.replace('|-INPUT_PORT-|', 'uvm_tlm_analysis_fifo #(' + uPort.transaction.name + ') ' + 'from_' + uPort.origin + ';\n\t|-INPUT_PORT-|')

        for idx, uPort in enumerate(self.port_out):
            tbRefmod = tbRefmod.replace('|-OUTPUT_PORT-|', 'uvm_analysis_export #(' + uPort.transaction.name + ') ' + uPort.origin + '_to_'+ uPort.direction + ';\n\t|-OUTPUT_PORT-|')

        for idx, uPort in enumerate(self.port_in):
            tbRefmod = tbRefmod.replace('|-PORT_CREATION-|', 'from_' + uPort.origin + ' = new("' + 'from_' + uPort.origin + '", this)' + ';\n\t\t|-PORT_CREATION-|')

        for idx, uPort in enumerate(self.port_out):
            tbRefmod = tbRefmod.replace('|-PORT_CREATION-|', uPort.origin + '_to_'+ uPort.direction + ' = new("' + uPort.origin + '_to_'+ uPort.direction + '", this)' + ';\n\t\t|-PORT_CREATION-|')

        tbRefmod = tbRefmod.replace('|-REFMOD_POLICY-|', self.policy.replace('\n','\n\t\t'))

        # Cleanup
        tbRefmod = tbRefmod.replace('|-INPUT_TRANSA-|', '')
        tbRefmod = tbRefmod.replace('|-OUTPUT_TRANSA-|', '')
        tbRefmod = tbRefmod.replace('|-TRANSA_CREATION-|', '')
        tbRefmod = tbRefmod.replace('|-INPUT_PORT-|', '')
        tbRefmod = tbRefmod.replace('|-OUTPUT_PORT-|', '')
        tbRefmod = tbRefmod.replace('|-PORT_CREATION-|', '')

        refmod_file = open(outputdir + '/' + self.name + ".sv", "wt")
        n = refmod_file.write(tbRefmod)
        refmod_file.close()

class Comparator:

    def __init__(self, name, instance, transaction):
        self.name = name
        self.transaction = transaction
        self.instance = instance
        self.name = 'uvm_in_order_class_comparator #('+ self.transaction.name + ')'

class Scoreboard:

    def __init__(self, name, instance):
        self.name = name
        self.instance = instance
        self.port = []
        self.refmod = []
        self.comp = []

    def addPort(self, port):
        self.port.append(port)

    def addComp(self, comp):
        self.comp.append(comp)

    def addRefmod(self, refmod):
        self.refmod.append(refmod)

    def writeScoreboard(self, outputdir):

        with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/scoreboard/scoreboard.tb', 'r') as file:
            tbScoreboard=file.read()

        tbScoreboard = tbScoreboard.replace('|-SCOREBOARD-|', self.name)

        for idx,uRefmod in enumerate(self.refmod):
            tbScoreboard = tbScoreboard.replace('|-REFMOD-|', uRefmod.name + ' ' +  uRefmod.instance + ';\n\t|-REFMOD-|')

        for idx,uComp in enumerate(self.comp):
            tbScoreboard = tbScoreboard.replace('|-COMP-|', uComp.name + ' ' +  uComp.instance  + ';\n\t|-COMP-|')

        for idx,uPort in enumerate(self.port):
            tbScoreboard = tbScoreboard.replace('|-PORTS-|', 'uvm_analysis_port #(' + uPort.transaction.name + ') ' + uPort.origin + '_to_' + uPort.direction + ';\n\t|-PORTS-|')

        for idx,uRefmod in enumerate(self.refmod):
            tbScoreboard = tbScoreboard.replace('|-REFMOD_CREATION-|', uRefmod.instance + ' = ' + uRefmod.name + '::type_id::create("' + uRefmod.instance + '", this)' +  ';\n\t\t|-REFMOD_CREATION-|')

        for idx,uComp in enumerate(self.comp):
            tbScoreboard = tbScoreboard.replace('|-COMPARATOR_CREATION-|', uComp.instance + ' = ' + uComp.name + '::type_id::create("' + uComp.instance + '", this)' +  ';\n\t\t|-COMPARATOR_CREATION-|')

        for idx,uPort in enumerate(self.port):
            tbScoreboard = tbScoreboard.replace('|-PORTS_CREATION-|', uPort.origin + '_to_' + uPort.direction + '= new("' + uPort.origin + '_to_' + uPort.direction + '", this)' + ';\n\t\t|-PORTS_CREATION-|')

        for idx,uPort in enumerate(self.port):
            if uPort.endComp == 0:
                tbScoreboard = tbScoreboard.replace('|-CONNECTIONS-|', uPort.origin + '_to_' + uPort.direction + '.connect(' + uPort.direction + '.' 'from_' + uPort.origin + ');\n\t\t|-CONNECTIONS-|')
            elif uPort.endComp == 1:
                tbScoreboard = tbScoreboard.replace('|-CONNECTIONS-|', uPort.origin + '_to_' + uPort.direction + '.connect(' + uPort.direction + '.' 'before_export' + ');\n\t\t|-CONNECTIONS-|')
            else:
                for idx,uRefmod in enumerate(self.refmod):
                    if uPort.direction + '_rfm' == uRefmod.instance:
                        tbScoreboard = tbScoreboard.replace('|-CONNECTIONS-|', uPort.origin + '_to_' + uPort.direction + '.connect(' + uPort.direction + '_rfm.' 'from_' + uPort.origin + '.analysis_export);\n\t\t|-CONNECTIONS-|')
                for idy,uComp in enumerate(self.comp):
                    if uPort.direction == uComp.instance:
                        tbScoreboard = tbScoreboard.replace('|-CONNECTIONS-|', uPort.origin + '_to_' + uPort.direction + '.connect(' + uPort.direction + '.' 'before_export' + ');\n\t\t|-CONNECTIONS-|')

        # Refmod Port Creation
        for idx,uPort in enumerate(self.port):
            for idy,uRefmod in enumerate(self.refmod):
                if uPort.direction == uRefmod.instance:
                    port_aux = Port('rfm_in', uPort.direction, uPort.origin , uPort.transaction, 0)
                    self.refmod[idy].addPortIn(port_aux)

        for idx,uRefmod in enumerate(self.refmod):
            for idz, uPort_out in enumerate(uRefmod.port_out):
                if (uPort_out.endComp == 0):
                    for idy,uRefmod_out in enumerate(self.refmod):
                        if (uPort_out.direction + '_rfm') == (uRefmod_out.instance):
                            port_aux = Port('rfm_in', uPort_out.direction, uPort_out.origin , uPort_out.transaction, 0)
                            self.refmod[idy].addPortIn(port_aux)

        # Refmod -> Comp connection
        for idy,uRefmod in enumerate(self.refmod):
            for idx,uPort in enumerate(uRefmod.port_out):
                if idx == 0:
                    tbScoreboard = tbScoreboard.replace('|-CONNECTIONS-|', uRefmod.instance + '.' + uPort.origin + '_to_'+ uPort.direction + '.connect(' + uPort.direction + '.' 'after_export' + ');\n\t\t|-CONNECTIONS-|')
                else:
                    tbScoreboard = tbScoreboard.replace('|-CONNECTIONS-|', uRefmod.instance + '.' + uPort.origin + '_to_'+ uPort.direction + '.connect(' + uPort.direction + '_rfm.' + 'from_' + uPort.origin + ');\n\t\t|-CONNECTIONS-|')

        # CLEANUP
        tbScoreboard = tbScoreboard.replace('|-REFMOD-|', '')
        tbScoreboard = tbScoreboard.replace('|-COMP-|', '')
        tbScoreboard = tbScoreboard.replace('|-PORTS-|', '')
        tbScoreboard = tbScoreboard.replace('|-REFMOD_CREATION-|', '')
        tbScoreboard = tbScoreboard.replace('|-COMPARATOR_CREATION-|', '')
        tbScoreboard = tbScoreboard.replace('|-PORTS_CREATION-|', '')
        tbScoreboard = tbScoreboard.replace('|-CONNECTIONS-|', '')

        scoreboard_file = open(outputdir + '/' + self.name + "_scoreboard.sv", "wt")
        n = scoreboard_file.write(tbScoreboard)
        scoreboard_file.close()

class Vip:
    def __init__(self, name, instance, interface, file_package):
        self.name = name + '_env'
        self.interface = interface
        self.instance = instance
        self.file_package = file_package
        self.port = []
        self.include = []

    def addPort(self, tlm_port):
        self.port.append(tlm_port)

    def addInclude(self, include_file):
        self.include.append(include_file)

class Env:
    def __init__(self, name, instance, port, scoreboard):
        self.name = name + '_env'
        self.instance = instance
        self.port = [port]
        self.scoreboard = scoreboard
        self.agent = []
        self.vip = []

    def addPort(self, port):
        self.port.append(port)

    def setScoreboard (self, scoreboard):
        self.scoreboard = scoreboard

    def addAgent(self, agent):
        self.agent.append(agent)

    def addVip(self, vip):
        self.vip.append(vip)

    def writeEnv(self, outputdir):

        with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/env.tb', 'r') as file:
            tbEnv=file.read()

        tbEnv = tbEnv.replace('|-ENV-|', self.name)

        for idx,agent in enumerate(self.agent):
            tbEnv = tbEnv.replace('|-AGENT-|', agent.name + '_agent ' +  agent.instance + ';\n\t|-AGENT-|')

        tbEnv = tbEnv.replace('|-SCOREBOARD-|', self.scoreboard.name + '_scoreboard ' +  self.scoreboard.instance  + ';\n\t|-SCOREBOARD-|')

        for idx,agent in enumerate(self.agent):
            tbEnv = tbEnv.replace('|-AGENT_CREATION-|', agent.instance + ' = ' + agent.name + '_agent' + '::type_id::create("' + agent.instance + '", this)' +  ';\n\t\t|-AGENT_CREATION-|')

        tbEnv = tbEnv.replace('|-SCOREBOARD_CREATION-|', self.scoreboard.instance + ' = ' + self.scoreboard.name + '_scoreboard' + '::type_id::create("' + self.scoreboard.instance + '", this)' +  ';\n\t\t|-SCOREBOARD_CREATION-|')

        for idx,uVip in enumerate(self.vip):
            tbEnv = tbEnv.replace('|-VIP-|', uVip.name + ' ' +  uVip.instance + ';\n\t|-VIP-|')
            tbEnv = tbEnv.replace('|-VIP_CREATION-|', uVip.instance + ' = ' + uVip.name + '::create("' + uVip.instance + '", this)' +  ';\n\t\t|-VIP_CREATION-|')

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

        for uVip in self.vip:
            for uPort in uVip.port:
                envPortVipC = Port(uPort.origin + '_to_' + uPort.direction, uPort.direction, uPort.origin, uPort.transaction, 3)
                self.scoreboard.addPort(copy.copy(envPortVipC))
                tbEnv = tbEnv.replace('|-CONNECTIONS-|', uVip.instance + '.' + uPort.name + '.connect(' + self.scoreboard.instance + '.' + uPort.origin + '_to_' + uPort.direction + ');\n\t\t|-CONNECTIONS-|')


        # CLEANUP
        tbEnv = tbEnv.replace('|-AGENT-|', '')
        tbEnv = tbEnv.replace('|-VIP-|', '')
        tbEnv = tbEnv.replace('|-REFMOD-|', '')
        tbEnv = tbEnv.replace('|-SCOREBOARD-|', '')
        tbEnv = tbEnv.replace('|-SCOREBOARD_CREATION-|', '')
        tbEnv = tbEnv.replace('|-AGENT_CREATION-|', '')
        tbEnv = tbEnv.replace('|-VIP_CREATION-|', '')
        tbEnv = tbEnv.replace('|-SCOREBOARD_CREATION-|', '')
        tbEnv = tbEnv.replace('|-CONNECTIONS-|', '')


        env_file = open(outputdir + '/' + self.name + ".sv", "wt")
        n = env_file.write(tbEnv)
        env_file.close()

class Sequence:

    def __init__(self, name, agent, transaction):
        self.name = name + '_sequence'
        self.agent = [agent]
        self.transaction = transaction

    def writeSequence(self, outputdir):

            with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/sequence.tb', 'r') as file:
                tbSequence=file.read()

            tbSequence = tbSequence.replace('|-SEQUENCE-|', self.name)
            tbSequence = tbSequence.replace('|-TRANSACTION-|', self.transaction.name)

            sequence_file = open(outputdir + '/' + self.name + ".sv", "wt")
            n = sequence_file.write(tbSequence)
            sequence_file.close()

class Test:
    def __init__(self, env, name):
        self.name = name + '_test'
        self.env = env
        self.sequence = []

    def addSequence(self, sequence):
        self.sequence.append(sequence)

    def writeTest(self, outputdir):

        with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/test.tb', 'r') as file:
            tbTest=file.read()

        tbTest = tbTest.replace('|-TEST-|', self.name)

        tbTest = tbTest.replace('|-ENV-|', self.env.name + ' env_h;')

        for idx,sequence in enumerate(self.sequence):
            tbTest = tbTest.replace('|-SEQUENCE-|', sequence.name + ' seq_' + str(idx) + ';\n\t|-SEQUENCE-|')

        tbTest = tbTest.replace('|-ENV_CREATION-|', 'env_h' + ' = ' + self.env.name + '::type_id::create("env_h", this)' +  ';\n\t\t|-ENV_CREATION-|')
        for idx,sequence in enumerate(self.sequence):
            tbTest = tbTest.replace('|-SEQUENCE_CREATION-|', 'seq_' + str(idx) + ' = ' + sequence.name + '::type_id::create("'+ 'seq_' + str(idx) +'", this)' +  ';\n\t\t|-SEQUENCE_CREATION-|')
            for agent in sequence.agent:
                tbTest = tbTest.replace('|-SEQUENCE_START-|', 'seq_' + str(idx) + '.start(env_h.' + agent.instance + '.sqr)' + ';\n\t\t|-SEQUENCE_START-|')

        # CLEANUP
        tbTest = tbTest.replace('|-TEST-|', '')
        tbTest = tbTest.replace('|-ENV-|', '')
        tbTest = tbTest.replace('|-SEQUENCE-|', '')
        tbTest = tbTest.replace('|-ENV_CREATION-|', '')
        tbTest = tbTest.replace('|-SEQUENCE_CREATION-|', '')
        tbTest = tbTest.replace('|-SEQUENCE_START-|', '')


        test_file = open(outputdir + '/' + self.name + ".sv", "wt")
        n = test_file.write(tbTest)
        test_file.close()

class Module:
    def __init__(self, name):
        self.name = name
        self.clock = []
        self.reset = []
        self.signal = []
        self.interface = []
        self.env = []
        self.agent = []
        self.vip = []
        self.test = []

    def addSignal(self, signal):
        self.signal.append(signal)

    def addInterface(self, interface):
        self.interface.append(interface)

    def addClock(self, clock):
        self.clock.append(clock)

    def addReset(self, reset):
        self.reset.append(reset)

    def addEnv(self, env):
        self.env.append(env)

    def addAgent(self, agent):
        self.agent.append(agent)

    def addVip(self, vip):
        self.vip.append(vip)

    def addTest(self, test):
        self.test.append(test)

    def writeWrapper(self, outputdir):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/wrapper.tb', 'r') as file:
            tbWrapper=file.read()

        tbWrapper = tbWrapper.replace('|-MODULE-|', self.name)

        for idx,uAgent in enumerate(self.agent):
            tbWrapper = tbWrapper.replace('|-INTERFACE-|', uAgent.interface.name + ' ' + uAgent.interface.instance + '_if' +',\n\t|-INTERFACE-|')

        for idx,uVip in enumerate(self.vip):
            tbWrapper = tbWrapper.replace('|-INTERFACE-|', uVip.interface.name + ' ' + uVip.interface.instance + '_if' +',\n\t|-INTERFACE-|')

        for idx,uClock in enumerate(self.clock):
            tbWrapper = tbWrapper.replace('|-INTERFACE-|', 'input ' + uClock.name +',\n\t|-INTERFACE-|')

        for idx,uReset in enumerate(self.reset):
            tbWrapper = tbWrapper.replace('|-INTERFACE-|', 'input ' + uReset.name +',\n\t|-INTERFACE-|')

        for idx,uAgent in enumerate(self.agent):
            for idy,busSig in enumerate(uAgent.interface.signal):
                    if busSig.connect is not None:
                        tbWrapper = tbWrapper.replace('|-CONNECTIONS-|', '.'+ busSig.connect + '(' + uAgent.interface.instance + '_if.' + busSig.name +') ' +',\n\t\t|-CONNECTIONS-|')
                    else:
                        tbWrapper = tbWrapper.replace('|-CONNECTIONS-|', '.'+ busSig.name + '(' + uAgent.interface.instance + '_if.' + busSig.name +') ' +',\n\t\t|-CONNECTIONS-|')

        for idx,uVip in enumerate(self.vip):
            for idy,busSig in enumerate(uVip.interface.signal):
                    if busSig.connect is not None:
                        tbWrapper = tbWrapper.replace('|-CONNECTIONS-|', '.'+ busSig.connect + '(' + uVip.interface.instance + '_if.' + busSig.name +') ' +',\n\t\t|-CONNECTIONS-|')
                    else:
                        tbWrapper = tbWrapper.replace('|-CONNECTIONS-|', '.'+ busSig.name + '(' + uVip.interface.instance + '_if.' + busSig.name +') ' +',\n\t\t|-CONNECTIONS-|')

        for idx,uClock in enumerate(self.clock):
            tbWrapper = tbWrapper.replace('|-CONNECTIONS-|', '.' + uClock.name + '(' + uClock.name + ')' +',\n\t\t|-CONNECTIONS-|')

        for idx,uReset in enumerate(self.reset):
            tbWrapper = tbWrapper.replace('|-CONNECTIONS-|', '.' + uReset.name + '(' + uReset.name + ')' +',\n\t\t|-CONNECTIONS-|')

        #CLEANUP
        tbWrapper = tbWrapper.replace(',\n\t|-INTERFACE-|','')
        tbWrapper = tbWrapper.replace(',\n\t\t|-CONNECTIONS-|','')

        wrapper_file = open(outputdir + '/' + self.name + "_wrapper.sv", "wt")
        n = wrapper_file.write(tbWrapper)
        wrapper_file.close()

    def writeTop(self, outputdir):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/top.tb', 'r') as file:
            tbTop=file.read()

        tbTop = tbTop.replace('|-PACKAGE-|', self.name)
        tbTop = tbTop.replace('|-MODULE_NAME-|', self.name)

        for idx,uClock in enumerate(self.clock):
            tbTop = tbTop.replace('|-CLOCK-|', 'logic ' + uClock.name +';\n\t|-CLOCK-|')
            tbTop = tbTop.replace('|-CLOCK_PERIOD-|', 'localparam P_' + uClock.name.upper() + ' = ' + str(uClock.period) +'ns;\n\t|-CLOCK_PERIOD-|')
            tbTop = tbTop.replace('|-CLOCK_CH-|', 'always #(P_' + uClock.name.upper() + '/2)' + uClock.name + '= ~' + uClock.name +';\n\t|-CLOCK_CH-|')

        for idx,uReset in enumerate(self.reset):
            tbTop = tbTop.replace('|-RESET-|', 'logic ' + uReset.name +';\n\t\t|-RESET-|')
            tbTop = tbTop.replace('|-RESET_PERIOD-|', 'localparam P_' + uReset.name.upper() + ' = ' + str(uReset.period) + 'ns;\n\t|-RESET_PERIOD-|')
            tbTop = tbTop.replace('|-RESET_CH-|', 'always begin\n\t\t#(P_' + uReset.name.upper() + ') ' + uReset.name +' = 0; '+ '\n\t\t#(' + str(uReset.duration) + ') ' + uReset.name + ' = 1;' +'\n\t|-RESET_CH-|')

        for idx, uAgent in enumerate(self.agent):
            tbTop = tbTop.replace('|-INTERFACE-|', uAgent.interface.name + ' ' + uAgent.interface.instance + '_if_top (\n\t\t.' \
            + uAgent.interface.clock.name + '(' + uAgent.interface.clock.name + '), .' + \
            uAgent.interface.reset.name + '(' + uAgent.interface.reset.name + ')\n\t);'+ '\n\t\t|-INTERFACE-|')
            tbTop = tbTop.replace('|-INTERFACE_CONNECTION-|', '.' + uAgent.interface.instance + '_if (' + uAgent.interface.instance + '_if_top)' +',\n\t\t|-INTERFACE_CONNECTION-|')

        for idx, uClock in enumerate(self.clock):
            tbTop = tbTop.replace('|-INTERFACE_CONNECTION-|', '.' + uClock.name + '(' + uClock.name + ')' +',\n\t\t|-INTERFACE_CONNECTION-|')
            tbTop = tbTop.replace('|-INITIAL_CLOCK-|', uClock.name + ' = 0;' +'\n\t\t|-INITIAL_CLOCK-|')

        for idx, uReset in enumerate(self.reset):
            tbTop = tbTop.replace('|-INTERFACE_CONNECTION-|', '.' + uReset.name + '(' + uReset.name + ')' +',\n\t\t|-INTERFACE_CONNECTION-|')
            tbTop = tbTop.replace('|-INITIAL_RESET-|', uReset.name + ' = 1;' +'\n\t\t|-INITIAL_RESET-|')

        for idx, uAgent in enumerate(self.agent):
            tbTop = tbTop.replace('|-INTERFACE_CDB-|', \
                        'uvm_config_db#(virtual ' + uAgent.interface.name + ')::set(null, "*.env_h.' + uAgent.instance + '.*", "VIRTUAL_IF", ' \
                         + uAgent.interface.instance + '_if_top)' +';\n\t\t|-INTERFACE_CDB-|')

        for idx, uVip in enumerate(self.vip):
            tbTop = tbTop.replace('|-INTERFACE_CDB-|', \
                        'uvm_config_db#(virtual ' + uVip.interface.name + ')::set(null, "*.env_h.' + uVip.instance + '.*", "VIRTUAL_IF", ' \
                         + uVip.interface.instance + '_if_top)' +';\n\t\t|-INTERFACE_CDB-|')


        #CLEANUP
        tbTop = tbTop.replace('|-CLOCK-|', '')
        tbTop = tbTop.replace('|-RESET-|', '')
        tbTop = tbTop.replace('|-CLOCK_PERIOD-|', '')
        tbTop = tbTop.replace('|-RESET_PERIOD-|', '')
        tbTop = tbTop.replace('|-INITIAL_RESET-|', '')
        tbTop = tbTop.replace('|-INITIAL_CLOCK-|', '')
        tbTop = tbTop.replace('|-CLOCK_CH-|', '')
        tbTop = tbTop.replace('|-RESET_CH-|', 'end')
        tbTop = tbTop.replace('|-INTERFACE-|', '')
        tbTop = tbTop.replace(',\n\t\t|-INTERFACE_CONNECTION-|', '')
        tbTop = tbTop.replace('|-INTERFACE_CDB-|', '')
        tbTop = tbTop.replace('\n\n', '\n')


        top_file = open(outputdir + '/' + self.name + "_top.sv", "wt")
        n = top_file.write(tbTop)
        top_file.close()

    def writeModule(self, outputdir):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/frontend/module.fe', 'r') as file:
            tbModule=file.read()

        tbModule = tbModule.replace('|-MODULE-|', self.name)

        tbModule = tbModule.replace('|-MODULE_NAME-|', self.name)

        for idx,uClock in enumerate(self.clock):
            tbModule = tbModule.replace('|-SIGNALS-|', 'input ' + uClock.name +',\n\t\t|-SIGNALS-|')

        for idx,uReset in enumerate(self.reset):
            tbModule = tbModule.replace('|-SIGNALS-|', 'input ' + uReset.name +',\n\t\t|-SIGNALS-|')

        for uSignal in self.signal:
                tbModule = tbModule.replace('|-SIGNALS-|', uSignal.io + ' ' + uSignal.type + ' ' + uSignal.name + ',\n\t\t|-SIGNALS-|')


        tbModule = tbModule.replace(',\n\t\t|-SIGNALS-|', '')

        module_file = open(outputdir + '/rtl/src/' + self.name + ".sv", "wt")
        n = module_file.write(tbModule)
        module_file.close()

    def writeMakefile(self,  outputdir):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/makefile_verif.tb', 'r') as file:
            tbMakefile=file.read()

        tbMakefile = tbMakefile.replace('|-MODULE-|', self.name)

        aux_files = []
        for idx, uAgent in enumerate(self.agent):
            if uAgent.interface.name not in aux_files:
                tbMakefile = tbMakefile.replace('|-INTERFACE-|', '../../tb/' + uAgent.interface.name + '.sv \ \n\t|-INTERFACE-|')

            aux_files.append(uAgent.interface.name)
        
        for idx, uVip in enumerate(self.vip):
            for idy, uInclude in enumerate(uVip.include):
                tbMakefile = tbMakefile.replace('|-INTERFACE-|', uInclude +' \ \n\t|-INTERFACE-|')

        test_string = """|-TEST-|:
\t@xrun -64bit -uvm  +incdir+$(RTL_SRC) $(PKGS) $(IF) $(RTL) $(WRAPPER) ../../tb/|-MODULE-|_top.sv +UVM_TESTNAME=|-TEST-| -covtest |-TEST-|-$(SEED) -svseed $(SEED) -defparam top.min_cover=$(COVER) -defparam top.min_transa=$(TRANSA) $(RUN_ARGS_COMMON) -xmlibdirpath ../../workspace/rtlsim $(RUN_ARGS)"""

        for idx, uTest in enumerate(self.test):
            aux_string = test_string.replace('|-TEST-|', uTest.name)
            aux_string = test_string.replace('|-MODULE-|', self.name)
            tbMakefile = tbMakefile.replace('|-TEST-|', aux_string + '\n\n|-TEST-|')


        tbMakefile = tbMakefile.replace('\n\n|-TEST-|', '')
        tbMakefile = tbMakefile.replace(' \ \n\t|-INTERFACE-|', '')

        module_file = open(outputdir + "/../scripts/rtlsim/Makefile", "wt")
        n = module_file.write(tbMakefile)
        module_file.close()


class Synth:
    def __init__(self, name):
        self.name = name
        self.pdk = ''
        self.pdk_files = []


    def setPDK(self, pdk_dir):
        self.pdk = pdk_dir

    def addPDKFile(self, pdk_file):
        self.pdk_files.append(pdk_file)

    def writeTcl(self, output_dir):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/frontend/synth.fe', 'r') as file:
            tbTcl=file.read()

        tbTcl = tbTcl.replace('|-MODULE-|', self.name)
        tbTcl = tbTcl.replace('|-TECHLIBASE-|', self.pdk)

        for idx,uFile in enumerate(self.pdk_files):
            tbTcl = tbTcl.replace('|-TECHLIBPATH-|', '$TECHLIBBASE' + uFile + ' \ ' + '\n                    |-TECHLIBPATH-|')

        tbTcl = tbTcl.replace(' \ \n                    |-TECHLIBPATH-|', '')


        tcl_file = open(output_dir + '/scripts/synth_logic/synth.tcl', "wt")
        n = tcl_file.write(tbTcl)
        tcl_file.close()

    def writeMakefile(Self, output_dir):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/frontend/makefile_synth.fe', 'r') as file:
            tbMake=file.read()

        mk_file = open(output_dir + '/scripts/synth_logic/Makefile', "wt")
        n = mk_file.write(tbMake)
        mk_file.close()

class Package:
    def __init__(self, name):
        self.name = name
        self.vip = []

    def addVip(self, vip):
        self.vip.append(vip)

    def writePackage(self, outputdir):
        pkg = """package {MODULE}_pkg;
    `include "uvm_macros.svh"
    import uvm_pkg::*;
    |-IMPORT-|

    |-FILES-|
endpackage""".format(MODULE=self.name)

        f = []
        for (dirpath, dirnames, filenames) in os.walk(outputdir):
            f.extend(filenames)

        for filename in f:
            if '_top.sv' not in filename and '_wrapper.sv' not in filename and '_interface.sv' not in filename:
                pkg = pkg.replace('|-FILES-|', '`include ../../tb/"' + filename +'"\n\t|-FILES-|')

        for uVip in self.vip:
            import_name = uVip.file_package.replace('.sv', '')
            if '/' in import_name:
                string = import_name.rsplit("/", 1)
            pkg = pkg.replace('|-IMPORT-|', 'import ' + string[1] +'::*\n\t|-IMPORT-|')

        pkg = pkg.replace('|-FILES-|', '')
        pkg = pkg.replace('|-IMPORT-|', '')

        pkg_file = open(outputdir + '/' + self.name + "_pkg.sv", "wt")
        n = pkg_file.write(pkg)
        pkg_file.close()

class Formal:
    def __init__(self, name):
        self.name = name
        self.clock = []
        self.reset = []
        self.signal = []

    def addSignal(self, signal):
        self.signal.append(signal)

    def addClock(self, clock):
        self.clock.append(clock)

    def addReset(self, reset):
        self.reset.append(reset)

    def writeVerifModule(self, output_dir):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/module_assertions.tb', 'r') as file:
            tbVMod=file.read()

        tbVMod = tbVMod.replace('|-MODULE-|', self.name)

        for idx,uClock in enumerate(self.clock):
            tbVMod = tbVMod.replace('|-SIGNALS-|', 'input logic' + uClock.name +',\n\t\t|-SIGNALS-|')

        for idx,uReset in enumerate(self.reset):
            tbVMod = tbVMod.replace('|-SIGNALS-|', 'input logic' + uReset.name +',\n\t\t|-SIGNALS-|')

        for uSignal in self.signal:
            tbVMod = tbVMod.replace('|-SIGNALS-|', 'input' + ' ' + uSignal.type + ' ' + uSignal.name + ',\n\t\t|-SIGNALS-|')


        tbVMod = tbVMod.replace(',\n\t\t|-SIGNALS-|', '')

        vmodule_file = open(output_dir + '/../formal/properties/v_' + self.name + '.sva', "wt")
        n = vmodule_file.write(tbVMod)
        vmodule_file.close()

        with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/bindings.tb', 'r') as file:
            tbBind=file.read()

        tbBind = tbBind.replace('|-MODULE-|', self.name)

        for idx,uClock in enumerate(self.clock):
            tbBind = tbBind.replace('|-SIGNALS-|', '.' + uClock.name + '(' + uClock.name + ')' +',\n\t\t|-SIGNALS-|')

        for idx,uReset in enumerate(self.reset):
            tbBind = tbBind.replace('|-SIGNALS-|', '.' + uReset.name + '(' + uReset.name + ')' +',\n\t\t|-SIGNALS-|')

        for uSignal in self.signal:
            tbBind = tbBind.replace('|-SIGNALS-|', '.' + uSignal.name + '(' + uSignal.name + ')' +',\n\t\t|-SIGNALS-|')

        tbBind = tbBind.replace(',\n\t\t|-SIGNALS-|', '')

        bidings_file = open(output_dir + '/../formal/properties/bindings.sva', "wt")
        n = bidings_file.write(tbBind)
        bidings_file.close()

    def writeTcl(self, output_dir):

        with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/fpv.tb', 'r') as file:
            tbTcl=file.read()

        tbTcl = tbTcl.replace('|-MODULE-|', self.name)

        for idx,uClock in enumerate(self.clock):
            tbTcl = tbTcl.replace('|-CLOCK-|', 'clock ' + uClock.name +'\n|-CLOCK-|')

        for idx,uReset in enumerate(self.reset):
            tbTcl = tbTcl.replace('|-RESET-|', 'reset ~' + uReset.name +'\n|-RESET-|')

        tbTcl = tbTcl.replace('|-CLOCK-|', '')
        tbTcl = tbTcl.replace('|-RESET-|', '')

        tcl_file = open(output_dir + '/../scripts/formal/formal.tcl', "wt")
        n = tcl_file.write(tbTcl)
        tcl_file.close()

    def writeMakefile(Self, output_dir):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/../src/templates/verification/formal_mk.tb', 'r') as file:
            tbMake=file.read()

        if 'verification' in output_dir:
            mk_file = open(output_dir + '/../scripts/formal/Makefile', "wt")
            n = mk_file.write(tbMake)
            mk_file.close()
        else:
            tbMake = tbMake.replace('-fpv ', '-fpv ../../../verification/scripts/formal/')
            mk_file = open(output_dir + '/rtl/tb/Makefile', "wt")
            n = mk_file.write(tbMake)
            mk_file.close()

class Parser:

    def __init__(self, name, inputfile, outputdir):
        self.name = name
        self.inputfile = inputfile
        self.outputdir = outputdir

    def parse_verif(self):
        with open(self.inputfile, 'r') as file:
            tbConfig=file.read()

        tbConfig_Split = "".join([s for s in tbConfig.splitlines(True) if s.strip("\r\n")])

        tbConfig_Split = tbConfig_Split.splitlines()

        tbSplit_agent = []
        tbSplit_comp = []
        tbSplit_signal = []
        tbSplit_field = []
        tbSplit_clock = []
        tbSplit_reset = []
        tbSplit_interface = []
        tbSplit_transa = []
        tbSplit_refmod = []
        tbSplit_module = []
        tbSplit_test = []
        tbSplit_sequence = []
        tbSplit_if_instance = []
        tbSplit_vip = []

        for line in tbConfig_Split:
            if 'agent' in line and '=' not in line:
                current_analysis='agent'
            if 'comp' in line and '=' not in line:
                current_analysis='comp'
            if 'signal' in line and '=' not in line:
                current_analysis='signal'
            if 'field' in line and '=' not in line:
                current_analysis='field'
            if 'clock' in line and '=' not in line:
                current_analysis='clock'
            if 'reset' in line and '=' not in line:
                current_analysis='reset'
            if 'interface' in line and '=' not in line:
                current_analysis='interface'
            if 'transaction' in line and '=' not in line:
                current_analysis='transaction'
            if 'refmod' in line and '=' not in line:
                current_analysis='refmod'
            if 'module' in line and '=' not in line:
                current_analysis='module'
            if 'test' in line and '=' not in line:
                current_analysis='test'
            if 'sequence' in line and '=' not in line:
                current_analysis='sequence'
            if 'if_instance' in line and '=' not in line:
                current_analysis='if_instance'
            if 'vip' in line and '=' not in line:
                current_analysis='vip'
            if '}' in line and '=' not in line:
                current_analysis=current_analysis

            if current_analysis == 'agent':
                tbSplit_agent.append(line)
            if current_analysis == 'comp':
                tbSplit_comp.append(line)
            if current_analysis == 'signal':
                tbSplit_signal.append(line)
            if current_analysis == 'field':
                tbSplit_field.append(line)
            if current_analysis == 'clock':
                tbSplit_clock.append(line)
            if current_analysis == 'reset':
                tbSplit_reset.append(line)
            if current_analysis == 'interface':
                tbSplit_interface.append(line)
            if current_analysis == 'transaction':
                tbSplit_transa.append(line)
            if current_analysis == 'refmod':
                tbSplit_refmod.append(line)
            if current_analysis == 'module':
                tbSplit_module.append(line)
            if current_analysis == 'test':
                tbSplit_test.append(line)
            if current_analysis == 'sequence':
                tbSplit_sequence.append(line)
            if current_analysis == 'if_instance':
                tbSplit_if_instance.append(line)
            if current_analysis == 'vip':
                tbSplit_vip.append(line)
            if current_analysis == 'NONE':
                pass

        list_agent = []
        list_comp = []
        list_signal = []
        list_field = []
        list_clock = []
        list_reset = []
        list_interface = []
        list_if_instance = []
        list_transa = []
        list_refmod = []
        list_test = []
        list_sequence = []
        list_vip = []

        for line in tbSplit_module:
            if 'module' in line and '=' not in line:
                auxName = ''

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if '}' in line:
                moduleName = auxName

        for line in tbSplit_clock:
            if 'clock' in line and '=' not in line:
                auxName = 'NONE'
                auxPeriod = 'NONE'

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if 'period' in line:
                string = line.split("=", 1)
                auxPeriod = string[1]
                auxPeriod = auxPeriod.replace(" ","")

            if '}' in line:
                auxClock = Clock(auxName, auxPeriod)
                list_clock.append(auxClock)

        for line in tbSplit_reset:
            if 'reset' in line and '=' not in line:
                auxName = 'NONE'
                auxPeriod = 'NONE'
                auxDuration = 'NONE'

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if 'period' in line:
                string = line.split("=", 1)
                auxPeriod = string[1]
                auxPeriod = auxPeriod.replace(" ","")

            if 'duration' in line:
                string = line.split("=", 1)
                auxDuration = string[1]
                auxDuration = auxDuration.replace(" ","")

            if '}' in line:
                auxReset = Reset(auxName, auxPeriod, auxDuration)
                list_reset.append(auxReset)

        for line in tbSplit_signal:
            if 'signal' in line and '=' not in line:
                auxName = 'NONE'
                auxType = 'NONE'
                auxIo = 'NONE'
                auxConnect = 'NONE'

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if 'type' in line:
                string = line.split("=", 1)
                auxType = string[1]
                auxType = auxType.replace(" ","")

            if 'io' in line:
                string = line.split("=", 1)
                auxIo = string[1]
                auxIo = auxIo.replace(" ","")

            if '}' in line:
                auxSignal = Signal(auxName, auxType, auxIo)
                list_signal.append(auxSignal)

        for line in tbSplit_field:
            if 'field' in line and '=' not in line:
                auxName = 'NONE'
                auxType = 'NONE'

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if 'type' in line:
                string = line.split("=", 1)
                auxType = string[1]
                auxType = auxType.replace(" ","")


            if (auxName is not 'NONE') and (auxType is not 'NONE'):
                auxField = Field(auxName, auxType)
                list_field.append(auxField)

        for line in tbSplit_interface:

            if 'interface' in line and '=' not in line:
                auxName = ''
                auxInstance = ''
                auxSignal_list = []

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if 'clock' in line:
                string = line.split("=", 1)
                auxClock_name = string[1]
                auxClock_name = auxClock_name.replace(" ","")

                for idx,uClock in enumerate(list_clock):
                    if (uClock.name == auxClock_name):
                        auxClock = uClock
                        break

            if 'reset' in line:
                string = line.split("=", 1)
                auxReset_name = string[1]
                auxReset_name = auxReset_name.replace(" ","")

                for idx,uReset in enumerate(list_reset):
                    if (uReset.name == auxReset_name):
                        auxReset = uReset
                        break

            if 'signal' in line:
                string = line.split("=", 1)
                auxSignal_name = string[1]
                auxSignal_name = auxSignal_name.replace(" ","")

                for idx,uSignal in enumerate(list_signal):
                    if (uSignal.name == auxSignal_name):
                        auxSignal = uSignal
                        break

                auxSignal_list.append(auxSignal)


            if '}' in line:
                for line in tbSplit_if_instance:
                    if 'if_instance' in line and '=' not in line:
                        auxInstance = ''
                        auxName_con = ''
                        auxSig_if = []
                        auxDut_if = []
                        auxSignal_sig_list = []
                        auxInterface = None
                        for uSignal in auxSignal_list:
                            auxSignal_sig_list.append(uSignal)

                    if 'type' in line:
                        string = line.split("=", 1)
                        auxName_con = string[1]
                        auxName_con = auxName_con.replace(" ","")

                    if 'instance' in line and 'if_instance' not in line:
                        string = line.split("=", 1)
                        auxInstance = string[1]
                        auxInstance = auxInstance.replace(" ","")

                    if 'con' in line:
                        string = line.split("=", 1)
                        auxConnect_name = string[1]
                        auxConnect_name = auxConnect_name.replace(" ","")
                        connection = auxConnect_name.split(",", 1)
                        auxSig_if.append(connection[0])
                        auxDut_if.append(connection[1])

                    if '}' in line:
                        if auxName_con==auxName:
                            auxInterface = Interface(auxName, auxInstance, auxClock, auxReset)
                            for idx,uSignal in enumerate(auxSignal_list):
                                signal_aux = copy.copy(uSignal)
                                for idy, uSignal_aux in enumerate(auxSig_if):
                                    if uSignal_aux == signal_aux.name:
                                        signal_aux.addConnection(auxDut_if[idy])
                                auxInterface.addSignal(signal_aux)

                            list_interface.append(auxInterface)
                        else:
                            pass

        for line in tbSplit_transa:

            if 'transaction' in line and '=' not in line:
                auxName = ''
                auxField_list = []

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")


            if 'field' in line:
                string = line.split("=", 1)
                auxField_name = string[1]
                auxField_name = auxField_name.replace(" ","")

                for idx,uField in enumerate(list_field):
                    if (uField.name == auxField_name):
                        auxField = uField
                        break

                auxField_list.append(auxField)


            if '}' in line:

                auxTransaction = Transaction(auxName)
                for idx,uField in enumerate(auxField_list):
                    auxTransaction.addField(uField)

                list_transa.append(auxTransaction)

        for line in tbSplit_comp:

            if 'comp' in line and '=' not in line:
                auxName = ''
                auxInstance =''

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if 'instance' in line:
                string = line.split("=", 1)
                auxInstance = string[1]
                auxInstance = auxInstance.replace(" ","")

            if 'transaction' in line:
                string = line.split("=", 1)
                auxTransaction_name = string[1]
                auxTransaction_name = auxTransaction_name.replace(" ","")

                for idx,uTransaction in enumerate(list_transa):
                    if (uTransaction.name == (auxTransaction_name + '_transaction')):
                        auxTransaction = uTransaction
                        break

            if '}' in line:

                auxComp = Comparator(auxName, auxInstance, auxTransaction)
                list_comp.append(auxComp)

        for line in tbSplit_refmod:

            if 'refmod' in line and '=' not in line:
                auxName = ''
                auxInstance =''
                auxPort_out = []

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if 'instance' in line:
                string = line.split("=", 1)
                auxInstance = string[1]
                auxInstance = auxInstance.replace(" ","")

            if 'refmod_policy' in line:
                string = line.split("=", 1)
                auxRefmod_policy = string[1]
                auxRefmod_policy = auxRefmod_policy.replace(" ","")

            if 'comp' in line:
                string = line.split("=", 1)
                auxComp = string[1]
                auxComp = auxComp.replace(" ","")

            if 'connect' in line:
                string = line.split("=", 1)
                auxConnect_name = string[1]
                auxConnect_name = auxConnect_name.replace(" ","")
                connection = auxConnect_name.split(",", 1)
                for uTransaction_out in list_transa:
                    if uTransaction_out.name == (connection[1] + '_transaction'):
                        aux_Transa = uTransaction_out
                        break

                auxPort = Port(auxName, connection[0], auxInstance, aux_Transa, 0)
                auxPort_out.append(auxPort)

            if '}' in line:

                for idx,uComp in enumerate(list_comp):
                    if (uComp.instance == auxComp):
                        auxTransa_comp = uComp.transaction
                        break

                port_comp = Port('rfmtocomp', auxComp, auxInstance, auxTransa_comp, 1)

                auxRfm = Refmod(auxName, auxInstance, auxRefmod_policy, port_comp, auxComp)
                if not auxPort_out:
                    pass
                else:
                    for idx, uConnect in enumerate(auxPort_out):
                        auxRfm.addPortOut(uConnect)

                list_refmod.append(auxRfm)

        for line in tbSplit_agent:

            if 'agent' in line and '=' not in line:
                auxName = ''
                auxInstance = ''

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if 'instance' in line:
                string = line.split("=", 1)
                auxInstance = string[1]
                auxInstance = auxInstance.replace(" ","")

            if 'type' in line:
                string = line.split("=", 1)
                auxType = string[1]
                auxType = auxType.replace(" ","")

            if 'driver_policy' in line:
                string = line.split("=", 1)
                auxDriver_policy = string[1]
                auxDriver_policy = auxDriver_policy.replace(" ","")

            if 'monitor_policy' in line:
                string = line.split("=", 1)
                auxMonitor_policy = string[1]
                auxMonitor_policy = auxMonitor_policy.replace(" ","")

            if 'transaction' in line:
                string = line.split("=", 1)
                auxTransaction_name = string[1]
                auxTransaction_name = auxTransaction_name.replace(" ","")

                for idx,uTransaction in enumerate(list_transa):
                    if (uTransaction.name == (auxTransaction_name + '_transaction')):
                        auxTransaction = uTransaction
                        break

            if 'interface' in line:
                string = line.split("=", 1)
                auxInterface_instance = string[1]
                auxInterface_instance = auxInterface_instance.replace(" ","")
                for idx,uInterface in enumerate(list_interface):
                    if (uInterface.instance == auxInterface_instance):
                        auxInterface = uInterface
                        break

            if 'refmod' in line:
                string = line.split("=", 1)
                auxRefmod_name = string[1]
                auxRefmod_name = auxRefmod_name.replace(" ","")

            if 'comp' in line:
                string = line.split("=", 1)
                auxComp_name = string[1]
                auxComp_name = auxComp_name.replace(" ","")

            if '}' in line:

                auxAgent = Agent(auxName, auxInstance, auxInterface, auxTransaction, auxDriver_policy, auxMonitor_policy, auxType)

                if (auxAgent.type == 'input'):
                    auxAgent.setRefmodConn(auxRefmod_name + '_rfm')
                elif (auxAgent.type == 'output'):
                    auxAgent.setCompConn(auxComp_name)
                else:
                    auxAgent.setRefmodConn(auxRefmod_name + '_rfm')
                    auxAgent.setCompConn(auxComp_name)

                list_agent.append(auxAgent)


        for line in tbSplit_vip:

            if 'vip' in line and '=' not in line:
                auxName = ''
                auxInstance = ''
                auxInterface = ''
                auxFile_package = ''
                auxInclude = []
                auxPort = []
                auxPort_destination = []
                auxPort_transa = []

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if 'instance' in line:
                string = line.split("=", 1)
                auxInstance = string[1]
                auxInstance = auxInstance.replace(" ","")

            if 'interface' in line:
                string = line.split("=", 1)
                auxInterface_instance = string[1]
                auxInterface_instance = auxInterface_instance.replace(" ","")
                for idx,uInterface in enumerate(list_interface):
                    if (uInterface.instance == auxInterface_instance):
                        auxInterface = uInterface
                        break

            if 'file_package' in line:
                string = line.split("=", 1)
                auxFile_package = string[1]
                auxFile_package = auxFile_package.replace(" ","")

            if 'include' in line:
                string = line.split("=", 1)
                auxInclude_name = string[1]
                auxInclude_name = auxInclude_name.replace(" ","")
                auxInclude.append(auxInclude_name)

            if 'tlm_port' in line:
                string = line.split("=", 1)
                auxConnect_name = string[1]
                auxConnect_name = auxConnect_name.replace(" ","")
                connection = auxConnect_name.split(",", 1)
                auxPort.append(connection[0])
                connection2 = connection[1].split(",", 1)
                auxPort_destination.append(connection2[0])
                auxPort_transa.append(connection[1])

            if '}' in line:

                auxVip = Vip(auxName, auxInstance, auxInterface, auxFile_package)
                for idx,uPort in enumerate(auxPort):
                    auxTransa = Transaction(auxPort_transa[idx])
                    port_create = Port(uPort, auxPort_destination[idx], auxInstance, copy.copy(auxTransa), 0)
                    auxVip.addPort(copy.copy(port_create))

                for idx,uInclude in enumerate(auxInclude):
                    auxVip.addInclude(uInclude)

                list_vip.append(copy.copy(auxVip))

        # Creating ENV

        scoreboard = Scoreboard(moduleName, moduleName +'_scb')

        for uComp in list_comp:
            scoreboard.addComp(uComp)

        for uRefmod in list_refmod:
            scoreboard.addRefmod(uRefmod)

        env = Env(moduleName, 'env', [], scoreboard)

        for uAgent in list_agent:
            env.addAgent(uAgent)

        for uVip in list_vip:
            env.addVip(uVip)

        env.writeEnv(self.outputdir)
        env.scoreboard.writeScoreboard(self.outputdir)

        for refmod in env.scoreboard.refmod:
            refmod.writeRefmod(self.outputdir)

        different_agent_name = []
        different_agent = []

        for agent in env.agent:
            if agent.name not in different_agent_name:
                different_agent_name.append(agent.name)
                different_agent.append(agent)
            else:
                pass

        for agent in different_agent:
            agent.writeAgentAll(self.outputdir)

        # Creating Tests and Sequences

        for line in tbSplit_sequence:
            if 'sequence' in line and '=' not in line:
                auxName = 'NONE'

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if 'transaction' in line:
                string = line.split("=", 1)
                auxTransaction_name = string[1]
                auxTransaction_name = auxTransaction_name.replace(" ","")

                for idx,uTransaction in enumerate(list_transa):
                    if (uTransaction.name == (auxTransaction_name + '_transaction')):
                        auxTransaction = uTransaction
                        break

            if 'agent' in line:
                string = line.split("=", 1)
                auxAgent_instance = string[1]
                auxAgent_instance = auxAgent_instance.replace(" ","")

                for idx,uAgent in enumerate(list_agent):
                    if (uAgent.instance == auxAgent_instance):
                        auxAgent = uAgent
                        break

            if '}' in line:
                auxSequence = Sequence(auxName, auxAgent, auxTransaction)
                list_sequence.append(auxSequence)


        auxSequence = []
        for line in tbSplit_test:
            if 'test' in line and '=' not in line:
                auxName = 'NONE'

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if 'sequence' in line:
                string = line.split("=", 1)
                auxSequence_name = string[1]
                auxSequence_name = auxSequence_name.replace(" ","")

                for idx,uSequence in enumerate(list_sequence):
                    if (uSequence.name == (auxSequence_name + '_sequence')):
                        auxSequence.append(uSequence)
                        break

            if '}' in line:
                auxTest= Test(env, auxName)
                for uSequence in auxSequence:
                    auxTest.addSequence(uSequence)

                list_test.append(auxTest)


        for sequence in list_sequence:
            sequence.writeSequence(self.outputdir)

        for test in list_test:
            test.writeTest(self.outputdir)

        Dut = Module(moduleName)

        for uClock in list_clock:
            Dut.addClock(uClock)

        for uReset in list_reset:
            Dut.addReset(uReset)

        for idx,uAgent in enumerate(list_agent):
            Dut.addAgent(uAgent)

        for idx,uVip in enumerate(list_vip):
            Dut.addVip(uVip)

        for uSignal in list_signal:
            Dut.addSignal(uSignal)

        for uTest in list_test:
            Dut.addTest(uTest)

        Dut.addEnv(env)

        Dut.writeWrapper(self.outputdir)
        Dut.writeTop(self.outputdir)
        Dut.writeMakefile(self.outputdir)

        pkg = Package(moduleName)

        for idx,uVip in enumerate(list_vip):
            pkg.addVip(uVip)

        pkg.writePackage(self.outputdir)

        formal = Formal(moduleName)

        for uSignal in list_signal:
            formal.addSignal(uSignal)

        for uClock in list_clock:
            formal.addClock(uClock)

        for uReset in list_reset:
            formal.addReset(uReset)


        formal.writeMakefile(self.outputdir)
        formal.writeTcl(self.outputdir)
        formal.writeVerifModule(self.outputdir)

    def parse_fe(self):
        with open(self.inputfile, 'r') as file:
            tbConfig=file.read()

        tbConfig_Split = "".join([s for s in tbConfig.splitlines(True) if s.strip("\r\n")])

        tbConfig_Split = tbConfig_Split.splitlines()

        tbSplit_signal = []
        tbSplit_clock = []
        tbSplit_reset = []
        tbSplit_module = []
        tbSplit_pdk = []

        for line in tbConfig_Split:
            if 'signal' in line and '=' not in line:
                current_analysis='signal'
            if 'clock' in line and '=' not in line:
                current_analysis='clock'
            if 'reset' in line and '=' not in line:
                current_analysis='reset'
            if 'module' in line and '=' not in line:
                current_analysis='module'
            if 'pdk' in line and '=' not in line:
                current_analysis='pdk'
            if '}' in line and '=' not in line:
                current_analysis=current_analysis

            if current_analysis == 'signal':
                tbSplit_signal.append(line)
            if current_analysis == 'clock':
                tbSplit_clock.append(line)
            if current_analysis == 'reset':
                tbSplit_reset.append(line)
            if current_analysis == 'module':
                tbSplit_module.append(line)
            if current_analysis == 'pdk':
                tbSplit_pdk.append(line)
            if current_analysis == 'NONE':
                pass

        list_signal = []
        list_clock = []
        list_reset = []
        list_pdk_files = []
        list_synth_Script = []

        for line in tbSplit_module:
            if 'module' in line and '=' not in line:
                auxName = ''

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if '}' in line:
                moduleName = auxName

        for line in tbSplit_clock:
            if 'clock' in line and '=' not in line:
                auxName = 'NONE'
                auxPeriod = 'NONE'

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if 'period' in line:
                string = line.split("=", 1)
                auxPeriod = string[1]
                auxPeriod = auxPeriod.replace(" ","")

            if '}' in line:
                auxClock = Clock(auxName, auxPeriod)
                list_clock.append(auxClock)

        for line in tbSplit_reset:
            if 'reset' in line and '=' not in line:
                auxName = 'NONE'
                auxPeriod = 'NONE'
                auxDuration = 'NONE'

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if 'period' in line:
                string = line.split("=", 1)
                auxPeriod = string[1]
                auxPeriod = auxPeriod.replace(" ","")

            if 'duration' in line:
                string = line.split("=", 1)
                auxDuration = string[1]
                auxDuration = auxDuration.replace(" ","")

            if '}' in line:
                auxReset = Reset(auxName, auxPeriod, auxDuration)
                list_reset.append(auxReset)

        for line in tbSplit_signal:
            if 'signal' in line and '=' not in line:
                auxName = 'NONE'
                auxType = 'NONE'
                auxIo = 'NONE'
                auxConnect = 'NONE'

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if 'type' in line:
                string = line.split("=", 1)
                auxType = string[1]
                auxType = auxType.replace(" ","")

            if 'io' in line:
                string = line.split("=", 1)
                auxIo = string[1]
                auxIo = auxIo.replace(" ","")

            if '}' in line:
                auxSignal = Signal(auxName, auxType, auxIo)
                list_signal.append(auxSignal)

        for line in tbSplit_pdk:
            if 'pdk' in line and '=' not in line:
                auxName = 'NONE'
                auxDir = 'NONE'
                auxFile = 'NONE'

            if 'name' in line:
                string = line.split("=", 1)
                auxName = string[1]
                auxName = auxName.replace(" ","")

            if 'dir' in line:
                string = line.split("=", 1)
                auxDir = string[1]
                auxDir = auxDir.replace(" ","")

            if 'file' in line:
                string = line.split("=", 1)
                auxFile = string[1]
                auxFile = auxFile.replace(" ","")
                list_pdk_files.append(auxFile)

            if '}' in line:
                auxSynth = Synth(moduleName)
                auxSynth.setPDK(auxDir)
                for file_s in list_pdk_files:
                    auxSynth.addPDKFile(file_s)

                list_synth_Script.append(auxSynth)


        Dut = Module(moduleName)

        for uClock in list_clock:
            Dut.addClock(uClock)

        for uReset in list_reset:
            Dut.addReset(uReset)

        for uSignal in list_signal:
            Dut.addSignal(uSignal)

        Dut.writeModule(self.outputdir)

        for uSynth in list_synth_Script:
            uSynth.writeTcl(self.outputdir)
            uSynth.writeMakefile(self.outputdir)

        formal = Formal(moduleName)

        formal.writeMakefile(self.outputdir)



def display_title_bar():

    # Clears the terminal screen, and displays a title bar.
    print(Fore.BLUE + "##################################################")
    print(Fore.BLUE + "           ▀▄ ▄▀  █▀▄▀█  █▀▀▀  █▄  █           ")
    print(Fore.BLUE + "             █    █ █ █  █▀▀▀  █ █ █           ")
    print(Fore.BLUE + "           ▄▀ ▀▄  █   █  █▄▄▄  █  ▀█           ")
    print(Fore.BLUE + "                                               ")
    print(Fore.BLUE + "                █     █▀▀█  █▀▀█               ")
    print(Fore.BLUE + "                █     █▄▄█  █▀▀▄               ")
    print(Fore.BLUE + "                █▄▄█  █  █  █▄▄█               ")
    print(Fore.BLUE + "##################################################")
    print(Fore.BLUE + "##################################################")
    print(Fore.BLUE + "# This script is used to automate generation of   ")
    print(Fore.BLUE + "# Reference flow for hardware projects in Frontend")
    print(Fore.BLUE + "# and Verification.                               ")
    print(Fore.BLUE + "##################################################")
    print(Fore.BLUE + "##################################################")
    print(Fore.BLUE + "# Aurora Integrated Reference Flow Generation ")
    print(Fore.BLUE + "# Author: Jose Iuri Barbosa de Brito            ")
    print(Fore.BLUE + "# MIT License                                   ")
    print(Fore.BLUE + "# Copyright: Copyright (c) 2020, XMEN Lab - Universidade Federal de Campina Grande")
    print(Fore.BLUE + "# Credits: ")
    print(Fore.BLUE + "# Version: 0.2")
    print(Fore.BLUE + "# Maintainer: Jose Iuri Barbosa de Brio")
    print(Fore.BLUE + "# Email: jose.brito@embedded.ufcg.edu.br")
    print(Fore.BLUE + "# Status: In Progress")
    print(Fore.BLUE + "##################################################\n\n")

class CapitalisedHelpFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = 'Usage: '
        return super(CapitalisedHelpFormatter, self).add_usage(
            usage, actions, groups, prefix)

    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ', '.join(action.option_strings) + ' ' + args_string

def main(argv):

    inputfile = ''
    outputdir = './'

    mode = ''

    help_s = """Aurora Integrated Workflow v0.2 (c) Copyright 2020, XMEN Lab - Universidade Federal de Campina Grande"""


    parser_arg = argparse.ArgumentParser(description=help_s, allow_abbrev=False, formatter_class=CapitalisedHelpFormatter)

    parser_arg._positionals.title = 'Positional arguments'

    parser_arg._optionals.title = 'Optional arguments'

    parser_arg.add_argument("mode", type=str, help="Choose the mode for generation (verif|fe)")

    parser_arg.add_argument("-i","--ifile", type=str, required=True, help="Select the input configuration file", metavar="input_file")

    parser_arg.add_argument("-o","--odir", type=str, required=False, help="Select the output directory", default='./', metavar="output_dir")

    args = parser_arg.parse_args()
    mode = args.mode
    inputfile = args.ifile
    outputdir = args.odir

    if (mode == 'verif') :

        verification_path =  Path(outputdir)

        display_title_bar()

        verification_path = verification_path / 'verification'
        Path(verification_path).mkdir(parents=True, exist_ok=True)
        doc_path = verification_path / 'docs'
        Path(doc_path).mkdir(parents=True, exist_ok=True)
        tb_path = verification_path / 'tb'
        Path(tb_path).mkdir(parents=True, exist_ok=True)

        Path(verification_path / 'logs').mkdir(parents=True, exist_ok=True)
        Path(verification_path / 'reports').mkdir(parents=True, exist_ok=True)
        Path(verification_path / 'scripts').mkdir(parents=True, exist_ok=True)

        Path(verification_path / 'scripts' / 'gatesim').mkdir(parents=True, exist_ok=True)
        Path(verification_path / 'scripts' / 'rtlsim').mkdir(parents=True, exist_ok=True)
        Path(verification_path / 'scripts' / 'verif_manager').mkdir(parents=True, exist_ok=True)
        Path(verification_path / 'scripts' / 'formal').mkdir(parents=True, exist_ok=True)

        Path(verification_path / 'src').mkdir(parents=True, exist_ok=True)
        Path(verification_path / 'vplan').mkdir(parents=True, exist_ok=True)
        Path(verification_path / 'workspace').mkdir(parents=True, exist_ok=True)

        Path(verification_path / 'formal').mkdir(parents=True, exist_ok=True)
        Path(verification_path / 'formal' / 'properties').mkdir(parents=True, exist_ok=True)

        print(Fore.BLUE + "# GENERATING DIRECTORIES IN " + str(verification_path) + "\n")
        print(Fore.BLUE + "##################################################\n\n")

        outputdir = outputdir + '/verification/tb'
        uParser = Parser('Parser', inputfile, outputdir)

        print(Fore.BLUE + "# GENERATING FILES \n")
        print(Fore.BLUE + "##################################################\n\n")
        uParser.parse_verif()

    elif (mode == 'fe'):

        frontend_path =  Path(outputdir)

        display_title_bar()

        frontend_path = frontend_path / 'frontend'
        Path(frontend_path).mkdir(parents=True, exist_ok=True)
        doc_path = frontend_path / 'docs'
        Path(doc_path).mkdir(parents=True, exist_ok=True)


        Path(frontend_path / 'logs').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'logs' / 'gatesim').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'logs' / 'lec').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'logs' / 'power').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'logs' / 'rtlsim').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'logs' / 'synth_logic').mkdir(parents=True, exist_ok=True)

        Path(frontend_path / 'reports').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'reports' / 'gatesim').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'reports' / 'lec').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'reports' / 'power').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'reports' / 'rtlsim').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'reports' / 'synth_logic').mkdir(parents=True, exist_ok=True)

        Path(frontend_path / 'scripts').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'scripts' / 'gatesim').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'scripts' / 'lec').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'scripts' / 'power').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'scripts' / 'rtlsim').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'scripts' / 'synth_logic').mkdir(parents=True, exist_ok=True)

        Path(frontend_path / 'parasitics').mkdir(parents=True, exist_ok=True)

        Path(frontend_path / 'rtl').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'rtl' / 'src').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'rtl' / 'tb').mkdir(parents=True, exist_ok=True)

        Path(frontend_path / 'software').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'software' / 'api').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'software' / 'apps').mkdir(parents=True, exist_ok=True)

        Path(frontend_path / 'structural').mkdir(parents=True, exist_ok=True)

        Path(frontend_path / 'switching').mkdir(parents=True, exist_ok=True)

        Path(frontend_path / 'timing').mkdir(parents=True, exist_ok=True)

        Path(frontend_path / 'workspace').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'workspace' / 'gatesim').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'workspace' / 'lec').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'workspace' / 'power').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'workspace' / 'rtlsim').mkdir(parents=True, exist_ok=True)
        Path(frontend_path / 'workspace' / 'synth_logic').mkdir(parents=True, exist_ok=True)

        print(Fore.BLUE + "# GENERATING DIRECTORIES IN " + str(frontend_path) + "\n")
        print(Fore.BLUE + "################################################\n\n")

        outputdir = outputdir + '/frontend'

        print(Fore.BLUE + "# GENERATING FILES \n")
        print(Fore.BLUE + "################################################\n\n")

        uParser = Parser('Parser', inputfile, outputdir)
        uParser.parse_fe()

    else:
        pass
        # print (help_s)
        # sys.exit(2)


if __name__== "__main__" :
    main(sys.argv[1:])
