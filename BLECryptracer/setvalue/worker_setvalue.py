"""
    Copyright (C) 2018 projectbtle@tutanota.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import sys
import fnmatch
import re
import collections
import timeit
import itertools
from time import sleep
from multiprocessing import JoinableQueue
from androguard.misc import *
from androguard.core import *
from androguard import session

# Custom constants.
METHOD_INTERNAL = 0
METHOD_EXTERNAL = 1
METHOD_EMPTY = 2

# Dalvik opcodes and operand indices.
INVOKE_OPCODES = [0x6E, 0x6F, 0x70, 0x71, 0x72, 0x74, 0x75, 0x76, 0x77, 0x78]
INVOKE_RANGE_OPCODES = [0x74, 0x75, 0x76, 0x77, 0x78]
INVOKE_VIRTUAL_OPCODES = [0x6E, 0x74]
INVOKE_SUPER_OPCODES = [0x6F, 0x75]
INVOKE_DIRECT_OPCODES = [0x70, 0x76]
INVOKE_STATIC_OPCODES = [0x71, 0x77]
INVOKE_INTERFACE_OPCODES = [0x72, 0x78]
CONST_DECL_OPCODES = [0x12, 0x13, 0x14, 0x15,
                      0x16, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C]
CONST_OPERAND_INDEX = 0
AGET_OPCODES = [0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A]
AGET_OPERAND_INDEX = 0
AGET_OPERAND_SOURCE_INDEX = 1
SGET_OPCODES = [0x60, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66]
SGET_OPERAND_INDEX = 0
SGET_OPERAND_SOURCE_INDEX = 1
IGET_OPCODES = [0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58]
IGET_OPERAND_INDEX = 0
IGET_OPERAND_SOURCE_INDEX = 2
APUT_OPCODES = [0x4B, 0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x51]
APUT_OPERAND_INDEX = 1
APUT_OPERAND_SOURCE_INDEX = 0
SPUT_OPCODES = [0x67, 0x68, 0x69, 0x6A, 0x6B, 0x6C, 0x6D]
SPUT_OPERAND_SOURCE_INDEX = 0
SPUT_OPERAND_INDEX = 1
IPUT_OPCODES = [0x59, 0x5A, 0x5B, 0x5C, 0x5D, 0x5E, 0x5F]
IPUT_OPERAND_FIELD_INDEX = 2
IPUT_OPERAND_SOURCE_INDEX = 0
GET_TO_PUT_OFFSET = 0x7
PUT_TO_GET_OFFSET = -0x7
GOTO_OPCODES = [0x28, 0x29, 0x2A]
GOTO_OPERAND_INDEX = 0
MOVE_RESULT_OPCODES = [0x0A, 0x0B, 0x0C]
MOVE_RESULT_OPERAND_INDEX = 0
MOVE_OPCODES = [0x01, 0x02, 0x05, 0x07, 0x08]
MOVE_OPERAND_INDEX = 0
MOVE_OPERAND_SOURCE_INDEX = 1
NEW_ARRAY_OPCODES = [0x23]
NEW_ARRAY_OPERAND_INDEX = 0
NEW_INSTANCE_OPCODES = [0x22]
NEW_INSTANCE_OPERAND_INDEX = 0
FILLED_ARRAY_OPCODES = [0x24, 0x25]
RETURN_OPCODES = [0x0F, 0x10, 0x11]
RETURN_OPERAND = 0
COMPARE_OPCODES = [0x2D, 0x2E, 0x2F, 0x30, 0x31]
COMPARE_OPERAND_INDEX = 0
COMPARE_OPERAND_SOURCE1_INDEX = 1
COMPARE_OPERAND_SOURCE2_INDEX = 2
CONDITIONAL_OPCODES = [0x32, 0x33, 0x34, 0x35,
                       0x36, 0x37, 0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D]
CONDITIONAL_OPERAND_INDEX = 0
CONDITIONAL_DESTINATION = 1
OPERATION_OPCODES = xrange(0x7B, 0xE2)
OPERATION_OPERAND_INDEX = 0
OPERATION_OPERAND_SOURCE_INDEX = 1

# Access flags.
ACCESS_FLAG_PUBLIC = 0x1
ACCESS_FLAG_PRIVATE = 0x2
ACCESS_FLAG_PROTECTED = 0x4
ACCESS_FLAG_STATIC = 0x8
ACCESS_FLAG_FINAL = 0x10
ACCESS_FLAG_SYNC = 0x20
ACCESS_FLAG_BRIDGE = 0x40
ACCESS_FLAG_VARARGS = 0x80
ACCESS_FLAG_NATIVE = 0x100
ACCESS_FLAG_INTERFACE = 0x200
ACCESS_FLAG_ABSTRACT = 0x400
ACCESS_FLAG_STRICT = 0x800
ACCESS_FLAG_SYNTH = 0x1000
ACCESS_FLAG_ENUM = 0x4000
ACCESS_FLAG_UNUSED = 0x8000
ACCESS_FLAG_CONSTRUCTOR = 0x10000
ACCESS_FLAG_SYNC2 = 0x20000

# Operand type.
OPERAND_REGISTER = 0
OPERAND_LITERAL = 1
OPERAND_RAW = 2
OPERAND_OFFSET = 3
OPERAND_KIND = 0x100

# Confidence levels.
CONFIDENCE_LEVEL_HIGH = "High"
CONFIDENCE_LEVEL_MED = "Medium"
CONFIDENCE_LEVEL_LOW = "Low"

# Libraries of interest.
CRYPTO_PACKAGES = ["Ljavax/crypto", "Ljava/security"]
NET_PACKAGES = ["Ljava/net/URLConnection;",
                "Ljava/net/HttpURLConnection;", 
                "Ljavax/net/ssl/HttpsURLConnection;"]
#################################

# Timing-related.
MAX_RUNTIME = 1800

# Related to the instruction queue.
QUEUE_APPEND = 1
QUEUE_PREPEND = 2


class WorkerSetvalue():
    def __init__(self):        
        # Output values.
        self.found_crypto = False
        self.setvalue = False
        self.crypto = False
        self.net_use = False
        self.location_setvalue = None
        self.location_ble_crypto = None
        self.confidence_level = CONFIDENCE_LEVEL_HIGH

        # Keep track of methods.
        self.stored_methods = []  # Methods to try at Confidence Level "Medium"
        self.source_methods = []  # Methods to try at Confidence Level "Low"
        self.all_methods = []
        self.stored_instructions = []

        # Stats.
        self.num_ble_methods = 0
        self.all_ble_methods = ""
    
        self.start_time = None 
        
        # Mainly used to prevent excessive recursion.
        self.instruction_queue = collections.deque()
        
        # Initialise object list.
        self.named_object_list = []
        self.nonnamed_object_list = []
        self.initialise_named_object_list()
        self.initialise_nonnamed_object_list()
        
    def main(self, in_queue, out_queue, process_id):
        """Obtain the file of an APK and initate processing.
        
        Keyword arguments:
        in_queue -- the queue from which to obtain the path to the APK.
        out_queue -- the queue to which to put the output string.
        process_id -- the ID assigned to this worker process by the main.
        """
        
        # Get APK from main process.
        for queue_input in iter(in_queue.get, 'STOP'):
            filename = str(queue_input).strip()
            print "\n\n[MAIN] Thread {1} - Running AnalyzeAPK against file {0}".format(
                filename, str(process_id))

            # Reset values for each new APK.
            self.androguard_a = None
            self.androguard_d = None
            self.androguard_dx = None
            self.start_time = timeit.default_timer()
            self.found_crypto = False
            self.setvalue = False
            self.crypto = False
            self.net_use = False
            self.location_setvalue = None
            self.location_ble_crypto = None
            self.stored_methods = []
            self.source_methods = []
            self.all_methods = []
            self.stored_instructions = []
            self.confidence_level = CONFIDENCE_LEVEL_HIGH
            self.num_ble_methods = 0
            self.all_ble_methods = ""
            self.instruction_queue.clear()

            # Get default session.
            sess = get_default_session()

            # Try Androguard's AnalyzeAPK() against the APK.
            # If it fails, then we cannot proceed with this APK,
            # so move on to next.
            try:
                self.androguard_a, self.androguard_d, self.androguard_dx = AnalyzeAPK(filename, session=sess)
            except Exception as e:
                runtime = self.elapsed_time()
                out_queue.put(filename 
                                  + "," 
                                  + "Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error," 
                                  + str(runtime) 
                                  + "\n" 
                                  + "err_divAnalyzeAPK error. " 
                                  + str(e) 
                                  + "\n\n")
                in_queue.task_done()
                # Reset the session for the next analysis.
                # Otherwise, memory consumption builds up over time (Androguard 3.1.0).
                sess.reset()
                sleep(0.1)
                continue

            # If, for some reason, even after AnalyzeAPK succeeded,
            # if any of the analysis objects are None (null),
            # then move to next APK.
            if ((self.androguard_a == None) or 
                    (self.androguard_d == None) or 
                    (self.androguard_dx == None)):
                runtime = self.elapsed_time()
                out_queue.put(filename 
                                  + "," 
                                  + "Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error," 
                                  + str(runtime) 
                                  + "\n" 
                                  + "err_diva, d, or dx is Null.\n\n")
                in_queue.task_done()
                sess.reset()
                sleep(0.1)
                continue

            apk_package = self.androguard_a.get_package()

            # If AnalyzeAPK succeeded, and none of the analysis file are None, then proceed.
            try:
                self.initial_checks()
                if self.found_crypto != True:
                    pass
                runtime = self.elapsed_time()
                out_queue.put(filename 
                                  + "," 
                                  + apk_package 
                                  + "," + str(self.setvalue) 
                                  + "," + str(self.crypto) 
                                  + "," + str(self.found_crypto) 
                                  + "," + self.confidence_level 
                                  + "," + str(self.net_use) 
                                  + "," + str(self.location_setvalue) 
                                  + "," + str(self.location_ble_crypto) 
                                  + "," + str(self.num_ble_methods) 
                                  + "," + str(self.all_ble_methods) 
                                  + "," + str(runtime) 
                                  + "\n")
                in_queue.task_done()
                sess.reset()
                sleep(0.1)
                continue
            except Exception as e:
                runtime = self.elapsed_time()
                out_queue.put(filename 
                                  + "," + apk_package 
                                  + "," + "Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error"
                                  ",Error," 
                                  + str(runtime) 
                                  + "\n" 
                                  + "err_div" + str(e) 
                                  + "\n\n")
                in_queue.task_done()
                sess.reset()
                sleep(0.1)
                continue

                
    def initial_checks(self):
        """Obtain list of prioritised calls to getValue variants. """
        
        # First get paths from any methods calling BluetoothGattCharacteristic->setValue()
        ext_methods = self.androguard_dx.find_methods(
            "Landroid/bluetooth/BluetoothGattCharacteristic;", "setValue", ".")
        setvalue_methods = []
        for ext_method in ext_methods:
            for element in ext_method.get_xref_from():
                if element[1] not in setvalue_methods:
                    setvalue_methods.append(element[1])
                    # Keep track of all methods that call setValue.
                    ble_method_name = element[1].get_class_name(
                    ) + element[1].get_name() + "".join(element[1].get_descriptor().split()) + "\\"
                    self.all_ble_methods = self.all_ble_methods + ble_method_name
        ext_methods = None

        # If there are no calls to setValue, then there is nothing to analyse.
        if setvalue_methods == []:
            return
        else:
            self.setvalue = True
            self.num_ble_methods = len(setvalue_methods)

        # Find whether crypto is used anywhere within the APK.
        # We can just move onto the next APK if there is no crypto.
        crypto_methods = []
        crypto_calls = []
        for crypto_pkg in CRYPTO_PACKAGES:
            search_crypto = crypto_pkg + "/."
            crypto_methods.extend(self.androguard_dx.find_methods(search_crypto, ".", "."))
        for crypto_method in crypto_methods:
            for cryptoelement in crypto_method.get_xref_from():
                crypto_calls.append(cryptoelement[1])
        if crypto_calls == []:
            return
        else:
            self.crypto = True

        crypto_methods = None
        crypto_calls = None

        # Find whether connectivity functions are used at all within the APK.
        net_methods = []
        net_calls = []
        for net_pkg in NET_PACKAGES:
            search_net = net_pkg
            net_methods.extend(self.androguard_dx.find_methods(search_net, ".", "."))
        for net_method in net_methods:
            for netelement in net_method.get_xref_from():
                net_calls.append(netelement[1])
        if len(net_calls) > 0:
            self.net_use = True

        net_methods = None
        net_calls = None

        # Prioritise the methods and then call tracing function.
        prioritised_setvalue_methods = None
        if len(setvalue_methods) == 1:
            prioritised_setvalue_methods = setvalue_methods
        else:
            prioritised_setvalue_methods = self.prioritise_methods(setvalue_methods)
        self.gatt_trace(prioritised_setvalue_methods)


    def prioritise_methods(self, setvalue_methods):
        """Return list of prioritised methods.
        
        Keyword arguments:
        getvalue_methods -- list of unprioritised methods.
        """
        
        package = self.androguard_a.get_package()
        split_package = package.split(".")
        len_package_name = len(split_package)

        intermediate_methods = []
        for setvalue_method in setvalue_methods:
            full_method_classname = setvalue_method.get_class_name()
            method_classname = full_method_classname[1:]
            split_classname = method_classname.split("/")
            len_classname = len(split_classname)
            compare_len = len_package_name
            if len_classname < len_package_name:
                compare_len = len_classname

            dist = 0
            for i in range(0, compare_len):
                if split_package[i] == split_classname[i]:
                    dist += 1
                else:
                    break
            intermediate_methods.append((dist, setvalue_method))

        sorted_methods = sorted(intermediate_methods,
                                key=lambda mtd: mtd[0], reverse=True)
        intermediate_methods = None
        output_methods = []
        for sorted_method in sorted_methods:
            output_methods.append(sorted_method[1])

        return output_methods


    def gatt_trace(self, setvalue_methods):
        # Start trace for each method that calls setValue().
        for path_idx, method in enumerate(setvalue_methods):
            # If we have found crypto use with BLE in one of the previous iterations, then stop.
            if self.found_crypto == True:
                return
            # If we've run out of time, then stop analysing this APK and move onto the next.
            if self.time_check() == True:
                return

            self.location_setvalue = str(method.get_class_name()) + \
                str(method.get_name()) + str(method.get_descriptor())

            # Get the calling method.
            search_string = "Landroid/bluetooth/BluetoothGattCharacteristic;->setValue"
            # The setValue method is an instance method which takes an instance and a byte array as input.
            setvalue_invoke_operand = 1
            # Identify the type of register that holds the byte array input to setValue.
            # The register type determines the trace method (internal or external).
            id_reg = self.identify_register(
                method, INVOKE_OPCODES, search_string, setvalue_invoke_operand)
            if id_reg == []:
                continue
            else:
                for individual_method in id_reg:
                    register_type = individual_method[0]
                    index = individual_method[1]
                    self.add_to_queue([self.decide_trace_route, method,
                                index, register_type], QUEUE_PREPEND)
                    self.instruction_scheduler()

        # Reset to reduce items in memory.
        setvalue_methods = None

        if self.found_crypto == True:
            return
        if self.time_check() == True:
            return

        # Start the analysis again with the stored methods.
        # False positives may arise due to this.
        self.confidence_level = CONFIDENCE_LEVEL_MED
        # Clear the instruction queue.
        self.instruction_queue.clear()
        while self.stored_methods != []:
            if self.found_crypto == True:
                return
            if self.time_check() == True:
                return
            method_tuples = self.stored_methods.pop()
            tuples = []
            for method_tuple in method_tuples:
                tuples.append(method_tuple)
            self.add_to_queue(tuples, QUEUE_APPEND)
            self.instruction_scheduler()

        if self.found_crypto == True:
            return
        if self.time_check() == True:
            return

        # Final search through all encountered methods. Potential for false positives.
        self.confidence_level = CONFIDENCE_LEVEL_LOW
        self.instruction_queue.clear()
        for source_method in self.source_methods:
            if self.found_crypto == True:
                return
            if self.time_check() == True:
                return
            self.add_to_queue([self.trace_through_method, source_method], QUEUE_APPEND)
            self.instruction_scheduler()


    def add_to_queue(self, queueItem, insertionType=QUEUE_APPEND):
        """Add a function object to queue.
        
        Keyword arguments:
        queueItem -- function block
        insertionType -- QUEUE_APPEND or QUEUE_PREPEND
        """
        
        # If the same analysis has already been done, then don't add it to the list.
        if str(queueItem) in self.all_methods:
            return
        else:
            # Keep track of methods, so that we don't repeat.
            self.all_methods.append(str(queueItem))

        # Append or prepend as required.
        if insertionType == QUEUE_APPEND:
            self.instruction_queue.append(queueItem)
        elif insertionType == QUEUE_PREPEND:
            self.instruction_queue.appendleft(queueItem)
        else:
            pass
        return


    def instruction_scheduler(self):
        """Call queue handler as long as queue is not empty. """
        
        while (self.found_crypto != True) and (self.time_check() != True) and (self.instruction_queue):
            self.handle_queue()


    def handle_queue(self):
        """Pop first function object and execute. """
        
        function_block = self.instruction_queue.popleft()
        # Add the method to a list for final analysis (if crypto is not found before then).
        method_item = function_block[1]
        if method_item not in self.source_methods:
            self.source_methods.append(method_item)
        # Execute the method with the provided arguments.
        function_ref = function_block[0]
        function_block.remove(function_ref)
        function_ref(*function_block)


    def decide_trace_route(self, method, index, register_type):
        # Identify whether this method takes an instance as first parameter.
        # Static methods do not. Instance methods do.
        isThis = None
        try:
            method.get_instructions()
            method_access_flags = method.get_access_flags()
            if (ACCESS_FLAG_STATIC & method_access_flags) == ACCESS_FLAG_STATIC:
                isThis = False
            else:
                isThis = True
        except:
            isThis = None

        # Identify path to take.
        if (register_type == "p0") and (isThis == True):
            # Identify calls to <init>
            self.add_to_queue([self.trace_init, method], QUEUE_PREPEND)
        elif (register_type[0] == "p") and (register_type[1] != "0"):
            self.add_to_queue([self.trace_external, method,
                        register_type], QUEUE_PREPEND)
        elif register_type[0] == "v":
            self.add_to_queue([self.trace_internal_reverse, method,
                        index, register_type], QUEUE_PREPEND)
        else:
            pass
        return

        
    def identify_register(self, method, opcodes, search_term, register_idx=-1):
        """Return argument register and instruction index for instruction satisfying search term.
        
        Keyword arguments:
        method -- the method of interest
        opcodes -- array of opcodes
        search_term -- the actual search term to look for within instruction output.
        register_idx -- register index
        """
        
        argument_register_name = ""
        index = -1
        output = []
        if not isinstance(opcodes, list):
            opcodes = [opcodes]
        (num_registers, num_local_registers,
         num_param_registers) = self.find_number_of_registers(method)
        # Get the dalvik instructions.
        list_instructions = list(method.get_instructions())
        # Go through the instructions to find the required method.
        for index, instruction in enumerate(list_instructions):
            operands = None
            last_operand = None
            argument_register = None
            if (instruction.get_op_value() in opcodes):
                operands = instruction.get_operands(0)
                last_operand = "".join(operands[len(operands)-1][2].split())
                search_term_joined = "".join(search_term.split())
                if search_term_joined in last_operand:
                    # Figure out which type of register is used to carry the argument to the function 
                    #  (this will determine whether we should trace within the current method, or via function call).
                    # Hack for the case where invoke doesn't have "this" as argument. (This should not be necessary now).
                    if (instruction.get_op_value() in INVOKE_OPCODES) and (register_idx == (len(operands)-1)):
                        argument_register = operands[register_idx-1][1]
                    else:
                        argument_register = operands[register_idx][1]
                    argument_register_name = self.identify_register_type(
                        num_local_registers, argument_register)
                    if (argument_register_name != "") and (index != -1):
                        output.append([argument_register_name, index])
                        argument_register_name = ""
                        index = -1
        return output


    def find_number_of_registers(self, method):
        """Return numbers for all, local and parameter registers for a method.
        
        Keyword arguments:
        method -- method of interest.
        """
        
        # Find number of registers.
        num_registers = method.code.get_registers_size()
        num_parameter_registers = method.code.get_ins_size()
        num_local_registers = num_registers - num_parameter_registers
        return(num_registers, num_local_registers, num_parameter_registers)


    def identify_register_type(self, num_local_registers, argument_register):
        register_name = None
        if argument_register < num_local_registers:
            register_name = "v" + str(argument_register)
        elif argument_register == num_local_registers:
            register_name = "p0"
        else:
            register_num = argument_register - num_local_registers
            register_name = "p" + str(register_num)
        return register_name


    def trace_internal_reverse(self, method, index, register_type, end_index=0):
        register_id = int(register_type[1:])
        instructions = method.get_instructions()
        list_instructions = list(instructions)
        num_instructions = len(list_instructions)

        # We are backtracing, so we need to reverse the order of the instructions.
        reversed_instructions = reversed(list_instructions)

        # Save some memory.
        instructions = None
        list_instructions = None

        # The index from which to start the search
        start_idx = num_instructions - index

        (num_registers, num_local_registers,
         num_param_registers) = self.find_number_of_registers(method)

        # Store method for further analysis if no crypto is found in the initial stages.
        for idx, instruction in enumerate(reversed_instructions):
            if self.found_crypto == True:
                return
            if self.time_check() == True:
                return

            # Skip the instructions that occur after the instruction of interest is called
            #  i.e., the first instructions in the reversed list),
            #  since we only want to check what happens to the register value *before* the instruction of interest.
            if idx < start_idx:
                continue

            if (end_index != 0) and (idx == end_index):
                # End of branch or search list reached.
                return

            instr_op_value = instruction.get_op_value()
            operands = instruction.get_operands(0)
                
            # Check if the register of interest is present among the operands.
            for i in range(0, len(operands)):
                if (operands[i][0] == OPERAND_REGISTER) and (operands[i][1] == register_id):                    
                    # Test for different ways in which the register could have been assigned a value.
                    #  The checks on i are to ensure that the register of interest is in the correct parameter position.
                    # ==============================================================
                    if (instr_op_value in CONST_DECL_OPCODES) and (i == CONST_OPERAND_INDEX):
                        # If a register has been initialised with a const opcode,
                        # then no cryptographic processing can have been applied to it.
                        # We can stop this run of the trace.
                        return
                    # ==============================================================
                    elif (instr_op_value in NEW_ARRAY_OPCODES) and (i == NEW_ARRAY_OPERAND_INDEX):
                        # If a register has been initialised with a new-array opcode,
                        # then no cryptographic processing can have been applied to it.
                        # We can stop this run of the trace.
                        return
                    # ==============================================================
                    elif (instr_op_value in NEW_INSTANCE_OPCODES) and (i == NEW_INSTANCE_OPERAND_INDEX):
                        # If a register is a new instance of a class,
                        # then check whether that class is related to the crypto-libraries in any way.
                        isCrypto = False
                        isCrypto = self.crypto_search(instruction.get_output(), method)
                        if isCrypto == True:
                            return
                        return
                    # ==============================================================
                    elif (instr_op_value in INVOKE_OPCODES):
                        # If the register is used as input when invoking an <init> method,
                        # then check whether that method is related to crypto.
                        isCrypto = False
                        isCrypto = self.crypto_search(instruction.get_output(), method)
                        if isCrypto == True:
                            return

                        # If the method is <init>, trace the other inputs to the method as well,
                        # but with Medium confidence level.
                        for input_register_idx, input_reg in enumerate(operands):
                            if (input_register_idx != i) and (operands[input_register_idx][0] == OPERAND_REGISTER):
                                input_register_num = operands[input_register_idx][1]
                                input_register_name = self.identify_register_type(
                                    num_local_registers, input_register_num)
                                if self.confidence_level == CONFIDENCE_LEVEL_HIGH:
                                    if (self.decide_trace_route, method, num_instructions-idx-1, input_register_name) not in self.stored_methods:
                                        self.stored_methods.append(
                                        (self.decide_trace_route, method, num_instructions-idx-1, input_register_name))
                                else:
                                    self.add_to_queue([self.decide_trace_route, method,
                                                num_instructions-idx-1, input_register_name], QUEUE_APPEND)
                    # ==============================================================
                    elif (instr_op_value in OPERATION_OPCODES) and (i == OPERATION_OPERAND_INDEX):
                        # If the register holds the output of an arithmetic or logic operation,
                        # then trace the source register.
                        operation_source_register = operands[OPERATION_OPERAND_SOURCE_INDEX][1]
                        operation_source_register_name = self.identify_register_type(
                            num_local_registers, operation_source_register)
                        if operation_source_register_name[0] == "p":
                            self.add_to_queue([self.decide_trace_route, method,
                                        idx, operation_source_register_name], QUEUE_PREPEND)
                        elif operation_source_register_name[0] == "v":
                            self.add_to_queue([self.decide_trace_route, method, num_instructions -
                                        idx-1, operation_source_register_name], QUEUE_PREPEND)
                        return
                    # ==============================================================
                    elif (instr_op_value in AGET_OPCODES) and (i == AGET_OPERAND_INDEX):
                        # If the register value is a result of an aget, then trace the source register.
                        aget_source_register = operands[AGET_OPERAND_SOURCE_INDEX][1]
                        aget_source_register_name = self.identify_register_type(
                            num_local_registers, aget_source_register)
                        if aget_source_register_name[0] == "p":
                            self.add_to_queue([self.decide_trace_route, method,
                                        idx, aget_source_register_name], QUEUE_PREPEND)
                        elif aget_source_register_name[0] == "v":
                            self.add_to_queue([self.decide_trace_route, method,
                                        num_instructions-idx-1, aget_source_register_name], QUEUE_PREPEND)
                        return
                    # ==============================================================
                    elif (instr_op_value in SGET_OPCODES) and (i == SGET_OPERAND_INDEX):
                        # If the register value is a result of an sget, then trace any sput operations for the field.
                        sget_source_instance_field = operands[SGET_OPERAND_SOURCE_INDEX][2]
                        # If the instance field is to do with crypto, then end.
                        isCrypto = False
                        isCrypto = self.crypto_search(
                            str(sget_source_instance_field), method)
                        if isCrypto == True:
                            return

                        # If the field isn't directly to do wth crypto,
                        # find methods that make use of this field.
                        all_field_writes = []
                        all_field_reads = []
                        field_analysis = self.find_field_analysis_objects(sget_source_instance_field)
                        for single_field in field_analysis:
                            list_field_write = list(single_field.xrefwrite)
                            for list_field_write_item in list_field_write:
                                if list_field_write_item[1] not in all_field_writes:
                                    all_field_writes.append(
                                        list_field_write_item[1])
                            list_field_read = list(single_field.xrefread)
                            for list_field_read_item in list_field_read:
                                if list_field_read_item[1] not in all_field_reads:
                                    all_field_reads.append(list_field_read_item[1])
                        for list_field_write_element in all_field_writes:
                            write_field_method = list_field_write_element
                            sput_opcode = instr_op_value + GET_TO_PUT_OFFSET
                            id_reg = self.identify_register(
                                write_field_method, sput_opcode, sget_source_instance_field, SPUT_OPERAND_SOURCE_INDEX)
                            if id_reg != []:
                                for individual_method in id_reg:
                                    register_type = individual_method[0]
                                    index = individual_method[1]
                                    self.add_to_queue(
                                        [self.decide_trace_route, write_field_method, index, register_type], QUEUE_APPEND)
                        for list_field_read_element in all_field_reads:
                            read_field_method = list_field_read_element
                            id_reg = self.identify_register(
                                read_field_method, instr_op_value, sget_source_instance_field, SGET_OPERAND_INDEX)
                            if id_reg != []:
                                for individual_method in id_reg:
                                    register_type = individual_method[0]
                                    index = individual_method[1]
                                    self.add_to_queue(
                                        [self.trace_register_basic, read_field_method, index, register_type], QUEUE_APPEND)
                        return
                    # ==============================================================
                    elif (instr_op_value in IGET_OPCODES) and (i == IGET_OPERAND_INDEX):
                        # If the register value is the result of an iget, then trace any iput operations for the field.
                        get_source_instance_field = operands[IGET_OPERAND_SOURCE_INDEX][2]
                        # If the instance field is to do with crypto, then end.
                        isCrypto = False
                        isCrypto = self.crypto_search(
                            str(get_source_instance_field), method)
                        if isCrypto == True:
                            return

                        # If the field isn't directly to do wth crypto:
                        # Find methods that make use of this field.
                        all_field_writes = []
                        all_field_reads = []
                        field_analysis = self.find_field_analysis_objects(get_source_instance_field)
                        for single_field in field_analysis:
                            list_field_write = list(single_field.xrefwrite)
                            for list_field_write_item in list_field_write:
                                if list_field_write_item[1] not in all_field_writes:
                                    all_field_writes.append(
                                        list_field_write_item[1])
                            list_field_read = list(single_field.xrefread)
                            for list_field_read_item in list_field_read:
                                if list_field_read_item[1] not in all_field_reads:
                                    all_field_reads.append(list_field_read_item[1])
                        for list_field_write_element in all_field_writes:
                            iput_opcode = instr_op_value + GET_TO_PUT_OFFSET
                            id_reg = self.identify_register(
                                list_field_write_element, iput_opcode, get_source_instance_field, IPUT_OPERAND_SOURCE_INDEX)
                            if id_reg != []:
                                for individual_method in id_reg:
                                    register_type = individual_method[0]
                                    index = individual_method[1]
                                    self.add_to_queue(
                                        [self.decide_trace_route, list_field_write_element, index, register_type], QUEUE_APPEND)
                        for list_field_read_element in all_field_reads:
                            id_reg = self.identify_register(
                                list_field_read_element, instr_op_value, get_source_instance_field, IGET_OPERAND_INDEX)
                            if id_reg != []:
                                for individual_method in id_reg:
                                    register_type = individual_method[0]
                                    index = individual_method[1]
                                    self.add_to_queue(
                                        [self.trace_register_basic, list_field_read_element, index, register_type], QUEUE_APPEND)
                        return
                    # ==============================================================
                    elif (instr_op_value in APUT_OPCODES) and (i == APUT_OPERAND_INDEX):
                        # If the register value is the result of an aput, then trace the source.
                        # Find where the source value comes from.
                        put_source_register = operands[APUT_OPERAND_SOURCE_INDEX][1]
                        put_source_register_name = self.identify_register_type(
                            num_local_registers, put_source_register)
                        if put_source_register_name[0] == "p":
                            self.add_to_queue([self.decide_trace_route, method,
                                        idx, put_source_register_name], QUEUE_PREPEND)
                        elif put_source_register_name[0] == "v":
                            self.add_to_queue([self.decide_trace_route, method,
                                        num_instructions-idx-1, put_source_register_name], QUEUE_PREPEND)
                        return
                    # ==============================================================
                    elif (instr_op_value in MOVE_RESULT_OPCODES) and (i == MOVE_RESULT_OPERAND_INDEX):
                        # If the register value is from move-result, then trace the preceding operation..
                        # Since we're using a reversed list, use .next() to get the previous instruction.
                        prev_instr = reversed_instructions.next()
                        prev_op_value = prev_instr.get_op_value()
                        prev_operands = prev_instr.get_operands()
                        # Move-result could be to get result of method invocation or filled-array-object. We need to find out which.
                        if prev_op_value in FILLED_ARRAY_OPCODES:
                            prev_regs = []
                            for x in range(0, len(prev_operands)-1):
                                prev_reg_num = prev_operands[x][1]
                                prev_reg_name = self.identify_register_type(
                                    num_local_registers, prev_reg_num)
                                if prev_reg_name not in prev_regs:
                                    prev_regs.append(prev_reg_name)
                                    if prev_reg_name[0] == "p":
                                        self.add_to_queue(
                                            [self.decide_trace_route, method, idx, prev_reg_name], QUEUE_PREPEND)
                                    elif prev_reg_name[0] == "v":
                                        self.add_to_queue(
                                            [self.decide_trace_route, method, num_instructions-idx-2, prev_reg_name], QUEUE_PREPEND)
                            prev_regs = None
                            return
                        elif prev_op_value in INVOKE_OPCODES:
                            isCrypto = False
                            isCrypto = self.crypto_search(
                                prev_instr.get_output(), method)
                            if isCrypto == True:
                                return
                            
                            # If the value is from a named object.
                            for named_obj_idx, named_object in enumerate(self.named_object_list):
                                for named_item in named_object[2]:
                                    full_name_string = named_object[0] + "->" + named_item
                                    if (full_name_string in str(prev_operands[len(prev_operands)-1])):
                                        named_item_string_register_num = prev_operands[1][1]
                                        named_item_string_register = self.identify_register_type(
                                            num_local_registers, named_item_string_register_num)
                                        named_string = None
                                        if named_item_string_register[0] == "v":
                                            named_string = self.string_search_internal(
                                                method, num_instructions-idx-2, named_item_string_register_num)
                                        if named_string:
                                            self.find_get_named_item(named_string, named_obj_idx)
                            
                            # Trace the invoked method as well, if it's not an external method.
                            prev_last_operand = prev_operands[len(
                                prev_operands)-1][2]
                            prev_methods = self.find_method(prev_last_operand)
                            for prev_method in prev_methods:
                                try:
                                    prev_method.get_instructions()
                                    # Call the method that identifies the register containing the return value of the invoked method, and then backtraces that register.
                                    self.add_to_queue(
                                        [self.trace_return, prev_method], QUEUE_PREPEND)
                                except:
                                    # Probably an external method.
                                    pass
                                # Also see if any other classes extend this class.
                                if prev_op_value not in INVOKE_STATIC_OPCODES:
                                    prev_op_register = prev_operands[0][1]
                                    prev_register_name = self.identify_register_type(
                                        num_local_registers, prev_op_register)
                                    prev_op_instance = ""
                                    if prev_register_name[0] == "v":
                                        prev_op_instance = self.find_first_instance(
                                            method, num_instructions-idx-2, prev_op_register)
                                    implementing_methods = self.find_implementing_methods(prev_method)
                                    superclass_methods = self.check_for_superclass_methods(prev_method)
                                    extending_methods = []
                                    extending_methods = itertools.chain(implementing_methods, superclass_methods)
                                    if (extending_methods != []) and (extending_methods != None):
                                        for extending_method in extending_methods:
                                            # See if the class is actually instantiated (within the method).  
                                            if prev_op_instance != extending_method.get_class_name():
                                                continue
                                            if self.confidence_level == CONFIDENCE_LEVEL_HIGH:
                                                if (self.trace_return, extending_method) not in self.stored_methods:
                                                    self.stored_methods.append((self.trace_return, extending_method))
                                            else:
                                                self.add_to_queue(
                                                        [self.trace_return, extending_method], QUEUE_APPEND)
                                    

                            # Backtrace the function arguments as well.
                            # This is to handle cases where the immediate preceding invoked method
                            # might be performing some formatting function on the actual cryptographically processed data.
                            for op_idx in range(0, len(prev_operands)):
                                if prev_operands[op_idx][0] != OPERAND_REGISTER:
                                    continue
                                op_register = prev_operands[op_idx][1]
                                op_register_name = self.identify_register_type(
                                    num_local_registers, op_register)
                                if (((method, num_instructions-idx-2, op_register_name) not in self.stored_methods) and 
                                        ([self.decide_trace_route, method, num_instructions-idx-2, op_register_name] not in self.all_methods)):
                                    if self.confidence_level == CONFIDENCE_LEVEL_HIGH:
                                        self.stored_methods.append(
                                            (self.decide_trace_route, method, num_instructions-idx-2, op_register_name))
                                    else:
                                        self.add_to_queue(
                                            [self.decide_trace_route, method, num_instructions-idx-2, op_register_name], QUEUE_APPEND)
                        return
                    # ==============================================================
                    elif (instr_op_value in MOVE_OPCODES) and (i == MOVE_OPERAND_INDEX):
                        # If the register value is from a move-object operation, then trace source registers.
                        move_from_register = operands[MOVE_OPERAND_SOURCE_INDEX][1]
                        move_from_register_name = self.identify_register_type(
                            num_local_registers, move_from_register)
                        if move_from_register_name[0] == "p":
                            self.add_to_queue([self.decide_trace_route, method,
                                        idx, move_from_register_name], QUEUE_PREPEND)
                        elif move_from_register_name[0] == "v":
                            self.add_to_queue([self.decide_trace_route, method,
                                        num_instructions-idx-1, move_from_register_name], QUEUE_PREPEND)
                        return


    def find_first_instance(self, method, index, op_register):
        instructions = method.get_instructions()
        (num_registers, num_local_registers,
         num_param_registers) = self.find_number_of_registers(method) 
        list_instructions = list(instructions)
        num_instructions = len(list_instructions)
        reversed_instructions = reversed(list_instructions)
        start_idx = num_instructions - index
        for idx, instruction in enumerate(reversed_instructions):
            if self.found_crypto == True:
                return
            if self.time_check() == True:
                return
            if idx < start_idx:
                continue
                
            op_code = instruction.get_op_value()
            operands = instruction.get_operands()
            for i in range(0, len(operands)):
                if (operands[i][0] == OPERAND_REGISTER) and (operands[i][1] == op_register):
                    if (op_code in NEW_INSTANCE_OPCODES):
                        return operands[1][2]
                    elif (op_code in MOVE_RESULT_OPCODES):
                        prev_instr = reversed_instructions.next()
                        prev_opcode = prev_instr.get_op_value()
                        instance_reg = (prev_instr.get_operands())[0][1]
                        instance_reg_name = self.identify_register_type(num_local_registers, instance_reg)
                        if instance_reg_name[0] == "p":
                            return ""
                        if prev_opcode in INVOKE_OPCODES:
                            if ("Ljava/lang/Class;->newInstance") in prev_instr.get_output():                                
                                return self.find_first_instance(method, num_instructions-idx-2, instance_reg)
                            elif ("Ljava/lang/Class;->forName") in prev_instr.get_output():
                                const_instr = reversed_instructions.next()
                                if const_instr.get_op_value() in CONST_DECL_OPCODES:
                                    const_operands = const_instr.get_operands()
                                    return self.class_string_to_smali(const_operands[1][2])
        return ""
     
    def class_string_to_smali(self, string):
        new_string = string.replace("u'","").replace("'","")
        smalistring = "L"
        string_split = new_string.split(".")
        for idx, element in enumerate(string_split):
            if idx > 0:
                smalistring = smalistring + "/" + element
            else:
                smalistring = smalistring + element
        smalistring = smalistring + ";"
        return smalistring
        
    def string_search_internal(self, method, index, register_num):
        instructions = method.get_instructions()
        list_instructions = list(instructions)
        num_instructions = len(list_instructions)
        reversed_instructions = reversed(list_instructions)
        start_idx = num_instructions - index

        for idx, instruction in enumerate(reversed_instructions):
            if self.found_crypto == True:
                return
            if self.time_check() == True:
                return
            if idx < start_idx:
                continue

            operands = instruction.get_operands(0)
            for i in range(0, len(operands)):
                if (operands[i][0] == OPERAND_REGISTER) and (operands[i][1] == register_num):
                    instr_op_value = instruction.get_op_value()
                    if (instr_op_value == 0x1A) and (i == CONST_OPERAND_INDEX):
                        return operands[1][2]


    def find_get_named_item(self, search_named_string, named_obj_idx):
        put_named_types = self.named_object_list[named_obj_idx][1]
        put_prefix = self.named_object_list[named_obj_idx][0]
        for put_named_type in put_named_types:
            put_methods = self.androguard_dx.find_methods(
                put_prefix, put_named_type, ".")
            search_term = put_prefix + "->" + put_named_type
            named_methods = []
            for put_method in put_methods:
                for element in put_method.get_xref_from():
                    named_methods.append(element[1])
            put_methods = None
            for named_method in named_methods:
                id_reg = self.identify_register(
                    named_method, INVOKE_OPCODES, search_term, 1)
                if id_reg != []:
                    for individual_method in id_reg:
                        register_type = individual_method[0]
                        index = individual_method[1]
                        named_string = None
                        if register_type[0] == "v":
                            named_string = self.string_search_internal(
                                named_method, index, int(register_type[1:]))
                        if named_string == search_named_string:
                            content_operand = 2
                            id_reg2 = self.identify_register(
                                named_method, INVOKE_OPCODES, search_term, content_operand)
                            if id_reg2 != []:
                                for individual_method2 in id_reg2:
                                    content_register_type = individual_method2[0]
                                    index2 = individual_method2[1]
                                    self.add_to_queue([self.decide_trace_route, named_method,
                                                index2, content_register_type], QUEUE_PREPEND)
                                            
    def find_associated_method_call(self, associated_method_operand, operand_idx):
        # Because execute doesn't actually have a method definition, we have to go about this differently.
        split_operand = associated_method_operand.split("->")
        target_class = split_operand[0].strip()
        target_name = split_operand[1].split("(")[0].strip()
        target_desc = "(" + split_operand[1].split("(")[1].strip()
        associated_methods = []
        
        dx_associated_methods = self.androguard_dx.find_methods(re.escape(target_class), 
                                                                    re.escape(target_name), 
                                                                    re.escape(target_desc))
        calling_methods = []
        for dx_associated_method in dx_associated_methods:
            for element in dx_associated_method.get_xref_from():
                if element[1] not in calling_methods:
                    calling_methods.append(element[1])
        
        for path_idx, method in enumerate(calling_methods):
            id_reg = self.identify_register(
                method, INVOKE_OPCODES, associated_method_operand, operand_idx)
            if id_reg == []:
                continue
            else:
                for individual_method in id_reg:
                    register_type = individual_method[0]
                    index = individual_method[1]
                    self.add_to_queue([self.decide_trace_route, method,
                                index, register_type], QUEUE_PREPEND)
                    self.instruction_scheduler()
        
    def trace_external(self, method, register_name):
        argument_register_name = ""
        out_method = None
        index = -1
        register_idx = int(register_name[1:])
        path_idx = None
        method_path = None
        method_class = "".join(method.get_class_name().split())
        method_name = "".join(method.get_name().split())
        method_desc = "".join(method.get_descriptor().split())

        # If the methods are to do with AsyncTask (for example), then searching for calls to doInBackground won't work.
        is_associated_method = False
        # Get superclass, so that we can be sure of the method.
        superclass_methods = self.check_for_superclass_methods(method)
        superclass_name = ""
        if len(superclass_methods) > 0:
            superclass_name = superclass_methods[0].get_class_name()
            for nonnamed_object in self.nonnamed_object_list:
                for nonnamed_method in nonnamed_object[1]:
                    if ((nonnamed_method in method_name) and 
                        ((nonnamed_object[0] == superclass_name) 
                            or (nonnamed_object[0] == method_class))):
                        is_associated_method = True
                        for item in nonnamed_object[2]:
                            self.find_associated_method_call(method_class + "->" + item, nonnamed_object[3])
        # Avoid incorrect searches of superclasses when the method is AsyncTask.
        if is_associated_method == True:
            return
            
        # Normal methods.
        all_methods = self.androguard_dx.find_methods(re.escape(method.get_class_name()), re.escape(
            method.get_name()), re.escape(method.get_descriptor()))
        out_methods = []
        for target_method in all_methods:
            for element in target_method.get_xref_from():
                out_methods.append(element[1])

        search_string = method.get_class_name() + "->" + method.get_name() + \
            method.get_descriptor()

        for path_idx, out_method in enumerate(out_methods):
            if self.found_crypto:
                return

            id_reg = self.identify_register(
                out_method, INVOKE_OPCODES, search_string, register_idx)
            if id_reg != []:
                for individual_method in id_reg:
                    argument_register_name = individual_method[0]
                    index = individual_method[1]
                    self.add_to_queue([self.decide_trace_route, out_method,
                                index, argument_register_name], QUEUE_APPEND)

            
        # If the method is not an abstract method,
        #  then check if its class implements an interface class or extends an abstract class.
        # First see if the method is an external method.
        try:
            method.get_instructions()
        except:
            return
        method_access_flags = method.get_access_flags()
        if (ACCESS_FLAG_ABSTRACT & method_access_flags) == ACCESS_FLAG_ABSTRACT:
            return

        implementing_methods = self.check_for_interface_class(method)
        for implementing_method in implementing_methods:
            if self.confidence_level == CONFIDENCE_LEVEL_HIGH:
                if (self.decide_trace_route, implementing_method, 1, register_name) not in self.stored_methods:
                    self.stored_methods.append((self.decide_trace_route, implementing_method, 1, register_name))
            else:
                self.add_to_queue([self.decide_trace_route,
                            implementing_method, 1, register_name], QUEUE_APPEND)
                                
        for superclass_method in superclass_methods:
            if self.confidence_level == CONFIDENCE_LEVEL_HIGH:
                if (self.decide_trace_route, superclass_method, 1, register_name) not in self.stored_methods:
                    self.stored_methods.append((self.decide_trace_route, superclass_method, 1, register_name))
            else:
                self.add_to_queue([self.decide_trace_route,
                            superclass_method, 1, register_name], QUEUE_APPEND)
        
        return

    def check_for_superclass_methods(self, method):
        implementing_methods = []
        method_class = "".join(method.get_class_name().split())
        method_name = "".join(method.get_name().split())
        method_desc = "".join(method.get_descriptor().split())
    
        try:
            method.get_instructions()
        except:
            return implementing_methods
        all_classes = self.androguard_dx.find_classes(re.escape(method_class))
        class_list = []
        for one_class in all_classes:
            class_list.append(one_class.get_vm_class())

        superclass_list = []
        for found_class in class_list:
            superclass_name = None
            try:
                superclass_name = found_class.get_superclassname()
            except:
                superclass_name = found_class.get_name()
            if (superclass_name != method.get_class_name()) and (superclass_name != None):
                superclasses = self.androguard_dx.find_classes(re.escape(superclass_name))
                for superclass in superclasses:
                    superclass_list.append(superclass)
        
        for superclass_item in superclass_list:
            superclass_method_objs = superclass_item.get_methods()
        
            for superclass_method_obj in superclass_method_objs:
                superclass_method = superclass_method_obj.get_method()
                superclass_method_name = "".join(superclass_method.get_name().split())
                superclass_method_desc = "".join(superclass_method.get_descriptor().split())
                if (superclass_method_name == method_name) and (superclass_method_desc == method_desc):
                    implementing_methods.append(superclass_method)

        return implementing_methods
        
    def find_implementing_methods(self, method):
        """ Return methods implementing an abstract method. """
        
        implementing_methods = []
        method_class = "".join(method.get_class_name().split())
        method_name = "".join(method.get_name().split())
        method_desc = "".join(method.get_descriptor().split())

        class_list = []
        for d in self.androguard_d:
            all_classes = d.get_classes()            
            for one_class in all_classes:
                class_interfaces = one_class.get_interfaces()
                if len(class_interfaces) < 1:
                    continue
                if (method_class in class_interfaces) and (one_class not in class_list):
                    class_list.append(one_class)

        for class_item in class_list:
            try:
                all_methods = class_item.get_methods()
                for one_method in all_methods:
                    try:
                        one_method.get_instructions()
                    except:
                        # Probably external method.
                        # This branch should never be reached.
                        continue
                    method_access_flags = one_method.get_access_flags()
                    if (ACCESS_FLAG_ABSTRACT & method_access_flags) == ACCESS_FLAG_ABSTRACT:
                        continue
                    else:
                        found_method_name = "".join(one_method.get_name().split())
                        found_method_desc = "".join(one_method.get_descriptor().split())
                        if (found_method_name == method_name) and (found_method_desc == method_desc):
                            implementing_methods.append(one_method)
            except:
                continue
        return implementing_methods
        
    def check_for_interface_class(self, method):
        implementing_methods = []
        method_class = "".join(method.get_class_name().split())
        method_name = "".join(method.get_name().split())
        method_desc = "".join(method.get_descriptor().split())

        all_classes = self.androguard_dx.find_classes(re.escape(method_class))
        class_list = []
        for one_class in all_classes:
            class_list.append(one_class.get_vm_class())

        interface_class_list = []
        for found_class in class_list:
            interface_list = found_class.get_interfaces()
            for interface in interface_list:
                interface_classes = self.androguard_dx.find_classes(re.escape(interface))
                for interface_class in interface_classes:
                    interface_class_list.append(interface_class.get_vm_class())

        for interface_class_item in interface_class_list:
            all_methods = interface_class_item.get_methods()
            for one_method in all_methods:
                found_method_name = "".join(one_method.get_name().split())
                found_method_desc = "".join(one_method.get_descriptor().split())
                if (found_method_name == method_name) and (found_method_desc == method_desc):
                    implementing_methods.append(one_method)
        return implementing_methods


    def trace_init(self, method):
        method_class = method.get_class_name()
        constructor_methods = []
        dx_find_methods = self.androguard_dx.find_methods(re.escape(method_class), ".", ".")
        for dx_find_method in dx_find_methods:
            dx_method = dx_find_method.get_method()
            try:
                dx_method.get_instructions()
            except:
                # Probably external method.
                continue
            method_access_flags = dx_method.get_access_flags()
            if (ACCESS_FLAG_CONSTRUCTOR & method_access_flags) == ACCESS_FLAG_CONSTRUCTOR:
                constructor_methods.append(dx_method)

        dx_find_methods = None

        # Trace through each <init> method to see if crypto is being used.
        for constructor_method in constructor_methods:
            self.add_to_queue([self.trace_through_method, 
                        constructor_method], QUEUE_PREPEND)
        return


    def trace_return(self, method):
        instructions = None
        try:
            instructions = method.get_instructions()
        except:
            # This is probably an external method.
            return METHOD_EXTERNAL

        list_instructions = list(instructions)
        num_instructions = len(list_instructions)
        instructions = None
        if (num_instructions <= 0):
            return METHOD_EMPTY

        (num_registers, num_local_registers,
         num_param_registers) = self.find_number_of_registers(method)
        for idx, instruction in enumerate(list_instructions):
            if instruction.get_op_value() in RETURN_OPCODES:
                ops = instruction.get_operands()
                trace_operand = ops[RETURN_OPERAND][1]
                trace_register_name = self.identify_register_type(
                    num_local_registers, trace_operand)
                # Backtrace the register.
                self.add_to_queue([self.decide_trace_route, method,
                            idx, trace_register_name], QUEUE_PREPEND)
                return METHOD_INTERNAL
        return METHOD_INTERNAL


    def trace_register_basic(self, method, index, register_type):
        instructions = None
        register_id = int(register_type[1:])

        try:
            instructions = method.get_instructions()
        except:
            # This is probably an external method.
            return
        list_instructions = list(instructions)
        num_instructions = len(list_instructions)
        instructions = None

        if (num_instructions <= 0):
            return

        for idx, instruction in enumerate(list_instructions):
            if idx <= index:
                continue

            instr_op_value = instruction.get_op_value()
            operands = instruction.get_operands(0)

            for i in range(0, len(operands)):
                if (operands[i][0] == OPERAND_REGISTER) and (operands[i][1] == register_id):
                    shouldStop = self.check_for_stop_conditions(instr_op_value, i)
                    if shouldStop == True:
                        return

                    isCrypto = False
                    isCrypto = self.crypto_search(instruction.get_output(), method)
                    if isCrypto == True:
                        return
        return


    def check_for_stop_conditions(self, instr_op_value, i):
        """Check for instances of register value change. """
        
        stopCondition = False
        # The next conditions are all conditions where the value of our register changes due to some operation.
        # We stop our search at this point, because we may no longer be dealing with the output of getValue().
        # ==============================================================
        if (instr_op_value in CONST_DECL_OPCODES) and (i == CONST_OPERAND_INDEX):  # const declarations
            stopCondition = True
        # ==============================================================
        elif (instr_op_value in NEW_ARRAY_OPCODES) and (i == NEW_ARRAY_OPERAND_INDEX):  # new-array declarations
            stopCondition = True
        # ==============================================================
        elif (instr_op_value in NEW_INSTANCE_OPCODES) and (i == NEW_INSTANCE_OPERAND_INDEX):  # new-instance declarations
            stopCondition = True
        # ==============================================================
        # result of arithmetic/logic operation.
        elif (instr_op_value in OPERATION_OPCODES) and (i == OPERATION_OPERAND_INDEX):
            stopCondition = True
        # ==============================================================
        elif (instr_op_value in AGET_OPCODES) and (i == AGET_OPERAND_INDEX):
            stopCondition = True
        # ==============================================================
        elif (instr_op_value in SGET_OPCODES) and (i == SGET_OPERAND_INDEX):
            stopCondition = True
        # ==============================================================
        elif (instr_op_value in IGET_OPCODES) and (i == IGET_OPERAND_INDEX):
            stopCondition = True
        # ==============================================================
        elif ((instr_op_value in IPUT_OPCODES) or (instr_op_value in APUT_OPCODES)) and (i == APUT_OPERAND_INDEX):
            stopCondition = True
        # ==============================================================
        elif (instr_op_value in MOVE_RESULT_OPCODES) and (i == MOVE_RESULT_OPERAND_INDEX):
            stopCondition = True
        # ==============================================================
        elif (instr_op_value in MOVE_OPCODES) and (i == MOVE_OPERAND_INDEX):
            stopCondition = True
        # ==============================================================
        elif (instr_op_value in COMPARE_OPCODES) and (i == COMPARE_OPERAND_INDEX):
            stopCondition = True

        return stopCondition


    def trace_through_method(self, method):
        """Perform a "loose" search through all instructions of a method. """
        
        instructions = None

        try:
            instructions = method.get_instructions()
        except:
            # This is probably an external method.
            return

        for instruction in instructions:
            isCrypto = False
            isCrypto = self.crypto_search(instruction.get_output(), method)
            if isCrypto == True:
                return
        return


    def find_method(self, method_operand):
        """Given a string (containing a reference to a method), find the corresponding method. """
        
        split_operand = method_operand.split("->")
        target_class = split_operand[0].strip()
        target_name = split_operand[1].split("(")[0].strip()
        target_desc = "(" + split_operand[1].split("(")[1].strip()
        target_method = "".join(method_operand.split())

        list_methods = []
        dx_find_methods = self.androguard_dx.find_methods(
            re.escape(target_class), re.escape(target_name), re.escape(target_desc))

        for dx_find_method in dx_find_methods:
            dx_method = dx_find_method.get_method()
            list_methods.append(dx_method)

        return list_methods

        
    def find_field_analysis_objects(self, field_full_string):
        """Return a list of fields matching search string. """
        
        list_fields = []
        split_source = field_full_string.replace("->", " ").split()
        for single_field in self.androguard_dx.get_fields():
            if (single_field.field.get_class_name() + single_field.field.get_name() + single_field.field.get_descriptor()) == (split_source[0]+split_source[1]+split_source[2]):
                list_fields.append(single_field)
        return list_fields


    def crypto_search(self, string_to_search, method):
        """Look for calls to crypto within input string. """

        for crypto_pkg in CRYPTO_PACKAGES:
            if (crypto_pkg in string_to_search) and ("InvalidParameterException" not in string_to_search):
                self.found_crypto = True
                self.location_ble_crypto = str(method.get_class_name()) + str(method.get_name()) + str(method.get_descriptor())
                return True
        return False


    def elapsed_time(self):
        """Return time elapsed since program execution started. """
        
        stoptime = timeit.default_timer()
        runtime = stoptime - self.start_time
        return runtime

        
    def time_check(self):
        """Check if elapsed time is greater than max alowable runtime. """
        
        # Set a timeout so that one app doesn't take too long to analyse.
        if(self.elapsed_time() >= MAX_RUNTIME):
            self.confidence_level = "Timeout"
            return True
        return False
        
        
    def initialise_named_object_list(self):
        self.named_object_list = [
                                    [   "Landroid/content/Intent;",
                                        [
                                            "putExtra"
                                        ], 
                                        [
                                            "getBooleanArrayExtra"
                                           , "getBooleanExtra"
                                           , "getBundleExtra"
                                           , "getByteArrayExtra"
                                           , "getByteExtra"
                                           , "getCharArrayExtra"
                                           , "getCharExtra"
                                           , "getCharSequenceArrayExtra"
                                           , "getCharSequenceArrayListExtra"
                                           , "getCharSequenceExtra"
                                           , "getDoubleArrayExtra"
                                           , "getDoubleExtra"
                                           , "getFloatArrayExtra"
                                           , "getFloatExtra"
                                           , "getIntArrayExtra"
                                           , "getIntExtra"
                                           , "getIntegerArrayListExtra"
                                           , "getLongArrayExtra"
                                           , "getLongExtra"
                                           , "getParcelableArrayExtra"
                                           , "getParcelableArrayListExtra"
                                           , "getParcelableExtra"
                                           , "getSerializableExtra"
                                           , "getShortArrayExtra"
                                           , "getShortExtra"
                                           , "getStringArrayExtra"
                                           , "getStringArrayListExtra"
                                           , "getStringExtra"
                                        ]
                                    ],
                                    [   "Landroid/os/Bundle;", 
                                        [
                                            "putBinder"
                                            ,"putBundle"
                                            ,"putByte"
                                            ,"putByteArray"
                                            ,"putChar"
                                            ,"putCharArray"
                                            ,"putCharSequence"
                                            ,"putCharSequenceArray"
                                            ,"putCharSequenceArrayList"
                                            ,"putFloat"
                                            ,"putFloatArray"
                                            ,"putIntegerArrayList"
                                            ,"putParcelable"
                                            ,"putParcelableArray"
                                            ,"putParcelableArrayList"
                                            ,"putSerializable"
                                            ,"putShort"
                                            ,"putShortArray"
                                            ,"putSize"
                                            ,"putSizeF"
                                            ,"putSparseParcelableArray"
                                            ,"putStringArrayList"
                                            ,"putBoolean"
                                            ,"putBooleanArray"
                                            ,"putDouble"
                                            ,"putDoubleArray"
                                            ,"putInt"
                                            ,"putIntArray"
                                            ,"putLong"
                                            ,"putLongArray"
                                            ,"putString"
                                            ,"putStringArray"
                                        ],
                                        [
                                            "getBinder"
                                            ,"getBundle"
                                            ,"getByte"
                                            ,"getByteArray"
                                            ,"getChar"
                                            ,"getCharArray"
                                            ,"getCharSequence"
                                            ,"getCharSequence"
                                            ,"getCharSequenceArray"
                                            ,"getCharSequenceArrayList"
                                            ,"getFloat"
                                            ,"getFloatArray"
                                            ,"getIntegerArrayList"
                                            ,"getParcelable"
                                            ,"getParcelableArray"
                                            ,"getParcelableArrayList"
                                            ,"getSerializable"
                                            ,"getShort"
                                            ,"getShortArray"
                                            ,"getSize"
                                            ,"getSizeF"
                                            ,"getSparseParcelableArray"
                                            ,"getStringArrayList"
                                            ,"get"
                                            ,"getBoolean"
                                            ,"getBooleanArray"
                                            ,"getDouble"
                                            ,"getDoubleArray"
                                            ,"getInt"
                                            ,"getIntArray"
                                            ,"getLong"
                                            ,"getLongArray"
                                            ,"getString"
                                            ,"getStringArray"
                                        ]
                                    ]
                                ]
                                
    def initialise_nonnamed_object_list(self):
        self.nonnamed_object_list = [
                                        [
                                            "Landroid/os/AsyncTask;",
                                            [
                                                "doInBackground"
                                            ], 
                                            [
                                                "execute([Ljava/lang/Object;)Landroid/os/AsyncTask;", 
                                                "execute(Ljava/lang/Runnable;)"
                                            ],
                                            1,
                                        ],
                                    ]
