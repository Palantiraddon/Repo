################################################################################
#      Copyright (C) 2015 Surfacingx                                           #
#                                                                              #
#  This Program is free software; you can redistribute it and/or modify        #
#  it under the terms of the GNU General Public License as published by        #
#  the Free Software Foundation; either version 2, or (at your option)         #
#  any later version.                                                          #
#                                                                              #
#  This Program is distributed in the hope that it will be useful,             #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
#  GNU General Public License for more details.                                #
#                                                                              #
#  You should have received a copy of the GNU General Public License           #
#  along with XBMC; see the file COPYING.  If not, write to                    #
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.       #
#  http://www.gnu.org/copyleft/gpl.html                                        #
################################################################################

import xbmc, xbmcaddon, xbmcgui, xbmcplugin, os, sys, xbmcvfs, glob
import shutil
import urllib2,urllib
import re

import uservar
import fnmatch
import base64
try:    from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database
from datetime import date, datetime, timedelta
from urlparse import urljoin
from resources.libs import extract, downloader, notify, debridit, traktit, loginit, skinSwitch, uploadLog, yt, wizard as wiz

ADDON_ID         = uservar.ADDON_ID
ADDONTITLE       = uservar.ADDONTITLE
ADDON            = wiz.addonId(ADDON_ID)
VERSION          = wiz.addonInfo(ADDON_ID,'version')
ADDONPATH        = wiz.addonInfo(ADDON_ID,'path')
DIALOG           = xbmcgui.Dialog()
DP               = xbmcgui.DialogProgress()
HOME             = xbmc.translatePath('special://home/')
LOG              = xbmc.translatePath('special://logpath/')
PROFILE          = xbmc.translatePath('special://profile/')
ADDONS           = os.path.join(HOME,      'addons')
USERDATA         = os.path.join(HOME,      'userdata')
PLUGIN           = os.path.join(ADDONS,    ADDON_ID)
PACKAGES         = os.path.join(ADDONS,    'packages')
ADDOND           = os.path.join(USERDATA,  'addon_data')
ADDONDATA        = os.path.join(USERDATA,  'addon_data', ADDON_ID)
ADVANCED         = os.path.join(USERDATA,  'advancedsettings.xml')
SOURCES          = os.path.join(USERDATA,  'sources.xml')
FAVOURITES       = os.path.join(USERDATA,  'favourites.xml')
PROFILES         = os.path.join(USERDATA,  'profiles.xml')
GUISETTINGS      = os.path.join(USERDATA,  'guisettings.xml')
THUMBS           = os.path.join(USERDATA,  'Thumbnails')
DATABASE         = os.path.join(USERDATA,  'Database')
FANART           = os.path.join(ADDONPATH, 'fanart.jpg')
ICON             = os.path.join(ADDONPATH, 'icon.png')
ART              = os.path.join(ADDONPATH, 'resources', 'art')
WIZLOG           = os.path.join(ADDONDATA, 'wizard.log')
SKIN             = xbmc.getSkinDir()
BUILDNAME        = wiz.getS('buildname')
DEFAULTSKIN      = wiz.getS('defaultskin')
DEFAULTNAME      = wiz.getS('defaultskinname')
DEFAULTIGNORE    = wiz.getS('defaultskinignore')
BUILDVERSION     = wiz.getS('buildversion')
BUILDTHEME       = wiz.getS('buildtheme')
BUILDLATEST      = wiz.getS('latestversion')
INSTALLMETHOD    = wiz.getS('installmethod')
SHOW15           = wiz.getS('show15')
SHOW16           = wiz.getS('show16')
SHOW17           = wiz.getS('show17')
SHOW18           = wiz.getS('show18')
SHOWADULT        = wiz.getS('adult')
SHOWMAINT        = wiz.getS('showmaint')
AUTOCLEANUP      = wiz.getS('autoclean')
AUTOCACHE        = wiz.getS('clearcache')
AUTOPACKAGES     = wiz.getS('clearpackages')
AUTOTHUMBS       = wiz.getS('clearthumbs')
AUTOFEQ          = wiz.getS('autocleanfeq')
AUTONEXTRUN      = wiz.getS('nextautocleanup')
INCLUDEVIDEO     = wiz.getS('includevideo')
INCLUDEALL       = wiz.getS('includeall')
INCLUDEBOB       = wiz.getS('includebob')
INCLUDEPHOENIX   = wiz.getS('includephoenix')
INCLUDESPECTO    = wiz.getS('includespecto')
INCLUDEGENESIS   = wiz.getS('includegenesis')
INCLUDEEXODUS    = wiz.getS('includeexodus')
INCLUDEONECHAN   = wiz.getS('includeonechan')
INCLUDESALTS     = wiz.getS('includesalts')
INCLUDESALTSHD   = wiz.getS('includesaltslite')
SEPERATE         = wiz.getS('seperate')
NOTIFY           = wiz.getS('notify')
NOTEID           = wiz.getS('noteid')
NOTEDISMISS      = wiz.getS('notedismiss')
TRAKTSAVE        = wiz.getS('traktlastsave')
REALSAVE         = wiz.getS('debridlastsave')
LOGINSAVE        = wiz.getS('loginlastsave')
KEEPFAVS         = wiz.getS('keepfavourites')
KEEPSOURCES      = wiz.getS('keepsources')
KEEPPROFILES     = wiz.getS('keepprofiles')
KEEPADVANCED     = wiz.getS('keepadvanced')
KEEPREPOS        = wiz.getS('keeprepos')
KEEPSUPER        = wiz.getS('keepsuper')
KEEPWHITELIST    = wiz.getS('keepwhitelist')
KEEPTRAKT        = wiz.getS('keeptrakt')
KEEPREAL         = wiz.getS('keepdebrid')
KEEPLOGIN        = wiz.getS('keeplogin')
LOGINSAVE        = wiz.getS('loginlastsave')
DEVELOPER        = wiz.getS('developer')
THIRDPARTY       = wiz.getS('enable3rd')
THIRD1NAME       = wiz.getS('wizard1name')
THIRD1URL        = wiz.getS('wizard1url')
THIRD2NAME       = wiz.getS('wizard2name')
THIRD2URL        = wiz.getS('wizard2url')
THIRD3NAME       = wiz.getS('wizard3name')
THIRD3URL        = wiz.getS('wizard3url')
BACKUPLOCATION   = ADDON.getSetting('path') if not ADDON.getSetting('path') == '' else 'special://home/'
MYBUILDS         = os.path.join(BACKUPLOCATION, 'My_Builds', '')
AUTOFEQ          = int(float(AUTOFEQ)) if AUTOFEQ.isdigit() else 0
TODAY            = date.today()
TOMORROW         = TODAY + timedelta(days=1)
THREEDAYS        = TODAY + timedelta(days=3)
KODIV            = float(xbmc.getInfoLabel("System.BuildVersion")[:4])
if KODIV > 17:
	from resources.libs import zfile as zipfile #FTG mod for Kodi 18
else:
	import zipfile
MCNAME           = wiz.mediaCenter()
EXCLUDES         = uservar.EXCLUDES
BUILDFILE        = uservar.BUILDFILE
APKFILE          = uservar.APKFILE
YOUTUBETITLE     = uservar.YOUTUBETITLE
YOUTUBEFILE      = uservar.YOUTUBEFILE
ADDONFILE        = uservar.ADDONFILE
ADVANCEDFILE     = uservar.ADVANCEDFILE
UPDATECHECK      = uservar.UPDATECHECK if str(uservar.UPDATECHECK).isdigit() else 1
NEXTCHECK        = TODAY + timedelta(days=UPDATECHECK)
NOTIFICATION     = uservar.NOTIFICATION
ENABLE           = uservar.ENABLE
HEADERMESSAGE    = uservar.HEADERMESSAGE
AUTOUPDATE       = uservar.AUTOUPDATE
WIZARDFILE       = uservar.WIZARDFILE
HIDECONTACT      = uservar.HIDECONTACT
CONTACT          = uservar.CONTACT
CONTACTICON      = uservar.CONTACTICON if not uservar.CONTACTICON == 'http://' else ICON 
CONTACTFANART    = uservar.CONTACTFANART if not uservar.CONTACTFANART == 'http://' else FANART
HIDESPACERS      = uservar.HIDESPACERS
COLOR1           = uservar.COLOR1
COLOR2           = uservar.COLOR2
THEME1           = uservar.THEME1
THEME2           = uservar.THEME2
THEME3           = uservar.THEME3
THEME4           = uservar.THEME4
THEME5           = uservar.THEME5
ICONBUILDS       = uservar.ICONBUILDS if not uservar.ICONBUILDS == 'http://' else ICON
ICONMAINT        = uservar.ICONMAINT if not uservar.ICONMAINT == 'http://' else ICON
ICONAPK          = uservar.ICONAPK if not uservar.ICONAPK == 'http://' else ICON
ICONADDONS       = uservar.ICONADDONS if not uservar.ICONADDONS == 'http://' else ICON
ICONYOUTUBE      = uservar.ICONYOUTUBE if not uservar.ICONYOUTUBE == 'http://' else ICON
ICONSAVE         = uservar.ICONSAVE if not uservar.ICONSAVE == 'http://' else ICON
ICONTRAKT        = uservar.ICONTRAKT if not uservar.ICONTRAKT == 'http://' else ICON
ICONREAL         = uservar.ICONREAL if not uservar.ICONREAL == 'http://' else ICON
ICONLOGIN        = uservar.ICONLOGIN if not uservar.ICONLOGIN == 'http://' else ICON
ICONCONTACT      = uservar.ICONCONTACT if not uservar.ICONCONTACT == 'http://' else ICON
ICONSETTINGS     = uservar.ICONSETTINGS if not uservar.ICONSETTINGS == 'http://' else ICON
LOGFILES         = wiz.LOGFILES
TRAKTID          = traktit.TRAKTID
DEBRIDID         = debridit.DEBRIDID
LOGINID          = loginit.LOGINID
MODURL           = 'http://tribeca.tvaddons.ag/tools/maintenance/modules/'
MODURL2          = 'http://mirrors.kodi.tv/addons/jarvis/'
INSTALLMETHODS   = ['Always Ask', 'Reload Profile', 'Force Close']
DEFAULTPLUGINS   = ['metadata.album.universal', 'metadata.artists.universal', 'metadata.common.fanart.tv', 'metadata.common.imdb.com', 'metadata.common.musicbrainz.org', 'metadata.themoviedb.org', 'metadata.tvdb.com', 'service.xbmc.versioncheck']

###########################
###### Menu Items   #######
###########################
#addDir (display,mode,name=None,url=None,menu=None,overwrite=True,fanart=FANART,icon=ICON, themeit=None)
#addFile(display,mode,name=None,url=None,menu=None,overwrite=True,fanart=FANART,icon=ICON, themeit=None)

def index():
	if AUTOUPDATE == 'Yes':
		if wiz.workingURL(WIZARDFILE) == True:
			ver = wiz.checkWizard('version')
			if ver > VERSION: addFile('%s [v%s] [COLOR red][B][UPDATE v%s][/B][/COLOR]' % (ADDONTITLE, VERSION, ver), 'wizardupdate', themeit=THEME2)
			else: addFile('%s [v%s]' % (ADDONTITLE, VERSION), '', themeit=THEME2)
		else: addFile('%s [v%s]' % (ADDONTITLE, VERSION), '', themeit=THEME2)
	else: addFile('%s [v%s]' % (ADDONTITLE, VERSION), '', themeit=THEME2)
	if len(BUILDNAME) > 0:
		version = wiz.checkBuild(BUILDNAME, 'version')
		build = '%s (v%s)' % (BUILDNAME, BUILDVERSION)
		if version > BUILDVERSION: build = '%s [COLOR red][B][UPDATE v%s][/B][/COLOR]' % (build, version)
		addDir(build,'viewbuild',BUILDNAME, themeit=THEME4)
		themefile = wiz.themeCount(BUILDNAME)
		if not themefile == False:
			addFile('None' if BUILDTHEME == "" else BUILDTHEME, 'theme', BUILDNAME, themeit=THEME5)
	else: addDir('Full', 'builds', themeit=THEME4)
	if HIDESPACERS == 'No': addFile(wiz.sep(), '', themeit=THEME3)
	addDir ('Instalar Wizard Palantir'        ,'builds',   icon=ICONBUILDS,   themeit=THEME1)
	##if wiz.platform() == 'android' or DEVELOPER == 'true': addDir ('Instalar APK' ,'apk', icon=ICONAPK, themeit=THEME1)
	##if HIDECONTACT == 'No': addFile('Contacto' ,'contact', icon=ICONCONTACT,  themeit=THEME1)
	##if HIDESPACERS == 'No': addFile(wiz.sep(), '', themeit=THEME3)
	##addFile('Ajustes'      ,'settings', icon=ICONSETTINGS, themeit=THEME1)
	if DEVELOPER == 'true': addDir('Menu','developer', icon=ICONSETTINGS, themeit=THEME1)
	setView('Archivos', 'viewType')

def buildMenu():
	WORKINGURL = wiz.workingURL(BUILDFILE)
	if not WORKINGURL == True:
		addFile('%s Version: %s' % (MCNAME, KODIV), '', icon=ICONBUILDS, themeit=THEME3)
		##addDir ('Guardar datos'       ,'savedata', icon=ICONSAVE,     themeit=THEME3)
		if HIDESPACERS == 'No': addFile(wiz.sep(), '', themeit=THEME3)
		addFile('La URL no es valida', '', icon=ICONBUILDS, themeit=THEME3)
		addFile('%s' % WORKINGURL, '', icon=ICONBUILDS, themeit=THEME3)
	else:
		total, count15, count16, count17, count18, adultcount, hidden = wiz.buildCount()
		third = False; addin = []
		if THIRDPARTY == 'true':
			if not THIRD1NAME == '' and not THIRD1URL == '': third = True; addin.append('1')
			if not THIRD2NAME == '' and not THIRD2URL == '': third = True; addin.append('2')
			if not THIRD3NAME == '' and not THIRD3URL == '': third = True; addin.append('3')
		link  = wiz.openURL(BUILDFILE).replace('\n','').replace('\r','').replace('\t','').replace('gui=""', 'gui="http://"').replace('theme=""', 'theme="http://"').replace('adult=""', 'adult="no"')
		match = re.compile('name="(.+?)".+?ersion="(.+?)".+?rl="(.+?)".+?ui="(.+?)".+?odi="(.+?)".+?heme="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?dult="(.+?)".+?escription="(.+?)"').findall(link)
		if total == 1 and third == False:
			for name, version, url, gui, kodi, theme, icon, fanart, adult, description in match:
				if not SHOWADULT == 'true' and adult.lower() == 'yes': continue
				if not DEVELOPER == 'true' and wiz.strTest(name): continue
				viewBuild(match[0][0])
				return
		addFile('%s Version: %s' % (MCNAME, KODIV), '', icon=ICONBUILDS, themeit=THEME3)
		##addDir ('Guardar datos'       ,'savedata', icon=ICONSAVE,     themeit=THEME3)
		if HIDESPACERS == 'No': addFile(wiz.sep(), '', themeit=THEME3)
		if third == True:
			for item in addin:
				name = eval('THIRD%sNAME' % item)
				addDir ("[B]%s[/B]" % name, 'viewthirdparty', item, icon=ICONBUILDS, themeit=THEME3)
		if len(match) >= 1:
			if SEPERATE == 'true':
				for name, version, url, gui, kodi, theme, icon, fanart, adult, description in match:
					if not SHOWADULT == 'true' and adult.lower() == 'yes': continue
					if not DEVELOPER == 'true' and wiz.strTest(name): continue
					menu = createMenu('install', '', name)
					addDir('[%s] %s (v%s)' % (float(kodi), name, version), 'viewbuild', name, description=description, fanart=fanart,icon=icon, menu=menu, themeit=THEME2)
			else:
				if count18 > 0:
					state = '+' if SHOW18 == 'false' else '-'
					addFile('[B]%s Leia (%s)[/B]' % (state, count18), 'togglesetting',  'show17', themeit=THEME3)
					if SHOW18 == 'true':
						for name, version, url, gui, kodi, theme, icon, fanart, adult, description in match:
							if not SHOWADULT == 'true' and adult.lower() == 'yes': continue
							if not DEVELOPER == 'true' and wiz.strTest(name): continue
							kodiv = int(float(kodi))
							if kodiv == 18:
								menu = createMenu('install', '', name)
								addDir('[%s] %s (v%s)' % (float(kodi), name, version), 'viewbuild', name, description=description, fanart=fanart,icon=icon, menu=menu, themeit=THEME2)
				if count17 > 0:
					state = '+' if SHOW17 == 'false' else '-'
					addFile('[B]%s Krypton (%s)[/B]' % (state, count17), 'togglesetting',  'show17', themeit=THEME3)
					if SHOW17 == 'true':
						for name, version, url, gui, kodi, theme, icon, fanart, adult, description in match:
							if not SHOWADULT == 'true' and adult.lower() == 'yes': continue
							if not DEVELOPER == 'true' and wiz.strTest(name): continue
							kodiv = int(float(kodi))
							if kodiv == 17:
								menu = createMenu('install', '', name)
								addDir('[%s] %s (v%s)' % (float(kodi), name, version), 'viewbuild', name, description=description, fanart=fanart,icon=icon, menu=menu, themeit=THEME2)
				if count16 > 0:
					state = '+' if SHOW16 == 'false' else '-'
					addFile('[B]%s Jarvis (%s)[/B]' % (state, count16), 'togglesetting',  'show16', themeit=THEME3)
					if SHOW16 == 'true':
						for name, version, url, gui, kodi, theme, icon, fanart, adult, description in match:
							if not SHOWADULT == 'true' and adult.lower() == 'yes': continue
							if not DEVELOPER == 'true' and wiz.strTest(name): continue
							kodiv = int(float(kodi))
							if kodiv == 16:
								menu = createMenu('install', '', name)
								addDir('[%s] %s (v%s)' % (float(kodi), name, version), 'viewbuild', name, description=description, fanart=fanart,icon=icon, menu=menu, themeit=THEME2)
				if count15 > 0:
					state = '+' if SHOW15 == 'false' else '-'
					addFile('[B]%s Isengard and Below Builds(%s)[/B]' % (state, count15), 'togglesetting',  'show15', themeit=THEME3)
					if SHOW15 == 'true':
						for name, version, url, gui, kodi, theme, icon, fanart, adult, description in match:
							if not SHOWADULT == 'true' and adult.lower() == 'yes': continue
							if not DEVELOPER == 'true' and wiz.strTest(name): continue
							kodiv = int(float(kodi))
							if kodiv <= 15:
								menu = createMenu('install', '', name)
								addDir('[%s] %s (v%s)' % (float(kodi), name, version), 'viewbuild', name, description=description, fanart=fanart,icon=icon, menu=menu, themeit=THEME2)
		elif hidden > 0: 
			if adultcount > 0:
				addFile('Actualmente solo hay construcciones para adultos', '', icon=ICONBUILDS, themeit=THEME3)
				addFile('Habilitar Mostrar adultos en configuraciones de complementos > Misc', '', icon=ICONBUILDS, themeit=THEME3)
			else:
				addFile('Actualmente no hay Wizard desde %s' % ADDONTITLE, '', icon=ICONBUILDS, themeit=THEME3)
		else: addFile('Archivo de texto wizard no construido correctamente.', '', icon=ICONBUILDS, themeit=THEME3)
	setView('files', 'viewType')

