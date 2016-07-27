
import pygame

from lib import pyg, tools,  grid


class MyApp(pyg.App):

	def __init__(self):
		pyg.App.__init__(self)
		
		dblue = pygame.Color(200,200,255)
		lblue = pygame.Color(250,250,255)
		dgrey = pygame.Color("grey")
		lgrey = pygame.Color("lightgrey")
		
		self.land = grid.Grid(40,19,10, (10,10), lc=dblue, bg=lblue)
		self.ca = grid.GridCA(19,19,10, (430,10), lc=lgrey, bc=dgrey)
		
		self.land.model.set((2, 2), 1)
		
		self.dragger = tools.Dragger()
		
		self.timerIndicator = False
		self.setTimer("ca.clock", 250)
		
	def onTimer(self, name, event):
		if "ca.clock" == name:
			if not self.ca.hit(pygame.mouse.get_pos()):
				self.ca.step()
				self.timerIndicator = not self.timerIndicator
				self.update()
				
	def onEvent(self, event):
	
		pyg.App.onEvent(self, event)
		
		if event.type == pygame.locals.MOUSEMOTION:
		
			self.ca.onMouseMove(event)
			
			if self.dragger.grabbing():
				self.ca.onMouseDrag(event, self.dragger.button)
				
		elif event.type == pygame.locals.MOUSEBUTTONDOWN:
		
			if event.button == 1:
				self.ca.onMouseSet(event)
				self.dragger.grab(event.button)
				
			if event.button == 2:
				self.ca.ca.reset()
				
			if event.button == 3:
				self.ca.onMouseClear(event)
				self.dragger.grab(event.button)
				
		elif event.type == pygame.locals.MOUSEBUTTONUP:
		
			self.dragger.drop()
			
		return True
			
	def onDraw(self):
		self.land.draw(self.screen)
		self.ca.draw(self.screen)
		
		self.drawTimerIndicator(self.screen)
		
	def drawTimerIndicator(self, surf):
		c = pygame.Color("lightgrey")
		r = (10,280,10,10)
		
		if self.timerIndicator:
			pygame.draw.rect(surf, c, r)
		else:
			pygame.draw.rect(surf, c, r, 1)
			


if "__main__" == __name__:
	a = MyApp()
	a.run()
