import glob
import re
import os
for filename in glob.glob('*.php'):
	print filename
	fl = open(filename,'r')
	f = fl.read()
	f =re.sub(r'\<\?php', '', f, flags=re.IGNORECASE)
	f =re.sub(r'namespace InstagramAPI;', '', f, flags=re.IGNORECASE)
	f =re.sub(r' extends Response', ':', f, flags=re.IGNORECASE)
	f =re.sub(r'\{', '', f, flags=re.IGNORECASE)
	re.sub(r'\}', '', f, flags=re.IGNORECASE)
	f =re.sub(r'/', '#', f, flags=re.IGNORECASE)
	f =re.sub(r'\*', '#', f, flags=re.IGNORECASE)
	f =re.sub(r'public \$', '', f, flags=re.IGNORECASE)
	f =re.sub(r';', '=None', f, flags=re.IGNORECASE)
	fl.close()
	fl = open(filename, 'w')
	fl.write(f)
	os.rename(filename,filename.rsplit('.',1)[0]+'.py')