def viewBuild(name):
	WORKINGURL = wiz.workingURL(BUILDFILE)
	if not WORKINGURL == True:
		addFile('Url no valida', '', themeit=THEME3)
		addFile('%s' % WORKINGURL, '', themeit=THEME3)
		return
	if wiz.checkBuild(name, 'version') == False: 
		addFile('Error al leer el archivo txt', '', themeit=THEME3)
		addFile('%s no se encontro el Wizard.' % name, '', themeit=THEME3)
		return
	link = wiz.openURL(BUILDFILE).replace('\n','').replace('\r','').replace('\t','').replace('gui=""', 'gui="http://"').replace('theme=""', 'theme="http://"')
	match = re.compile('name="%s".+?ersion="(.+?)".+?rl="(.+?)".+?ui="(.+?)".+?odi="(.+?)".+?heme="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?review="(.+?)".+?dult="(.+?)".+?escription="(.+?)"' % name).findall(link)
	for version, url, gui, kodi, themefile, icon, fanart, preview, adult, description in match:
		icon        = icon   if wiz.workingURL(icon)   else ICON
		fanart      = fanart if wiz.workingURL(fanart) else FANART
		build       = '%s (v%s)' % (name, version)
		if BUILDNAME == name and version > BUILDVERSION:
			build = '%s [COLOR red][ACTUAL v%s][/COLOR]' % (build, BUILDVERSION)
		addFile(build, '', description=description, fanart=fanart, icon=icon, themeit=THEME4)
		if HIDESPACERS == 'No': addFile(wiz.sep(), '', themeit=THEME3)
		temp1 = int(float(KODIV)); temp2 = int(float(kodi))
		if not temp1 == temp2: 
			if temp1 == 16 and temp2 <= 15: warning = False
			else: warning = True
		else: warning = False
		if warning == True:
			addFile('[I]Wizard para kodi version %s(Instalado : %s)[/I]' % (str(kodi), str(KODIV)), '', fanart=fanart, icon=icon, themeit=THEME3)
		addFile(wiz.sep('INSTALAR'), '', fanart=fanart, icon=icon, themeit=THEME3)
		addFile('Instalar', 'install', name, 'normal' , description=description, fanart=fanart, icon=icon, themeit=THEME1)
		if not gui == 'http://': addFile('Apply guiFix'    , 'install', name, 'gui'     , description=description, fanart=fanart, icon=icon, themeit=THEME1)
		if not themefile == 'http://':
			if wiz.workingURL(themefile) == True:
				addFile(wiz.sep('THEMES'), '', fanart=fanart, icon=icon, themeit=THEME3)
				link  = wiz.openURL(themefile).replace('\n','').replace('\r','').replace('\t','')
				match = re.compile('name="(.+?)".+?rl="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?dult="(.+?)".+?escription="(.+?)"').findall(link)
				for themename, themeurl, themeicon, themefanart, themeadult, description in match:
					if not SHOWADULT == 'true' and themeadult.lower() == 'yes': continue
					themeicon   = themeicon   if themeicon   == 'http://' else icon
					themefanart = themefanart if themefanart == 'http://' else fanart
					addFile(themename if not themename == BUILDTHEME else "[B]%s (Instalado)[/B]" % themename, 'theme', name, themename, description=description, fanart=themefanart, icon=themeicon, themeit=THEME3)
	setView('files', 'viewType')

def viewThirdList(number):
	name = eval('THIRD%sNAME' % number)
	url  = eval('THIRD%sURL' % number)
	work = wiz.workingURL(url)
	if not work == True:
		addFile('Url no valida', '', icon=ICONBUILDS, themeit=THEME3)
		addFile('%s' % WORKINGURL, '', icon=ICONBUILDS, themeit=THEME3)
	else:
		type, buildslist = wiz.thirdParty(url)
		addFile("[B]%s[/B]" % name, '', themeit=THEME3)
		if HIDESPACERS == 'No': addFile(wiz.sep(), '', themeit=THEME3)
		if type:
			for name, version, url, kodi, icon, fanart, adult, description in buildslist:
				if not SHOWADULT == 'true' and adult.lower() == 'yes': continue
				addFile("[%s] %s v%s" % (kodi, name, version), 'installthird', name, url, icon=icon, fanart=fanart, description=description, themeit=THEME2)
		else:
			for name, url, icon, fanart, description in buildslist:
				addFile(name, 'installthird', name, url, icon=icon, fanart=fanart, description=description, themeit=THEME2)

def editThirdParty(number):
	name  = eval('THIRD%sNAME' % number)
	url   = eval('THIRD%sURL' % number)
	name2 = wiz.getKeyboard(name, 'Nombre del Wizard')
	url2  = wiz.getKeyboard(url, 'URL del TXT del Wizard')
	
	wiz.setS('wizard%sname' % number, name2)
	wiz.setS('wizard%surl' % number, url2)

def apkScraper(name=""):
	if name == 'kodi':
		kodiurl1 = 'http://mirrors.kodi.tv/releases/android/arm/'
		kodiurl2 = 'http://mirrors.kodi.tv/releases/android/arm/old/'
		url1 = wiz.openURL(kodiurl1).replace('\n', '').replace('\r', '').replace('\t', '')
		url2 = wiz.openURL(kodiurl2).replace('\n', '').replace('\r', '').replace('\t', '')
		x = 0
		match1 = re.compile('<tr><td><a href="(.+?)">(.+?)</a></td><td>(.+?)</td><td>(.+?)</td></tr>').findall(url1)
		match2 = re.compile('<tr><td><a href="(.+?)">(.+?)</a></td><td>(.+?)</td><td>(.+?)</td></tr>').findall(url2)
		
		addFile("Official Kodi Apk\'s", themeit=THEME1)
		rc = False
		for url, name, size, date in match1:
			if url in ['../', 'old/']: continue
			if not url.endswith('.apk'): continue
			if not url.find('_') == -1 and rc == True: continue
			try:
				tempname = name.split('-')
				if not url.find('_') == -1:
					rc = True
					name2, v2 = tempname[2].split('_')
				else: 
					name2 = tempname[2]
					v2 = ''
				title = "[COLOR %s]%s v%s%s %s[/COLOR] [COLOR %s]%s[/COLOR] [COLOR %s]%s[/COLOR]" % (COLOR1, tempname[0].title(), tempname[1], v2.upper(), name2, COLOR2, size.replace(' ', ''), COLOR1, date)
				download = urljoin(kodiurl1, url)
				addFile(title, 'apkinstall', "%s v%s%s %s" % (tempname[0].title(), tempname[1], v2.upper(), name2), download)
				x += 1
			except:
				wiz.log("Error on: %s" % name)
			
		for url, name, size, date in match2:
			if url in ['../', 'old/']: continue
			if not url.endswith('.apk'): continue
			if not url.find('_') == -1: continue
			try:
				tempname = name.split('-')
				title = "[COLOR %s]%s v%s %s[/COLOR] [COLOR %s]%s[/COLOR] [COLOR %s]%s[/COLOR]" % (COLOR1, tempname[0].title(), tempname[1], tempname[2], COLOR2, size.replace(' ', ''), COLOR1, date)
				download = urljoin(kodiurl2, url)
				addFile(title, 'apkinstall', "%s v%s %s" % (tempname[0].title(), tempname[1], tempname[2]), download)
				x += 1
			except:
				wiz.log("Error on: %s" % name)
		if x == 0: addFile("Error Kodi Actualmente caido.")
	elif name == 'spmc':
		spmcurl1 = 'https://github.com/koying/SPMC/releases'
		url1 = wiz.openURL(spmcurl1).replace('\n', '').replace('\r', '').replace('\t', '')
		x = 0
		match1 = re.compile('<div.+?lass="release-body.+?div class="release-header".+?a href=.+?>(.+?)</a>.+?ul class="release-downloads">(.+?)</ul>.+?/div>').findall(url1)
		
		addFile("Official SPMC Apk\'s", themeit=THEME1)

		for name, urls in match1:
			tempurl = ''
			match2 = re.compile('<li>.+?<a href="(.+?)" rel="nofollow">.+?<small class="text-gray float-right">(.+?)</small>.+?strong>(.+?)</strong>.+?</a>.+?</li>').findall(urls)
			for apkurl, apksize, apkname in match2:
				if apkname.find('armeabi') == -1: continue
				if apkname.find('launcher') > -1: continue
				tempurl = urljoin('https://github.com', apkurl)
				break
			if tempurl == '': continue
			try:
				name = "SPMC %s" % name
				title = "[COLOR %s]%s[/COLOR] [COLOR %s]%s[/COLOR]" % (COLOR1, name, COLOR2, apksize.replace(' ', ''))
				download = tempurl
				addFile(title, 'apkinstall', name, download)
				x += 1
			except Exception, e:
				wiz.log("Error on: %s / %s" % (name, str(e)))
		if x == 0: addFile("Error SPMC Actualmente caido.")

def installFromKodi(plugin, over=True):
	if over == True:
		xbmc.sleep(2000)
	#wiz.ebi('InstallAddon(%s)' % plugin)
	wiz.ebi('RunPlugin(plugin://%s)' % plugin)
	if not wiz.whileWindow('yesnodialog'):
		return False
	xbmc.sleep(500)
	if wiz.whileWindow('okdialog'):
		return False
	wiz.whileWindow('progressdialog')
	if os.path.exists(os.path.join(ADDONS, plugin)): return True
	else: return False

def installDep(name, DP=None):
	dep=os.path.join(ADDONS,name,'addon.xml')
	if os.path.exists(dep):
		source = open(dep,mode='r'); link = source.read(); source.close(); 
		match  = wiz.parseDOM(link, 'import', ret='addon')
		for depends in match:
			if not 'xbmc.python' in depends:
				if not DP == None:
					DP.update(0, '', '[COLOR %s]%s[/COLOR]' % (COLOR1, depends))
				wiz.createTemp(depends)
				# continue
				# dependspath=os.path.join(ADDONS, depends)
				# if not os.path.exists(dependspath):
					# zipname = '%s-%s.zip' % (depends, match2[match.index(depends)])
					# depzip = urljoin("%s%s/" % (MODURL2, depends), zipname)
					# if not wiz.workingURL(depzip) == True:
						# depzip = urljoin(MODURL, '%s.zip' % depends)
						# if not wiz.workingURL(depzip) == True:
							# wiz.createTemp(depends)
							# if KODIV >= 17: wiz.addonDatabase(depends, 1)
							# continue
					# lib=os.path.join(PACKAGES, '%s.zip' % depends)
					# try: os.remove(lib)
					# except: pass
					# DP.update(0, '[COLOR %s][B]Downloading Dependency:[/B][/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, depends),'', 'Please Wait')
					# downloader.download(depzip, lib, DP)
					# xbmc.sleep(100)
					# title = '[COLOR %s][B]Installing Dependency:[/B][/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, depends)
					# DP.update(0, title,'', 'Please Wait')
					# percent, errors, error = extract.all(lib,ADDONS,DP, title=title)
					# if KODIV >= 17: wiz.addonDatabase(depends, 1)
					# installed(depends)
					# installDep(depends)
					# xbmc.sleep(100)
					# DP.close()

def installed(addon):
	url = os.path.join(ADDONS,addon,'addon.xml')
	if os.path.exists(url):
		try:
			list  = open(url,mode='r'); g = list.read(); list.close()
			name = wiz.parseDOM(g, 'addon', ret='name', attrs = {'id': addon})
			icon  = os.path.join(ADDONS,addon,'icon.png')
			wiz.LogNotify('[COLOR %s]%s[/COLOR]' % (COLOR1, name[0]), '[COLOR %s]Addons Habilitados[/COLOR]' % COLOR2, '2000', icon)
		except: pass

