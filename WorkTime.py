
import sublime
import sublime_plugin
import os
import time


DELAY_TIME = 1
DEFAULT_TOMATO_TIME = 25
TICK_INTERVAL = 1
ENDING_WORDS = '快乐的时间总是过得特别快, 又到时间讲bye bye!'
CACHE_FILE_PATH = "/WorkTime.cache"
WORKTIME_SETTINGS = "WorkTime.sublime-settings"

# ------------------------------------------------------------------------------
# Setting
# ------------------------------------------------------------------------------
class WorkTimeDo():
	def __init__(self):
		self.settings = sublime.load_settings(WORKTIME_SETTINGS)
		self.filename = sublime.packages_path() + CACHE_FILE_PATH

	def get_config(self, key, default):
		return self.settings.get(key,default)

	def say_ending(self):
		if sublime.platform() == "osx":
			os.popen('say ' + ENDING_WORDS)

	def save_time(self, time = None):
		try:
			fp = open(self.filename, "w+")
			fp.write(time)
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

	def clear_time(self):
		self.save_time('')

# ------------------------------------------------------------------------------
# Tomato
# ------------------------------------------------------------------------------
class Tomato(WorkTimeDo):

	def __init__(self):
		super(Tomato, self).__init__()
		self.total_time = self.get_config("tomato_time", DEFAULT_TOMATO_TIME) * 60
		self.counter = 0
		self.actived = False
		self.status_visiable = True
		self.check_last_time()

	def start(self, start_time = 0):
		self.counter = start_time
		self.actived = True
		# self.total_time = self.get_config("tomato_time", DEFAULT_TOMATO_TIME) * 60
		self.save_time(str(time.time()))

	def stop(self):
		self.counter = 0
		self.actived = False
		self.clear_time()
		self.say_ending()
		sublime.message_dialog("Have a rest!")


	def update(self):
		self.counter += 1
		self.show_progress()
		if self.counter >= self.total_time:
			self.stop()

	def is_actived(self):
		return self.actived

	def set_status_visiable(self, flag):
		self.status_visiable = flag
		self.show_progress()
	
	def get_status_visiable(self):
		return self.status_visiable

	def show_progress(self):
		if self.status_visiable is False:
			sublime.status_message('')
			return

		progress = int(self.counter / self.total_time * 100)
		msg = "|" + \
			progress * "-" + \
			"o" + \
			(100 - progress) * "-" + \
			"|"

		sublime.status_message(msg)


	def check_last_time(self):
		last_time = self.load_time()
		try:
			last_time = float(last_time)
		except:
			self.clear_time()
			return

		cur_time = time.time()
		result = cur_time - last_time
		if result >= self.total_time:
			self.clear_time()
		else:
			self.start(int(result))



class Tick():

	def __init__(self):
		self.thread_flag = False

	def callback(self):
		if not self.thread_flag: return

		if tomato.is_actived():
			tomato.update()

		sublime.set_timeout_async(self.callback, 1000)

	def start(self):
		self.thread_flag = True
		self.callback()

	def stop(self):
		self.thread_flag = False


def delay():
	global tomato
	global tick
	tomato = Tomato()
	tick = Tick() 
	tick.start()

sublime.set_timeout_async(lambda:delay(), DELAY_TIME * 1000)
# ------------------------------------------------------------------------------
# Tomato
# ------------------------------------------------------------------------------
class NewTomatoCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		tomato.start()

	def is_visible(self):
		return not tomato.is_actived()



class ShowTomatoProgressCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		tomato.set_status_visiable(True)

	def is_visible(self):
		 return tomato.is_actived() and not tomato.get_status_visiable()



class HideTomatoProgressCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		tomato.set_status_visiable(False)

	def is_visible(self):
		 return tomato.is_actived() and tomato.get_status_visiable()

