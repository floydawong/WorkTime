
import sublime
import sublime_plugin
import os, time, re, copy


DELAY_TIME = 1
TICK_INTERVAL = 1
DEFAULT_TOMATO_TIME = 25
TASK_FILE = "Task.wkt"
PACKAGE_NAME = "/WorkTime/"
CACHE_FILE_PATH = "WorkTime.cache"
WORKTIME_SETTINGS = "WorkTime.sublime-settings"

# ------------------------------------------------------------------------------
# Setting
# ------------------------------------------------------------------------------
class WorkTimeDo():
	def __init__(self):
		self.settings = sublime.load_settings(WORKTIME_SETTINGS)
		self.filename = sublime.packages_path() + PACKAGE_NAME + CACHE_FILE_PATH

	def get_config(self, key, default):
		return self.settings.get(key,default)

	def say_ending(self):
		if sublime.platform() == "osx":
			os.popen('say ' + self.get_config("ending_words"))

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

# ------------------------------------------------------------------------------
# Task
# ------------------------------------------------------------------------------
TASK_TIME_PATTERN = r"\#\s?((1|0?)[0-9]|2[0-3]):([0-5][0-9])\s?"
TASK_DESC_PATTERN = r"\#\s?.+\s?"

def parse_time(line):
	pattern = re.compile(TASK_TIME_PATTERN)
	match = pattern.match(line)
	if match :
		time = match.groups()
		return "%s:%s" % (time[0], time[2])


def parse_desc(line):
	pattern = re.compile(TASK_DESC_PATTERN)
	match = pattern.match(line)
	if match :
		line = line.replace('#', '')
		return line


def parse_wkt(name):
	fp = None
	try:
		fp = open(name)
	except:
		sublime.error_message("Cann't open %s" % TASK_FILE)
		return

	task_list = []
	index = -1

	for line in fp.readlines():
		task_time = parse_time(line)
		if task_time:
			index += 1
			task_list.append({})
			task_list[index]["time"] = task_time
			task_list[index]["desc"] = ""
			continue

		desc = parse_desc(line)
		if desc:
			task_list[index]["desc"] = desc

	fp.close()
	task.register(task_list)



class Task():

	def __init__(self):
		self.task_list = []
		self.cache_task = []
		self.actived = False

	def register(self, task_list):
		self.task_list = task_list
		self.cache_task = copy.deepcopy(self.task_list)

		if len(self.task_list) is 0:
			self.actived = False
		else:
			self.actived = True

	def is_actived(self):
		return self.actived

	def update(self):
		s = time.strftime("%H:%M", time.localtime()) 
		for info in self.cache_task:
			task_time = info.get("time")
			if task_time == s:
				sublime.message_dialog(task_time + "\n" + info.get("desc"))
				self.cache_task.remove(info)
		
				if len(self.cache_task) == 0:
					sublime.message_dialog("Complete all the tasks.")

# ------------------------------------------------------------------------------
# Tick
# ------------------------------------------------------------------------------
class Tick():

	def __init__(self):
		self.thread_flag = False

	def callback(self):
		if not self.thread_flag: return

		if tomato.is_actived():
			tomato.update()

		if task.is_actived():
			task.update()
		sublime.set_timeout_async(self.callback, 1000)

	def start(self):
		self.thread_flag = True
		self.callback()

	def stop(self):
		self.thread_flag = False



def delay():
	global tomato
	global task
	global tick
	tomato = Tomato()
	task = Task()
	parse_wkt(sublime.packages_path() + PACKAGE_NAME + TASK_FILE)
	tick = Tick() 
	tick.start()

sublime.set_timeout_async(lambda:delay(), DELAY_TIME * 1000)

# ------------------------------------------------------------------------------
# Tomato Command
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

# ------------------------------------------------------------------------------
# Task Command
# ------------------------------------------------------------------------------
class OpenWorkTimeNoteCommand(sublime_plugin.WindowCommand):

	def run(self):
		view = self.window.open_file(TASK_FILE)



class WorkTimeEventCommand(sublime_plugin.EventListener):

	def on_post_save(self, view):
		if view.file_name().find(TASK_FILE) < 0:
			return
		parse_wkt(view.file_name())


