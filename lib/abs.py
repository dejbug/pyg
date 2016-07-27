import types


def deprecated(cls): return cls


class ContextManager(object):
	def __init__(self, methods):
		assert isinstance(methods, (str, unicode))
		assert " " in methods

		self.om, self.cm = methods.split(" ")

	def __call__(self, cls):
		setattr(cls, "__enter__", lambda obj: getattr(cls, self.om)(obj))
		setattr(cls, "__exit__", lambda obj, x, m, t: getattr(cls, self.cm)(obj))

		return cls


def Singleton(cls):
	@staticmethod
	def __new(_cls, *args, **kwargs):
		if not _cls._obj:
			_cls._obj = super(cls, _cls).__new__(_cls)
		else:
			setattr(_cls, "__init__", lambda self, *args, **kwargs: None)

		return _cls._obj

	setattr(cls, "_obj", None)
	setattr(cls, "__new__", __new)

	return cls


class Tupelable(object):
	def __init__(self, attributes=""):
		self.attributes = attributes.split(" ")

	def __call__(self, obj):
		for a in self.attributes:
			setattr(obj, a, None)

		def _init(this, *args, **kwargs):
			for i in xrange(min(len(self.attributes), len(args))):
				setattr(this, self.attributes[i], args[i])

			for k, v in kwargs:
				if k in self.attributes:
					setattr(this, k, v)


		setattr(obj, "__init__", _init)
		setattr(obj, "__getitem__", lambda this, key: getattr(this, key))
		setattr(obj, "__setitem__", lambda this, key, val: setattr(obj, key, val))

		def _str(this):
			ss = []
			for a in self.attributes:
				# add quote to strings
				vv = getattr(this, a)
				vf = "'%s'" if isinstance(vv, (str, unicode)) else "%s"
				v = vf % vv

				s = "%s=%s" % (a, v)
				ss.append(s)
			return "%s(%s)" % (type(this).__name__, ", ".join(ss))
		setattr(obj, "__str__", _str)

		return obj


class Listable(object):
	def __init__(self, seqname="data"):
		self.seqname = seqname

	def __call__(self, obj):
		setattr(obj, "__iter__", lambda this: this.__dict__[self.seqname].__iter__())
		setattr(obj, "__len__", lambda this: this.__dict__[self.seqname].__len__())
		setattr(obj, "__nonzero__", lambda this: this.__dict__[self.seqname].__len__() > 0)
		setattr(obj, "__getitem__", lambda this, key: this.__dict__[self.seqname].__getitem__(key))
		return obj


class Stackable(object):
	def __init__(self, key=None):
		self.key = key

	def __call__(self, cls):
		key = lambda obj: obj.__dict__[self.key]

		def none(obj, *args, **kwargs):
			return None

		def last(obj):
			if not key(obj): return None
			return key(obj)[-1]

		def pop(obj):
			if not key(obj): return None
			return key(obj).pop()

		def push(obj, item):
			key(obj).append(item)

		setattr(cls, "push", lambda obj, item: push(obj, item) if self.key else none)
		setattr(cls, "pop", lambda obj: pop(obj) if self.key else none)
		setattr(cls, "last", lambda obj: last(obj) if self.key else none)

		return cls


class O(object):
	"""Transforms a dictionary into an object."""
	def __init__(self, d):
		self.__dict__.update(d)

	def __getitem__(self, key):
		return self.__dict__.__getitem__(key)

	def __str__(self):
		return str(self.__dict__)


class Match(O):
	"""Transforms a 're.MatchObject' into an object (i.e. makes its
	groups accessible via the dot operator)."""
	def __init__(self, r):
		O.__init__(self, r.groupdict() if r else {})


