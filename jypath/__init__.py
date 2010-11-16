#TODO: Token class to handle filters and other node selectors
#class Token:
#	pass

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

			self.append ([j for j in i.split ('/') if j])

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
			if key == "*":
				for k in obj.keys ():
					result.append (obj[k])
			elif key in obj.keys():
				result.append(obj[key])
			if recursive:
				for k in obj.keys():
					result.extend (self._find_key (obj[k], key, True))
		elif isinstance (obj, list):
			if key == "*":
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
	a = {'a': [{'b': {'x': {'x': {'x': True}}}},{'b': True, 'c': False},{'b': "foo"}]}
	bq = BaseQuery ('/a/*/*')
	print bq.execute (a)
	
"""	print bp.query ('/a/*/*')
	print bp.query ('a//x')
	print bp.query ('a//b')
	print bp.query ('//x')
	try:
		yp = YPathQuery ("a: [1,2,3]")
		print yp.query ("/a")
	except NameError:
	    pass
	try:
		jp = JPathQuery ("{\"a\": [1,2,3,true,\"foo\"]}")
		print jp.query ("/a")
	except NameError:
	    pass"""