def maintMenu(view=None):
	on = '[B][COLOR green]SI[/COLOR][/B]'; off = '[B][COLOR red]NO[/COLOR][/B]'
	autoclean   = 'false' if AUTOCLEANUP    == 'false' else 'false'
	cache       = 'false' if AUTOCACHE      == 'false' else 'false'
	packages    = 'false' if AUTOPACKAGES   == 'false' else 'false'
	thumbs      = 'false' if AUTOTHUMBS     == 'false' else 'false'
	maint       = 'true' if SHOWMAINT      == 'true' else 'false'
	includevid  = 'true' if INCLUDEVIDEO   == 'true' else 'false'
	includeall  = 'true' if INCLUDEALL     == 'true' else 'false'
	thirdparty  = 'true' if THIRDPARTY     == 'true' else 'false'
	if wiz.Grab_Log(True) == False: kodilog = 0
	else: kodilog = errorChecking(wiz.Grab_Log(True), True, True)
	if wiz.Grab_Log(True, True) == False: kodioldlog = 0
	else: kodioldlog = errorChecking(wiz.Grab_Log(True,True), True, True)
	errorsinlog = int(kodilog) + int(kodioldlog)
	errorsfound = str(errorsinlog) + ' Errores encontrados' if errorsinlog > 0 else 'Ninguno'
	wizlogsize = ': [COLOR red]No encontrado[/COLOR]' if not os.path.exists(WIZLOG) else ": [COLOR green]%s[/COLOR]" % wiz.convertSize(os.path.getsize(WIZLOG))
	if includeall == 'true':
		includebob = 'true'
		includepho = 'true'
		includespe = 'true'
		includegen = 'true'
		includeexo = 'true'
		includeone = 'true'
		includesal = 'true'
		includeshd = 'true'
	else:
		includebob = 'true' if INCLUDEBOB     == 'true' else 'false'
		includepho = 'true' if INCLUDEPHOENIX == 'true' else 'false'
		includespe = 'true' if INCLUDESPECTO  == 'true' else 'false'
		includegen = 'true' if INCLUDEGENESIS == 'true' else 'false'
		includeexo = 'true' if INCLUDEEXODUS  == 'true' else 'false'
		includeone = 'true' if INCLUDEONECHAN == 'true' else 'false'
		includesal = 'true' if INCLUDESALTS   == 'true' else 'false'
		includeshd = 'true' if INCLUDESALTSHD == 'true' else 'false'
	sizepack   = wiz.getSize(PACKAGES)
	sizethumb  = wiz.getSize(THUMBS)
	sizecache  = wiz.getCacheSize()
	totalsize  = sizepack+sizethumb+sizecache
	feq        = ['Always', 'Daily', '3 Days', 'Weekly']
	addDir ('[B]Limpiar Herramientas[/B]'       ,'maint', 'clean',  icon=ICONMAINT, themeit=THEME1)
	if view == "clean" or SHOWMAINT == 'true': 
		addFile('Limpieza Total: [COLOR green][B]%s[/B][/COLOR]' % wiz.convertSize(totalsize)  ,'fullclean',       icon=ICONMAINT, themeit=THEME3)
		addFile('Limpiar Cache: [COLOR green][B]%s[/B][/COLOR]' % wiz.convertSize(sizecache)     ,'clearcache',      icon=ICONMAINT, themeit=THEME3)
		addFile('Limpiar Packages: [COLOR green][B]%s[/B][/COLOR]' % wiz.convertSize(sizepack)   ,'clearpackages',   icon=ICONMAINT, themeit=THEME3)
		addFile('Limpiar Thumbnails: [COLOR green][B]%s[/B][/COLOR]' % wiz.convertSize(sizethumb),'clearthumb',      icon=ICONMAINT, themeit=THEME3)
		addFile('Limpiar Todos los Thumbnails', 'oldThumbs',      icon=ICONMAINT, themeit=THEME3)
		addFile('Limpiar Crash Logs',               'clearcrash',      icon=ICONMAINT, themeit=THEME3)
		addFile('Purgar Databases',                'purgedb',         icon=ICONMAINT, themeit=THEME3)
		addFile('Fresh Start',                    'freshstart',      icon=ICONMAINT, themeit=THEME3)
	addDir ('[B]Addon Herramientas[/B]',       'maint', 'addon',  icon=ICONMAINT, themeit=THEME1)
	if view == "addon" or SHOWMAINT == 'true': 
		addFile('Eliminar Addons',                  'removeaddons',    icon=ICONMAINT, themeit=THEME3)
		addDir ('Eliminar Addon Data',              'removeaddondata', icon=ICONMAINT, themeit=THEME3)
		addDir ('Habilitar/deshabilitar Addons',          'enableaddons',    icon=ICONMAINT, themeit=THEME3)
		addFile('Habilitar/deshabilitar Addons de Adultos',    'toggleadult',     icon=ICONMAINT, themeit=THEME3)
		addFile('Forzar Update Addons',            'forceupdate',     icon=ICONMAINT, themeit=THEME3)
		addFile('Ocultar password',   'hidepassword',   icon=ICONMAINT, themeit=THEME3)
		addFile('Mostrar password', 'unhidepassword', icon=ICONMAINT, themeit=THEME3)
	addDir ('[B]Herramientas varias[/B]'     ,'maint', 'misc',   icon=ICONMAINT, themeit=THEME1)
	if view == "misc" or SHOWMAINT == 'true': 
		addFile('Kodi 17 Fix',                    'kodi17fix',       icon=ICONMAINT, themeit=THEME3)
		addFile('Recargar Skin',                    'forceskin',       icon=ICONMAINT, themeit=THEME3)
		addFile('Actualizar perfil',                 'forceprofile',    icon=ICONMAINT, themeit=THEME3)
		addFile('Forzar cierre de Kodi',               'forceclose',      icon=ICONMAINT, themeit=THEME3)
		addFile('Subir Kodi.log',                'uploadlog',       icon=ICONMAINT, themeit=THEME3)
		addFile('Ver Errores en el Log: %s' % (errorsfound), 'viewerrorlog',    icon=ICONMAINT, themeit=THEME3)
		addFile('Ver Log File',                  'viewlog',         icon=ICONMAINT, themeit=THEME3)
		addFile('Ver Wizard Log File',           'viewwizlog',      icon=ICONMAINT, themeit=THEME3)
		addFile('Eliminar Wizard Log File%s' % wizlogsize,'clearwizlog',     icon=ICONMAINT, themeit=THEME3)
	addDir ('[B]Back up/Restore[/B]'     ,'maint', 'backup',   icon=ICONMAINT, themeit=THEME1)
	if view == "backup" or SHOWMAINT == 'true':
		addFile('Limpiar el Back Up de la carpeta',        'clearbackup',     icon=ICONMAINT,   themeit=THEME3)
		addFile('Ubicacion del Back Up: [COLOR %s]%s[/COLOR]' % (COLOR2, MYBUILDS),'settings', 'Maintenance', icon=ICONMAINT, themeit=THEME3)
		addFile('[Back Up]: Wizard',               'backupbuild',     icon=ICONMAINT,   themeit=THEME3)
		addFile('[Back Up]: GuiFix',              'backupgui',       icon=ICONMAINT,   themeit=THEME3)
		addFile('[Back Up]: Tema',               'backuptheme',     icon=ICONMAINT,   themeit=THEME3)
		addFile('[Back Up]: Addon_data',          'backupaddon',     icon=ICONMAINT,   themeit=THEME3)
		addFile('[Restore]: Local Wizard',         'restorezip',      icon=ICONMAINT,   themeit=THEME3)
		addFile('[Restore]: Local GuiFix',        'restoregui',      icon=ICONMAINT,   themeit=THEME3)
		addFile('[Restore]: Local Addon_data',    'restoreaddon',    icon=ICONMAINT,   themeit=THEME3)
		addFile('[Restore]: Externo Wizard',      'restoreextzip',   icon=ICONMAINT,   themeit=THEME3)
		addFile('[Restore]: Externo GuiFix',     'restoreextgui',   icon=ICONMAINT,   themeit=THEME3)
		addFile('[Restore]: Externo Addon_data', 'restoreextaddon', icon=ICONMAINT,   themeit=THEME3)
	addDir ('[B]Ajustes / arreglos del sistema[/B]',       'maint', 'tweaks', icon=ICONMAINT, themeit=THEME1)
	if view == "tweaks" or SHOWMAINT == 'true': 
		if not ADVANCEDFILE == 'http://' and not ADVANCEDFILE == '':
			addDir ('Advanced Settings',            'advancedsetting',  icon=ICONMAINT, themeit=THEME3)
		else: 
			if os.path.exists(ADVANCED):
				addFile('Ver actual AdvancedSettings.xml',   'currentsettings', icon=ICONMAINT, themeit=THEME3)
				addFile('Borrar actual AdvancedSettings.xml', 'removeadvanced',  icon=ICONMAINT, themeit=THEME3)
			addFile('Configuracin rapida de AdvancedSettings.xml',    'autoadvanced',    icon=ICONMAINT, themeit=THEME3)
		addFile('Explorar fuentes para enlaces rotos',  'checksources',    icon=ICONMAINT, themeit=THEME3)
		addFile('Escanear para repositorios rotos',   'checkrepos',      icon=ICONMAINT, themeit=THEME3)
		addFile('Addons no actualizados',        'fixaddonupdate',  icon=ICONMAINT, themeit=THEME3)
		addFile('Eliminar nombres de archivo no Ascii',     'asciicheck',      icon=ICONMAINT, themeit=THEME3)
		addFile('Convertir rutas a especiales',       'convertpath',     icon=ICONMAINT, themeit=THEME3)
		addDir ('Informacion del sistema',             'systeminfo',      icon=ICONMAINT, themeit=THEME3)
	addFile('Mostrar todas las Herramientas: %s' % maint.replace('true',on).replace('false',off) ,'togglesetting', 'showmaint', icon=ICONMAINT, themeit=THEME2)
	addDir ('[I]<< Volver al menu Principal[/I]', icon=ICONMAINT, themeit=THEME2)
	addFile('Asistentes de terceros: %s' % thirdparty.replace('true',on).replace('false',off) ,'togglesetting', 'enable3rd', fanart=FANART, icon=ICONMAINT, themeit=THEME1)
	if thirdparty == 'true':
		first = THIRD1NAME if not THIRD1NAME == '' else 'Not Set'
		secon = THIRD2NAME if not THIRD2NAME == '' else 'Not Set'
		third = THIRD3NAME if not THIRD3NAME == '' else 'Not Set'
		addFile('Editar Asistentes de terceros 1: [COLOR %s]%s[/COLOR]' % (COLOR2, first), 'editthird', '1', icon=ICONMAINT, themeit=THEME3)
		addFile('Editar Asistentes de terceros 2: [COLOR %s]%s[/COLOR]' % (COLOR2, secon), 'editthird', '2', icon=ICONMAINT, themeit=THEME3)
		addFile('Editar Asistentes de terceros 3: [COLOR %s]%s[/COLOR]' % (COLOR2, third), 'editthird', '3', icon=ICONMAINT, themeit=THEME3)
	addFile('Auto Limpieza', '', fanart=FANART, icon=ICONMAINT, themeit=THEME1)
	addFile('Limpieza automatica al inicio: %s' % autoclean.replace('true',on).replace('false',off) ,'togglesetting', 'autoclean',   icon=ICONMAINT, themeit=THEME3)
	if autoclean == 'true':
		addFile('--- Frecuencia de limpieza automatica: [B][COLOR green]%s[/COLOR][/B]' % feq[AUTOFEQ], 'changefeq', icon=ICONMAINT, themeit=THEME3)
		addFile('--- Limpiar Cache: %s' % cache.replace('true',on).replace('false',off), 'togglesetting', 'clearcache', icon=ICONMAINT, themeit=THEME3)
		addFile('--- Limpiar Packages: %s' % packages.replace('true',on).replace('false',off), 'togglesetting', 'clearpackages', icon=ICONMAINT, themeit=THEME3)
		addFile('--- Limpiar Imagenes: %s' % thumbs.replace('true',on).replace('false',off), 'togglesetting', 'clearthumbs', icon=ICONMAINT, themeit=THEME3)
	addFile('Limpiar Video Cache', '', fanart=FANART, icon=ICONMAINT, themeit=THEME1)
	addFile('Incluido Video Cache en Limpiar Cache: %s' % includevid.replace('true',on).replace('false',off), 'togglecache', 'includevideo', icon=ICONMAINT, themeit=THEME3)
	if includevid == 'true':
		addFile('--- Incluir todos los Addons de video: %s' % includeall.replace('true',on).replace('false',off), 'togglecache', 'includeall', icon=ICONMAINT, themeit=THEME3)
		addFile('--- Habilitar todos los Addons de video', 'togglecache', 'true', icon=ICONMAINT, themeit=THEME3)
		addFile('--- Deshabilitar todos los Addons de video', 'togglecache', 'false', icon=ICONMAINT, themeit=THEME3)
	setView('files', 'viewType')

def advancedWindow(url=None):
	if not ADVANCEDFILE == 'http://':
		if url == None:
			ADVANCEDWORKING = wiz.workingURL(ADVANCEDFILE)
			TEMPADVANCEDFILE = uservar.ADVANCEDFILE
		else:
			ADVANCEDWORKING  = wiz.workingURL(url)
			TEMPADVANCEDFILE = url
		addFile('Configuracion rapida AdvancedSettings.xml', 'autoadvanced', icon=ICONMAINT, themeit=THEME3)
		if os.path.exists(ADVANCED): 
			addFile('Ver AdvancedSettings.xml', 'currentsettings', icon=ICONMAINT, themeit=THEME3)
			addFile('Eliminar AdvancedSettings.xml', 'removeadvanced',  icon=ICONMAINT, themeit=THEME3)
		if ADVANCEDWORKING == True:
			if HIDESPACERS == 'No': addFile(wiz.sep(), '', icon=ICONMAINT, themeit=THEME3)
			link = wiz.openURL(TEMPADVANCEDFILE).replace('\n','').replace('\r','').replace('\t','')
			match = re.compile('name="(.+?)".+?ection="(.+?)".+?rl="(.+?)".+?con="(.+?)".+?anart="(.+?)".+?escription="(.+?)"').findall(link)
			if len(match) > 0:
				for name, section, url, icon, fanart, description in match:
					if section.lower() == "yes":
						addDir ("[B]%s[/B]" % name, 'advancedsetting', url, description=description, icon=icon, fanart=fanart, themeit=THEME3)
					else:
						addFile(name, 'writeadvanced', name, url, description=description, icon=icon, fanart=fanart, themeit=THEME2)
			else: wiz.log("[Advanced Settings] ERROR")
		else: wiz.log("[Advanced Settings] URL no localizada: %s" % ADVANCEDWORKING)
	else: wiz.log("[Advanced Settings] no disponible")

def writeAdvanced(name, url):
	ADVANCEDWORKING = wiz.workingURL(url)
	if ADVANCEDWORKING == True:
		if os.path.exists(ADVANCED): choice = DIALOG.yesno(ADDONTITLE, "[COLOR %s]Deseas sobrescribir su Configuracion del Advanced Settings actual [COLOR %s]%s[/COLOR]?[/COLOR]" % (COLOR2, COLOR1, name), yeslabel="[B][COLOR green]Sobrescribir[/COLOR][/B]", nolabel="[B][COLOR red]Cancelar[/COLOR][/B]")
		else: choice = DIALOG.yesno(ADDONTITLE, "[COLOR %s]Te gustaria descargar e instalar [COLOR %s]%s[/COLOR]?[/COLOR]" % (COLOR2, COLOR1, name), yeslabel="[B][COLOR green]Instalar[/COLOR][/B]", nolabel="[B][COLOR red]Cancelar[/COLOR][/B]")

		if choice == 1:
			file = wiz.openURL(url)
			f = open(ADVANCED, 'w'); 
			f.write(file)
			f.close()
			DIALOG.ok(ADDONTITLE, '[COLOR %s]AdvancedSettings.xml instalado con exito.  Una vez que hagas clic en Aceptar, forzaras el cierre de kodi.[/COLOR]' % COLOR2)
			wiz.killxbmc(True)
		else: wiz.log("[Advanced Settings] instalacion cancelada"); wiz.LogNotify('[COLOR %s]%s[/COLOR]' % (COLOR1, ADDONTITLE), "[COLOR %s]Cancelado![/COLOR]" % COLOR2); return
	else: wiz.log("[Advanced Settings] URL no Valida: %s" % ADVANCEDWORKING); wiz.LogNotify('[COLOR %s]%s[/COLOR]' % (COLOR1, ADDONTITLE), "[COLOR %s]URL no localizada[/COLOR]" % COLOR2)

def viewAdvanced():
	f = open(ADVANCED)
	a = f.read().replace('\t', '    ')
	wiz.TextBox(ADDONTITLE, a)
	f.close()

def removeAdvanced():
	if os.path.exists(ADVANCED):
		wiz.removeFile(ADVANCED)
	else: LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]AdvancedSettings.xml no encontrado[/COLOR]")

def showAutoAdvanced():
	notify.autoConfig()

def getIP():
	site  = 'http://whatismyipaddress.com/'
	if not wiz.workingURL(site): return 'Unknown', 'Unknown', 'Unknown'
	page  = wiz.openURL(site).replace('\n','').replace('\r','')
	if not 'Access Denied' in page:
		ipmatch   = re.compile('whatismyipaddress.com/ip/(.+?)"').findall(page)
		ipfinal   = ipmatch[0] if (len(ipmatch) > 0) else 'Unknown'
		details   = re.compile('"font-size:14px;">(.+?)</td>').findall(page)
		provider  = details[0] if (len(details) > 0) else 'Unknown'
		location  = details[1]+', '+details[2]+', '+details[3] if (len(details) > 2) else 'Unknown'
		return ipfinal, provider, location
	else: return 'Unknown', 'Unknown', 'Unknown'

