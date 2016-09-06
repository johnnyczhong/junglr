#author: johnny
#prog_name: threads.py

# thread-1: accept user input, spawns player threads
# thread-2: rate limiter control
# thread-n: player threads, run function that makes api_calls

from player_api import Player
import queue
import threading
import time

player_q = queue.Queue(10)
queue_lock = threading.Lock()
cv = threading.Condition(queue_lock)

# thread to handle stdin
# starts thread that waits for user input, then passes on player object to the queue
class get_summoner_name(threading.Thread):
	def __init__(self, q):
		threading.Thread.__init__(self)
		self.q = q

	#get stdin from user, add player object to queue
	def run(self):
		print('starting name thread')
		sn_quit = False
		while not sn_quit:
			summ_name = input('provide summoner name: ')
			cv.acquire()
			if summ_name == 'q':
				sn_quit = True
			self.q.put(summ_name)
			cv.release()
		print('stopping name thread')

# thread object that gets and prints name data member of player object in queue
# has timer and counter for rate limiting
# currently prints at 1 second intervals.
# goal is for a thread which gets and makes api calls
class player_processing(threading.Thread):
	def  __init__(self, q):
		threading.Thread.__init__(self)
		self.q = q
		self.delay = 5 #seconds per reset
		self.call_limit = 1 # calls before reset
		self.counter = 0
		self.summ = None

	def run(self):
		print('starting api thread')
		self.quit = ''
		now = time.time() # current time
		self.reset_time = now + self.delay # time to reset
		while self.quit != 'q':
			if not self.q.empty():
				cv.acquire()
				self.summ = Player(self.q.get())
				self.quit = self.summ.summ_name
				if self.quit == 'q':
					break
				cv.release()
				self.update()
		print('stopping api thread')

	def update(self):
		print('processing: ' + self.summ.summ_name)
		run_seq = [self.summ.set_ranked_mains, 
			self.summ.set_league]
		cv.wait_for(self.check_lock, 5) # max timeout of 5s
		action = self.summ.basic_update()
		self.counter += 1
		if action != 'no action':
			for func in run_seq:
				cv.acquire()
				cv.wait_for(self.check_lock, 5)
				func()
				self.counter += 1
				print(time.time())
				cv.release()
			self.summ.push_db_update()
		print('done processing ' + self.summ.summ_name)

	def check_lock(self):
		unlocked = True
		exceed_call_limit = (self.counter >= self.call_limit)
		if exceed_call_limit:
			unlocked = False
		while not unlocked or (time.time() >= self.reset_time): # loop until lock can be opened
			if time.time() >= self.reset_time: # check if enough time has elapsed to reset
				unlocked = True # open lock
				self.counter = 0
				self.reset_time = time.time() + self.delay #reset to current time
		return unlocked

if __name__ == '__main__':
	processing = player_processing(player_q)
	get_name = get_summoner_name(player_q)

	get_name.start()
	processing.start()

	get_name.join()
	processing.join()
