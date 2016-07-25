import os
import pygame, pygame.locals
import abs


@abs.Singleton
class UserEventIndex(object):
	def __init__(self):
		self.nextIndex = pygame.USEREVENT

	def getNext(self):
		index = self.nextIndex
		self.nextIndex += 1
		return index


def UserEvent(cls):
	"""usage:

			@UserEvent
			class MyEvent1(object): pass

			@UserEvent
			class MyEvent2(object): pass

			myEvent2 = MyEvent2()
			myEvent2.post(action="something", arg1="arg1", extra="extra")
	"""
	@classmethod
	def make(cls, *args, **kwargs):
		return pygame.event.Event(cls.TYPE, *args, **kwargs)

	@classmethod
	def post(cls, *args, **kwargs):
		event = cls.make(*args, **kwargs)
		pygame.event.post(event)

	setattr(cls, "make", make)
	setattr(cls, "post", post)
	setattr(cls, "TYPE", UserEventIndex().getNext())

	return cls


@abs.Singleton
class App(object):
	UPDATE_TIMER_ID = "__update__"

	def __init__(self, size=(640,300), pos=None, bg=(255,255,255), title="",
		initMixer=True, resizable=False, bestDepth=True, noFrame=False,
		quitOnEscape=True):

		self.quitOnEscape = quitOnEscape

		self.bg = bg

		self.running = False
		self.timers = {}

		if initMixer:
			pygame.mixer.pre_init(44100, -16, 2, 512) # must come before pygame.init()!

		if isinstance(pos, tuple) and len(pos) == 2 and pos[0] >= 0 and pos[1] >= 0:
			os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % pos

		pygame.init()

		if initMixer:
			pygame.mixer.init()
			pygame.mixer.set_num_channels(10)


		flags = pygame.DOUBLEBUF | (pygame.RESIZABLE if resizable else 0) | (pygame.NOFRAME if noFrame else 0)
		depth = 0 if bestDepth else 32

		self.screen = pygame.display.set_mode(size, flags, depth)

		pygame.display.set_caption(title)

	@classmethod
	def getNextUserEvent(cls):
		return UserEventIndex().getNext()

	def postQuitEvent(self):
		pygame.event.post(pygame.event.Event(pygame.locals.QUIT))

	def setTimer(self, name, msec=0):
		if name not in self.timers:
			self.timers[name] = self.getNextUserEvent()

		pygame.time.set_timer(self.timers[name], msec)

	def setUpdateTimer(self, msec=0):
		self.setTimer(self.UPDATE_TIMER_ID, msec)

	def onUpdateTimer(self):
		return True

	def onTimer(self, name, event):
		if name == self.UPDATE_TIMER_ID:
			return self.onUpdateTimer()

	def onQuitEvent(self, event):
		self.running = False
		return True

	def onEvent(self, event):
		"""Return True if you want update() to be called. Or call update()
			manually.
		"""
		return False

	def onDraw(self):
		pass

	def saveScreenShot(self, path, force=False):
		if not force and os.path.exists(path):
			raise Exception, "screenshot file already exists"

		pygame.image.save(self.screen, path)

	def onEraseBackground(self):
		self.screen.fill(self.bg)

	def update(self):
		"""Don't call this from within onDraw().
		"""
		self.onEraseBackground()
		self.onDraw()
		pygame.display.update()

	def run(self):
		self.running = True

		while self.running:
			event = pygame.event.wait()

			update = False
			handled = False

			if event.type >= pygame.USEREVENT:
				for k,v in self.timers.items():
					if event.type == v:
						result = self.onTimer(k, event)
						update = update or result

						handled = True
						break

			elif event.type == pygame.locals.VIDEOEXPOSE:
				update = True

			elif event.type == pygame.locals.QUIT:
				result = self.onQuitEvent(event)
				update = update or result
				handled = True

			elif event.type == pygame.locals.KEYDOWN:
				if event.key == pygame.locals.K_ESCAPE:
					if self.quitOnEscape:
						self.postQuitEvent()
						update = True

			#elif event.type == pygame.locals.ACTIVEEVENT: update = True
			#elif event.type == pygame.locals.VIDEORESIZE: update = True

			if not handled:
				result = self.onEvent(event)
				update = update or result

			if update:
				self.update()


class Text(object):
	def __init__(self, face="arial", h=24, text="",
		fg=pygame.Color("black"), bg=None):
		self.font = pygame.font.SysFont(face, h)
		self.fg = fg
		self.bg = bg
		self.aa = True
		self.img = None

		self.set(text)

	def set(self, text):
		if self.bg:
			self.img = self.font.render(text, self.aa, self.fg, self.bg)
		else:
			self.img = self.font.render(text, self.aa, self.fg)

	def draw(self, surf, pos):
		surf.blit(self.img, pos)

