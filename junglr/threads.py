#author: johnny zhong
#prog_name thread2.py

import rate_limiter
import player
import threading
import time
import random

class update_summoner(threading.Thread):
	def __init__(self, rate_limiter, summ_name):
		threading.Thread.__init__(self)
		self.rate_limiter = rate_limiter
		self.summ_name = summ_name

	# def run(self):
	# 	sn_quit = False
	# 	while not sn_quit:
	# 		summ_name = input('provide summoner name: ')
	# 		if summ_name == 'q':
	# 			sn_quit = True
	# 			self.rate_limiter.quit()
	# 		elif summ_name != '':
	# 			self.process(summ_name)

	def run(self):
		summ = player.Player(self.summ_name)
		summ.update(self.rate_limiter)

	def process(self, summ_name):
		summ = player.Player(summ_name)
		summ.update(self.rate_limiter)
	# want to enqueue api calls to rate_limiter
	# but some api calls are dependent on if the previous is successful
	# run jobs in sequence where result of the job will enqueue the other

# purpose: player api calls incr counter
# if counter > calls at any time, self.locked = True
# all player threads will stop at any api calls until self.locked = False
class rate_limiter(threading.Thread):
	def __init__(self, calls, time_seconds):
		threading.Thread.__init__(self)

		# for locking access to this resource
		self.thread_lock = threading.Lock()
		self.cv = threading.Condition(self.thread_lock)

		# init counters and rate params
		self.stop = False
		self.time_seconds = time_seconds 
		self.calls = calls
		self.counter = 0
		self.unlocked = True
		print(str(self.calls) + ' calls per ' + str(self.time_seconds))

		# track time
		now = time.time()
		self.reset_time = now + self.time_seconds

	def run(self):
		while not self.stop:
			if time.time() >= self.reset_time: # check if enough time has elapsed to reset
				self.unlocked = True # open lock
				self.counter = 0 # reset counter
				self.reset_time = time.time() + self.time_seconds #reset to current time
				print('run reset counter at: ' + str(time.time()))

	def check_lock(self):
		exceed_call_limit = (self.counter >= self.calls)
		if exceed_call_limit:
			self.unlocked = False
			print('LOCKED!')
		while not self.unlocked or (time.time() >= self.reset_time): # loop until lock can be opened
			if time.time() >= self.reset_time: # check if enough time has elapsed to reset
				self.unlocked = True # open lock
				self.counter = 0
				self.reset_time = time.time() + self.time_seconds #reset to current time
				print('check lock reset counter at: ' + str(time.time()))
		# print(self.counter)
		return self.unlocked
		
	def quit(self):
		self.stop = True

def rl_test(rl):
	now = time.time()
	future = now + 20 #20 seconds
	while time.time() < future:
		rl.cv.acquire()
		rl.counter += 1
		rl.cv.wait_for(rl.check_lock, 10)
		rl.cv.release()
		print(rl.counter)

def main():
	rl = rate_limiter(100, 10)
	# rl.start()

	rl_test(rl)

	# update_thread = update_summoner(rate_limiter)
	# update_thread.start()
	# new_match = match_data_pull(rate_limiter)
	# new_match.start()
	# randoms = random_summoners(rate_limiter)
	# randoms.start()


if __name__ == '__main__':
	main()
