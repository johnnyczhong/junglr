#author: johnny
#prog_name: threads.py

from player_api import Player
import queue
import threading
import time


q = queue.Queue(10)
queue_lock = threading.Lock()
cv = threading.Condition(queue_lock)


# thread to handle stdin
# starts thread that waits for user input, then passes on player object to the queue
# 
class get_summoner_name(threading.Thread):
	def __init__(self, q):
		threading.Thread.__init__(self)
		self.q = q

	#get stdin from user, add player object to queue
	def run(self):
		print('starting name thread')
		quit = False
		while not quit:
			summ_name = input('provide summoner name: ')
			cv.acquire()
			if summ_name == 'quit':
				quit = True
			q.put(Player(summ_name))
			cv.release()
		print('stopping name thread')

# thread object that gets and prints name data member of player object in queue
# has timer and counter for rate limiting
# currently prints at 1 second intervals.
# goal is for a thread which gets and makes api calls
class print_1sec_interval(threading.Thread):
	def  __init__(self, q):
		threading.Thread.__init__(self)
		self.q = q
		self.c = 0

	def run(self):
		print('starting print thread')
		quit = False
		now = time.time() # current time
		self.reset_time = now + 1 # time to reset
		while not quit:
			# does this need to reference the global name?
			# I thought all python values were passed by ref
			cv.acquire()
			if not self.q.empty():
				name = self.q.get().summ_name
				if name == 'quit':
					quit = True
					print('quitting! next print should be quit')
				cv.wait_for(self.check_lock, 5) # max timeout of 5s
				print(name)
				self.c += 1
				print(self.c)
			cv.release()
		print('stopping print thread')

	def check_lock(self):
		unlocked = True
		if self.c >= 1: # 1 req per second for testing
			unlocked = False
			# print('locked')
		while not unlocked or (time.time() >= self.reset_time): # loop until lock can be opened
			if time.time() >= self.reset_time: # check if enough time has elapsed to reset
				unlocked = True # open lock
				self.c = 0 # reset counter
				self.reset_time = time.time() + 1 #reset to current time
				# print('unlocked')
		return unlocked


if __name__ == '__main__':
	summ_thread = get_summoner_name(q)
	print_thread = print_1sec_interval(q)

	summ_thread.start()
	print_thread.start()

	summ_thread.join()
	print_thread.join()
