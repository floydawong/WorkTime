
import sublime
import sublime_plugin


def play_sound():
	# import os  
	# os.popen2('aplay -q' + soundFile)  
	# os.popen2('open 1.mp3')
	pass


class TomatoTime():

	def __init__(self):
		self.total_time      = 0
		self.finish_time     = 30 * 25
		self.tick_interval   = 2000
		self.thread_flag     = False
		self.status_visiable = True


	def tick(self):
		if self.thread_flag is False:
			return

		self.show_status()

		if self.chekck_finish() is True:
			sublime.message_dialog("Have a rest!")
			return
		else:
			self.total_time += 1

		sublime.set_timeout_async(self.tick, self.tick_interval)


	def start(self):
		self.thread_flag = True
		self.resume()


	def stop(self):
		self.total_time = 0
		self.thread_flag = False


	def resume(self):
		sublime.set_timeout_async(self.tick, 0)


	def stopped(self):
		return self.thread_flag


	def chekck_finish(self):
		if self.total_time >= self.finish_time:
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

		progress = int(self.total_time / self.finish_time * 100)
		msg = "|" + \
			progress * "-" + \
			"o" + \
			(100 - progress) * "-" + \
			"|"

		sublime.status_message(msg)


tomato = TomatoTime()


class NewTomatoCommand(sublime_plugin.TextCommand):

	def run(self, edit):
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