class ExplicitMatch(Match):
	"""Instead of translating all the groups in the MatchObject, only those
	whose labels are specified in the argument list are considered.

	Instead of a simple string argument also a tuple can be passed where
	the first element is the label, the second an optional transformation
	function (which is to be applied to the matched group referenced by that
	label), and an optional default value in case the group wasn't matched
	(overriding the global default value, if present).

	Also a global default value can be specified with the keyword parameter
	'default=<value>'.
	"""

	def __init__(self, r, *args, **kwargs):
		Match.__init__(self, None)

		# Save the global default value if passed. Default to 'None'.
		self.default = kwargs['default'] if 'default' in kwargs else None

		# We're only interested in the dictionary of named groups in
		# the MatchObject.
		groups = r.groupdict() if r else {}

		# Skip this if no argument were passed.
		for arg in args:
			# A simple string was passed, so commit the group with that label.
			if isinstance(arg, types.StringTypes):
				self.__dict__[arg] = groups[arg] if arg in groups else self.default

			# A tuple was passed...
			elif isinstance(arg, tuple):
				# ...so first determine which elements are present.
				key 	= arg[0] if len(arg) > 0 else None
				cast	= arg[1] if len(arg) > 1 else None
				default	= arg[2] if len(arg) > 2 else self.default

				# Skip this if the required first element is missing.
				if key:
					# Is the group present? Default to either the specific
					# default or the global default or 'None'.
					lexeme = groups[key] if key in groups else default
					# Transform.
					if cast:
						lexeme = cast(lexeme)
					# Commit.
					self.__dict__[key] = lexeme


class Array(object):
	"""Defines standard array operations. To be used as a base class."""

	def __init__(self, data=[], name=None):
		"""The various array operations will need to access the subclass'
		internal data. Pass the getter function for that data into
		the 'callback' argument."""
		assert isinstance(data, list)
		self._name = name or "data"
		self.__dict__[self._name] = data or []

	def get(self):
		return self.__dict__[self._name]

	def set(self, data=[]):
		self.__dict__[self._name] = data

	def clr(self):
		self.set([])

	def __nonzero__(self):
		return self.get().__nonzero__()

	def __len__(self):
		return self.get().__len__()

	def __iter__(self):
		return self.get().__iter__()

	def __getitem__(self, key):
		return self.get().__getitem__(key)

	def __setitem__(self, key, value):
		return self.get().__setitem__(key, value)

	def __delitem__(self, key):
		return self.get().__delitem__(key)

	def __contains__(self, value):
		return self.get().__contains__(value)

	def append(self, value):
		return self.__dict__[self._name].append(value)



class CallbackManager(object):
	def __init__(self):
		self.callbacks = {}
		self.listeners = []

	def AddCallback(self, name, callback):
		"""Add individual functions implementing a single callback interface method."""
		self.callbacks.update({name:callback})

	def AddListener(self, listener):
		"""Add objects implementing the full callback interface."""
		self.listeners.append(listener)

	def Notify(self, name, *args, **kwargs):
		self.NotifyListeners(name, *args, **kwargs)
		self.NotifyCallbacks(name, *args, **kwargs)

	def NotifyListeners(self, name, *args, **kwargs):
		for listener in self.listeners:
			if name not in listener.__class__.__dict__:
				raise KeyError("Callback '%s' not found in listener '%s'." % (name, listener))
			listener.__class__.__dict__[name](*args, **kwargs)

	def NotifyCallbacks(self, name, *args, **kwargs):
		callbacks = [callback for _name, callback in self.callbacks if _name == name]
		for callback in callbacks:
			callback(*args, **kwargs)


class Flags(object):
	def __init__(self, flags=0):
		self.flags = flags

	def SetFlags(self, flags):
		self.flags = flags

	def GetFlags(self):
		return self.flags

	def SetFlag(self, mask, flag, on=True):
		self.flags = (self.flags &~ mask) | (flag if on else 0)

	def GetFlag(self, mask):
		return self.flags & mask

	def HasFlag(self, mask, flag):
		return self.flags & mask == flag


class objdict(dict):
# [ source:] http://goodcode.io/articles/python-dict-object/
	def __getattr__(self, name):
		if name in self:
			return self[name]
		else:
			raise AttributeError("No such attribute: " + name)

	def __setattr__(self, name, value):
		self[name] = value

	def __delattr__(self, name):
		if name in self:
			del self[name]
		else:
			raise AttributeError("No such attribute: " + name)

