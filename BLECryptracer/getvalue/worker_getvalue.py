import os
import sys
import fnmatch
import re
import timeit
import collections
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

# Operand types.
OPERAND_REGISTER = 0
OPERAND_LITERAL = 1
OPERAND_RAW = 2
OPERAND_OFFSET = 3
OPERAND_KIND = 0x100

# Libraries of interest.
CRYPTO_PACKAGES = ["Ljavax/crypto", "Ljava/security"]

####### TOREMOVE #############
# Methods of ineterst.
METHOD_PACKAGES = ["execute([Ljava/lang/Object;)Landroid/os/AsyncTask;", "execute(Ljava/lang/Runnable;)", "Landroid/os/Handler;->dispatchMessage", "Landroid/os/Messenger;", "Landroid/content/SharedPreferences"]
################################


# Confidence levels.
CONFIDENCE_LEVEL_HIGH = "High"
CONFIDENCE_LEVEL_MED = "Medium"
CONFIDENCE_LEVEL_LOW = "Low"

# Timing-related.
MAX_RUNTIME = 1800

# Related to the instruction queue.
QUEUE_APPEND = 1
QUEUE_PREPEND = 2

class WorkerGetvalue:
    def __init__(self):
        # Output values.
        self.found_crypto = False
        self.getvalue = False
        self.crypto = False
        self.location_getvalue = None
        self.location_ble_crypto = None
        self.confidence_level = CONFIDENCE_LEVEL_HIGH

        # Keep track of methods that we have already analysed,
        # and methods that are to be analysed at lower confidence levels.
        self.stored_methods = []
        self.source_methods = []
        self.all_methods = []
        self.stored_instructions = []

        # Stats.
        self.num_ble_methods = 0
        self.all_ble_methods = ""
        self.start_time = None
        
        # Androguard-related.
        self.androguard_a = None
        self.androguard_d = None
        self.androguard_dx = None
        
        # Mainly used to prevent excessive recursion.
        self.instruction_queue = collections.deque()

        # Initialise object list.
        self.named_object_list = []
        self.initialise_named_object_list()
        
        ####### TOREMOVE ########
        self.notes = ""
        
    def main(self, in_queue, out_queue, process_id):
        """Obtain the file of an APK and initate processing.
        
        Keyword arguments:
        in_queue -- the queue from which to obtain the path to the APK.
        out_queue -- the queue to which to put the output string.
        process_id -- the ID assigned to this worker process by the main.
        """

        # Get job from queue.
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
            self.getvalue = False
            self.crypto = False
            self.location_getvalue = None
            self.location_ble_crypto = None
            self.stored_methods = []
            self.source_methods = []
            self.all_methods = []
            self.stored_instructions = []
            self.confidence_level = CONFIDENCE_LEVEL_HIGH
            self.num_ble_methods = 0
            self.all_ble_methods = ""
            self.instruction_queue.clear()
            ####### TOREMOVE ########
            self.notes = ""

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
                                  ",Error,"
                                  + str(runtime) 
                                  + "\n" 
                                  + "err_divAnalyzeAPK error. " 
                                  + str(e) 
                                  + "\n\n")
                in_queue.task_done()
                # Reset the session for the next analysis. Otherwise memory consumption increases with each new APK (Bug in Androguard 3.1.0).
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
                                  + "," + apk_package 
                                  + "," + str(self.getvalue) 
                                  + "," + str(self.crypto) 
                                  + "," + str(self.found_crypto) 
                                  + "," + self.confidence_level 
                                  + "," + str(self.location_getvalue) 
                                  + "," + str(self.location_ble_crypto) 
                                  + "," + str(self.num_ble_methods) 
                                  + "," + str(self.all_ble_methods) 
                                  + "," + str(runtime) 
                                  + "," + str(self.notes) ### TOREMOVE ###
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

        # First get paths from any methods calling BluetoothGattCharacteristic->getValue() variants.
        ext_methods = []
        ext_methods.extend(self.androguard_dx.find_methods(
            "Landroid/bluetooth/BluetoothGattCharacteristic;", "getValue", "."))
        ext_methods.extend(self.androguard_dx.find_methods(
            "Landroid/bluetooth/BluetoothGattCharacteristic;", "getIntValue", "."))
        ext_methods.extend(self.androguard_dx.find_methods(
            "Landroid/bluetooth/BluetoothGattCharacteristic;", "getFloatValue", "."))
        ext_methods.extend(self.androguard_dx.find_methods(
            "Landroid/bluetooth/BluetoothGattCharacteristic;", "getStringValue", "."))
        getvalue_methods = []
        for ext_method in ext_methods:
            for element in ext_method.get_xref_from():
                if element[1] not in getvalue_methods:
                    getvalue_methods.append(element[1])
                    ble_method_name = element[1].get_class_name(
                    ) + element[1].get_name() + "".join(element[1].get_descriptor().split()) + "\\"
                    self.all_ble_methods = self.all_ble_methods + ble_method_name
        ext_methods = None

        # If there are no methods calling getValue, then move onto next APK.
        if getvalue_methods == []:
            return
        else:
            self.getvalue = True
            self.num_ble_methods = len(getvalue_methods)

        # Find whether crypto is used at all within the APK.
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

        # Prioritise the methods and then call tracing function.
        prioritised_getvalue_methods = None
        if len(getvalue_methods) == 1:
            prioritised_getvalue_methods = getvalue_methods
        else:
            prioritised_getvalue_methods = self.prioritise_methods(getvalue_methods)
        self.gatt_trace(prioritised_getvalue_methods)


    def prioritise_methods(self, getvalue_methods):
        """Return list of prioritised methods.
        
        Keyword arguments:
        getvalue_methods -- list of unprioritised methods.
        """

        package = self.androguard_a.get_package()
        split_package = package.split(".")
        len_package_name = len(split_package)

        intermediate_methods = []
        for getvalue_method in getvalue_methods:
            full_method_classname = getvalue_method.get_class_name()
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
            intermediate_methods.append((dist, getvalue_method))

        sorted_methods = sorted(intermediate_methods,
                                key=lambda mtd: mtd[0], reverse=True)
        intermediate_methods = None
        output_methods = []
        for sorted_method in sorted_methods:
            output_methods.append(sorted_method[1])

        return output_methods


    def gatt_trace(self, getvalue_methods):
        # Start trace for each method that calls getValue().
        for path_idx, method in enumerate(getvalue_methods):
            # If we have found crypto use with BLE in one of the previous iterations, then stop.
            if self.found_crypto == True:
                return
            # If we've run out of time, then stop analysing this APK and move onto the next.
            if (self.time_check()):
                return

            self.location_getvalue = str(method.get_class_name()) + \
                str(method.get_name()) + str(method.get_descriptor())

            # Get the calling method.
            search_string = "Landroid/bluetooth/BluetoothGattCharacteristic;->getValue"
            # getValue is invoked using invoke-virtual, which is opcode 0x6E
            id_reg = self.identify_register(method, INVOKE_OPCODES, search_string)
            if (id_reg == []):
                search_string = "Landroid/bluetooth/BluetoothGattCharacteristic;->getIntValue"
                id_reg = self.identify_register(method, INVOKE_OPCODES, search_string)
            if (id_reg == []):
                search_string = "Landroid/bluetooth/BluetoothGattCharacteristic;->getFloatValue"
                id_reg = self.identify_register(method, INVOKE_OPCODES, search_string)
            if (id_reg == []):
                search_string = "Landroid/bluetooth/BluetoothGattCharacteristic;->getStringValue"
                id_reg = self.identify_register(method, INVOKE_OPCODES, search_string)

            if (id_reg == []):
                continue
            else:
                for individual_method in id_reg:
                    register_type = individual_method[0]
                    index = individual_method[1]
                    register_num = self.find_register_num_from_type(method, register_type)
                    self.add_to_queue([self.trace_forward_thorough, method,
                                index+1, register_num], QUEUE_PREPEND)
                self.instruction_scheduler()

        # Reset to reduce items in memory.
        getvalue_methods = None

        # If we've already found crypto, we're done.
        if self.found_crypto == True:
            return
        if (self.time_check()):
            return

        self.confidence_level = CONFIDENCE_LEVEL_MED
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
        if (self.time_check()):
            return

        # Final search through methods.
        self.confidence_level = CONFIDENCE_LEVEL_LOW
        self.instruction_queue.clear()
        for source_method in self.source_methods:
            if self.found_crypto == True:
                return
            if (self.time_check()):
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
        # Add the method to a list for later analysis.
        method_item = function_block[1]
        if method_item not in self.source_methods:
            self.source_methods.append(method_item)
        # Execute the method with the provided arguments.
        function_ref = function_block[0]
        function_block.remove(function_ref)
        function_ref(*function_block)


    def identify_register(self, method, opcodes, search_term, register_idx=-1, override_invoke=False):
        """Return argument register and instruction index for instruction satisfying search term.
        
        Keyword arguments:
        method -- the method of interest
        opcodes -- array of opcodes
        search_term -- the actual search term to look for within instruction output.
        register_idx -- register index
        """

        argument_register_name = ""
        index = -1
        if not isinstance(opcodes, list):
            opcodes = [opcodes]
        output = []
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
                    # Figure out which type of register is used to carry the argument
                    #  to the function (this will determine whether we should trace
                    #  within the current method, or via function call).
                    if ((instruction.get_op_value() in INVOKE_OPCODES) and
                        (override_invoke==False)):
                        # The output will be in the next instruction.
                        index += 1
                        next_instruction = list_instructions[index]
                        if (next_instruction.get_op_value() in MOVE_RESULT_OPCODES):
                            all_next_operands = next_instruction.get_operands(0)
                            argument_register = all_next_operands[0][1]
                        else:
                            pass
                    else:
                        argument_register = operands[register_idx][1]
                    if (argument_register != None):
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
        
        num_registers = method.code.get_registers_size()
        num_parameter_registers = method.code.get_ins_size()
        num_local_registers = num_registers - num_parameter_registers
        return(num_registers, num_local_registers, num_parameter_registers)


    def find_register_num_from_type(self, method, register_type):
        """Return register number for given method and type.
        
        Keyword arguments:
        method -- method of interest
        register_type -- register name (e.g., v5, p1)
        """
        
        register_num = None
        (num_registers, num_local_registers,
         num_parameter_registers) = self.find_number_of_registers(method)
        if register_type[0] == "v":
            register_num = int(register_type[1:])
        else:
            register_num = int(register_type[1:]) + num_local_registers
        return register_num


    def is_this_argument(self, method):
        """Return True for instance method and False for static method.
        
        Keyword arguments:
        method -- method of interest
        """
        
        isThis = None
        method_access_flags = method.get_access_flags()
        if (ACCESS_FLAG_STATIC & method_access_flags) == ACCESS_FLAG_STATIC:
            isThis = False
        else:
            isThis = True

        return isThis


    def identify_register_type(self, num_local_registers, argument_register):
        """Return register name (e.g., p1 or v5).
        
        Keyword arguments:
        num_local_registers -- number of local registers in method
        argument_register -- the number of the register of interest
        """
        
        register_name = None
        if argument_register < num_local_registers:
            register_name = "v" + str(argument_register)
        elif argument_register == num_local_registers:
            register_name = "p0"
        else:
            register_num = argument_register - num_local_registers
            register_name = "p" + str(register_num)
        return register_name


    def trace_forward_thorough(self, method, index, input_register_num, end_index=0):
        """Trace from given index within method instructions to find where register's value is used.
        
        Keyword arguments:
        method -- method of interest
        index -- instruction index at which to start trace
        input_register_num -- register of interest
        end_index -- instruction index at which to stop trace
        """

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

        # The index from which to start the search.
        start_idx = index

        (num_registers, num_local_registers,
         num_parameter_registers) = self.find_number_of_registers(method)

        offset_tally = 0        
        
        for idx, instruction in enumerate(list_instructions):            
            if self.found_crypto:
                return
            if (self.time_check()):
                return

            offset_tally += instruction.get_length()

            if idx < start_idx:
                continue

            # Prevent sections of the instruction list from being analysed twice (in the case of branches).
            if (end_index != 0) and (idx == end_index):
                return

            instr_op_value = instruction.get_op_value()
            operands = instruction.get_operands(0)
            
            # If there's a GOTO instruction, then we need to skip
            #   to the relevant part of the code.
            if ((instr_op_value in GOTO_OPCODES) and 
                (str([method,instruction]) not in self.stored_instructions)):
                [new_offset] = bytecodes.dvm.determineNext(
                            instruction, offset_tally-instruction.get_length(), None)
                # The instruction to go to.
                new_idx = self.instruction_index_by_offset(
                    method, new_offset) + 1

                self.add_to_queue([self.trace_forward_thorough, method,
                                new_idx, input_register_num], QUEUE_PREPEND)
                self.stored_instructions.append(str([method,instruction]))
                return
                
            # Check if our register is present among the operands.
            # In general, we only care about the first time we come across it (i.e., the last time it occurred before being used to invoke the method of interest)
            for i in range(0, len(operands)):
                if (operands[i][0] == OPERAND_REGISTER) and (operands[i][1] == input_register_num):
                    register_num = operands[i][1]
                    # Test for different ways in which the register could have been assigned a value. The checks on i are to ensure that the register of interest is in the correct parameter position.
                    # Look for stop conditions.
                    # ==============================================================
                    shouldStop = self.check_for_stop_conditions(instr_op_value, i)
                    if shouldStop == True:
                        return
                    # ==============================================================
                    elif (instr_op_value in INVOKE_OPCODES):
                        # Check if the invoked method takes parameters related to crypto.
                        isCrypto = False
                        isCrypto = self.crypto_search(instruction.get_output(), method)
                        if isCrypto == True:
                            return

                        instr_operands = instruction.get_operands()
                        instr_last_operand = instr_operands[len(
                            instr_operands)-1][2]

                        # If the value is being added to a named object (e.g., Bundle or Intent)
                        for named_obj_idx, named_object in enumerate(self.named_object_list):
                            for named_item in named_object[1]:
                                full_name_string = named_object[0] + "->" + named_item
                                if (full_name_string in str(instr_last_operand)) and (i == 2):
                                    named_item_string_register_num = instr_operands[1][1]
                                    named_item_string_register = self.identify_register_type(
                                        num_local_registers, named_item_string_register_num)
                                    named_string = None
                                    if named_item_string_register[0] == "v":
                                        named_string = self.string_search_internal(
                                            method, idx, named_item_string_register_num)
                                    if named_string:
                                        self.find_get_named_item(named_string, named_obj_idx)

                        # Find the actual method that is called, from the string in the last operand.
                        invoked_methods = self.find_method(instr_last_operand)
                        # Search through the called methods.
                        for invoke_method in invoked_methods:
                            self.add_to_queue(
                                    [self.trace_called_method, invoke_method, i], QUEUE_PREPEND)

                            # If the method is an instance method, then trace the instance as well.
                            if instr_op_value in INVOKE_STATIC_OPCODES:
                                # Not an instance method
                                pass
                            else:
                                instance_register_num = instr_operands[0][1]
                                if self.confidence_level == CONFIDENCE_LEVEL_HIGH:
                                    self.stored_methods.append((self.trace_forward_thorough, method, idx+1, instance_register_num))
                                else:
                                    self.add_to_queue([self.trace_forward_thorough, method, idx+1, instance_register_num], QUEUE_PREPEND)               

                        # Also trace the output.
                        next_index = idx+1
                        next_instruction = list_instructions[next_index]
                        if (next_instruction.get_op_value() in MOVE_RESULT_OPCODES):
                            all_operands = next_instruction.get_operands(0)
                            argument_register_num = all_operands[0][1]
                            self.add_to_queue([self.trace_forward_thorough, method,
                                        next_index+1, argument_register_num], QUEUE_PREPEND)
                        elif instr_op_value not in INVOKE_DIRECT_OPCODES:
                            pass
                            
                        break
                    # ==============================================================
                    elif (instr_op_value in FILLED_ARRAY_OPCODES) and (i != len(operands)-1):
                        next_index = idx+1
                        next_instruction = list_instructions[next_index]
                        if (next_instruction.get_op_value() in MOVE_RESULT_OPCODES):
                            all_operands = next_instruction.get_operands(0)
                            argument_register_num = all_operands[0][1]
                            self.add_to_queue([self.trace_forward_thorough, method,
                                        next_index+1, argument_register_num], QUEUE_APPEND)
                        else:
                            pass
                        break
                    # ==============================================================
                    elif (instr_op_value in CONDITIONAL_OPCODES) and (i == CONDITIONAL_OPERAND_INDEX):
                        (first_branch, second_branch) = bytecodes.dvm.determineNext(
                            instruction, offset_tally-instruction.get_length(), None)
                        # First branch
                        first_branch_index = self.instruction_index_by_offset(
                            method, first_branch) + 1
                        # Second branch
                        second_branch_index = self.instruction_index_by_offset(
                            method, second_branch) + 1
                        # Add both branches to queue.
                        if (first_branch_index != -1) and (second_branch_index != -1):
                            self.add_to_queue([self.trace_forward_thorough, method, first_branch_index,
                                        register_num, second_branch_index], QUEUE_PREPEND)
                            self.add_to_queue([self.trace_forward_thorough, method,
                                        second_branch_index, register_num], QUEUE_PREPEND)
                        break
                    # ==============================================================
                    elif (instr_op_value in OPERATION_OPCODES) and (i == OPERATION_OPERAND_SOURCE_INDEX):
                        destination_register = operands[OPERATION_OPERAND_INDEX][1]
                        self.add_to_queue([self.trace_forward_thorough, method, idx+1,
                                        destination_register], QUEUE_PREPEND)
                        break
                    # ==============================================================
                    elif (instr_op_value in AGET_OPCODES) and (i == AGET_OPERAND_SOURCE_INDEX):
                        destination_register = operands[AGET_OPERAND_INDEX][1]
                        self.add_to_queue([self.trace_forward_thorough, method, idx+1,
                                        destination_register], QUEUE_PREPEND)
                        break
                    # ==============================================================
                    # This shouldn't be called, because we are tracing a register, not field.
                    elif (instr_op_value in SGET_OPCODES) and (i == SGET_OPERAND_SOURCE_INDEX):
                        destination_register = operands[SGET_OPERAND_INDEX][1]
                        self.add_to_queue([self.trace_forward_thorough, method, idx+1,
                                        destination_register], QUEUE_PREPEND)
                        break
                    # ==============================================================
                    # This shouldn't be called, because we are tracing a register, not field.
                    elif (instr_op_value in IGET_OPCODES) and (i == IGET_OPERAND_SOURCE_INDEX):
                        destination_register = operands[IGET_OPERAND_INDEX][1]
                        self.add_to_queue([self.trace_forward_thorough, method, idx+1,
                                        destination_register], QUEUE_PREPEND)
                        break
                    # ==============================================================
                    elif (instr_op_value in APUT_OPCODES) and (i == APUT_OPERAND_SOURCE_INDEX):
                        destination_register = operands[APUT_OPERAND_INDEX][1]
                        self.add_to_queue([self.trace_forward_thorough, method, idx+1,
                                        destination_register], QUEUE_PREPEND)
                        break
                    # ==============================================================
                    elif (instr_op_value in SPUT_OPCODES) and (i == SPUT_OPERAND_SOURCE_INDEX):
                        sput_instance_field = operands[SPUT_OPERAND_INDEX][2]
                        field_analysis = self.find_field_analysis_objects(
                            sput_instance_field)

                        all_field_reads = []
                        for single_field in field_analysis:
                            list_field_read = list(single_field.xrefread)
                            for list_field_read_item in list_field_read:
                                if list_field_read_item[1] not in all_field_reads:
                                    all_field_reads.append(list_field_read_item[1])
                        for list_field_read_element in all_field_reads:
                            sget_opcode = instr_op_value + PUT_TO_GET_OFFSET
                            id_reg = self.identify_register(
                                list_field_read_element, sget_opcode, sput_instance_field, SGET_OPERAND_INDEX)
                            if id_reg != []:
                                for individual_method in id_reg:
                                    get_register_type = individual_method[0]
                                    method_index = individual_method[1]
                                    get_register_num = self.find_register_num_from_type(
                                        list_field_read_element, get_register_type)
                                    self.add_to_queue(
                                        [self.trace_forward_thorough, list_field_read_element, method_index+1, get_register_num], QUEUE_PREPEND)
                        break
                    # ==============================================================
                    elif (instr_op_value in IPUT_OPCODES) and (i == IPUT_OPERAND_SOURCE_INDEX):
                        iput_instance_field = operands[IPUT_OPERAND_FIELD_INDEX][2]
                        field_analysis = self.find_field_analysis_objects(
                            iput_instance_field)

                        all_field_reads = []
                        for single_field in field_analysis:
                            list_field_read = list(single_field.xrefread)
                            for list_field_read_item in list_field_read:
                                if list_field_read_item[1] not in all_field_reads:
                                    all_field_reads.append(list_field_read_item[1])
                        for list_field_read_element in all_field_reads:
                            iget_opcode = instr_op_value + PUT_TO_GET_OFFSET
                            id_reg = self.identify_register(
                                list_field_read_element, iget_opcode, iput_instance_field, IGET_OPERAND_INDEX)
                            if id_reg != []:
                                for individual_method in id_reg:
                                    iget_register_type = individual_method[0]
                                    method_index = individual_method[1]
                                    iget_register_num = self.find_register_num_from_type(
                                        list_field_read_element, iget_register_type)
                                    self.add_to_queue(
                                        [self.trace_forward_thorough, list_field_read_element, method_index+1, iget_register_num], QUEUE_PREPEND)
                        break
                    # ==============================================================
                    elif (instr_op_value in MOVE_OPCODES) and (i == MOVE_OPERAND_SOURCE_INDEX):
                        destination_register = operands[MOVE_OPERAND_INDEX][1]                        
                        self.add_to_queue([self.trace_forward_thorough, method, idx+1,
                                        destination_register], QUEUE_PREPEND)
                        break
                    # ==============================================================
                    elif (instr_op_value in COMPARE_OPCODES) and ((i == COMPARE_OPERAND_SOURCE1_INDEX) or (i == COMPARE_OPERAND_SOURCE2_INDEX)):
                        destination_register = operands[COMPARE_OPERAND_INDEX][1]
                        self.add_to_queue([self.trace_forward_thorough, method, idx+1,
                                        destination_register], QUEUE_PREPEND)
                        break
                    # ==============================================================
                    elif (instr_op_value in RETURN_OPCODES) and (i == RETURN_OPERAND):                        
                        return_reg_type = self.identify_register_type(num_local_registers, register_num)
                        if ((return_reg_type[0] == "p") and 
                            (self.confidence_level == CONFIDENCE_LEVEL_HIGH)):
                            self.stored_methods.append((self.trace_calling_method, method))
                        else:
                            self.add_to_queue(
                                        [self.trace_calling_method, method], QUEUE_PREPEND)
                        # Also find super class.
                        superclass_methods = self.check_for_superclass(method)
                        for superclass_method in superclass_methods:
                            if self.confidence_level == CONFIDENCE_LEVEL_HIGH:
                                self.stored_methods.append((self.trace_calling_method, superclass_method))
                            else:
                                self.add_to_queue(
                                        [self.trace_calling_method, superclass_method], QUEUE_APPEND)
                        return
                    # ==============================================================

    def check_for_superclass(self, method):
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
            interface = found_class.get_superclassname()
            if interface != method.get_class_name():
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
        

    def find_get_named_item(self, search_named_string, named_obj_idx):
        get_named_types = self.named_object_list[named_obj_idx][2]
        get_prefix = self.named_object_list[named_obj_idx][0]
        for get_named_type in get_named_types:
            get_methods = self.androguard_dx.find_methods(
                get_prefix, get_named_type, ".")
            search_term = get_prefix + "->" + get_named_type
            named_methods = []
            for get_method in get_methods:
                for element in get_method.get_xref_from():
                    named_methods.append(element[1])
            for named_method in named_methods:
                id_reg = self.identify_register(
                    named_method, INVOKE_OPCODES, search_term, 1, True)
                if id_reg != []:
                    for individual_method in id_reg:
                        register_type = individual_method[0]
                        index = individual_method[1]
                        named_string = None
                        if (register_type != ""):
                            if register_type[0] == "v":
                                named_string = self.string_search_internal(
                                    named_method, index, int(register_type[1:]))
                        if named_string == search_named_string:
                            method_instructions = named_method.get_instructions()
                            list_instructions = list(method_instructions)
                            move_instruction = list_instructions[index+1]
                            if move_instruction.get_op_value() not in MOVE_RESULT_OPCODES:
                                continue
                            move_instruction_operands = move_instruction.get_operands()
                            move_register = move_instruction_operands[0][1]
                            self.add_to_queue([self.trace_forward_thorough, named_method,
                                        index+2, move_register], QUEUE_PREPEND)


    def string_search_internal(self, method, index, register_num):
        """Search backwards for string. 
        
        Keyword arguments:
        method -- method of interest
        index -- instruction index from which to begin backtracing
        register_num -- register of interest
        """
        
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


    def instruction_index_by_offset(self, method, offset):
        """Return instruction at specified offset within method. """
        
        tally = 0
        list_instructions = list(method.get_instructions())
        for idx, instruction in enumerate(list_instructions):
            if instruction.get_length() != None:
                tally += instruction.get_length()
                if tally == offset:
                    return idx
        return -1


    def check_for_stop_conditions(self, instr_op_value, i):
        """Check for instances of register value change. """
        
        bool_stop_condition = False
        # The next conditions are all conditions where the value of our register changes due to some operation.
        # We stop our search at this point, because we may no longer be dealing with the output of getValue().
        # ==============================================================
        if (instr_op_value in CONST_DECL_OPCODES) and (i == CONST_OPERAND_INDEX):  # const declarations
            bool_stop_condition = True
        # ==============================================================
        elif (instr_op_value in NEW_ARRAY_OPCODES) and (i == NEW_ARRAY_OPERAND_INDEX):  # new-array declarations
            bool_stop_condition = True
        # ==============================================================
        elif (instr_op_value in NEW_INSTANCE_OPCODES) and (i == NEW_INSTANCE_OPERAND_INDEX):  # new-instance declarations
            bool_stop_condition = True
        # ==============================================================
        elif (instr_op_value in OPERATION_OPCODES) and (i == OPERATION_OPERAND_INDEX):
            bool_stop_condition = True
        # ==============================================================
        elif (instr_op_value in AGET_OPCODES) and (i == AGET_OPERAND_INDEX):
            bool_stop_condition = True
        # ==============================================================
        elif (instr_op_value in SGET_OPCODES) and (i == SGET_OPERAND_INDEX):
            bool_stop_condition = True
        # ==============================================================
        elif (instr_op_value in IGET_OPCODES) and (i == IGET_OPERAND_INDEX):
            bool_stop_condition = True
        # ==============================================================
        elif ((instr_op_value in IPUT_OPCODES) or (instr_op_value in APUT_OPCODES)) and (i == APUT_OPERAND_INDEX):
            bool_stop_condition = True
        # ==============================================================
        # move-result. Need to get previous
        elif (instr_op_value in MOVE_RESULT_OPCODES) and (i == MOVE_RESULT_OPERAND_INDEX):
            bool_stop_condition = True
        # ==============================================================
        elif (instr_op_value in MOVE_OPCODES) and (i == MOVE_OPERAND_INDEX):  # move-object
            bool_stop_condition = True
        # ==============================================================
        elif (instr_op_value in COMPARE_OPCODES) and (i == COMPARE_OPERAND_INDEX):
            bool_stop_condition = True

        return bool_stop_condition


    def trace_calling_method(self, method):
        """Find methods that call input method, and trace return register. """
        
        # Don't go through the method if we have already gone through it.
        if ((method in self.source_methods) and 
            (self.confidence_level == CONFIDENCE_LEVEL_LOW)):
            return
        ext_methods = self.androguard_dx.find_methods(re.escape(method.get_class_name()), re.escape(
            method.get_name()), re.escape(method.get_descriptor()))
            
        calling_methods = []
        for ext_method in ext_methods:
            for element in ext_method.get_xref_from():
                calling_methods.append(element[1])
        if calling_methods == []:
            return

        search_string = method.get_class_name() + "->" + method.get_name() + \
            method.get_descriptor()

        for path_idx, calling_method in enumerate(calling_methods):
            if self.found_crypto:
                return

            id_reg = self.identify_register(calling_method, INVOKE_OPCODES, search_string)
            if id_reg != []:
                for individual_method in id_reg:
                    register_type = individual_method[0]
                    index = individual_method[1]
                    register_num = self.find_register_num_from_type(calling_method, register_type)
                    self.add_to_queue([self.trace_forward_thorough, calling_method,
                                index+1, register_num], QUEUE_PREPEND)


    def trace_called_method(self, method, parameter_register_num):
        # Search from the beginning.
        index = 0
        instructions = None
        try:
            instructions = method.get_instructions()
        except:
            # This is probably an external method
            return

        list_instructions = list(instructions)
        num_instructions = len(list_instructions)
        instructions = None
        if (num_instructions <= 0):
            method_access_flags = method.get_access_flags()
            if (ACCESS_FLAG_ABSTRACT & method_access_flags) == ACCESS_FLAG_ABSTRACT:
                implementing_methods = self.find_implementing_methods(method)
                for implementing_method in implementing_methods:
                    if self.confidence_level == CONFIDENCE_LEVEL_HIGH:
                        self.stored_methods.append(
                            (self.trace_called_method, implementing_method, parameter_register_num))
                    else:
                        self.add_to_queue([self.trace_called_method, implementing_method,
                                    parameter_register_num], QUEUE_APPEND)
            return

        # Find register.
        (num_registers, num_local_registers,
         num_param_registers) = self.find_number_of_registers(method)
        register_id = num_local_registers + parameter_register_num
        self.add_to_queue([self.trace_forward_thorough, method,
                    index, register_id], QUEUE_APPEND)


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


    def trace_through_method(self, method):
        """Perform a "loose" search through all instructions of a method. """

        instructions = None

        try:
            instructions = method.get_instructions()
        except:
            # This is probably an external method
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

        if len(list_methods) > 1:
            pass

        return list_methods


    def find_field_analysis_objects(self, field_full_string):
        """Return a list of fields matching search string. """

        list_fields = []
        split_source = field_full_string.replace("->", " ").split()
        for single_field in self.androguard_dx.get_fields():
            if (single_field.field.get_class_name() + single_field.field.get_name() + single_field.field.get_descriptor()) == (split_source[0]+split_source[1]+split_source[2]):
                list_fields.append(single_field)
        
        ############## TOREMOVE #####################
        if ("Landroid/os/Message;" in field_full_string) and ("Landroid/os/Message;" not in self.notes):
            self.notes = self.notes + "Landroid/os/Message field[" + self.confidence_level+ "]\\"
        ######################################
        return list_fields


    def crypto_search(self, string_to_search, method):
        """Look for calls to crypto within input string. """

        ####### TOREMOVE #############
        for method_pkg in METHOD_PACKAGES:
            if (method_pkg in string_to_search) and (method_pkg not in self.notes):
                self.notes = self.notes + method_pkg + "[" + self.confidence_level + "]\\"
        ################################
        for crypto_pkg in CRYPTO_PACKAGES:
            if (crypto_pkg in string_to_search) and ("InvalidParameterException" not in string_to_search):
                self.found_crypto = True
                self.location_ble_crypto = str(method.get_class_name(
                )) + str(method.get_name()) + str(method.get_descriptor())
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