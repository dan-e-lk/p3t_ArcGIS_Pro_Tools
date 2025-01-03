
import arcpy
import datetime


class Print2:
	def __init__(self, logfile_path):
		# start a new txt file
		self.log = open(logfile_path,'w')

		# start logging
		datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		self.log.write("Logging Start Time: ")
		self.log.write(str(datetime_now)) # start the log text with current date/time.

	def print2(self, msg, level = 'i'):
		""" print, arcmap AddMessage and return string all in one!"""
		# print(msg)
		msg = str(msg)
		if level == 'i':
			arcpy.AddMessage(msg)
			self.log.write('\n' + msg)
		elif level == 'w':
			arcpy.AddWarning(msg)
			self.log.write('\n!WARNING: ' + msg)

	def log_close(self):
		datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		self.log.write("\n\nLogging End Time: ")
		self.log.write(str(datetime_now))
		self.log.close()


# use case example: AR_AR.py, Caribou_Habitat_Classification.py
# only works on arc





# below is not really being used right now. Print2 is being used more often for simplicity sake.
class Log():
	"""
	when building arcmap tools we need a module to print message both on console and arcmap message window.
	you can also set the logging level to have more messages printed out only during debug mode.
	"""
	def __init__(self, logging_level, disp_time_n_lvl = True, print_or_return = 'print'):
		"""
		logging_level should be one of ['DEBUG','INFO','WARNING','ERROR','CRITICAL']
		print_or_return should be one of ['print','write','both']
		if chosen 'print', the logger module will print out the message on ArcMap progress window (along with date and time) but won't return the message.
		if chosen 'return', the logger module will not print out the message but will return the message. This return value can be used to create your own log file.
		if chosen 'both, the logger module will both print out and return the message. This may result in double printing on some console.'
		You can choose not to display time and logging level if you set disp_time_n_lvl = False.
		"""

		self.disp_time_n_lvl = disp_time_n_lvl
		self.level_dict = {'DEBUG': 10,'INFO':20,'WARNING':30,'ERROR':40,'CRITICAL':50}
		self.cutoff_level = self.level_dict[logging_level]

		# all_msg stores all msg regardless of the level
		# you can use this to print out your logfile at the end of the script
		self.all_msg = ''

		self.iprint = True
		self.ireturn = True
		if print_or_return == 'print':
			self.ireturn = False
		if print_or_return == 'return':
			self.iprint = False

	def logger(self, msg,level='INFO'):
		current_level = self.level_dict[level]
		new_msg = self.msg_editor(msg, level)
		self.all_msg += new_msg + '\n'

		if current_level >= self.cutoff_level:

			if self.iprint:
				print(new_msg)
				if current_level == 50:
					arcpy.AddError(msg)
				elif current_level >= 30:
					arcpy.AddWarning(msg)
				else:
					arcpy.AddMessage(msg)

			if self.ireturn: return new_msg

	def msg_editor(self, msg, level):
		if self.disp_time_n_lvl:
			datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') # eg. '2018.09.07 14:41:13.659'
			new_msg = '%s - %s - %s'%(datetime_now, level, msg)
			return new_msg
		else:
			return msg




# if __name__ == '__main__':
# 	# this is an example of how you would use this script:
# 	# you must first create an instance of this log class with level setting
	
# 	print("\n*************** TEST 1 ***************\n")
# 	test1 = Log('WARNING') # level is set to WARNING. print_or_return is set to 'print' by default. # this means that DEBUG or INFO messages won't get printed out.

# 	test1.logger("test1 - This message won't get printed out because it's at level DEBUG", 'DEBUG')
# 	test1.logger("test1 - This message won't get printed out because it's at level INFO") # logger is set to INFO by default, so no need to specify it.
# 	test1.logger("test1 - This message will get printed out on both console and arcmap because it's at WARNING level", 'WARNING')
# 	test1.logger("test1 - This message will get printed out on both console and arcmap because it's at CRITICAL level.", 'CRITICAL')
# 	z = test1.logger("test1 - This message will be printed out on both console and arcmap but won't be stored in variable z")
# 	print('printing z: %s'%z) # should print out "printing z: None"



# 	print("\n\n*************** TEST 2 ***************\n")
# 	test2 = Log('INFO','return') # print_or_return is set to return only. this instance will not print anything unless you use print function.
# 	a = test2.logger("test2 - This message string is from variable a")
# 	b = test2.logger("test2 - This message string is from variable b")
# 	print('printing a and b:\n%s   %s'%(a,b))




# 	print("\n\n*************** TEST 3 ***************\n")
# 	test3 = Log('DEBUG','both',False) # test3 will both print and return the messages. It will also NOT display time and level.
# 	c = test3.logger("test3 - This will be stored in variable c and will be printed at the same time")
# 	test3.logger("test3 - This message should be printed out at error level", "ERROR")
# 	print('printing variable c: %s'%c)


# 	# alternatively, you can return all messages regardless of level or print_or_return setting by calling all_msg instance variable
# 	print("\n\n*************** TEST 4 ***************\n")	
# 	print("Let's print all the logger messages out regardless of all settings!\n")
# 	print(test1.all_msg)
# 	print(test2.all_msg)
# 	print(test3.all_msg)
# 	# arcpy.AddMessage(test1.all_msg + test2.all_msg + test3.all_msg)
	
