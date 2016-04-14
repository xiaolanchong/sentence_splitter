# -*- encoding: utf-8 -*-

import sys
import os.path
import regex  # [:upper:]

pIsPi = \
    '\u000AB' +\
    '\u02018' +\
    '\u0201B' +\
    '\u0201C' +\
    '\u0201F' +\
    '\u02039' +\
    '\u02E02' +\
    '\u02E04' +\
    '\u02E09' +\
    '\u02E0C' +\
    '\u02E1C' +\
    '\u02E20'

pIsPf = \
    '\u000BB' +\
'\u02019' +\
'\u0201D' +\
'\u0203A' +\
'\u02E03' +\
'\u02E05' +\
'\u02E0A' +\
'\u02E0D' +\
'\u02E1D' +\
'\u02E21'

def subst_char_class(rule):
    rule = rule.replace(r'\p{IsPf}', pIsPf)
    rule = rule.replace(r'\p{IsPi}', pIsPi)
    rule = rule.replace(r'\p{IsAlnum}', r'[:alnum:]')
    rule = rule.replace(r'\p{IsUpper}', r'[:upper:]')
    return rule
    #res


def getprefixfile(language):
    mydir = "nonbreaking_prefixes"
    prefixfile = os.path.join(os.path.dirname(__file__), mydir, "nonbreaking_prefix." + language)
    return prefixfile

NONBREAKING_PREFIX = {}
language = "en"
QUIET = False
HELP = False

argc = 0
while argc < len(sys.argv):
    arg = sys.argv[argc]
    if arg == '-l':
        if argc == len(sys.argv) - 1:
            print('No language specified')
            exit(-1)
        language = sys.argv[argc + 1]
        argc += 1
    elif arg == '-q':
        QUIET = True
    elif arg == '-h':
        HELP = True
    argc += 1


if HELP:
    print("Usage ./split.py (-l [en|de|...]) < textfile > splitfile\n")
    exit(0)

if not QUIET:
	print ( "Sentence Splitter v3")
	print ( "Language: ", language)


prefixfile = getprefixfile(language)
#default back to English if we don't have a language-specific prefix file
if not os.path.isfile(prefixfile):
    prefixfile = getprefixfile("en");
    print ( "WARNING: No known abbreviations for language '$language', attempting fall-back to English version...\n")
    if not os.path.isfile(prefixfile):
        print ("ERROR: No abbreviations files found in " + prefixfile)
        exit(-1)


def getprefixcontents(prefixfile):
    NONBREAKING_PREFIX = {}
    with open(prefixfile, encoding='utf8') as file:
        for line in file.readlines():
            line = line.strip()
            if len(line) and line[0] !=  "#":
                m = regex.match('(.*)[\s]+(\#NUMERIC_ONLY\#)', line)
                if m:
                    NONBREAKING_PREFIX[m.group(1)] = 2
                else:
                    NONBREAKING_PREFIX[line] = 1
    return NONBREAKING_PREFIX

NONBREAKING_PREFIX = getprefixcontents(prefixfile)



def process_string(text):
    lines = text.split('\n')
    return process_lines(lines)

def process_file(file_name):
    lines = []
    with open(file_name, encoding='r') as file:
        lines = file.readlines()

    return process_lines(lines)

def process_lines(lines):
    ##loop text, add lines together until we get a blank line or a <p>
    out_text = ''
    re_tag = regex.compile('^<.+>$')
    text = ""
    for line in lines:
        line = line.strip()
        m = re_tag.match(line)
        if m is None:
            m = regex.match('^\s*$', line)

        if m is not None:
            #time to process this block, we've hit a blank or <p>
            out_text += do_it_for(text, line)
            if regex.match('^\s*$') and len(text): ##if we have text followed by <P>
                out_text += "<P>\n"
                text = ""
        else:
            #append the text, with a space
            text += line + " "

    #do the leftover text
    if len(text):
        out_text += do_it_for(text, "")
    return out_text