def systemInfo():
	infoLabel = ['System.FriendlyName', 
				 'System.BuildVersion', 
				 'System.CpuUsage',
				 'System.ScreenMode',
				 'Network.IPAddress',
				 'Network.MacAddress',
				 'System.Uptime',
				 'System.TotalUptime',
				 'System.FreeSpace',
				 'System.UsedSpace',
				 'System.TotalSpace',
				 'System.Memory(free)',
				 'System.Memory(used)',
				 'System.Memory(total)']
	data      = []; x = 0
	for info in infoLabel:
		temp = wiz.getInfo(info)
		y = 0
		while temp == "Busy" and y < 10:
			temp = wiz.getInfo(info); y += 1; wiz.log("%s sleep %s" % (info, str(y))); xbmc.sleep(200)
		data.append(temp)
		x += 1
	storage_free  = data[8] if 'Una' in data[8] else wiz.convertSize(int(float(data[8][:-8]))*1024*1024)
	storage_used  = data[9] if 'Una' in data[9] else wiz.convertSize(int(float(data[9][:-8]))*1024*1024)
	storage_total = data[10] if 'Una' in data[10] else wiz.convertSize(int(float(data[10][:-8]))*1024*1024)
	ram_free      = wiz.convertSize(int(float(data[11][:-2]))*1024*1024)
	ram_used      = wiz.convertSize(int(float(data[12][:-2]))*1024*1024)
	ram_total     = wiz.convertSize(int(float(data[13][:-2]))*1024*1024)
	exter_ip, provider, location = getIP()
	
	picture = []; music = []; video = []; programs = []; repos = []; scripts = []; skins = []
	
	fold = glob.glob(os.path.join(ADDONS, '*/'))
	for folder in sorted(fold, key = lambda x: x):
		foldername = os.path.split(folder[:-1])[1]
		if foldername == 'packages': continue
		xml = os.path.join(folder, 'addon.xml')
		if os.path.exists(xml):
			f      = open(xml)
			a      = f.read()
			prov   = re.compile("<provides>(.+?)</provides>").findall(a)
			if len(prov) == 0:
				if foldername.startswith('skin'): skins.append(foldername)
				if foldername.startswith('repo'): repos.append(foldername)
				else: scripts.append(foldername)
			elif not (prov[0]).find('executable') == -1: programs.append(foldername)
			elif not (prov[0]).find('video') == -1: video.append(foldername)
			elif not (prov[0]).find('audio') == -1: music.append(foldername)
			elif not (prov[0]).find('image') == -1: picture.append(foldername)

	addFile('[B]Kodi Info:[/B]', '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Nombre:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[0]), '', icon=ICONMAINT, themeit=THEME3)
	addFile('[COLOR %s]Version:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[1]), '', icon=ICONMAINT, themeit=THEME3)
	addFile('[COLOR %s]Plataforma:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, wiz.platform().title()), '', icon=ICONMAINT, themeit=THEME3)
	addFile('[COLOR %s]Uso del CPU:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[2]), '', icon=ICONMAINT, themeit=THEME3)
	addFile('[COLOR %s]Modo de pantalla:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[3]), '', icon=ICONMAINT, themeit=THEME3)
	
	addFile('[B]Tiempo de actividad:[/B]', '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Actual:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[6]), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Total:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[7]), '', icon=ICONMAINT, themeit=THEME2)
	
	addFile('[B]Uso disco Local:[/B]', '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Uso:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, storage_free), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Libre:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, storage_used), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Total:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, storage_total), '', icon=ICONMAINT, themeit=THEME2)
	
	addFile('[B]Uso de la Ram:[/B]', '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Memoria usada:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, ram_free), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Memoria libre:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, ram_used), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Memoria total:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, ram_total), '', icon=ICONMAINT, themeit=THEME2)
	
	addFile('[B]Red:[/B]', '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]IP local:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[4]), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]IP Externa:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, exter_ip), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Proveedor:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, provider), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Localizacion:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, location), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Mac:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, data[5]), '', icon=ICONMAINT, themeit=THEME2)
	
	totalcount = len(picture) + len(music) + len(video) + len(programs) + len(scripts) + len(skins) + len(repos) 
	addFile('[B]Addons([COLOR %s]%s[/COLOR]):[/B]' % (COLOR1, totalcount), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Video Addons:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, str(len(video))), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Programas Addons:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, str(len(programs))), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Musica Addons:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, str(len(music))), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Imagenes Addons:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, str(len(picture))), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Repositorios:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, str(len(repos))), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Skins:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, str(len(skins))), '', icon=ICONMAINT, themeit=THEME2)
	addFile('[COLOR %s]Scripts/Modulos:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR1, COLOR2, str(len(scripts))), '', icon=ICONMAINT, themeit=THEME2)

def saveMenu():
	on = '[COLOR green]SI[/COLOR]'; off = '[COLOR red]NO[/COLOR]'
	trakt      = 'true' if KEEPTRAKT     == 'true' else 'false'
	real       = 'true' if KEEPREAL      == 'true' else 'false'
	login      = 'true' if KEEPLOGIN     == 'true' else 'false'
	sources    = 'true' if KEEPSOURCES   == 'true' else 'false'
	advanced   = 'true' if KEEPADVANCED  == 'true' else 'false'
	profiles   = 'true' if KEEPPROFILES  == 'true' else 'false'
	favourites = 'true' if KEEPFAVS      == 'true' else 'false'
	repos      = 'true' if KEEPREPOS     == 'true' else 'false'
	super      = 'true' if KEEPSUPER     == 'true' else 'false'
	whitelist  = 'true' if KEEPWHITELIST == 'true' else 'false'

	addFile('Importar Save Data',              'managedata', 'import', icon=ICONSAVE,  themeit=THEME1)
	addFile('Exportar Save Data',              'managedata', 'export', icon=ICONSAVE,  themeit=THEME1)
	addFile('- Haga clic para alternar la configuracion -', '', themeit=THEME3)
	addFile('Mantener \'Sources.xml\': %s' % sources.replace('true',on).replace('false',off)           ,'togglesetting', 'keepsources',    icon=ICONSAVE,  themeit=THEME1)
	addFile('Mantener \'Profiles.xml\': %s' % profiles.replace('true',on).replace('false',off)         ,'togglesetting', 'keepprofiles',   icon=ICONSAVE,  themeit=THEME1)
	addFile('Mantener \'Advancedsettings.xml\': %s' % advanced.replace('true',on).replace('false',off) ,'togglesetting', 'keepadvanced',   icon=ICONSAVE,  themeit=THEME1)
	addFile('Mantener \'Favourites.xml\': %s' % favourites.replace('true',on).replace('false',off)     ,'togglesetting', 'keepfavourites', icon=ICONSAVE,  themeit=THEME1)
	addFile('Mantener Super Favourites: %s' % super.replace('true',on).replace('false',off)            ,'togglesetting', 'keepsuper',      icon=ICONSAVE,  themeit=THEME1)
	addFile('Mantener Repositorios\'s: %s' % repos.replace('true',on).replace('false',off)           ,'togglesetting', 'keeprepos',      icon=ICONSAVE,  themeit=THEME1)
	addFile('Mantener Mi \'Lista blanca\': %s' % whitelist.replace('true',on).replace('false',off)        ,'togglesetting', 'keepwhitelist',  icon=ICONSAVE,  themeit=THEME1)
	if whitelist == 'true':
		addFile('Editar Mi Lista blanca',        'whitelist', 'edit',   icon=ICONSAVE,  themeit=THEME1)
		addFile('Ver Mi Lista blanca',        'whitelist', 'view',   icon=ICONSAVE,  themeit=THEME1)
		addFile('Borrar Mi Lista blanca',       'whitelist', 'clear',  icon=ICONSAVE,  themeit=THEME1)
		addFile('Importar Mi Lista blanca',      'whitelist', 'import', icon=ICONSAVE,  themeit=THEME1)
		addFile('Exportar Mi Lista blanca',      'whitelist', 'export', icon=ICONSAVE,  themeit=THEME1)
	setView('files', 'viewType')

def fixUpdate():
	if KODIV < 17: 
		dbfile = os.path.join(DATABASE, wiz.latestDB('Addons'))
		try:
			os.remove(dbfile)
		except Exception, e:
			wiz.log("No se puede eliminar %s, Purgar DB" % dbfile)
			wiz.purgeDb(dbfile)
	else:
		xbmc.log("Se elimino Addons.db solicitado pero no funciona en Kodi 17")

def removeAddonMenu():
	fold = glob.glob(os.path.join(ADDONS, '*/'))
	addonnames = []; addonids = []
	for folder in sorted(fold, key = lambda x: x):
		foldername = os.path.split(folder[:-1])[1]
		if foldername in EXCLUDES: continue
		elif foldername in DEFAULTPLUGINS: continue
		elif foldername == 'packages': continue
		xml = os.path.join(folder, 'addon.xml')
		if os.path.exists(xml):
			f      = open(xml)
			a      = f.read()
			match  = wiz.parseDOM(a, 'addon', ret='id')

			addid  = foldername if len(match) == 0 else match[0]
			try: 
				add = xbmcaddon.Addon(id=addid)
				addonnames.append(add.getAddonInfo('name'))
				addonids.append(addid)
			except:
				pass
	if len(addonnames) == 0:
		wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Sin Addons para eliminar[/COLOR]" % COLOR2)
		return
	if KODIV > 16:
		selected = DIALOG.multiselect("%s: Seleccione los addons que desea eliminar." % ADDONTITLE, addonnames)
	else:
		selected = []; choice = 0
		tempaddonnames = ["-- Click para continuar --"] + addonnames
		while not choice == -1:
			choice = DIALOG.select("%s: Seleccione los addons que desea eliminar." % ADDONTITLE, tempaddonnames)
			if choice == -1: break
			elif choice == 0: break
			else: 
				choice2 = (choice-1)
				if choice2 in selected:
					selected.remove(choice2)
					tempaddonnames[choice] = addonnames[choice2]
				else:
					selected.append(choice2)
					tempaddonnames[choice] = "[B][COLOR %s]%s[/COLOR][/B]" % (COLOR1, addonnames[choice2])
	if selected == None: return
	if len(selected) > 0:
		wiz.addonUpdates('set')
		for addon in selected:
			removeAddon(addonids[addon], addonnames[addon], True)

		xbmc.sleep(500)
		
		if INSTALLMETHOD == 1: todo = 1
		elif INSTALLMETHOD == 2: todo = 0
		else: todo = DIALOG.yesno(ADDONTITLE, "[COLOR %s]Te gustaria [COLOR %s]Forzar el cierre de[/COLOR] kodi con [COLOR %s]Perfil Actual [/COLOR]?[/COLOR]" % (COLOR2, COLOR1, COLOR1), yeslabel="[B][COLOR green]Perfil Actual[/COLOR][/B]", nolabel="[B][COLOR red]Forzar Cierre[/COLOR][/B]")
		if todo == 1: wiz.reloadFix('remove addon')
		else: wiz.addonUpdates('reset'); wiz.killxbmc(True)

def removeAddonDataMenu():
	if os.path.exists(ADDOND):
		addFile('[COLOR red][B][BORRAR][/B][/COLOR] Addon_Data', 'removedata', 'all', themeit=THEME2)
		addFile('[COLOR red][B][BORRAR][/B][/COLOR] Complementos', 'removedata', 'uninstalled', themeit=THEME2)
		addFile('[COLOR red][B][BORRAR][/B][/COLOR] Todas las carpetas vacias en Addon_Data', 'removedata', 'empty', themeit=THEME2)
		addFile('[COLOR red][B][BORRAR][/B][/COLOR] %s Addon_Data' % ADDONTITLE, 'resetaddon', themeit=THEME2)
		if HIDESPACERS == 'No': addFile(wiz.sep(), '', themeit=THEME3)
		fold = glob.glob(os.path.join(ADDOND, '*/'))
		for folder in sorted(fold, key = lambda x: x):
			foldername = folder.replace(ADDOND, '').replace('\\', '').replace('/', '')
			icon = os.path.join(folder.replace(ADDOND, ADDONS), 'icon.png')
			fanart = os.path.join(folder.replace(ADDOND, ADDONS), 'fanart.png')
			folderdisplay = foldername
			replace = {'audio.':'[COLOR orange][AUDIO] [/COLOR]', 'metadata.':'[COLOR cyan][METADATA] [/COLOR]', 'module.':'[COLOR orange][MODULOS] [/COLOR]', 'plugin.':'[COLOR blue][PLUGIN] [/COLOR]', 'program.':'[COLOR orange][PROGRAMAS] [/COLOR]', 'repository.':'[COLOR gold][REPO] [/COLOR]', 'script.':'[COLOR green][SCRIPT] [/COLOR]', 'service.':'[COLOR green][SERVICIOS] [/COLOR]', 'skin.':'[COLOR dodgerblue][SKIN] [/COLOR]', 'video.':'[COLOR orange][VIDEOS] [/COLOR]', 'weather.':'[COLOR yellow][TIEMPO] [/COLOR]'}
			for rep in replace:
				folderdisplay = folderdisplay.replace(rep, replace[rep])
			if foldername in EXCLUDES: folderdisplay = '[COLOR green][B][PROTEGIDO][/B][/COLOR] %s' % folderdisplay
			else: folderdisplay = '[COLOR red][B][BORRAR][/B][/COLOR] %s' % folderdisplay
			addFile(' %s' % folderdisplay, 'removedata', foldername, icon=icon, fanart=fanart, themeit=THEME2)
	else:
		addFile('No se encontro ninguna carpeta con Addons.', '', themeit=THEME3)
	setView('files', 'viewType')

def enableAddons():
	addFile("[I][B][COLOR red]!! Aviso: Deshabilitar algunos complementos puede causar problemas![/COLOR][/B][/I]", '', icon=ICONMAINT)
	fold = glob.glob(os.path.join(ADDONS, '*/'))
	x = 0
	for folder in sorted(fold, key = lambda x: x):
		foldername = os.path.split(folder[:-1])[1]
		if foldername in EXCLUDES: continue
		if foldername in DEFAULTPLUGINS: continue
		addonxml = os.path.join(folder, 'addon.xml')
		if os.path.exists(addonxml):
			x += 1
			fold   = folder.replace(ADDONS, '')[1:-1]
			f      = open(addonxml)
			a      = f.read().replace('\n','').replace('\r','').replace('\t','')
			match  = wiz.parseDOM(a, 'addon', ret='id')
			match2 = wiz.parseDOM(a, 'addon', ret='name')
			try:
				pluginid = match[0]
				name = match2[0]
			except:
				continue
			try:
				add    = xbmcaddon.Addon(id=pluginid)
				state  = "[COLOR green][Habilitado][/COLOR]"
				goto   = "false"
			except:
				state  = "[COLOR red][Deshabilitado][/COLOR]"
				goto   = "true"
				pass
			icon   = os.path.join(folder, 'icon.png') if os.path.exists(os.path.join(folder, 'icon.png')) else ICON
			fanart = os.path.join(folder, 'fanart.jpg') if os.path.exists(os.path.join(folder, 'fanart.jpg')) else FANART
			addFile("%s %s" % (state, name), 'toggleaddon', fold, goto, icon=icon, fanart=fanart)
			f.close()
	if x == 0:
		addFile("No se encontraron Addons para habilitar o deshabilitar.", '', icon=ICONMAINT)
	setView('files', 'viewType')

def changeFeq():
	feq        = ['Cada inicio', 'Cada dia', 'Cada tres dias', 'Cada semana']
	change     = DIALOG.select("[COLOR %s]How often would you list to Auto Clean on Startup?[/COLOR]" % COLOR2, feq)
	if not change == -1: 
		wiz.setS('autocleanfeq', str(change))
		wiz.LogNotify('[COLOR %s]Auto Limpieza[/COLOR]' % COLOR1, '[COLOR %s]Frecuencia actual %s[/COLOR]' % (COLOR2, feq[change]))

def developer():
	addFile('Convertir archivo TXT a 0.1.7',         'converttext',           themeit=THEME1)
	addFile('Crear QR Code',                      'createqr',              themeit=THEME1)
	addFile('Notificaciones de prueba',                  'testnotify',            themeit=THEME1)
	addFile('Actualizacion de prueba',                         'testupdate',            themeit=THEME1)
	addFile('Prueba primera ejecucion',                      'testfirst',             themeit=THEME1)
	addFile('Probar la configuracion de la primera ejecucion',             'testfirstrun',          themeit=THEME1)
	addFile('Prueba APk',             'testapk',          themeit=THEME1)
	
	setView('files', 'viewType')

###########################
###### Build Install ######
###########################
def buildWizard(name, type, theme=None, over=False):
	if over == False:
		testbuild = wiz.checkBuild(name, 'url')
		if testbuild == False:
			wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Incapaz de encontrar el Wizard[/COLOR]" % COLOR2)
			return
		testworking = wiz.workingURL(testbuild)
		if testworking == False:
			wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Wizard Zip Error: %s[/COLOR]" % (COLOR2, testworking))
			return
	if type == 'gui':
		if name == BUILDNAME:
			if over == True: yes = 1
			else: yes = DIALOG.yesno(ADDONTITLE, '[COLOR %s]Le gustaria aplicar el guifix para:' % COLOR2, '[COLOR %s]%s[/COLOR]?[/COLOR]' % (COLOR1, name), nolabel='[B][COLOR red]No, Cancelar[/COLOR][/B]',yeslabel='[B][COLOR green]Aplicar Fix[/COLOR][/B]')
		else: 
			yes = DIALOG.yesno("%s - [COLOR red]ATENCION!![/COLOR]" % ADDONTITLE, "[COLOR %s][COLOR %s]%s[/COLOR] El Wizard no esta actualmente instalado" % (COLOR2, COLOR1, name), "Te gustaria aplicar el guiFix de todos modos?.[/COLOR]", nolabel='[B][COLOR red]No, Cancelar[/COLOR][/B]',yeslabel='[B][COLOR green]Aplicar Fix[/COLOR][/B]')
		if yes:
			buildzip = wiz.checkBuild(name,'gui')
			zipname = name.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
			if not wiz.workingURL(buildzip) == True: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]GuiFix: Url no encontrada![/COLOR]' % COLOR2); return
			if not os.path.exists(PACKAGES): os.makedirs(PACKAGES)
			DP.create(ADDONTITLE,'[COLOR %s][B]descargando GuiFix:[/B][/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, name),'', 'Espere')
			lib=os.path.join(PACKAGES, '%s_guisettings.zip' % zipname)
			try: os.remove(lib)
			except: pass
			downloader.download(buildzip, lib, DP)
			xbmc.sleep(500)
			title = '[COLOR %s][B]Instalando:[/B][/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, name)
			DP.update(0, title,'', 'Espere')
			extract.all(lib,USERDATA,DP, title=title)
			DP.close()
			wiz.defaultSkin()
			wiz.lookandFeelData('save')
			if INSTALLMETHOD == 1: todo = 1
			elif INSTALLMETHOD == 2: todo = 0
			else: todo = DIALOG.yesno(ADDONTITLE, "[COLOR %s]El Gui fix se instalo correctamente.  quieres forzar el cierre de Kodi?[/COLOR]" % COLOR2, yeslabel="[B][COLOR red]SI[/COLOR][/B]", nolabel="[B][COLOR green]Forzar cierre[/COLOR][/B]")
			if todo == 1: wiz.reloadFix()
			else: DIALOG.ok(ADDONTITLE, "[COLOR %s]Para guardar los cambios, debe forzar el cierre de Kodi, presionar OK para forzar el cierre de Kodi.[/COLOR]" % COLOR2); wiz.killxbmc('true')
		else:
			wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]GuiFix: Cancelado![/COLOR]' % COLOR2)
	elif type == 'fresh':
		freshStart(name)
	elif type == 'normal':
		if url == 'normal':
			if KEEPTRAKT == 'false':
				traktit.autoUpdate('all')
				wiz.setS('traktlastsave', str(THREEDAYS))
			if KEEPREAL == 'false':
				debridit.autoUpdate('all')
				wiz.setS('debridlastsave', str(THREEDAYS))
			if KEEPLOGIN == 'false':
				loginit.autoUpdate('all')
				wiz.setS('loginlastsave', str(THREEDAYS))
		temp_kodiv = int(KODIV); buildv = int(float(wiz.checkBuild(name, 'kodi')))
		if not temp_kodiv == buildv: 
			if temp_kodiv == 16 and buildv <= 15: warning = False
			else: warning = True
		else: warning = False
		if warning == True:
			yes_pressed = DIALOG.yesno("%s - [COLOR red]ATENCION!![/COLOR]" % ADDONTITLE, '[COLOR %s]Existe la posibilidad de que skin no aparezca correctamente' % COLOR2, 'Al instalar un %s Wizard en Kodi %s instalado' % (wiz.checkBuild(name, 'kodi'), KODIV), 'Aun asi te gustaria instalar: [COLOR %s]%s v%s[/COLOR]?[/COLOR]' % (COLOR1, name, wiz.checkBuild(name,'version')), nolabel='[B][COLOR red]No, Cancelar[/COLOR][/B]',yeslabel='[B][COLOR green]Si, Instalar[/COLOR][/B]')
		else:
			if not over == False: yes_pressed = 1
			else: yes_pressed = DIALOG.yesno(ADDONTITLE, '[COLOR %s]Desea descargar e instalar?:' % COLOR2, '[COLOR %s]%s v%s[/COLOR]?[/COLOR]' % (COLOR1, name, wiz.checkBuild(name,'version')), nolabel='[B][COLOR red]No, Cancelar[/COLOR][/B]',yeslabel='[B][COLOR green]Si, Instalar[/COLOR][/B]')
		if yes_pressed:
			wiz.clearS('build')
			buildzip = wiz.checkBuild(name, 'url')
			zipname = name.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
			if not wiz.workingURL(buildzip) == True: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Wizard Instalacion: Url no encontrada![/COLOR]' % COLOR2); return
			if not os.path.exists(PACKAGES): os.makedirs(PACKAGES)
			DP.create(ADDONTITLE,'[COLOR %s][B]Descargando:[/B][/COLOR] [COLOR %s]%s v%s[/COLOR]' % (COLOR2, COLOR1, name, wiz.checkBuild(name,'version')),'', 'Espere')
			lib=os.path.join(PACKAGES, '%s.zip' % zipname)
			try: os.remove(lib)
			except: pass
			downloader.download(buildzip, lib, DP)
			xbmc.sleep(500)
			title = '[COLOR %s][B]Instalando:[/B][/COLOR] [COLOR %s]%s v%s[/COLOR]' % (COLOR2, COLOR1, name, wiz.checkBuild(name,'version'))
			DP.update(0, title,'', 'Espere')
			percent, errors, error = extract.all(lib,HOME,DP, title=title)
			if int(float(percent)) > 0:
				wiz.fixmetas()
				wiz.lookandFeelData('save')
				wiz.defaultSkin()
				#wiz.addonUpdates('set')
				wiz.setS('buildname', name)
				wiz.setS('buildversion', wiz.checkBuild( name,'version'))
				wiz.setS('buildtheme', '')
				wiz.setS('latestversion', wiz.checkBuild( name,'version'))
				wiz.setS('lastbuildcheck', str(NEXTCHECK))
				wiz.setS('installed', 'true')
				wiz.setS('extract', str(percent))
				wiz.setS('errors', str(errors))
				wiz.log('INSTALADO %s: [ERRORES:%s]' % (percent, errors))
				try: os.remove(lib)
				except: pass
				if int(float(errors)) > 0:
					yes=DIALOG.yesno(ADDONTITLE, '[COLOR %s][COLOR %s]%s v%s[/COLOR]' % (COLOR2, COLOR1, name, wiz.checkBuild( name,'version')), 'Completado: [COLOR %s]%s%s[/COLOR] [Errores:[COLOR %s]%s[/COLOR]]' % (COLOR1, percent, '%', COLOR1, errors), 'Le gustaria ver los errores?[/COLOR]', nolabel='[B][COLOR red]No[/COLOR][/B]', yeslabel='[B][COLOR green]Ver Errores[/COLOR][/B]')
					if yes:
						if isinstance(errors, unicode):
							error = error.encode('utf-8')
						wiz.TextBox(ADDONTITLE, error)
				DP.close()
				themefile = wiz.themeCount(name)
				if not themefile == False:
					buildWizard(name, 'theme')
				if KODIV >= 17: wiz.addonDatabase(ADDON_ID, 1)
				if INSTALLMETHOD == 1: todo = 1
				elif INSTALLMETHOD == 2: todo = 0
				else: todo = DIALOG.yesno(ADDONTITLE, "[COLOR %s]Quieres [COLOR %s]Forzar el cierre[/COLOR] de kodi para [COLOR %s]este perfil[/COLOR]?[/COLOR]" % (COLOR2, COLOR1, COLOR1), yeslabel="[B][COLOR red]NO[/COLOR][/B]", nolabel="[B][COLOR green]SI[/COLOR][/B]")
				if todo == 1: wiz.reloadFix()
				else: wiz.killxbmc(True)
			else:
				if isinstance(errors, unicode):
					error = error.encode('utf-8')
				wiz.TextBox("%s: Error Instalando Wizard" % ADDONTITLE, error)
		else:
			wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Instalacion cancelada![/COLOR]' % COLOR2)
	elif type == 'theme':
		if theme == None:
			themefile = wiz.checkBuild(name, 'theme')
			themelist = []
			if not themefile == 'http://' and wiz.workingURL(themefile) == True:
				themelist = wiz.themeCount(name, False)
				if len(themelist) > 0:
					if DIALOG.yesno(ADDONTITLE, "[COLOR %s]El Wizard [COLOR %s]%s[/COLOR] viene con [COLOR %s]%s[/COLOR] diferentes temas" % (COLOR2, COLOR1, name, COLOR1, len(themelist)), "Te gustaria instalar uno ahora?[/COLOR]", yeslabel="[B][COLOR green]SI[/COLOR][/B]", nolabel="[B][COLOR red]NO[/COLOR][/B]"):
						wiz.log("Lista: %s " % str(themelist))
						ret = DIALOG.select(ADDONTITLE, themelist)
						wiz.log("Tema seleccionado: %s" % ret)
						if not ret == -1: theme = themelist[ret]; installtheme = True
						else: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Tema Cancelado![/COLOR]' % COLOR2); return
					else: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Tema Cancelado![/COLOR]' % COLOR2); return
			else: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Teme no encontrado![/COLOR]' % COLOR2)
		else: installtheme = DIALOG.yesno(ADDONTITLE, '[COLOR %s]Te gustaria instalar el tema?' % COLOR2, '[COLOR %s]%s[/COLOR]' % (COLOR1, theme), 'para [COLOR %s]%s v%s[/COLOR]?[/COLOR]' % (COLOR1, name, wiz.checkBuild(name,'version')), yeslabel="[B][COLOR green]SI[/COLOR][/B]", nolabel="[B][COLOR red]NO[/COLOR][/B]")
		if installtheme:
			themezip = wiz.checkTheme(name, theme, 'url')
			zipname = name.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
			if not wiz.workingURL(themezip) == True: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]URL del tema no localizado![/COLOR]' % COLOR2); return False
			if not os.path.exists(PACKAGES): os.makedirs(PACKAGES)
			DP.create(ADDONTITLE,'[COLOR %s][B]Descargando:[/B][/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, theme),'', 'Espere')
			lib=os.path.join(PACKAGES, '%s.zip' % zipname)
			try: os.remove(lib)
			except: pass
			downloader.download(themezip, lib, DP)
			xbmc.sleep(500)
			DP.update(0,"", "Instalando %s " % name)
			test = False
			if url not in ["fresh", "normal"]:
				test = testTheme(lib) if not wiz.currSkin() in ['skin.confluence', 'skin.estuary'] else False
				test2 = testGui(lib) if not wiz.currSkin() in ['skin.confluence', 'skin.estuary'] else False
				if test == True:
					wiz.lookandFeelData('save')
					skin     = 'skin.confluence' if KODIV < 17 else 'skin.estuary'
					gotoskin = xbmc.getSkinDir()
					#if DIALOG.yesno(ADDONTITLE, "[COLOR %s]Installing the theme [COLOR %s]%s[/COLOR] requires the skin to be swaped back to [COLOR %s]%s[/COLOR]" % (COLOR2, COLOR1, theme, COLOR1, skin[5:]), "Would you like to switch the skin?[/COLOR]", yeslabel="[B][COLOR green]Switch Skin[/COLOR][/B]", nolabel="[B][COLOR red]Don't Switch[/COLOR][/B]"):
					skinSwitch.swapSkins(skin)
					x = 0
					xbmc.sleep(1000)
					while not xbmc.getCondVisibility("Window.isVisible(yesnodialog)") and x < 150:
						x += 1
						xbmc.sleep(200)
					if xbmc.getCondVisibility("Window.isVisible(yesnodialog)"):
						wiz.ebi('SendClick(11)')
					else: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Instalacion del tema: Intervalo de tiempo agotado![/COLOR]' % COLOR2); return
					xbmc.sleep(500)
			title = '[COLOR %s][B]Instalando tema:[/B][/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, theme)
			DP.update(0, title,'', 'Espere')
			percent, errors, error = extract.all(lib,HOME,DP, title=title)
			wiz.setS('buildtheme', theme)
			wiz.log('INSTALADO %s: [ERRORES:%s]' % (percent, errors))
			DP.close()
			if url not in ["fresh", "normal"]: 
				wiz.forceUpdate()
				if KODIV >= 17: wiz.kodi17Fix()
				if test2 == True:
					wiz.lookandFeelData('save')
					wiz.defaultSkin()
					gotoskin = wiz.getS('defaultskin')
					skinSwitch.swapSkins(gotoskin)
					x = 0
					xbmc.sleep(1000)
					while not xbmc.getCondVisibility("Window.isVisible(yesnodialog)") and x < 150:
						x += 1
						xbmc.sleep(200)

					if xbmc.getCondVisibility("Window.isVisible(yesnodialog)"):
						wiz.ebi('SendClick(11)')
					wiz.lookandFeelData('restore')
				elif test == True:
					skinSwitch.swapSkins(gotoskin)
					x = 0
					xbmc.sleep(1000)
					while not xbmc.getCondVisibility("Window.isVisible(yesnodialog)") and x < 150:
						x += 1
						xbmc.sleep(200)

					if xbmc.getCondVisibility("Window.isVisible(yesnodialog)"):
						wiz.ebi('SendClick(11)')
					else: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]nstalacion del tema: Intervalo de tiempo agotado![/COLOR]' % COLOR2); return
					wiz.lookandFeelData('restore')
				else:
					wiz.ebi("ReloadSkin()")
					xbmc.sleep(1000)
					wiz.ebi("Container.Refresh") 
		else:
			wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]nstalacion del tema: Cancelado![/COLOR]' % COLOR2)

def thirdPartyInstall(name, url):
	if not wiz.workingURL(url):
		LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]URL no valida[/COLOR]' % COLOR2); return
	type = DIALOG.yesno(ADDONTITLE, "[COLOR %s]Le gustaria realizar una [COLOR %s]Instalacion limpia[/COLOR] o [COLOR %s]Normal[/COLOR] para:[/COLOR]" % (COLOR2, COLOR1, COLOR1), "[COLOR %s]%s[/COLOR]" % (COLOR1, name), yeslabel="[B][COLOR green]SI[/COLOR][/B]", nolabel="[B][COLOR red]NO[/COLOR][/B]")
	if type == 1:
		freshStart('third', True)
	wiz.clearS('build')
	zipname = name.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
	if not os.path.exists(PACKAGES): os.makedirs(PACKAGES)
	DP.create(ADDONTITLE,'[COLOR %s][B]Descargando:[/B][/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, name),'', 'Espere')
	lib=os.path.join(PACKAGES, '%s.zip' % zipname)
	try: os.remove(lib)
	except: pass
	downloader.download(url, lib, DP)
	xbmc.sleep(500)
	title = '[COLOR %s][B]instalando:[/B][/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, name)
	DP.update(0, title,'', 'Espere')
	percent, errors, error = extract.all(lib,HOME,DP, title=title)
	if int(float(percent)) > 0:
		wiz.fixmetas()
		wiz.lookandFeelData('save')
		wiz.defaultSkin()
		#wiz.addonUpdates('set')
		wiz.setS('installed', 'true')
		wiz.setS('extract', str(percent))
		wiz.setS('errors', str(errors))
		wiz.log('INSTALADO %s: [ERRORES:%s]' % (percent, errors))
		try: os.remove(lib)
		except: pass
		if int(float(errors)) > 0:
			yes=DIALOG.yesno(ADDONTITLE, '[COLOR %s][COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, name), 'Completado: [COLOR %s]%s%s[/COLOR] [Errores:[COLOR %s]%s[/COLOR]]' % (COLOR1, percent, '%', COLOR1, errors), 'Quieres ver los errores?[/COLOR]', nolabel='[B][COLOR red]NO[/COLOR][/B]',yeslabel='[B][COLOR green]SI[/COLOR][/B]')
			if yes:
				if isinstance(errors, unicode):
					error = error.encode('utf-8')
				wiz.TextBox(ADDONTITLE, error)
	DP.close()
	if KODIV >= 17: wiz.addonDatabase(ADDON_ID, 1)
	if INSTALLMETHOD == 1: todo = 1
	elif INSTALLMETHOD == 2: todo = 0
	else: todo = DIALOG.yesno(ADDONTITLE, "[COLOR %s]Para [COLOR %s]Cerrar Kodi[/COLOR] Selecciona [COLOR %s]NO[/COLOR]" % (COLOR2, COLOR1, COLOR1), yeslabel="[B][COLOR red]SI[/COLOR][/B]", nolabel="[B][COLOR green]NO[/COLOR][/B]")
	if todo == 1: wiz.reloadFix()
	else: wiz.killxbmc(True)

def testTheme(path):
	zfile = zipfile.ZipFile(path)
	for item in zfile.infolist():
		if '/settings.xml' in item.filename:
			return True
	return False

def testGui(path):
	zfile = zipfile.ZipFile(path)
	for item in zfile.infolist():
		if '/guisettings.xml' in item.filename:
			return True
	return False

def apkInstaller(apk, url):
	wiz.log(apk)
	wiz.log(url)
	if wiz.platform() == 'android':
		yes = DIALOG.yesno(ADDONTITLE, "[COLOR %s]Te gustaria descargar e instalar:" % COLOR2, "[COLOR %s]%s[/COLOR]" % (COLOR1, apk), yeslabel="[B][COLOR green]SI[/COLOR][/B]", nolabel="[B][COLOR red]NO[/COLOR][/B]")
		if not yes: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]ERROR: Instalacion Cancelada[/COLOR]' % COLOR2); return
		display = apk
		if not os.path.exists(PACKAGES): os.makedirs(PACKAGES)
		if not wiz.workingURL(url) == True: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Intalacion APK: URL no valida![/COLOR]' % COLOR2); return
		DP.create(ADDONTITLE,'[COLOR %s][B]Descargando:[/B][/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, display),'', 'Espere')
		lib=os.path.join(PACKAGES, "%s.apk" % apk.replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', ''))
		try: os.remove(lib)
		except: pass
		downloader.download(url, lib, DP)
		xbmc.sleep(100)
		DP.close()
		notify.apkInstaller(apk)
		wiz.ebi('StartAndroidActivity("","android.intent.action.VIEW","application/vnd.android.package-archive","file:'+lib+'")')
	else: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]ERROR: Estas en Android?[/COLOR]' % COLOR2)

###########################
###### Misc Functions######
###########################

def createMenu(type, add, name):
	if   type == 'saveaddon':
		menu_items=[]
		add2  = urllib.quote_plus(add.lower().replace(' ', ''))
		add3  = add.replace('Debrid', 'Real Debrid')
		name2 = urllib.quote_plus(name.lower().replace(' ', ''))
		name = name.replace('url', 'URL Resolver')
		menu_items.append((THEME2 % name.title(),             ' '))
		menu_items.append((THEME3 % 'Guardar %s Data' % add3,               'RunPlugin(plugin://%s/?mode=save%s&name=%s)' %    (ADDON_ID, add2, name2)))
		menu_items.append((THEME3 % 'Restaurar %s Data' % add3,            'RunPlugin(plugin://%s/?mode=restore%s&name=%s)' % (ADDON_ID, add2, name2)))
		menu_items.append((THEME3 % 'Limpiar %s Data' % add3,              'RunPlugin(plugin://%s/?mode=clear%s&name=%s)' %   (ADDON_ID, add2, name2)))
	elif type == 'save'    :
		menu_items=[]
		add2  = urllib.quote_plus(add.lower().replace(' ', ''))
		add3  = add.replace('Debrid', 'Real Debrid')
		name2 = urllib.quote_plus(name.lower().replace(' ', ''))
		name = name.replace('url', 'URL Resolver')
		menu_items.append((THEME2 % name.title(),             ' '))
		menu_items.append((THEME3 % 'Registar %s' % add3,                'RunPlugin(plugin://%s/?mode=auth%s&name=%s)' %    (ADDON_ID, add2, name2)))
		menu_items.append((THEME3 % 'Guardar %s Data' % add3,               'RunPlugin(plugin://%s/?mode=save%s&name=%s)' %    (ADDON_ID, add2, name2)))
		menu_items.append((THEME3 % 'Restaurar %s Data' % add3,            'RunPlugin(plugin://%s/?mode=restore%s&name=%s)' % (ADDON_ID, add2, name2)))
		menu_items.append((THEME3 % 'Importar %s Data' % add3,             'RunPlugin(plugin://%s/?mode=import%s&name=%s)' %  (ADDON_ID, add2, name2)))
		menu_items.append((THEME3 % 'Limpiar Addon %s Data' % add3,        'RunPlugin(plugin://%s/?mode=addon%s&name=%s)' %   (ADDON_ID, add2, name2)))
	elif type == 'install'  :
		menu_items=[]
		name2 = urllib.quote_plus(name)
		menu_items.append((THEME2 % name,                                'RunAddon(%s, ?mode=viewbuild&name=%s)'  % (ADDON_ID, name2)))
		menu_items.append((THEME3 % 'Fresh Install',                     'RunPlugin(plugin://%s/?mode=install&name=%s&url=fresh)'  % (ADDON_ID, name2)))
		menu_items.append((THEME3 % 'Normal Install',                    'RunPlugin(plugin://%s/?mode=install&name=%s&url=normal)' % (ADDON_ID, name2)))
		menu_items.append((THEME3 % 'Aplicar guiFix',                      'RunPlugin(plugin://%s/?mode=install&name=%s&url=gui)'    % (ADDON_ID, name2)))
		menu_items.append((THEME3 % 'Wizard Informacion',                 'RunPlugin(plugin://%s/?mode=buildinfo&name=%s)'  % (ADDON_ID, name2)))
	menu_items.append((THEME2 % '%s Ajustes' % ADDONTITLE,              'RunPlugin(plugin://%s/?mode=settings)' % ADDON_ID))
	return menu_items

def toggleCache(state):
	cachelist = ['includevideo', 'includeall']
	titlelist = ['Include Video Addons', 'Include All Addons']
	if state in ['true', 'false']:
		for item in cachelist:
			wiz.setS(item, state)
	else:
		if not state in ['includevideo', 'includeall'] and wiz.getS('includeall') == 'true':
			try:
				item = titlelist[cachelist.index(state)]
				DIALOG.ok(ADDONTITLE, "[COLOR %s]Tendra que cerrar [COLOR %s]todos los Addons[/COLOR] o deshabilitarlos[/COLOR] [COLOR %s]%s[/COLOR]" % (COLOR2, COLOR1, COLOR1, item))
			except:
				wiz.LogNotify("[COLOR %s]Alternar cache[/COLOR]" % COLOR1, "[COLOR %s]Id no valida: %s[/COLOR]" % (COLOR2, state))
		else:
			new = 'true' if wiz.getS(state) == 'false' else 'false'
			wiz.setS(state, new)

def playVideo(url):
	if 'watch?v=' in url:
		a, b = url.split('?')
		find = b.split('&')
		for item in find:
			if item.startswith('v='):
				url = item[2:]
				break
			else: continue
	elif 'embed' in url or 'youtu.be' in url:
		a = url.split('/')
		if len(a[-1]) > 5:
			url = a[-1]
		elif len(a[-2]) > 5:
			url = a[-2]
	wiz.log("YouTube URL: %s" % url)
	yt.PlayVideo(url)

def viewLogFile():
	mainlog = wiz.Grab_Log(True)
	oldlog  = wiz.Grab_Log(True, True)
	which = 0; logtype = mainlog
	if not oldlog == False and not mainlog == False:
		which = DIALOG.select(ADDONTITLE, ["Ver %s" % mainlog.replace(LOG, ""), "Ver %s" % oldlog.replace(LOG, "")])
		if which == -1: wiz.LogNotify('[COLOR %s]Ver Log[/COLOR]' % COLOR1, '[COLOR %s]Ver Log Cancelado![/COLOR]' % COLOR2); return
	elif mainlog == False and oldlog == False:
		wiz.LogNotify('[COLOR %s]Ver Log[/COLOR]' % COLOR1, '[COLOR %s]Log no encontrado![/COLOR]' % COLOR2)
		return
	elif not mainlog == False: which = 0
	elif not oldlog == False: which = 1
	
	logtype = mainlog if which == 0 else oldlog
	msg     = wiz.Grab_Log(False) if which == 0 else wiz.Grab_Log(False, True)
	
	wiz.TextBox("%s - %s" % (ADDONTITLE, logtype), msg)

def errorChecking(log=None, count=None, all=None):
	if log == None:
		mainlog = wiz.Grab_Log(True)
		oldlog  = wiz.Grab_Log(True, True)
		if not oldlog == False and not mainlog == False:
			which = DIALOG.select(ADDONTITLE, ["Ver %s: %s errores" % (mainlog.replace(LOG, ""), errorChecking(mainlog, True, True)), "Ver %s: %s errores" % (oldlog.replace(LOG, ""), errorChecking(oldlog, True, True))])
			if which == -1: wiz.LogNotify('[COLOR %s]Ver Log[/COLOR]' % COLOR1, '[COLOR %s]Log no encontrado![/COLOR]' % COLOR2); return
		elif mainlog == False and oldlog == False:
			wiz.LogNotify('[COLOR %s]Ver Log[/COLOR]' % COLOR1, '[COLOR %s]Log no encontrado![/COLOR]' % COLOR2)
			return
		elif not mainlog == False: which = 0
		elif not oldlog == False: which = 1
		log = mainlog if which == 0 else oldlog
	if log == False:
		if count == None:
			wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Log no encontrado[/COLOR]" % COLOR2)
			return False
		else: 
			return 0
	else:
		if os.path.exists(log):
			f = open(log,mode='r'); a = f.read().replace('\n', '').replace('\r', ''); f.close()
			match = re.compile("-->La devolucion de llamada / script de Python devolvio el siguiente error<--(.+?)-->Informe de error de script de fin de Python<--").findall(a)
			if not count == None:
				if all == None: 
					x = 0
					for item in match:
						if ADDON_ID in item: x += 1
					return x
				else: return len(match)
			if len(match) > 0:
				x = 0; msg = ""
				for item in match:
					if all == None and not ADDON_ID in item: continue
					else: 
						x += 1
						msg += "[COLOR red]Error Numero %s[/COLOR]\n(PythonToCppException) : -->La devolucion de llamada / script de Python devolvio el siguiente error<--%s-->Informe de error de script de fin de Python<--\n\n" % (x, item.replace('                                          ', '\n').replace('\\\\','\\').replace(HOME, ''))
				if x > 0:
					wiz.TextBox(ADDONTITLE, msg)
				else: wiz.LogNotify(ADDONTITLE, "No se encontraron errores en el registro")
			else: wiz.LogNotify(ADDONTITLE, "No se encontraron errores en el registro")
		else: wiz.LogNotify(ADDONTITLE, "No se encontraron errores en el registro")

ACTION_PREVIOUS_MENU 			=  10	## ESC action
ACTION_NAV_BACK 				=  92	## Backspace action
ACTION_MOVE_LEFT				=   1	## Left arrow key
ACTION_MOVE_RIGHT 				=   2	## Right arrow key
ACTION_MOVE_UP 					=   3	## Up arrow key
ACTION_MOVE_DOWN 				=   4	## Down arrow key
ACTION_MOUSE_WHEEL_UP 			= 104	## Mouse wheel up
ACTION_MOUSE_WHEEL_DOWN			= 105	## Mouse wheel down
ACTION_MOVE_MOUSE 				= 107	## Down arrow key
ACTION_SELECT_ITEM				=   7	## Number Pad Enter
ACTION_BACKSPACE				= 110	## ?
ACTION_MOUSE_LEFT_CLICK 		= 100
ACTION_MOUSE_LONG_CLICK 		= 108

def LogViewer(default=None):
	class LogViewer(xbmcgui.WindowXMLDialog):
		def __init__(self,*args,**kwargs):
			self.default = kwargs['default']

		def onInit(self):
			self.title      = 101
			self.msg        = 102
			self.scrollbar  = 103
			self.upload     = 201
			self.kodi       = 202
			self.kodiold    = 203
			self.wizard     = 204 
			self.okbutton   = 205 
			f = open(self.default, 'r')
			self.logmsg = f.read()
			f.close()
			self.titlemsg = "%s: %s" % (ADDONTITLE, self.default.replace(LOG, '').replace(ADDONDATA, ''))
			self.showdialog()

		def showdialog(self):
			self.getControl(self.title).setLabel(self.titlemsg)
			self.getControl(self.msg).setText(wiz.highlightText(self.logmsg))
			self.setFocusId(self.scrollbar)
			
		def onClick(self, controlId):
			if   controlId == self.okbutton: self.close()
			elif controlId == self.upload: self.close(); uploadLog.Main()
			elif controlId == self.kodi:
				newmsg = wiz.Grab_Log(False)
				filename = wiz.Grab_Log(True)
				if newmsg == False:
					self.titlemsg = "%s: Ver Log Errores" % ADDONTITLE
					self.getControl(self.msg).setText("El archivo de registro no existe!")
				else:
					self.titlemsg = "%s: %s" % (ADDONTITLE, filename.replace(LOG, ''))
					self.getControl(self.title).setLabel(self.titlemsg)
					self.getControl(self.msg).setText(wiz.highlightText(newmsg))
					self.setFocusId(self.scrollbar)
			elif controlId == self.kodiold:  
				newmsg = wiz.Grab_Log(False, True)
				filename = wiz.Grab_Log(True, True)
				if newmsg == False:
					self.titlemsg = "%s: Ver Log Errores" % ADDONTITLE
					self.getControl(self.msg).setText("El archivo de registro no existe!")
				else:
					self.titlemsg = "%s: %s" % (ADDONTITLE, filename.replace(LOG, ''))
					self.getControl(self.title).setLabel(self.titlemsg)
					self.getControl(self.msg).setText(wiz.highlightText(newmsg))
					self.setFocusId(self.scrollbar)
			elif controlId == self.wizard:
				newmsg = wiz.Grab_Log(False, False, True)
				filename = wiz.Grab_Log(True, False, True)
				if newmsg == False:
					self.titlemsg = "%s: Ver Log Errores" % ADDONTITLE
					self.getControl(self.msg).setText("El archivo de registro no existe!")
				else:
					self.titlemsg = "%s: %s" % (ADDONTITLE, filename.replace(ADDONDATA, ''))
					self.getControl(self.title).setLabel(self.titlemsg)
					self.getControl(self.msg).setText(wiz.highlightText(newmsg))
					self.setFocusId(self.scrollbar)
		
		def onAction(self, action):
			if   action == ACTION_PREVIOUS_MENU: self.close()
			elif action == ACTION_NAV_BACK: self.close()
	if default == None: default = wiz.Grab_Log(True)
	lv = LogViewer( "LogViewer.xml" , ADDON.getAddonInfo('path'), 'DefaultSkin', default=default)
	lv.doModal()
	del lv

def removeAddon(addon, name, over=False):
	if not over == False:
		yes = 1
	else: 
		yes = DIALOG.yesno(ADDONTITLE, '[COLOR %s]Quieres eliminar los addons:'% COLOR2, 'Nombre: [COLOR %s]%s[/COLOR]' % (COLOR1, name), 'ID: [COLOR %s]%s[/COLOR][/COLOR]' % (COLOR1, addon), yeslabel='[B][COLOR green]SI[/COLOR][/B]', nolabel='[B][COLOR red]NO[/COLOR][/B]')
	if yes == 1:
		folder = os.path.join(ADDONS, addon)
		wiz.log("Removing Addon %s" % addon)
		wiz.cleanHouse(folder)
		xbmc.sleep(200)
		try: shutil.rmtree(folder)
		except Exception ,e: wiz.log("Error al borrar %s" % addon, xbmc.LOGNOTICE)
		removeAddonData(addon, name, over)
	if over == False:
		wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]%s Borrar[/COLOR]" % (COLOR2, name))

def removeAddonData(addon, name=None, over=False):
	if addon == 'all':
		if DIALOG.yesno(ADDONTITLE, '[COLOR %s]Quieres borrar [COLOR %s]TODOS[/COLOR] Los addons incluyendo Userdata?[/COLOR]' % (COLOR2, COLOR1), yeslabel='[B][COLOR green]SI[/COLOR][/B]', nolabel='[B][COLOR red]NO[/COLOR][/B]'):
			wiz.cleanHouse(ADDOND)
		else: wiz.LogNotify('[COLOR %s]Borrar Addon Data[/COLOR]' % COLOR1, '[COLOR %s]Cancelado![/COLOR]' % COLOR2)
	elif addon == 'uninstalled':
		if DIALOG.yesno(ADDONTITLE, '[COLOR %s]Quieres borrar [COLOR %s]TODOS[/COLOR] addon data / Userdata / addons?[/COLOR]' % (COLOR2, COLOR1), yeslabel='[B][COLOR green]SI[/COLOR][/B]', nolabel='[B][COLOR red]NO[/COLOR][/B]'):
			total = 0
			for folder in glob.glob(os.path.join(ADDOND, '*')):
				foldername = folder.replace(ADDOND, '').replace('\\', '').replace('/', '')
				if foldername in EXCLUDES: pass
				elif os.path.exists(os.path.join(ADDONS, foldername)): pass
				else: wiz.cleanHouse(folder); total += 1; wiz.log(folder); shutil.rmtree(folder)
			wiz.LogNotify('[COLOR %s]Limpiar sin instalar[/COLOR]' % COLOR1, '[COLOR %s]%s Carpeta(s) Eliminada(s)[/COLOR]' % (COLOR2, total))
		else: wiz.LogNotify('[COLOR %s]Borrar Addon Data[/COLOR]' % COLOR1, '[COLOR %s]Cancelado![/COLOR]' % COLOR2)
	elif addon == 'empty':
		if DIALOG.yesno(ADDONTITLE, '[COLOR %s]Quieres borrar [COLOR %s]TODOS[/COLOR] las carpetas vacias de Addon Data y Userdata?[/COLOR]' % (COLOR2, COLOR1), yeslabel='[B][COLOR green]SI[/COLOR][/B]', nolabel='[B][COLOR red]NO[/COLOR][/B]'):
			total = wiz.emptyfolder(ADDOND)
			wiz.LogNotify('[COLOR %s]Eliminar carpetas vacias[/COLOR]' % COLOR1, '[COLOR %s]%s Carpeta(s) Eliminada(s)[/COLOR]' % (COLOR2, total))
		else: wiz.LogNotify('[COLOR %s]Borrar Carpeta(s)[/COLOR]' % COLOR1, '[COLOR %s]Cancelado![/COLOR]' % COLOR2)
	else:
		addon_data = os.path.join(USERDATA, 'addon_data', addon)
		if addon in EXCLUDES:
			wiz.LogNotify("[COLOR %s]Plugin protegido[/COLOR]" % COLOR1, "[COLOR %s]No se puede eliminar de Addon_Data[/COLOR]" % COLOR2)
		elif os.path.exists(addon_data):  
			if DIALOG.yesno(ADDONTITLE, '[COLOR %s]Desea eliminar tambien los datos de los Addons para:[/COLOR]' % COLOR2, '[COLOR %s]%s[/COLOR]' % (COLOR1, addon), yeslabel='[B][COLOR green]SI[/COLOR][/B]', nolabel='[B][COLOR red]NO[/COLOR][/B]'):
				wiz.cleanHouse(addon_data)
				try:
					shutil.rmtree(addon_data)
				except:
					wiz.log("Error Borrar: %s" % addon_data)
			else: 
				wiz.log('Addon data de %s no eliminado' % addon)
	wiz.refresh()

def restoreit(type):
	if type == 'build':
		x = freshStart('restore')
		if x == False: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Local Restore Cancelado[/COLOR]" % COLOR2); return
	if not wiz.currSkin() in ['skin.confluence', 'skin.estuary']:
		wiz.skinToDefault()
	wiz.restoreLocal(type)

def restoreextit(type):
	if type == 'build':
		x = freshStart('restore')
		if x == False: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Externo Restore Cancelado[/COLOR]" % COLOR2); return
	wiz.restoreExternal(type)

def buildInfo(name):
	if wiz.workingURL(BUILDFILE) == True:
		if wiz.checkBuild(name, 'url'):
			name, version, url, gui, kodi, theme, icon, fanart, preview, adult, description = wiz.checkBuild(name, 'all')
			adult = 'Si' if adult.lower() == 'yes' else 'No'
			msg  = "[COLOR %s]Wizard:[/COLOR] [COLOR %s]%s[/COLOR][CR]" % (COLOR2, COLOR1, name)
			msg += "[COLOR %s]Version:[/COLOR] [COLOR %s]%s[/COLOR][CR]" % (COLOR2, COLOR1, version)
			if not theme == "http://":
				themecount = wiz.themeCount(name, False)
				msg += "[COLOR %s]Tema del Wizard(s):[/COLOR] [COLOR %s]%s[/COLOR][CR]" % (COLOR2, COLOR1, ', '.join(themecount))
			msg += "[COLOR %s]Kodi Version:[/COLOR] [COLOR %s]%s[/COLOR][CR]" % (COLOR2, COLOR1, kodi)
			msg += "[COLOR %s]Contenido para Adultos:[/COLOR] [COLOR %s]%s[/COLOR][CR]" % (COLOR2, COLOR1, adult)
			msg += "[COLOR %s]Descripcion:[/COLOR] [COLOR %s]%s[/COLOR][CR]" % (COLOR2, COLOR1, description)
			wiz.TextBox(ADDONTITLE, msg)
		else: wiz.log("Nombre del Wizard no valido!")
	else: wiz.log("El archivo de texto del Wizard no funciona: %s" % WORKINGURL)

def buildVideo(name):
	if wiz.workingURL(BUILDFILE) == True:
		videofile = wiz.checkBuild(name, 'preview')
		if videofile and not videofile == 'http://': playVideo(videofile)
		else: wiz.log("[%s]No se puede encontrar la URL para la vista previa del video" % name)
	else: wiz.log("El archivo de texto del Wizard no funciona: %s" % WORKINGURL)

def dependsList(plugin):
	addonxml = os.path.join(ADDONS, plugin, 'addon.xml')
	if os.path.exists(addonxml):
		source = open(addonxml,mode='r'); link = source.read(); source.close(); 
		match  = wiz.parseDOM(link, 'import', ret='addon')
		items  = []
		for depends in match:
			if not 'xbmc.python' in depends:
				items.append(depends)
		return items
	return []

def manageSaveData(do):
	if do == 'import':
		TEMP = os.path.join(ADDONDATA, 'temp')
		if not os.path.exists(TEMP): os.makedirs(TEMP)
		source = DIALOG.browse(1, '[COLOR %s]Seleccione la ubicacion del SaveData.zip[/COLOR]' % COLOR2, 'files', '.zip', False, False, HOME)
		if not source.endswith('.zip'):
			wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Error de importacion de datos![/COLOR]" % (COLOR2))
			return
		tempfile = os.path.join(MYBUILDS, 'SaveData.zip')
		goto = xbmcvfs.copy(source, tempfile)
		wiz.log("%s" % str(goto))
		extract.all(xbmc.translatePath(tempfile), TEMP)
		trakt  = os.path.join(TEMP, 'trakt')
		login  = os.path.join(TEMP, 'login')
		debrid = os.path.join(TEMP, 'debrid')
		x = 0
		wiz.cleanHouse(TEMP)
		wiz.removeFolder(TEMP)
		os.remove(tempfile)
		if x == 0: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Error Save Data [/COLOR]" % COLOR2)
		else: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Guardado de los datos completada[/COLOR]" % COLOR2)
	elif do == 'export':
		mybuilds = xbmc.translatePath(MYBUILDS)
		dir = [traktit.TRAKTFOLD, debridit.REALFOLD, loginit.LOGINFOLD]
		traktit.traktIt('update', 'all')
		loginit.loginIt('update', 'all')
		debridit.debridIt('update', 'all')
		source = DIALOG.browse(3, '[COLOR %s]Seleccione donde desea exportar el archivo guardado zip?[/COLOR]' % COLOR2, 'files', '', False, True, HOME)
		source = xbmc.translatePath(source)
		tempzip = os.path.join(mybuilds, 'SaveData.zip')
		zipf = zipfile.ZipFile(tempzip, mode='w')
		for fold in dir:
			if os.path.exists(fold):
				files = os.listdir(fold)
				for file in files:
					zipf.write(os.path.join(fold, file), os.path.join(fold, file).replace(ADDONDATA, ''), zipfile.ZIP_DEFLATED)
		zipf.close()
		if source == mybuilds:
			DIALOG.ok(ADDONTITLE, "[COLOR %s]Guardar datos ha sido respaldado para:[/COLOR]" % (COLOR2), "[COLOR %s]%s[/COLOR]" % (COLOR1, tempzip))
		else:
			try:
				xbmcvfs.copy(tempzip, os.path.join(source, 'SaveData.zip'))
				DIALOG.ok(ADDONTITLE, "[COLOR %s]Guardar datos ha sido respaldado para:[/COLOR]" % (COLOR2), "[COLOR %s]%s[/COLOR]" % (COLOR1, os.path.join(source, 'SaveData.zip')))
			except:
				DIALOG.ok(ADDONTITLE, "[COLOR %s]Guardar datos ha sido respaldado para:[/COLOR]" % (COLOR2), "[COLOR %s]%s[/COLOR]" % (COLOR1, tempzip))

###########################
###### Fresh Install ######
###########################
def freshStart(install=None, over=False):
	if KEEPTRAKT == 'false':
		traktit.autoUpdate('all')
		wiz.setS('traktlastsave', str(THREEDAYS))
	if KEEPREAL == 'false':
		debridit.autoUpdate('all')
		wiz.setS('debridlastsave', str(THREEDAYS))
	if KEEPLOGIN == 'false':
		loginit.autoUpdate('all')
		wiz.setS('loginlastsave', str(THREEDAYS))
	if over == True: yes_pressed = 1
	elif install == 'restore': yes_pressed=DIALOG.yesno(ADDONTITLE, "[COLOR %s]Desea restaurar su" % COLOR2, "Configuracion de Kodi a la configuracion predeterminada", "Antes de instalar la copia de seguridad local?[/COLOR]", nolabel='[B][COLOR red]NO[/COLOR][/B]', yeslabel='[B][COLOR green]SI[/COLOR][/B]')
	elif install: yes_pressed=DIALOG.yesno(ADDONTITLE, "[COLOR %s]Desea restaurar su" % COLOR2, "Configuracion de Kodi a la configuracion predeterminada", "Antes de instalar [COLOR %s]%s[/COLOR]?" % (COLOR1, install), nolabel='[B][COLOR red]NO[/COLOR][/B]', yeslabel='[B][COLOR green]SI[/COLOR][/B]')
	else: yes_pressed=DIALOG.yesno(ADDONTITLE, "[COLOR %s]Desea restaurar su" % COLOR2, "Configuracion de Kodi a la configuracion predeterminada?[/COLOR]", nolabel='[B][COLOR red]NO[/COLOR][/B]', yeslabel='[B][COLOR green]SI[/COLOR][/B]')
	if yes_pressed:
		if not wiz.currSkin() in ['skin.confluence', 'skin.estuary']:
			skin = 'skin.confluence' if KODIV < 17 else 'skin.estuary'
			#yes=DIALOG.yesno(ADDONTITLE, "[COLOR %s]The skin needs to be set back to [COLOR %s]%s[/COLOR]" % (COLOR2, COLOR1, skin[5:]), "Before doing a fresh install to clear all Texture files,", "Would you like us to do that for you?[/COLOR]", yeslabel="[B][COLOR green]Switch Skins[/COLOR][/B]", nolabel="[B][COLOR red]I'll Do It[/COLOR][/B]";
			#if yes:
			skinSwitch.swapSkins(skin)
			x = 0
			xbmc.sleep(1000)
			while not xbmc.getCondVisibility("Window.isVisible(yesnodialog)") and x < 150:
				x += 1
				xbmc.sleep(200)
				wiz.ebi('SendAction(Select)')
			if xbmc.getCondVisibility("Window.isVisible(yesnodialog)"):
				wiz.ebi('SendClick(11)')
			else: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Fresh Install: Skin Tiempo agotado![/COLOR]' % COLOR2); return False
			xbmc.sleep(1000)
		if not wiz.currSkin() in ['skin.confluence', 'skin.estuary']:
			wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Fresh Install: Skin ERROR![/COLOR]' % COLOR2)
			return
		wiz.addonUpdates('set')
		xbmcPath=os.path.abspath(HOME)
		DP.create(ADDONTITLE,"[COLOR %s]Calculando" % COLOR2,'', 'Espere![/COLOR]')
		total_files = sum([len(files) for r, d, files in os.walk(xbmcPath)]); del_file = 0
		DP.update(0, "[COLOR %s]Listas Incluidas." % COLOR2)
		EXCLUDES.append('My_Builds')
		EXCLUDES.append('archive_cache')
		if KEEPREPOS == 'true':
			repos = glob.glob(os.path.join(ADDONS, 'repo*/'))
			for item in repos:
				repofolder = os.path.split(item[:-1])[1]
				if not repofolder == EXCLUDES:
					EXCLUDES.append(repofolder)
		if KEEPSUPER == 'true':
			EXCLUDES.append('plugin.program.super.favourites')
		if KEEPWHITELIST == 'true':
			pvr = ''
			whitelist = wiz.whiteList('read')
			if len(whitelist) > 0:
				for item in whitelist:
					try: name, id, fold = item
					except: pass
					if fold.startswith('pvr'): pvr = id 
					depends = dependsList(fold)
					for plug in depends:
						if not plug in EXCLUDES:
							EXCLUDES.append(plug)
						depends2 = dependsList(plug)
						for plug2 in depends2:
							if not plug2 in EXCLUDES:
								EXCLUDES.append(plug2)
					if not fold in EXCLUDES:
						EXCLUDES.append(fold)
				if not pvr == '': wiz.setS('pvrclient', fold)
		if wiz.getS('pvrclient') == '':
			for item in EXCLUDES:
				if item.startswith('pvr'):
					wiz.setS('pvrclient', item)
		DP.update(0, "[COLOR %s]limpiando:" % COLOR2)
		latestAddonDB = wiz.latestDB('Addons')
		for root, dirs, files in os.walk(xbmcPath,topdown=True):
			dirs[:] = [d for d in dirs if d not in EXCLUDES]
			for name in files:
				del_file += 1
				fold = root.replace('/','\\').split('\\')
				x = len(fold)-1
				if name == 'sources.xml' and fold[-1] == 'userdata' and KEEPSOURCES == 'true': wiz.log("Keep Sources: %s" % os.path.join(root, name), xbmc.LOGNOTICE)
				elif name == 'favourites.xml' and fold[-1] == 'userdata' and KEEPFAVS == 'true': wiz.log("Keep Favourites: %s" % os.path.join(root, name), xbmc.LOGNOTICE)
				elif name == 'profiles.xml' and fold[-1] == 'userdata' and KEEPPROFILES == 'true': wiz.log("Keep Profiles: %s" % os.path.join(root, name), xbmc.LOGNOTICE)
				elif name == 'advancedsettings.xml' and fold[-1] == 'userdata' and KEEPADVANCED == 'true':  wiz.log("Keep Advanced Settings: %s" % os.path.join(root, name), xbmc.LOGNOTICE)
				elif name in LOGFILES: wiz.log("Keep Log File: %s" % name, xbmc.LOGNOTICE)
				elif name.endswith('.db'):
					try:
						if name == latestAddonDB and KODIV >= 17: wiz.log("Ignorar %s de v%s" % (name, KODIV), xbmc.LOGNOTICE)
						else: os.remove(os.path.join(root,name))
					except Exception, e: 
						if not name.startswith('Textures13'):
							wiz.log('Error al eliminar, Purging DB', xbmc.LOGNOTICE)
							wiz.log("-> %s" % (str(e)), xbmc.LOGNOTICE)
							wiz.purgeDb(os.path.join(root,name))
				else:
					DP.update(int(wiz.percentage(del_file, total_files)), '', '[COLOR %s]Archovos: [/COLOR][COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, name), '')
					try: os.remove(os.path.join(root,name))
					except Exception, e: 
						wiz.log("Error al eliminar %s" % os.path.join(root, name), xbmc.LOGNOTICE)
						wiz.log("-> / %s" % (str(e)), xbmc.LOGNOTICE)
			if DP.iscanceled(): 
				DP.close()
				wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Fresh Start Cancelado[/COLOR]" % COLOR2)
				return False
		for root, dirs, files in os.walk(xbmcPath,topdown=True):
			dirs[:] = [d for d in dirs if d not in EXCLUDES]
			for name in dirs:
				DP.update(100, '', 'Limpiar las carpetas vacias: [COLOR %s]%s[/COLOR]' % (COLOR1, name), '')
				if name not in ["Database","userdata","temp","addons","addon_data"]:
					shutil.rmtree(os.path.join(root,name),ignore_errors=True, onerror=None)
			if DP.iscanceled(): 
				DP.close()
				wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Fresh Start Cancelado[/COLOR]" % COLOR2)
				return False
		DP.close()
		wiz.clearS('build')
		if over == True:
			return True
		elif install == 'restore': 
			return True
		elif install: 
			buildWizard(install, 'normal', over=True)
		else:
			if INSTALLMETHOD == 1: todo = 1
			elif INSTALLMETHOD == 2: todo = 0
			else: todo = DIALOG.yesno(ADDONTITLE, "[COLOR %s]Quieres [COLOR %s]Forzar el cierre[/COLOR] de kodi para [COLOR %s]este perfil[/COLOR]?[/COLOR]" % (COLOR2, COLOR1, COLOR1), yeslabel="[B][COLOR red]NO[/COLOR][/B]", nolabel="[B][COLOR green]SI[/COLOR][/B]")
			if todo == 1: wiz.reloadFix('fresh')
			else: wiz.addonUpdates('reset'); wiz.killxbmc(True)
	else: 
		if not install == 'restore':
			wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), '[COLOR %s]Fresh Install: Cancelado![/COLOR]' % COLOR2)
			wiz.refresh()

