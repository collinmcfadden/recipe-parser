import re
from unicodedata import normalize


def slug(title, encoding=None):
	"""
	Method to create clean url slugs 
	"""
	clean_text = title.strip() \
					  .replace(' ', '-') \
					  .replace('&', " and ") \
					  .replace('/', " or ") 
	
	# Only allow alphanumeric characters and hyphens in url slugs 
	clean_text = re.sub('[^-a-zA-Z0-9]', '', clean_text)

	while '--' in clean_text:
		clean_text = clean_text.replace('--', '-')
	ascii_text = normalize('NFKD', clean_text)
	return ascii_text.lower()