def do_it_for(text, markup):
    result = preprocess(text)
    if len(text):
        return result
    if re_tag.match(markup):
        return markup + "\n"
    return ''

def preprocess(text):
	# clean up spaces at head and tail of each line as well as any double-spacing
    text = regex.sub(' +', ' ', text)
    text = regex.sub('\n ', '\n', text)
    text = regex.sub(' \n', '\n', text)
    text = regex.sub('^ ', '', text)
    text = regex.sub(' $', '', text)

	#this is one paragraph

	#####add sentence breaks as needed#####

	#non-period end of sentence markers (?!) followed by sentence starters.
    text = regex.sub (subst_char_class(r'([?!]) +([\'\"\(\[\¿\¡\p{IsPi}]*[\p{IsUpper}])'), '\1\n\2', text, regex.UNICODE)

	#multi-dots followed by sentence starters
    text = regex.sub (subst_char_class(r'(\.[\.]+) +([\'\"\(\[\¿\¡\p{IsPi}]*[\p{IsUpper}])'), '\1\n\2', text, regex.UNICODE)

	# add breaks for sentences that end with some sort of punctuation inside a quote or parenthetical and are followed by a possible sentence starter punctuation and upper case
    text = regex.sub (subst_char_class(r'([?!\.][\ ]*[\'\"\)\]\p{IsPf}]+) +([\'\"\(\[\¿\¡\p{IsPi}]*[\ ]*[\p{IsUpper}])'), '\1\n\2', text, regex.UNICODE)

	# add breaks for sentences that end with some sort of punctuation are followed by a sentence starter punctuation and upper case
    text = regex.sub (subst_char_class(r'([?!\.]) +([\'\"\(\[\¿\¡\p{IsPi}]+[\ ]*[\p{IsUpper}])'), '\1\n\2', text, regex.UNICODE)

	# special punctuation cases are covered. Check all remaining periods.
    words = text.split(' ')
    text = "";
    for i in range(len(words)-1):
        m = regex.match(subst_char_class(r'([\p{IsAlnum}\.\-]*)([\'\"\)\]\%\p{IsPf}]*)(\.+)$'), words[i], regex.UNICODE|regex.S)
        if m:
			#check if $1 is a known honorific and $2 is empty, never break
            prefix = m.group(1)
            starting_punct = m.group(2)
            if prefix and NONBREAKING_PREFIX.get(prefix) == 1 and not starting_punct:
				#not breaking;
                pass
            elif regex.match(subst_char_class(r'(\.)[\p{IsUpper}\-]+(\.+)$'), words[i], regex.UNICODE):
                pass
				#not breaking - upper case acronym
            elif  regex.match(subst_char_class(r'^([ ]*[\'\"\(\[\¿\¡\p{IsPi}]*[ ]*[\p{IsUpper}0-9])'), words[i+1], regex.UNICODE):
				#the next word has a bunch of initial quotes, maybe a space, then either upper case or a number
                if prefix and NONBREAKING_PREFIX.get(prefix, 0) == 2 and not starting_punct and (regex.match('^[0-9]+', words[i+1])):
                    pass
                else:
                    words[i] = words[i] + "\n"
				#we always add a return for these unless we have a numeric non-breaker and a number start



        text += words[i] + " "


	#we stopped one token from the end to allow for easy look-ahead. Append it now.
    text += words[-1]

	# clean up spaces at head and tail of each line as well as any double-spacing
    text = regex.sub(' +', ' ', text)
    text = regex.sub('\n ', '\n', text)
    text = regex.sub(' \n', '\n', text)
    text = regex.sub('^ ', '', text)
    text = regex.sub(' $', '', text)

	#add trailing break
    if not regex.match('\n$', text):
        text += "\n"

    return text

if __name__ == '__main__':
    file_name = '1.txt'
    process_file()

