#TODO: Token class to handle filters and other node selectors
#class Token:
#	pass

class Query(list):
	def __init__ (self, query):
		super(Query,self).__init__()
		if not isinstance(query, str):
			raise ValueError
		self.parse (query)
		
	def is_from_root (self):
		return self._from_root

	def parse (self, query):
		if query.startswith ('/'):
			self._from_root = True
		else:
			self._from_root = False
		
		for i in query.split('//'):
			if not i: continue

			self.append ([j for j in i.split ('/') if j])

class BasePath (object):
	def __init__ (self, obj):
		self._root = obj
		self._from_root = False

	def query (self, query):
		self._query = Query(query)

		if not self._query:
			return []
		
		prev = []
		if self._query.is_from_root ():
			prev.extend(self._execute_query_from_root ())
		else:
			prev.extend(self._execute_query (self._root, self._query[0]))


		if len(self._query) == 1:
			return prev

		for subq in self._query [1:]:
			tmp = []
			for obj in prev:
				tmp.extend (self._execute_query (obj, subq))
			prev = tmp
		
		return prev		

	def _execute_query_from_root (self):
		result = []

		#Non recursive as we start from the root path of the object
		for i in self._find_key (self._root, self._query[0][0]):
			if len(self._query[0]) > 1:
				result.extend (self._subquery (i, self._query[0][1:]))
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
	class JPath (BasePath):
		def __init__(self, jsonstr):		
			if not isinstance(jsonstr, str):
				raise ValueError
			super(JPath, self).__init__(json.loads (jsonstr))
except:
	pass

try:
	import yaml
	class YPath (BasePath):
		def __init__(self, yamlstr):
			if not isinstance(yamlstr, str):
				raise ValueError
			super(YPath, self).__init__(yaml.load (yamlstr))
except:
	pass

if __name__ == '__main__':
	bp = BasePath ({'a': [{'b': {'x': {'x': {'x': True}}}},{'b': True, 'c': False},{'b': "foo"}]})
	print bp.query ('/a/*/*')
	print bp.query ('a//x')
	print bp.query ('a//b')
        try:
		yp = YPath ("a: [1,2,3]")
		print yp.query ("/a")
        except NameError:
            pass
	try:
		jp = JPath ("{\"a\": [1,2,3,true,\"foo\"]}")
		print jp.query ("/a")
        except NameError:
            pass
