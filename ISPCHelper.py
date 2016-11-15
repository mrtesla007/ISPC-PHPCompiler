import json
import platform
import sys
import distutils.version

__version__ = 1.0

SUPPORTED_PLATFORMS = ['ubuntu', 'debian', '', 'linuxmint']  # '' and 'linuxmint' for development purposes

INSTALL_PARENT_PATH = '/opt/'
PHPMYADMIN_INSTALL_PATH = INSTALL_PARENT_PATH + 'phpmyadmin'
ROUNDCUBE_INSTALL_PATH = INSTALL_PARENT_PATH + 'roundcube'
PHP_INSTALL_PATH = INSTALL_PARENT_PATH + 'php{0}'


def parse_json(url):
	response = urllib2.urlopen(url)
	data = response.read().decode('utf-8')
	return json.loads(data)


def install_phpmyadmin():
	last_release = parse_json('https://api.github.com/repos/phpmyadmin/phpmyadmin/releases/latest')
	os.system('cd /tmp/ && wget -O pma.tar.gz ' + last_release['tarball_url'] + ' && tar zxf pma.tar.gz -C /opt/')
	os.system('mv ' + INSTALL_PARENT_PATH + 'phpmyadmin-phpmyadmin-* ' + PHPMYADMIN_INSTALL_PATH)
	os.system('rm /tmp/pma.tar.gz')
	
	apache_conf = '''
# phpMyAdmin ISPCHelper Apache configuration

Alias /phpmyadmin {0}

<Directory {0}>
    Options FollowSymLinks
	Require all granted

    <IfModule mod_fcgid.c>
            Options +ExecCGI
            AddHandler fcgid-script .php
            FCGIWrapper /var/www/php-fcgi-scripts/ispconfig/.php-fcgi-starter .php
            Order allow,deny
            allow from all
    </IfModule>
</Directory>

<Directory {0}/libraries>
    Require all denied
</Directory>
'''
	apache_conf.format(PHPMYADMIN_INSTALL_PATH)
	conf = open('/etc/apache2/conf-enabled/phpmyadmin.conf', 'w')
	conf.write(apache_conf)
	conf.close()
	
	os.system('service apache2 restart')
	
	
	

def install_roundcube():
	last_release = parse_json('https://api.github.com/repos/roundcube/roundcubemail/releases/latest')
	os.system('cd /tmp/ && wget -O roundcube.tar.gz ' + last_release['assets'][2]['browser_download_url'] + ' && tar zxf roundcube.tar.gz -C /opt/')
	os.system('mv ' + INSTALL_PARENT_PATH + 'roundcubemail-* ' + ROUNDCUBE_INSTALL_PATH)
	os.system('rm /tmp/roundcube.tar.gz')
	


def install_update_php(version):
	pass


def php_menu():
	php_versions = parse_json('https://raw.githubusercontent.com/SergiX44/ISPCHelper/master/php_versions.json')

	versions = {}
	i = 1
	for v in php_versions['versions']:
		print(str(i) + ') Update/install PHP ' + v['name'])
		versions[str(i)] = v
		i += 1

	sel = raw_input('\nChoose an option: ')
	if sel not in versions:
		print('Invalid selection.')
		main_menu()
	else:
		install_update_php(versions[sel])


def main_menu():
	print('1) Manage PHP Additional Versions')
	print('2) Install/update latest phpMyAdmin')
	print('3) Install/update latest Roundcube')

	menu = {
		'1': php_menu,
		'2': install_phpmyadmin,
		'3': install_roundcube
	}

	sel = raw_input('\nChoose an option: ')
	run_menu(sel, menu, main_menu)


def run_menu(sel, menu, caller):
	if sel in menu:
		menu[sel]()
	else:
		print('Invalid selection.')
		caller()


if __name__ == '__main__':
	print('-*- ISPConfig Helper {0} -*-\n'.format(__version__))

	if platform.dist()[0].lower() not in SUPPORTED_PLATFORMS:
		print('Your distribution is not supported.')
		sys.exit(1)
	main_menu()