#############################
###DELETE CACHE##############
####THANKS GUYS @ NaN #######
def clearCache():
	if DIALOG.yesno(ADDONTITLE, '[COLOR %s]Quieres limpiar cache?[/COLOR]' % COLOR2, nolabel='[B][COLOR red]NO[/COLOR][/B]', yeslabel='[B][COLOR green]SI[/COLOR][/B]'):
		wiz.clearCache()
		#clearThumb()

def totalClean():
	if DIALOG.yesno(ADDONTITLE, '[COLOR %s]Quieres limpiar cache, packages y thumbnails?[/COLOR]' % COLOR2, nolabel='[B][COLOR red]NO[/COLOR][/B]',yeslabel='[B][COLOR green]SI[/COLOR][/B]'):
		wiz.clearCache()
		wiz.clearPackages('total')
		clearThumb('total')

def clearThumb(type=None):
	latest = wiz.latestDB('Textures')
	if not type == None: choice = 1
	else: choice = DIALOG.yesno(ADDONTITLE, '[COLOR %s]Quieres eliminar %s de la carpeta Thumbnails?' % (COLOR2, latest), "Se volvera a crear en el proximo inicio.[/COLOR]", nolabel='[B][COLOR red]NO[/COLOR][/B]', yeslabel='[B][COLOR green]SI[/COLOR][/B]')
	if choice == 1:
		try: wiz.removeFile(os.join(DATABASE, latest))
		except: wiz.log('Error al borrar, Purging DB.'); wiz.purgeDb(latest)
		wiz.removeFolder(THUMBS)
		#if not type == 'total': wiz.killxbmc()
	else: wiz.log('Limpiar thumbnames cancelado')
	wiz.redoThumbs()

