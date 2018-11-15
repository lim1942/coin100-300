import traceback

class a(object):
	aa = 5

	def __init__(self,e):
		self.e = e
		self.b=1
		self.c=2
		self.d=3
		self.aa=4
		print(type(self))

	@classmethod
	def _print(cls):
		print(type(cls))
		print(cls.aa)

	@staticmethod
	def _print_():
		print('this a test---')


class f(a):
	"""docstring for f"""
	def __init__(self, e):
		super(f, self).__init__(e)
		

def fun():

	s = traceback.extract_stack()
	print(s)

	print (s[-2][0])


print(f(3)._print())
