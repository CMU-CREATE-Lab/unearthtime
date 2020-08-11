import re

from validators.url import url

search = re.compile(r'[_\-\s]+')
spaces = re.compile(r'\s+')


def capitalizefirst(value): return ''.join([value[0].capitalize(), value[1:]]) if len(value) > 1 else value.capitalize()


def ismalformedurl(value): return noneorempty(value) or not url(value)


def noneorempty(value): return not bool(value) or value.isspace()


def prefix(value, pref): return value if value.startswith(pref) else ''.join([pref, value])


def resolvequery(value): return ''.join([capitalizefirst(word) for word in search.sub(' ', value).strip().split(' ')])


def suffix(value, suff): return value if value.endswith(suff) else ''.join([value, suff])
