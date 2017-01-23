#author: johnny zhong
#date: 9/10/16

import queue
import threading
import time

# class for processing multiple objects at a limit
# speed of calls is determined by calls per time in seconds.
# need to somehow return result of function call

class task_processing(threading.Thread):
	def  __init__(self, q_size, calls, time_seconds, lock_timeout = 10):
		threading.Thread.__init__(self)

		# preparing queue and queue threading
		self.q = queue.Queue(q_size)
		queue_lock = threading.Lock()
		self.cv = threading.Condition(queue_lock)
		
		# accepting externally set parameters
		self.time_seconds = time_seconds 
		self.calls = calls
		self.lock_timeout = lock_timeout

		# init counter to track calls
		self.counter = 0 
		self.stop = False

		#set timer, which tracks time to reset counter
		now = time.time()
		self.reset_time = now + self.time_seconds

	# runs while-loop that runs the jobs queued
	def run(self):
		while not self.stop:
			if not self.q.empty():
				self.cv.acquire()
				params = self.q.get()
				self.cv.wait_for(self.check_lock, self.lock_timeout)
				self.cv.release()
				print(time.time())
				func, args, add_counter, kwargs = params['func'], params['args'], params['add_counter'], params['kwargs']
				# self.ret(func, args, kwargs)
				func(*args, **kwargs)
				if add_counter:
					self.counter += 1

	# the rate limiter, which checks the elapsed time and the number of calls made
	# when the limit on calls is reached and it is not yet time to reset
	# this function locks the queue until it is time to reset.
	# otherwise, processing is not locked. 
	def check_lock(self):
		unlocked = True
		exceed_call_limit = (self.counter >= self.calls - 1)
		if exceed_call_limit:
			print(self.counter)
			unlocked = False
		while not unlocked or (time.time() >= self.reset_time): # loop until lock can be opened
			if time.time() >= self.reset_time: # check if enough time has elapsed to reset
				unlocked = True # open lock
				self.counter = 0
				self.reset_time = time.time() + self.time_seconds #reset to current time
		return unlocked
		
	# add functions to the queue
	def enq(self, func, *args, add_counter = True, **kwargs):
		to_process = {'func':func, 'add_counter': add_counter, 'args':args, 'kwargs':kwargs}
		self.q.put(to_process)
		
	# submit a stop command to the queue
	def enq_stop(self):
		self.q.put({'func':self.imm_stop, 'add_counter': False, 'args':(), 'kwargs':{}})

	#immediately stops task processing.
	def imm_stop(self):
		self.stop = True
	
