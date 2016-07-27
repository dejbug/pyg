import pygame


class Dragger(object):
#TODO: implement auto-drop (after a timeout) so the system
#	doesn't freeze?

	def __init__(self):
		self.button = None
		
	def __del__(self):
		self.drop()
		
	def grabbing(self):
		return pygame.event.get_grab()
		
	def grab(self, button=None):
		if not self.grabbing():
			self.button = button
			pygame.event.set_grab(True)
			
	def drop(self):
		if self.grabbing():
			self.button = None
			pygame.event.set_grab(False)