def purgeDb():
	DB = []; display = []
	for dirpath, dirnames, files in os.walk(HOME):
		for f in fnmatch.filter(files, '*.db'):
			if f != 'Thumbs.db':
				found = os.path.join(dirpath, f)
				DB.append(found)
				dir = found.replace('\\', '/').split('/')
				display.append('(%s) %s' % (dir[len(dir)-2], dir[len(dir)-1]))
	if KODIV >= 16: 
		choice = DIALOG.multiselect("[COLOR %s]Seleciona DB File para purgar[/COLOR]" % COLOR2, display)
		if choice == None: wiz.LogNotify("[COLOR %s]Purgar Database[/COLOR]" % COLOR1, "[COLOR %s]Cancelado[/COLOR]" % COLOR2)
		elif len(choice) == 0: wiz.LogNotify("[COLOR %s]Purgar Database[/COLOR]" % COLOR1, "[COLOR %s]Cancelado[/COLOR]" % COLOR2)
		else: 
			for purge in choice: wiz.purgeDb(DB[purge])
	else:
		choice = DIALOG.select("[COLOR %s]Seleciona DB File para purgar[/COLOR]" % COLOR2, display)
		if choice == -1: wiz.LogNotify("[COLOR %s]Purgar Database[/COLOR]" % COLOR1, "[COLOR %s]Cancelado[/COLOR]" % COLOR2)
		else: wiz.purgeDb(DB[purge])

