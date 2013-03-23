import re

RE_MOBILE = re.compile(r"(iphone|ipod|blackberry|android|palm|windows\s+ce)", re.I)
RE_DESKTOP = re.compile(r"(windows|linux|os\s+[x9]|solaris|bsd)", re.I)
RE_BOT = re.compile(r"(spider|crawl|slurp|bot)")

def is_mobile(request):
  """
  Anything that looks like a phone isn't a desktop.
  Anything that looks like a desktop probably is.
  Anything that looks like a bot should default to desktop.
  
  """
  try:
    user_agent = request.headers.get('HTTP_X_OPERAMINI_PHONE_UA') or \
      request.headers.get('HTTP_X_SKYFIRE_PHONE') or \
      request.headers.get('HTTP_USER_AGENT', '')
  except AttributeError:
    # just in case it's not a django/bottle request, we fail with style
    return False

  return bool(RE_MOBILE.search(user_agent)) and \
    bool(RE_DESKTOP.search(user_agent)) or \
    bool(RE_BOT.search(user_agent))

def is_desktop(request):
    return not is_mobile(request)
    