#!/usr/bin/env python 3

import os
import sublime
import sublime_plugin
import random
import re
import sys

__version__ = '0.1.0'
__authors__ = ['Ryan Grannell (@RyanGrannell)']

is_python3 = sys.version_info[0] > 2
















# -- Snippet
#
# -- A wrapper for constructing sublime-texts XML snippets
# -- from a snippet body, tabtrigger, scope and description.

def Snippet (s_content, s_trigger, s_scope = None, s_description = None):

	def tag (name):
		return lambda content: '<' + name + '>' + content + '</' + name + '>\n'

	snippet     = tag('snippet')

	cdata       = lambda content: '<![CDATA[' + content + ']]>'
	content     = tag('content')
	trigger     = tag('tagTrigger')
	scope       = tag('scope')
	description = tag('description')

	text = content(cdata(s_content)) + trigger(s_trigger)

	if s_scope:
		if s_description:
			return snippet(
				text + scope(s_scope) + description(s_description))
		else:
			return snippet(
				text + scope(s_scope))
	else:
		if s_description:
			return snippet(
				text + description(s_description))
		else:
			return snippet(text)






def parse_args (line):
	# -- lex and parse expressions of the form
	# -- > (ps|ts) [scope] [tab-trigger]

	# -- combine the following into the following large regexp:
	#^>[ 	]+(t|p)[ 	]+([st]\.[^ 	]+)[ 	]+.+

	prompt          = '>'
	space_rexp      = '[ 	]+'
	storage_rexp    = '(t|p)'
	lang_rexp       = '([st]\.[^ 	]+)'
	trigger_rexp    = '.+'

	valid_args_rexp = re.compile(prompt + space_rexp + storage_rexp + \
		space_rexp + lang_rexp + space_rexp + trigger_rexp)

	if valid_args_rexp.search(line) is None:
		raise SyntaxError("could not match " + line + " as snippet arguments.")
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
		raise SyntaxError("snippet arguments missing.")

	args = compile_args(parse_args(snippet_args))
	body = compile_body(snippet_body)

	return Snippet(snippet_body, args['trigger'], args['language'])





test = "> t s.rstats snip\n" + \
	"$1 this is a $2 snippet."

compile_snippet(test)
#"~/.config/sublime-text-3/Packages/snipboard/$$.sublime-snippet"










# -- SnipboardCommand
#
#

class SnipboardCommand (sublime_plugin.WindowCommand):

	def run (self):

		window = self.window
		view = window.active_view()
		sel = view.sel()

		select_text = view.substr(sel[0])

		print(select_text)
