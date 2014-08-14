#!/usr/bin/env python 3

import os
import sublime
import sublime_plugin
import re
import random
import sys





__version__ = '0.1.0'
__authors__ = ['Ryan Grannell (@RyanGrannell)']

is_python3 = sys.version_info[0] > 2














# -- Snippet
#
# -- A wrapper for constructing sublime-texts XML snippets
# -- from a snippet body, tabtrigger, scope and description.

def Snippet (content, trigger = None, scope = None):

	if scope and scope is not '*':
		if trigger:

			template = '''
				<snippet>
					<content><![CDATA[{0}]]></content>
					<tabTrigger>{1}</tabTrigger>
					<scope>{2}</scope>
				</snippet>
				'''

			return template.format(content, trigger, scope)

		else:

			template = '''
				<snippet>
					<content><![CDATA[{0}]]></content>
					<scope>{1}</scope>
					<tabTrigger>$$</tabTrigger>
				</snippet>
				'''

			return template.format(content, scope)

	else:

		if trigger:

			template = '''
				<snippet>
					<content><![CDATA[{0}]]></content>
					<tabTrigger>{1}</tabTrigger>
				</snippet>
				'''

			return template.format(content, trigger)

		else:

			template = '''
				<snippet>
					<content><![CDATA[{0}]]></content>
					<tabTrigger>$$</tabTrigger>
				</snippet>
				'''

			return template.format(content)

# -- parse_args
#
# -- parse the snippets argument line.

def parse_args (line):
	# -- lex and parse expressions of the form
	# -- > (ps|ts) [scope] [tab-trigger]

	# -- combine the following into the following large regexp:
	#^>[ 	]+(t|p)[ 	]+([st]\.[^ 	]+)[ 	]+.+

	prompt          = '>'
	space_rexp      = '[ 	]+'
	storage_rexp    = '(t|p)'
	lang_rexp       = '[*]|([st]\.[^ 	]+)'
	trigger_rexp    = '.+'

	valid_args_rexp = re.compile(prompt + space_rexp + storage_rexp + \
		space_rexp + lang_rexp + space_rexp + trigger_rexp)

	if valid_args_rexp.search(line) is None:
		print("-- snipboard: could not match " + line + " as snippet arguments.")
	else:

		blocks = re.split(space_rexp, line, 3)

		return {
			'storage' : blocks[1],
			'language': blocks[2],
			'trigger' : blocks[3]
		}





# -- compile_args
#
# -- compile the arguments passed to a snipboard snippet to
# -- a form useable by normal sublime snippets.

def compile_args (args):

	language = args['language']
	storage  = args['storage']
	trigger  = args['trigger']

	# -- compile s.lang -> source.lang,
	# -- compile t.lang -> text   .lang

	language = re.sub('^s\.', 'source.', language)
	language = re.sub('^t\.', 'text.',   language)

	return {
		'storage' : storage,
		'language': language,
		'trigger' : trigger
	}





# -- constants
#
# -- shorthand replacements for existing sublime-text
# -- snippets.

env_vars = (
	# -- replace longer patterns first, as
	# -- $l will override $li.

	['$filename', '$TM_FILENAME'],
	['$filepath', '$TM_FILEPATH'],
	['$lineind',  '$TM_LINE_INDEX'],
	['$linenum',  '$TM_LINE_NUMBER'],
	['$softtab',  '$TM_SOFT_TABS'],
	['$tabsize',  '$TM_TAB_SIZE'],
	['$text',     '$SELECTION'],
	['$line',     '$TM_CURRENT_LINE'],
	['$word',     '$TM_CURRENT_WORD'],

	['$li', '$TM_LINE_INDEX'],
	['$ln', '$TM_LINE_NUMBER'],
	['$st', '$TM_SOFT_TABS'],
	['$ts', '$TM_TAB_SIZE'],
	['$fn', '$TM_FILENAME'],
	['$fp', '$TM_FILEPATH'],
	['$s',  '$SELECTION'],
	['$l',  '$TM_CURRENT_LINE'],
	['$w',  '$TM_CURRENT_WORD']
)





# -- compile_body
#
# -- replace any shorthand environmental variables with
# -- the required longer versions.

def compile_body (body):

	swap_vars = []

	for shorthand, longhand in env_vars:
		# -- use random bits for swapping, to
		# -- avoid serial substitions, as in
		# -- $l -> $line -> $linenum.
		# -- using a swap variable guarantees only a single substitution occurs.

		_         = str(random.getrandbits(128))

		body      = body.replace(shorthand, _)
		swap_vars = swap_vars + [[_, longhand]]

	for _, longhand in swap_vars:
		# -- replace the temporary variables with the longhands.

		body      = body.replace(_, longhand)

	return body



# -- compile_snippet
#
# -- compile a snipboard snippet into an XML sublime text snippet.

def compile_snippet (snippet):

	if snippet.startswith('>'):
		# -- snippet includes additional arguments on the first line.

		snippet_args = snippet.split('\n')   [0]
		snippet_body = snippet.split('\n', 1)[1]

		args = compile_args(parse_args(snippet_args))
		body = compile_body(snippet_body)

		return args, Snippet(body, args['trigger'], args['language'])

	else:
		# -- snippet does not include additional arguments; use defaults.

		snippet_body = snippet

		args         = {
			"storage":  't',
			"language": '*',
			"trigger":  '$$'
		}

		body         = compile_body(snippet_body)

		return args, Snippet(body)





# -- write_to_snipboard
#
# -- write the sublime text snippet to a file.

def write_to_snipboard (args, content):

	platform_name = sys.platform

	if args['storage'] is 't':
		# -- store snippet temporarily.

		dpaths = {
			'linux': os.path.expanduser('~/.config/sublime-text-3/Packages/snipboard/')
		}

		snippet_name = 'snipboard'

	elif args['storage'] is 'p':
		# -- store permanently, to user-snippets.

		dpaths = {
			'linux': os.path.expanduser('~/.config/sublime-text-3/Packages/User/')
		}

		# -- 50% chance of collision at 77,163 snippets.
		# -- change eventually to something better.
		snippet_name = 'snipboard-snippet-' + str(random.getrandbits(32))

	else:
		raise KeyError("-- snipboard: internal error in 'write_to_snipboard'")

	# -- check that the snippet directory actually exists.

	if not os.path.isdir(dpaths[platform_name]):
		raise IOError('-- snipboard: the file path "' + out_path + '" does not exist (platform ' + platform_name + ')')

	out_path = dpaths[platform_name] + snippet_name + '.sublime-snippet'

	# -- try write the snippet to a file.

	try:
		file = open(out_path, "w")
	except IOError:
		raise IOError('-- snipboard: could not open ' + out_path)
	else:
		print('-- snipboard: writing to ' + out_path)

		file.write(content)
		file.close()





# -- SnipboardCommand
#
# -- The interface to snipboard for SublimeText.

class SnipboardCommand (sublime_plugin.WindowCommand):

	def run (self):

		print('-- snipboard: initialised.')

		window = self.window
		view   = window.active_view()
		sel    = view.sel()

		# -- get text from the first selection when multiselecting.
		select_text = view.substr(sel[0])

		if select_text:
			args, xml = compile_snippet(select_text)
			write_to_snipboard(args, xml)
		else:
			raise SyntaxError('-- snipboard: cannot create a snippet from no input.')

