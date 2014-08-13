#!/usr/bin/env python 3

import os
import sublime
import sublime_plugin
import re
import sys





__version__ = '0.1.0'
__authors__ = ['Ryan Grannell (@RyanGrannell)']

is_python3 = sys.version_info[0] > 2
















# -- Snippet
#
# -- A wrapper for constructing sublime-texts XML snippets
# -- from a snippet body, tabtrigger, scope and description.

def Snippet (s_content, s_trigger, s_scope = None):

	if s_scope and s_scope is not '*':
		template = '''
			<snippet>
				<content><![CDATA[{0}]]></content>
				<tabTrigger>{1}</tabTrigger>
				<scope>{2}</scope>
			</snippet>
			'''

		return template.format(s_content, s_trigger, s_scope)

	else:
		template = '''
			<snippet>
				<content><![CDATA[{0}]]></content>
				<tabTrigger>{1}</tabTrigger>
			</snippet>
			'''

		return template.format(s_content, s_trigger)



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
		print("--snipboard: could not match " + line + " as snippet arguments.")
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

constants = (
	['$s',  '$SELECTION'],
	['$l',  '$TM_CURRENT_LINE'],
	['$w',  '$TM_CURRENT_WORD'],
	['$fn', '$TM_FILENAME'],
	['$fp', '$TM_FILEPATH'],
	['$li', '$TM_LINE_INDEX'],
	['$ln', '$TM_LINE_NUMBER'],
	['$st', '$TM_SOFT_TABS'],
	['$ts', '$TM_TAB_SIZE'],

	['$text',     '$SELECTION'],
	['$line',     '$TM_CURRENT_LINE'],
	['$word',     '$TM_CURRENT_WORD'],
	['$filename', '$TM_FILENAME'],
	['$filepath', '$TM_FILEPATH'],
	['$lineind',  '$TM_LINE_INDEX'],
	['$linenum',  '$TM_LINE_NUMBER'],
	['$softtab',  '$TM_SOFT_TABS'],
	['$tabsize',  '$TM_TAB_SIZE'],
)





# -- compile_body
#
# -- compile .

def compile_body (body):
	return body





# -- compile_snippet
#
# -- compile a snipboard snippet into an XML sublime text snippet.

def compile_snippet (snippet):

	snippet_args = snippet.split('\n')   [0]
	snippet_body = snippet.split('\n', 1)[1]

	if not snippet.startswith('>'):
		raise SyntaxError('-- snipboard: syntax error, snippet did not start with >.')
	else:

		args = compile_args(parse_args(snippet_args))
		body = compile_body(snippet_body)

		return Snippet(snippet_body, args['trigger'], args['language'])





# -- write_to_snipboard
#
# -- write the sublime text snippet to a file.

def write_to_snipboard (content):

	fpaths = {
		'linux': os.path.expanduser('~/.config/sublime-text-3/Packages/User/snipboard.sublime-snippet')
	}

	platform_name = sys.platform

	try:
		file = open(fpaths[platform_name], "w")
	except IOError:
		raise IOError('-- snipboard: could not open ' + fpaths[platform_name])
	else:
		print('-- snipboard: writing to ' + fpaths[platform_name])

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

		# -- get text from the first selection.
		select_text = view.substr(sel[0])
		xml         = compile_snippet(select_text)

		write_to_snipboard(xml)
