
import sublime
import sublime_plugin
import os
import time


TOTAL_TIME = 30 * 25
TICK_INTERVAL = 2
ENDING_WORDS = '快乐的时间总是过得特别快, 又到时间讲bye bye!'


def say_ending():
	if sublime.platform() == "osx":
		os.popen('say ' + ENDING_WORDS)


class LocalTime():

	def __init__(self):
		self.filename = sublime.packages_path() + "/WorkTime.cache"


	def save_time(self, time = ''):
		try:
			fp = open(self.filename, "w+")
			fp.write(str(time))
			fp.close()
		except:
			sublime.error_message("Cann't save current time to local.")


	def load_time(self):
		try:
			fp = open(self.filename)
			time = fp.read()
			fp.close()
			return time
		except:
			fp = open(self.filename, "w+")
			fp.close()
			return None



class TomatoTime():

	def __init__(self):
		self.counter         = 0
		self.thread_flag     = False
		self.status_visiable = True


	def tick(self):
		if self.thread_flag is False:
			return

		self.show_status()

		if self.chekck_finish() is True:
			say_ending()
			sublime.message_dialog("Have a rest!")
			return
		else:
			self.counter += 1

		sublime.set_timeout_async(self.tick, TICK_INTERVAL * 1000)


	def start(self):
		self.thread_flag = True
		sublime.set_timeout_async(self.tick)


	def stop(self):
		self.counter = 0
		self.thread_flag = False

		local_time.save_time()


	def resume(self, time):
		self.counter = time
		self.start()


	def stopped(self):
		return self.thread_flag


	def chekck_finish(self):
		if self.counter >= TOTAL_TIME:
			self.stop()
			return True
		return False


	def set_status_visiable(self, flag):
		self.status_visiable = flag
		if flag is False:
			sublime.status_message('')
		else:
			self.show_status()


	def get_status_visiable(self):
		return self.status_visiable


	def show_status(self):
		if self.status_visiable is False:
			return

		progress = int(self.counter / TOTAL_TIME * 100)
		msg = "|" + \
			progress * "-" + \
			"o" + \
			(100 - progress) * "-" + \
			"|"

		sublime.status_message(msg)


tomato = TomatoTime()
local_time = None


def delay_load():
	global local_time
	local_time = LocalTime()
	last_time = local_time.load_time()

	if last_time != "None":
		try:
			cur_time = int(time.time())
			result = cur_time - int(last_time)
			if result < TOTAL_TIME * TICK_INTERVAL:
				tomato.resume(result)
		except:
			pass

sublime.set_timeout_async(lambda:delay_load() , 5000)



class NewTomatoCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		local_time.save_time(int(time.time()))
		tomato.start()


	def is_visible(self):
		return not tomato.stopped()



class ShowTomatoProgressCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		tomato.set_status_visiable(True)


	def is_visible(self):
		return tomato.stopped() and not tomato.get_status_visiable()



class HideTomatoProgressCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		tomato.set_status_visiable(False)


	def is_visible(self):
		return tomato.stopped() and tomato.get_status_visiable()

