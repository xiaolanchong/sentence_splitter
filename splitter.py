# -*- encoding: utf-8 -*-

import sys
import os.path
import argparse
import regex  # supports POSIX classes

re_tag = regex.compile('^<.+>$')


def subst_char_class(rule):
    rule = rule.replace(r'\p{IsPi}', r'\p{Initial_Punctuation}')
    rule = rule.replace(r'\p{IsPf}', r'\p{Final_Punctuation}')
    rule = rule.replace(r'\p{IsAlnum}', r'\w')
    rule = rule.replace(r'\p{IsUpper}', r'\p{Uppercase_Letter}\p{Other_Letter}')
    return rule

# Prefix file utilities


def get_prefix_filename(language):
    prefixfile = getprefixfile(language)
    # default back to English if we don't have a language-specific prefix file
    if not os.path.isfile(prefixfile):
        prefixfile = getprefixfile("en");
        print("WARNING: No known abbreviations for language '{}', attempting fall-back to English version...\n".format(language))
        if not os.path.isfile(prefixfile):
            raise RuntimeError("ERROR: No abbreviations files found in " + prefixfile)
    return prefixfile


def load_prefix_file(prefixfile):
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


def getprefixfile(language):
    mydir = "nonbreaking_prefixes"
    prefixfile = os.path.join(os.path.dirname(__file__), mydir, "nonbreaking_prefix." + language)
    return prefixfile

################################################################################


class SentenceSplitter:
    def __init__(self, language):
        name = get_prefix_filename(language)
        self.NONBREAKING_PREFIX = load_prefix_file(name)

    def process_string(self, text):
        lines = text.split('\n')
        return process_lines(lines, self.NONBREAKING_PREFIX)

    def process_file(self, file_name):
        with open(file_name, mode='r', encoding='utf8') as file:
            lines = file.readlines()
        return process_lines(lines, self.NONBREAKING_PREFIX)


def process_lines(lines, NONBREAKING_PREFIX):
    # loop text, add lines together until we get a blank line or a <p>
    out_text = ''

    text = ""
    for line in lines:
        line = line.strip()
        m = re_tag.match(line)
        if m is None:
            m = regex.match('^\s*$', line)

        if m is not None:
            # time to process this block, we've hit a blank or <p>
            out_text += do_it_for(text, line, NONBREAKING_PREFIX)
            if regex.match('^\s*$', line) and len(text): ##if we have text followed by <P>
                out_text += "<P>\n"
                text = ""
        else:
            # append the text, with a space
            text += line + " "

    # do the leftover text
    if len(text):
        out_text += do_it_for(text, "", NONBREAKING_PREFIX)
    return out_text


def do_it_for(text, markup, NONBREAKING_PREFIX):
    result = preprocess(text, NONBREAKING_PREFIX)
    if len(text):
        return result
    if re_tag.match(markup):
        return markup + "\n"
    return ''


def preprocess(text, NONBREAKING_PREFIX):
    # clean up spaces at head and tail of each line as well as any double-spacing
    text = regex.sub(' +', ' ', text)
    text = regex.sub('\n ', '\n', text)
    text = regex.sub(' \n', '\n', text)
    text = regex.sub('^ ', '', text)
    text = regex.sub(' $', '', text)

    # this is one paragraph
    # add sentence breaks as needed#####
    # non-period end of sentence markers (?!) followed by sentence starters.
    text = regex.sub (subst_char_class(r'([?!]) +([\'\"\(\[\¿\¡\p{IsPi}]*[\p{IsUpper}])'), r'\1\n\2', text, regex.UNICODE)

    # multi-dots followed by sentence starters
    text = regex.sub (subst_char_class(r'(\.[\.]+) +([\'\"\(\[\¿\¡\p{IsPi}]*[\p{IsUpper}])'), r'\1\n\2', text, regex.UNICODE)

    # add breaks for sentences that end with some sort of punctuation inside a quote or parenthetical and
    # are followed by a possible sentence starter punctuation and upper case
    text = regex.sub (subst_char_class(r'([?!\.][\ ]*[\'\"\)\]\p{IsPf}]+) +([\'\"\(\[\¿\¡\p{IsPi}]*[\ ]*[\p{IsUpper}])'), r'\1\n\2', text, regex.UNICODE)

    # add breaks for sentences that end with some sort of punctuation are followed by a sentence starter punctuation and
    # upper case
    text = regex.sub(subst_char_class(r'([?!\.]) +([\'\"\(\[\¿\¡\p{IsPi}]+[\ ]*[\p{IsUpper}])'), r'\1\n\2', text, regex.UNICODE)

    text = regex.sub(subst_char_class(r'。'), r'。\n', text, regex.UNICODE)

    # special punctuation cases are covered. Check all remaining periods.
    words = text.split(' ')
    text = ""
    for i in range(len(words)-1):
        m = regex.match(subst_char_class(r'([\p{IsAlnum}\.\-]*)([\'\"\)\]\%\p{IsPf}]*)(\.+)$'), words[i], regex.UNICODE|regex.S)
        if m:
            # check if $1 is a known honorific and $2 is empty, never break
            prefix = m.group(1)
            starting_punct = m.group(2)
            if prefix and NONBREAKING_PREFIX.get(prefix) == 1 and not starting_punct:
                # not breaking;
                pass
            elif regex.match(subst_char_class(r'[\.][\p{IsUpper}\-]+(\.+)$'), words[i], regex.UNICODE):
                pass
                # not breaking - upper case acronym
            elif regex.match(subst_char_class(r'^([ ]*[\'\"\(\[\¿\¡\p{IsPi}]*[ ]*[\p{IsUpper}0-9])'), words[i+1], regex.UNICODE):
                # the next word has a bunch of initial quotes, maybe a space, then either upper case or a number
                if prefix and NONBREAKING_PREFIX.get(prefix, 0) == 2 and not starting_punct and (regex.match(r'^[0-9]+', words[i+1])):
                    pass
                else:
                    words[i] += "\n"
                # we always add a return for these unless we have a numeric non-breaker and a number start

        text += words[i] + " "

    # we stopped one token from the end to allow for easy look-ahead. Append it now.
    text += words[-1]

    # clean up spaces at head and tail of each line as well as any double-spacing
    text = regex.sub(r' +', ' ', text)
    text = regex.sub(r'\n ', '\n', text)
    text = regex.sub(r' \n', '\n', text)
    text = regex.sub(r'^ ', '', text)
    text = regex.sub(r' $', '', text)

    # add trailing break
    if len(text) != 0 and text[-1] != '\n':
        text += "\n"

    return text


def get_command_args(args):
   parser = argparse.ArgumentParser(description='Split a text into sentences.')
   parser.add_argument('--quiet', '-q', help='Be quiet', action='store_true')
   parser.add_argument('--language', '-l', default='en', metavar='en|fr|ru|ja|...',
                        type=str, help='Sets the language of the input text. English is default.')
   parser.add_argument('infile', help='Input file name')
   parser.add_argument('outfile', help='Output file name', nargs='?')

   res = parser.parse_args(args=args)
   return res.language, res.quiet, res.infile, res.outfile

def main():
   language, quiet, infile, outfile = get_command_args(sys.argv[1:])
   splitter = SentenceSplitter(language)
   text = splitter.process_file(infile)
   if outfile is None or len(outfile) == 0:
      print(text)
   else:
      with open(outfile, mode='w', encoding='utf8') as file:
         file.write(text)


if __name__ == '__main__':
    main()