##########################
### DEVELOPER MENU #######
##########################
def testnotify():
	url = wiz.workingURL(NOTIFICATION)
	if url == True:
		try:
			id, msg = wiz.splitNotify(NOTIFICATION)
			if id == False: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Atencion: Formato incorrecto[/COLOR]" % COLOR2); return
			notify.notification(msg, True)
		except Exception, e:
			wiz.log("Error: %s" % str(e), xbmc.LOGERROR)
	else: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]URL incorrecta[/COLOR]" % COLOR2)

def testupdate():
	if BUILDNAME == "":
		notify.updateWindow()
	else:
		notify.updateWindow(BUILDNAME, BUILDVERSION, BUILDLATEST, wiz.checkBuild(BUILDNAME, 'icon'), wiz.checkBuild(BUILDNAME, 'fanart'))

def testfirst():
	notify.firstRun()

def testfirstRun():
	notify.firstRunSettings()

###########################
## Making the Directory####
###########################

def addDir(display, mode=None, name=None, url=None, menu=None, description=ADDONTITLE, overwrite=True, fanart=FANART, icon=ICON, themeit=None):
	u = sys.argv[0]
	if not mode == None: u += "?mode=%s" % urllib.quote_plus(mode)
	if not name == None: u += "&name="+urllib.quote_plus(name)
	if not url == None: u += "&url="+urllib.quote_plus(url)
	ok=True
	if themeit: display = themeit % display
	liz=xbmcgui.ListItem(display, iconImage="DefaultFolder.png", thumbnailImage=icon)
	liz.setInfo( type="Video", infoLabels={ "Title": display, "Plot": description} )
	liz.setProperty( "Fanart_Image", fanart )
	if not menu == None: liz.addContextMenuItems(menu, replaceItems=overwrite)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok

