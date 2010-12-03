import logging
import re

class Token(object):
	_filter_re = re.compile ('^(.*)\[(.*)\]$')
	def __init__ (self, token):
		super(Token,self).__init__()
		self._filter = None
		self._key = None
		self.set_token (token)
		
	def set_token (self, token):
		match = self._filter_re.match (token)
		try:
			self._key, self._filter = match.groups()
			self._filter = Filter (self._filter)
		except AttributeError:
			self._filter = None
			self._key = token

		self._token = token
		
	def is_wildcard (self):
		return self._key == "*"
		
	def get_key (self):
		return self._key
		
	def has_filter (self):
		return bool(self._filter)
		
	def get_filter (self):
		return self._filter
		
	def get_token (self):
		return self._token
		
	def __repr__ (self):
		return self._token
		
	def __str__ (self):
		return self._token
		
	def __eq__ (self, b):
		if isinstance(b, Token):
			return self._token == b.get_token ()
		if isinstance(b, str):
			return self._token == b
		
	def match (self, child):
		self._filter.match (child)

class Filter(object):
	def __init__(self, filter_string):
		super(Filter, self).__init__()
		self._parse (filter_string)
		self._filter = filter_string
		
	def _parse (self, filter_string):
		logging.warning ("Method not implemented")
	
	def __repr__ (self):
		return self._filter
	
	def __str__ (self):
		return self.__repr__()
		
	def match (self, filter_string):
		logging.warning ("Method not implemented")

class BaseQuery(list):
	def __init__ (self, query):
		super(list,self).__init__()
		if not isinstance(query, str):
			raise ValueError
		self._parse (query)
		
	def is_from_root (self):
		return self._from_root
	
	def set_query (self, query):
		self._parse (query)

	def _parse (self, query):
		if query.startswith ('/') and not query.startswith('//'):
			self._from_root = True
		else:
			self._from_root = False
		
		for i in query.split('//'):
			if not i: continue

			self.append ([Token(key) for key in i.split ('/') if key])

	def execute (self, obj):
		prev = []
		if self.is_from_root ():
			prev.extend(self._execute_query_from_root (obj))
		else:
			prev.extend(self._execute_query (obj, self[0]))


		if len(self) == 1:
			return prev

		for subq in self[1:]:
			tmp = []
			for obj in prev:
				tmp.extend (self._execute_query (obj, subq))
			prev = tmp
		
		return prev		

	def _execute_query_from_root (self, obj):
		result = []

		#Non recursive as we start from the root path of the object
		for i in self._find_key (obj, self[0][0]):
			if len(self[0]) > 1:
				result.extend (self._subquery (i, self[0][1:]))
			elif i:
				result.append (i)
		
		return result

	def _execute_query (self, obj, query):
		result = []
		
		#Recursive search of the first item of the path
		for i in self._find_key (obj, query[0], True):
			if len(query) > 1:
				result.extend (self._subquery (i, query[1:]))
			else:
				result.append (i)
		
		return result
	
	def _subquery (self, obj, keys):
		if len(keys) < 1:
			return []
		if len(keys) == 1:
			return self._find_key (obj, keys[0])
		
		result = []
		for i in self._find_key (obj, keys[0]):
			result.extend (self._subquery (i, keys[1:]))

		
		return result

	def _find_key (self, obj, key, recursive=False):
		result = []
		if isinstance (obj, dict):
			if key.is_wildcard ():
				for k in obj.keys ():
					if key.has_filter () and key.get_filter().match (obj[k]):
						result.append (obj[k])
					else:
						result.append (obj[k])
			elif key in obj.keys():
				child = obj[str(key)]
				if key.has_filter () and key.get_filter().match (child):
					result.append(child)
				else:
					result.append(child)
			if recursive:
				for k in obj.keys():
					result.extend (self._find_key (obj[k], key, True))
		elif isinstance (obj, list):
			#TODO: Match filters on childs?
			if key.is_wildcard ():
				result.extend (obj)
			if recursive:
				for i in obj:
					result.extend(self._find_key (i, key, recursive))

		return result

try:
	import json
	class JPathQuery (BaseQuery):
		def execute(self, jsonstr):
			if not isinstance(jsonstr, str):
				raise ValueError
			super(JPath, self).execute(json.loads (jsonstr))
except:
	pass

try:
	import yaml
	class YPathQuery (BaseQuery):
		def execute(self, yamlstr):
			if not isinstance(yamlstr, str):
				raise ValueError
			super(YPath, self).execute(yaml.load (yamlstr))
except:
	pass

if __name__ == '__main__':
	a = {'a': [{'b': {'x': {'x': {'x': True}}}},{'b': True, 'a': False},{'b': "foo"}]}
	print BaseQuery ('/a/*/*').execute (a)
	print BaseQuery ('a//x').execute (a)
	print BaseQuery ('a//b').execute (a)
	print BaseQuery ('b').execute (a)	
	try:
		print YPathQuery ("a: [1,2,3]").execute("/a")
	except NameError:
	    pass
	try:
		print JPathQuery ("{\"a\": [1,2,3,true,\"foo\"]}").execute("/a")
	except NameError:
	    pass