def addFile(display, mode=None, name=None, url=None, menu=None, description=ADDONTITLE, overwrite=True, fanart=FANART, icon=ICON, themeit=None):
	u = sys.argv[0]
	if not mode == None: u += "?mode=%s" % urllib.quote_plus(mode)
	if not name == None: u += "&name="+urllib.quote_plus(name)
	if not url == None: u += "&url="+urllib.quote_plus(url)
	ok=True
	if themeit: display = themeit % display
	liz=xbmcgui.ListItem(display, iconImage="DefaultFolder.png", thumbnailImage=icon)
	liz.setInfo( type="Video", infoLabels={ "Title": display, "Plot": description} )
	liz.setProperty( "Fanart_Image", fanart )
	if not menu == None: liz.addContextMenuItems(menu, replaceItems=overwrite)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	return ok

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]

		return param

params=get_params()
url=None
name=None
mode=None

try:     mode=urllib.unquote_plus(params["mode"])
except:  pass
try:     name=urllib.unquote_plus(params["name"])
except:  pass
try:     url=urllib.unquote_plus(params["url"])
except:  pass

wiz.log('[ Version : \'%s\' ] [ Mode : \'%s\' ] [ Name : \'%s\' ] [ Url : \'%s\' ]' % (VERSION, mode if not mode == '' else None, name, url))

def setView(content, viewType):
	if wiz.getS('auto-view')=='true':
		views = wiz.getS(viewType)
		if views == '50' and KODIV >= 17 and SKIN == 'skin.estuary': views = '55'
		if views == '500' and KODIV >= 17 and SKIN == 'skin.estuary': views = '50'
		wiz.ebi("Container.SetViewMode(%s)" %  views)

if   mode==None             : index()

elif mode=='wizardupdate'   : wiz.wizardUpdate()
elif mode=='builds'         : buildMenu()
elif mode=='viewbuild'      : viewBuild(name)
elif mode=='buildinfo'      : buildInfo(name)
elif mode=='buildpreview'   : buildVideo(name)
elif mode=='install'        : buildWizard(name, url)
elif mode=='theme'          : buildWizard(name, mode, url)
elif mode=='viewthirdparty' : viewThirdList(name)
elif mode=='installthird'   : thirdPartyInstall(name, url)
elif mode=='editthird'      : editThirdParty(name); wiz.refresh()

elif mode=='maint'          : maintMenu(name)
elif mode=='kodi17fix'      : wiz.kodi17Fix()
elif mode=='advancedsetting': advancedWindow(name)
elif mode=='autoadvanced'   : showAutoAdvanced(); wiz.refresh()
elif mode=='removeadvanced' : removeAdvanced(); wiz.refresh()
elif mode=='asciicheck'     : wiz.asciiCheck()
elif mode=='backupbuild'    : wiz.backUpOptions('build')
elif mode=='backupgui'      : wiz.backUpOptions('guifix')
elif mode=='backuptheme'    : wiz.backUpOptions('theme')
elif mode=='backupaddon'    : wiz.backUpOptions('addondata')
elif mode=='oldThumbs'      : wiz.oldThumbs()
elif mode=='clearbackup'    : wiz.cleanupBackup()
elif mode=='convertpath'    : wiz.convertSpecial(HOME)
elif mode=='currentsettings': viewAdvanced()
elif mode=='fullclean'      : totalClean(); wiz.refresh()
elif mode=='clearcache'     : clearCache(); wiz.refresh()
elif mode=='clearpackages'  : wiz.clearPackages(); wiz.refresh()
elif mode=='clearcrash'     : wiz.clearCrash(); wiz.refresh()
elif mode=='clearthumb'     : clearThumb(); wiz.refresh()
elif mode=='checksources'   : wiz.checkSources(); wiz.refresh()
elif mode=='checkrepos'     : wiz.checkRepos(); wiz.refresh()
elif mode=='freshstart'     : freshStart()
elif mode=='forceupdate'    : wiz.forceUpdate()
elif mode=='forceprofile'   : wiz.reloadProfile(wiz.getInfo('System.ProfileName'))
elif mode=='forceclose'     : wiz.killxbmc()
elif mode=='forceskin'      : wiz.ebi("ReloadSkin()"); wiz.refresh()
elif mode=='hidepassword'   : wiz.hidePassword()
elif mode=='unhidepassword' : wiz.unhidePassword()
elif mode=='enableaddons'   : enableAddons()
elif mode=='toggleaddon'    : wiz.toggleAddon(name, url); wiz.refresh()
elif mode=='togglecache'    : toggleCache(name); wiz.refresh()
elif mode=='toggleadult'    : wiz.toggleAdult(); wiz.refresh()
elif mode=='changefeq'      : changeFeq(); wiz.refresh()
elif mode=='uploadlog'      : uploadLog.Main()
elif mode=='viewlog'        : LogViewer()
elif mode=='viewwizlog'     : LogViewer(WIZLOG)
elif mode=='viewerrorlog'   : errorChecking(all=True)
elif mode=='clearwizlog'    : f = open(WIZLOG, 'w'); f.close(); wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Registro del Wizard borrado![/COLOR]" % COLOR2)
elif mode=='purgedb'        : purgeDb()
elif mode=='fixaddonupdate' : fixUpdate()
elif mode=='removeaddons'   : removeAddonMenu()
elif mode=='removeaddon'    : removeAddon(name)
elif mode=='removeaddondata': removeAddonDataMenu()
elif mode=='removedata'     : removeAddonData(name)
elif mode=='resetaddon'     : total = wiz.cleanHouse(ADDONDATA, ignore=True); wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE), "[COLOR %s]Addon_Data reset[/COLOR]" % COLOR2)
elif mode=='systeminfo'     : systemInfo()
elif mode=='restorezip'     : restoreit('build')
elif mode=='restoregui'     : restoreit('gui')
elif mode=='restoreaddon'   : restoreit('addondata')
elif mode=='restoreextzip'  : restoreextit('build')
elif mode=='restoreextgui'  : restoreextit('gui')
elif mode=='restoreextaddon': restoreextit('addondata')
elif mode=='writeadvanced'  : writeAdvanced(name, url)

elif mode=='apk'            : apkMenu(name)
elif mode=='apkscrape'      : apkScraper(name)
elif mode=='apkinstall'     : apkInstaller(name, url)

elif mode=='youtube'        : youtubeMenu(name)
elif mode=='viewVideo'      : playVideo(url)

elif mode=='addons'         : addonMenu(name)
elif mode=='addoninstall'   : addonInstaller(name, url)

elif mode=='savedata'       : saveMenu()
elif mode=='togglesetting'  : wiz.setS(name, 'false' if wiz.getS(name) == 'true' else 'true'); wiz.refresh()
elif mode=='managedata'     : manageSaveData(name)
elif mode=='whitelist'      : wiz.whiteList(name)

elif mode=='trakt'          : traktMenu()
elif mode=='savetrakt'      : traktit.traktIt('update',      name)
elif mode=='restoretrakt'   : traktit.traktIt('restore',     name)
elif mode=='addontrakt'     : traktit.traktIt('clearaddon',  name)
elif mode=='cleartrakt'     : traktit.clearSaved(name)
elif mode=='authtrakt'      : traktit.activateTrakt(name); wiz.refresh()
elif mode=='updatetrakt'    : traktit.autoUpdate('all')
elif mode=='importtrakt'    : traktit.importlist(name); wiz.refresh()

elif mode=='realdebrid'     : realMenu()
elif mode=='savedebrid'     : debridit.debridIt('update',      name)
elif mode=='restoredebrid'  : debridit.debridIt('restore',     name)
elif mode=='addondebrid'    : debridit.debridIt('clearaddon',  name)
elif mode=='cleardebrid'    : debridit.clearSaved(name)
elif mode=='authdebrid'     : debridit.activateDebrid(name); wiz.refresh()
elif mode=='updatedebrid'   : debridit.autoUpdate('all')
elif mode=='importdebrid'   : debridit.importlist(name); wiz.refresh()

elif mode=='login'          : loginMenu()
elif mode=='savelogin'      : loginit.loginIt('update',      name)
elif mode=='restorelogin'   : loginit.loginIt('restore',     name)
elif mode=='addonlogin'     : loginit.loginIt('clearaddon',  name)
elif mode=='clearlogin'     : loginit.clearSaved(name)
elif mode=='authlogin'      : loginit.activateLogin(name); wiz.refresh()
elif mode=='updatelogin'    : loginit.autoUpdate('all')
elif mode=='importlogin'    : loginit.importlist(name); wiz.refresh()

elif mode=='contact'        : notify.contact(CONTACT)
elif mode=='settings'       : wiz.openS(name); wiz.refresh()
elif mode=='opensettings'   : id = eval(url.upper()+'ID')[name]['plugin']; addonid = wiz.addonId(id); addonid.openSettings(); wiz.refresh()

elif mode=='developer'      : developer()
elif mode=='converttext'    : wiz.convertText()
elif mode=='createqr'       : wiz.createQR()
elif mode=='testnotify'     : testnotify()
elif mode=='testupdate'     : testupdate()
elif mode=='testfirst'      : testfirst()
elif mode=='testfirstrun'   : testfirstRun()
elif mode=='testapk'        : notify.apkInstaller('SPMC')

xbmcplugin.endOfDirectory(int(sys.argv[1]))