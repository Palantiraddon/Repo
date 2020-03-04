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
from datetime import date, datetime, timedelta
from resources.libs import extract, downloader, notify, loginit, debridit, traktit, skinSwitch, uploadLog, wizard as wiz

ADDON_ID       = uservar.ADDON_ID
ADDONTITLE     = uservar.ADDONTITLE
ADDON          = wiz.addonId(ADDON_ID)
VERSION        = wiz.addonInfo(ADDON_ID,'version')
ADDONPATH      = wiz.addonInfo(ADDON_ID,'path')
ADDONID        = wiz.addonInfo(ADDON_ID,'id')
DIALOG         = xbmcgui.Dialog()
DP             = xbmcgui.DialogProgress()
HOME           = xbmc.translatePath('special://home/')
PROFILE        = xbmc.translatePath('special://profile/')
KODIHOME       = xbmc.translatePath('special://xbmc/')
ADDONS         = os.path.join(HOME,     'addons')
KODIADDONS     = os.path.join(KODIHOME, 'addons')
USERDATA       = os.path.join(HOME,     'userdata')
PLUGIN         = os.path.join(ADDONS,   ADDON_ID)
PACKAGES       = os.path.join(ADDONS,   'packages')
ADDONDATA      = os.path.join(USERDATA, 'addon_data', ADDON_ID)
FANART         = os.path.join(ADDONPATH,'fanart.jpg')
ICON           = os.path.join(ADDONPATH,'icon.png')
ART            = os.path.join(ADDONPATH,'resources', 'art')
SKIN           = xbmc.getSkinDir()
BUILDNAME      = wiz.getS('buildname')
DEFAULTSKIN    = wiz.getS('defaultskin')
DEFAULTNAME    = wiz.getS('defaultskinname')
DEFAULTIGNORE  = wiz.getS('defaultskinignore')
BUILDVERSION   = wiz.getS('buildversion')
BUILDLATEST    = wiz.getS('latestversion')
BUILDCHECK     = wiz.getS('lastbuildcheck')
DISABLEUPDATE  = wiz.getS('disableupdate')
AUTOCLEANUP    = wiz.getS('autoclean')
AUTOCACHE      = wiz.getS('clearcache')
AUTOPACKAGES   = wiz.getS('clearpackages')
AUTOTHUMBS     = wiz.getS('clearthumbs')
AUTOFEQ        = wiz.getS('autocleanfeq')
AUTONEXTRUN    = wiz.getS('nextautocleanup')
TRAKTSAVE      = wiz.getS('traktlastsave')
REALSAVE       = wiz.getS('debridlastsave')
LOGINSAVE      = wiz.getS('loginlastsave')
KEEPTRAKT      = wiz.getS('keeptrakt')
KEEPREAL       = wiz.getS('keepdebrid')
KEEPLOGIN      = wiz.getS('keeplogin')
INSTALLED      = wiz.getS('installed')
EXTRACT        = wiz.getS('extract')
EXTERROR       = wiz.getS('errors')
NOTIFY         = wiz.getS('notify')
NOTEDISMISS    = wiz.getS('notedismiss')
NOTEID         = wiz.getS('noteid')
BACKUPLOCATION = ADDON.getSetting('path') if not ADDON.getSetting('path') == '' else HOME
MYBUILDS       = os.path.join(BACKUPLOCATION, 'My_Builds', '')
NOTEID         = 0 if NOTEID == "" else int(NOTEID)
AUTOFEQ        = int(AUTOFEQ) if AUTOFEQ.isdigit() else 0
TODAY          = date.today()
TOMORROW       = TODAY + timedelta(days=1)
TWODAYS        = TODAY + timedelta(days=2)
THREEDAYS      = TODAY + timedelta(days=3)
ONEWEEK        = TODAY + timedelta(days=7)
KODIV          = float(xbmc.getInfoLabel("System.BuildVersion")[:4])
EXCLUDES       = uservar.EXCLUDES
BUILDFILE      = uservar.BUILDFILE
UPDATECHECK    = uservar.UPDATECHECK if str(uservar.UPDATECHECK).isdigit() else 1
NEXTCHECK      = TODAY + timedelta(days=UPDATECHECK)
NOTIFICATION   = uservar.NOTIFICATION
ENABLE         = uservar.ENABLE
HEADERMESSAGE  = uservar.HEADERMESSAGE
AUTOUPDATE     = uservar.AUTOUPDATE
WIZARDFILE     = uservar.WIZARDFILE
AUTOINSTALL    = uservar.AUTOINSTALL
REPOID         = uservar.REPOID
REPOADDONXML   = uservar.REPOADDONXML
REPOZIPURL     = uservar.REPOZIPURL
COLOR1         = uservar.COLOR1
COLOR2         = uservar.COLOR2
WORKING        = True if wiz.workingURL(BUILDFILE) == True else False
FAILED         = False

###########################
#### Check Updates   ######
###########################
def checkUpdate():
	BUILDNAME      = wiz.getS('buildname')
	BUILDVERSION   = wiz.getS('buildversion')
	link           = wiz.openURL(BUILDFILE).replace('\n','').replace('\r','').replace('\t','')
	match          = re.compile('name="%s".+?ersion="(.+?)".+?con="(.+?)".+?anart="(.+?)"' % BUILDNAME).findall(link)
	if len(match) > 0:
		version = match[0][0]
		icon    = match[0][1]
		fanart  = match[0][2]
		wiz.setS('latestversion', version)
		if version > BUILDVERSION:
			if DISABLEUPDATE == 'false':
				wiz.log("[Updates] [Version: %s] [Ultima Version: %s] Buscar Update" % (BUILDVERSION, version), xbmc.LOGNOTICE)
				notify.updateWindow(BUILDNAME, BUILDVERSION, version, icon, fanart)
			else: wiz.log("[Updates] [Version: %s] [Ultima Version: %s] Buscar Update Disabilitado" % (BUILDVERSION, version), xbmc.LOGNOTICE)
		else: wiz.log("[Updates] [Version: %s] [Ultima Version: %s]" % (BUILDVERSION, version), xbmc.LOGNOTICE)
	else: wiz.log("[Updates] ERROR: Archivo TXT no disponible", xbmc.LOGERROR)

def checkSkin():
	wiz.log("[Wizard] Skin no localizado")
	DEFAULTSKIN   = wiz.getS('defaultskin')
	DEFAULTNAME   = wiz.getS('defaultskinname')
	DEFAULTIGNORE = wiz.getS('defaultskinignore')
	gotoskin = False
	if not DEFAULTSKIN == '':
		if os.path.exists(os.path.join(ADDONS, DEFAULTSKIN)):
			if DIALOG.yesno(ADDONTITLE, "[COLOR %s]Parece que el skin se ha establecido de nuevo a [COLOR %s]%s[/COLOR]" % (COLOR2, COLOR1, SKIN[5:].title()), "Le gustaria volver a configurar el skin:[/COLOR]", '[COLOR %s]%s[/COLOR]' % (COLOR1, DEFAULTNAME)):
				gotoskin = DEFAULTSKIN
				gotoname = DEFAULTNAME
			else: wiz.log("El skin no se reinicio", xbmc.LOGNOTICE); wiz.setS('defaultskinignore', 'true'); gotoskin = False
		else: wiz.setS('defaultskin', ''); wiz.setS('defaultskinname', ''); DEFAULTSKIN = ''; DEFAULTNAME = ''
	if DEFAULTSKIN == '':
		skinname = []
		skinlist = []
		for folder in glob.glob(os.path.join(ADDONS, 'skin.*/')):
			xml = "%s/addon.xml" % folder
			if os.path.exists(xml):
				f  = open(xml,mode='r'); g = f.read().replace('\n','').replace('\r','').replace('\t',''); f.close();
				match  = wiz.parseDOM(g, 'addon', ret='id')
				match2 = wiz.parseDOM(g, 'addon', ret='name')
				wiz.log("%s: %s" % (folder, str(match[0])), xbmc.LOGNOTICE)
				if len(match) > 0: skinlist.append(str(match[0])); skinname.append(str(match2[0]))
				else: wiz.log("ID not found for %s" % folder, xbmc.LOGNOTICE)
			else: wiz.log("ID not found for %s" % folder, xbmc.LOGNOTICE)
		if len(skinlist) > 0:
			if len(skinlist) > 1:
				if DIALOG.yesno(ADDONTITLE, "[COLOR %s]Parece que el skin se ha establecido de nuevo a [COLOR %s]%s[/COLOR]" % (COLOR2, COLOR1, SKIN[5:].title()), "Le gustaria ver una lista de los skin disponibles?[/COLOR]"):
					choice = DIALOG.select("Seleccione el skin para cambiar", skinname)
					if choice == -1: wiz.log("El skin no se reinicio", xbmc.LOGNOTICE); wiz.setS('defaultskinignore', 'true')
					else: 
						gotoskin = skinlist[choice]
						gotoname = skinname[choice]
				else: wiz.log("El skin no se reinicio", xbmc.LOGNOTICE); wiz.setS('defaultskinignore', 'true')
			else:
				if DIALOG.yesno(ADDONTITLE, "[COLOR %s]Parece que el skin se ha establecido de nuevo a [COLOR %s]%s[/COLOR]" % (COLOR2, COLOR1, SKIN[5:].title()), "Le gustaria volver a configurar el skin:[/COLOR]", '[COLOR %s]%s[/COLOR]' % (COLOR1, skinname[0])):
					gotoskin = skinlist[0]
					gotoname = skinname[0]
				else: wiz.log("El skin no se reinicio", xbmc.LOGNOTICE); wiz.setS('defaultskinignore', 'true')
		else: wiz.log("No se encontraron skins en la carpeta de complementos.", xbmc.LOGNOTICE); wiz.setS('defaultskinignore', 'true'); gotoskin = False
	if gotoskin:
		skinSwitch.swapSkins(gotoskin)
		x = 0
		xbmc.sleep(1000)
		while not xbmc.getCondVisibility("Window.isVisible(yesnodialog)") and x < 150:
			x += 1
			xbmc.sleep(200)

		if xbmc.getCondVisibility("Window.isVisible(yesnodialog)"):
			wiz.ebi('SendClick(11)')
			wiz.lookandFeelData('restore')
		else: wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, ADDONTITLE),'[COLOR %s]Tiempo agotato[/COLOR]' % COLOR2)
	wiz.log("[Build Check] Skin Error", xbmc.LOGNOTICE)

while xbmc.Player().isPlayingVideo():
	xbmc.sleep(1000)

if KODIV >= 17:
	NOW = datetime.now()
	temp = wiz.getS('kodi17iscrap')
	if not temp == '':
		if temp > str(NOW - timedelta(minutes=2)):
			wiz.log("Matar el arranque del Script")
			sys.exit()
	wiz.log("%s" % (NOW))
	wiz.setS('kodi17iscrap', str(NOW))
	xbmc.sleep(1000)
	if not wiz.getS('kodi17iscrap') == str(NOW):
		wiz.log("Matar el arranque del Script")
		sys.exit()
	else:
		wiz.log("Continuar con el Script")

wiz.log("[Path Check] Iniciando", xbmc.LOGNOTICE)
path = os.path.split(ADDONPATH)
if not ADDONID == path[1]: DIALOG.ok(ADDONTITLE, '[COLOR %s]Asegurese de que la carpeta del complemento sea la misma que ADDON_ID.[/COLOR]' % COLOR2, '[COLOR %s]Plugin ID:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, ADDONID), '[COLOR %s]Carpeta del Plugin:[/COLOR] [COLOR %s]%s[/COLOR]' % (COLOR2, COLOR1, path)); wiz.log("[Path Check] ADDON ID y la carpeta del complemento no coinciden. %s / %s " % (ADDONID, path))
else: wiz.log("[Path Check] Bien!", xbmc.LOGNOTICE)

if KODIADDONS in ADDONPATH:
	wiz.log("Copiando la ruta al directorio de complementos", xbmc.LOGNOTICE)
	if not os.path.exists(ADDONS): os.makedirs(ADDONS)
	newpath = xbmc.translatePath(os.path.join('special://home/addons/', ADDONID))
	if os.path.exists(newpath):
		wiz.log("La carpeta ya existe, limpiando...", xbmc.LOGNOTICE)
		wiz.cleanHouse(newpath)
		wiz.removeFolder(newpath)
	try:
		wiz.copytree(ADDONPATH, newpath)
	except Exception, e:
		pass
	wiz.forceUpdate(True)

try:
	mybuilds = xbmc.translatePath(MYBUILDS)
	if not os.path.exists(mybuilds): xbmcvfs.mkdirs(mybuilds)
except:
	pass

wiz.log("[Auto Install Repo] Iniciando", xbmc.LOGNOTICE)
if AUTOINSTALL == 'Yes' and not os.path.exists(os.path.join(ADDONS, REPOID)):
	workingxml = wiz.workingURL(REPOADDONXML)
	if workingxml == True:
		ver = wiz.parseDOM(wiz.openURL(REPOADDONXML), 'addon', ret='version', attrs = {'id': REPOID})
		if len(ver) > 0:
			installzip = '%s-%s.zip' % (REPOID, ver[0])
			workingrepo = wiz.workingURL(REPOZIPURL+installzip)
			if workingrepo == True:
				DP.create(ADDONTITLE,'Descargando Repo...','', 'Espere')
				if not os.path.exists(PACKAGES): os.makedirs(PACKAGES)
				lib=os.path.join(PACKAGES, installzip)
				try: os.remove(lib)
				except: pass
				downloader.download(REPOZIPURL+installzip,lib, DP)
				extract.all(lib, ADDONS, DP)
				try:
					f = open(os.path.join(ADDONS, REPOID, 'addon.xml'), mode='r'); g = f.read(); f.close()
					name = wiz.parseDOM(g, 'addon', ret='name', attrs = {'id': REPOID})
					wiz.LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, name[0]), "[COLOR %s]Add-on updated[/COLOR]" % COLOR2, icon=os.path.join(ADDONS, REPOID, 'icon.png'))
				except:
					pass
				if KODIV >= 17: wiz.addonDatabase(REPOID, 1)
				DP.close()
				xbmc.sleep(500)
				wiz.forceUpdate(True)
				wiz.log("[Auto Install Repo] Instalado exitosamente", xbmc.LOGNOTICE)
			else: 
				wiz.LogNotify("[COLOR %s]Repo Error[/COLOR]" % COLOR1, "[COLOR %s]Invalida la url del zip![/COLOR]" % COLOR2)
				wiz.log("[Auto Install Repo] No se pudo crear una url funcional para el repositorio. %s" % workingrepo, xbmc.LOGERROR)
		else:
			wiz.log("Invalida la URL del Repo Zip", xbmc.LOGERROR)
	else: 
		wiz.LogNotify("[COLOR %s]Repo Error[/COLOR]" % COLOR1, "[COLOR %s]Invalido el archivo addon.xml![/COLOR]" % COLOR2)
		wiz.log("[Auto Install Repo] No se puede leer el archivo addon.xml.", xbmc.LOGERROR)
elif not AUTOINSTALL == 'Yes': wiz.log("[Auto Install Repo] No disponible", xbmc.LOGNOTICE)
elif os.path.exists(os.path.join(ADDONS, REPOID)): wiz.log("[Auto Install Repo] Repositorio ya instalado")

wiz.log("[Auto Update Wizard] Iniciando", xbmc.LOGNOTICE)
if AUTOUPDATE == 'Yes':
	wiz.wizardUpdate('startup')
else: wiz.log("[Auto Update Wizard] No Disponible", xbmc.LOGNOTICE)

wiz.log("[Notifications] Iniciando", xbmc.LOGNOTICE)
if ENABLE == 'Yes':
	if not NOTIFY == 'true':
		url = wiz.workingURL(NOTIFICATION)
		if url == True:
			id, msg = wiz.splitNotify(NOTIFICATION)
			if not id == False:
				try:
					id = int(id); NOTEID = int(NOTEID)
					if id == NOTEID:
						if NOTEDISMISS == 'false':
							notify.notification(msg)
						else: wiz.log("[Notifications] id[%s] Rechazado" % int(id), xbmc.LOGNOTICE)
					elif id > NOTEID:
						wiz.log("[Notifications] id: %s" % str(id), xbmc.LOGNOTICE)
						wiz.setS('noteid', str(id))
						wiz.setS('notedismiss', 'false')
						notify.notification(msg=msg)
						wiz.log("[Notifications] Completado", xbmc.LOGNOTICE)
				except Exception, e:
					wiz.log("Error en la ventana de notificaciones: %s" % str(e), xbmc.LOGERROR)
			else: wiz.log("[Notifications] El archivo de texto no esta formateado correctamente")
		else: wiz.log("[Notifications] URL(%s): %s" % (NOTIFICATION, url), xbmc.LOGNOTICE)
	else: wiz.log("[Notifications] Desactivado", xbmc.LOGNOTICE)
else: wiz.log("[Notifications] No disponible", xbmc.LOGNOTICE)

wiz.log("[Installed Check] Iniciando", xbmc.LOGNOTICE)
if INSTALLED == 'true':
	if KODIV >= 17:
		wiz.kodi17Fix()
		if SKIN in ['skin.confluence', 'skin.estuary']:
			checkSkin()
		FAILED = True
	elif not EXTRACT == '100' and not BUILDNAME == "":
		wiz.log("[Installed Check] Wizard extraido %s/100 con [ERRORES: %s]" % (EXTRACT, EXTERROR), xbmc.LOGNOTICE)
		yes=DIALOG.yesno(ADDONTITLE, '[COLOR %s]%s[/COLOR] [COLOR %s]no fue instalado correctamente' % (COLOR1, COLOR2, BUILDNAME), 'Instalado: [COLOR %s]%s[/COLOR] / Hay Errores: [COLOR %s]%s[/COLOR]' % (COLOR1, EXTRACT, COLOR1, EXTERROR), 'Le gustaria volver a intentarlo[/COLOR]', nolabel='[B]No Gracias![/B]', yeslabel='[B]Volver a Instalar[/B]')
		wiz.clearS('build')
		FAILED = True
		if yes: 
			wiz.ebi("PlayMedia(plugin://%s/?mode=install&name=%s&url=fresh)" % (ADDON_ID, urllib.quote_plus(BUILDNAME)))
			wiz.log("[Installed Check] Fresh Install Re-activado", xbmc.LOGNOTICE)
		else: wiz.log("[Installed Check] Reinstalar Ignoredo")
	elif SKIN in ['skin.confluence', 'skin.estuary']:
		wiz.log("[Installed Check] Skin Incorrecto: %s" % SKIN, xbmc.LOGNOTICE)
		defaults = wiz.getS('defaultskin')
		if not defaults == '':
			if os.path.exists(os.path.join(ADDONS, defaults)):
				skinSwitch.swapSkins(defaults)
				x = 0
				xbmc.sleep(1000)
				while not xbmc.getCondVisibility("Window.isVisible(yesnodialog)") and x < 150:
					x += 1
					xbmc.sleep(200)

				if xbmc.getCondVisibility("Window.isVisible(yesnodialog)"):
					wiz.ebi('SendClick(11)')
					wiz.lookandFeelData('restore')
		if not wiz.currSkin() == defaults and not BUILDNAME == "":
			gui = wiz.checkBuild(BUILDNAME, 'gui')
			FAILED = True
			if gui == 'http://':
				wiz.log("[Installed Check] Guifix estaba configurado para http://", xbmc.LOGNOTICE)
				DIALOG.ok(ADDONTITLE, "[COLOR %s]Parece que la configuracion del skin no se aplico al wizard." % COLOR2, "Lamentablemente, no se aplico ninguna correccion gui al wizard", "Usted tendra que volver a instalar el wizard y asegurese de forzar el cierre de Kodi.[/COLOR]")
			elif wiz.workingURL(gui):
				yes=DIALOG.yesno(ADDONTITLE, '%s no fue instalado correctamente!' % BUILDNAME, 'Parece que la configuracion del skin no se aplico correctamente.', 'Le gustaria aplicar el GuiFix', nolabel='[B]No, Cancelar[/B]', yeslabel='[B]Aplicar Fix[/B]')
				if yes: wiz.ebi("PlayMedia(plugin://%s/?mode=install&name=%s&url=gui)" % (ADDON_ID, urllib.quote_plus(BUILDNAME))); wiz.log("[Installed Check] Guifix se intenta instalar")
				else: wiz.log('[Installed Check] Guifix url cancelado: %s' % gui, xbmc.LOGNOTICE)
			else:
				DIALOG.ok(ADDONTITLE, "[COLOR %s]Parece que la configuracion del skin no se aplico al wizard." % COLOR2, "Lamentablemente, no se aplico ninguna correccion gui al wizard", "Usted tendra que volver a instalar el wizard y asegurese de forzar el cierre de Kodi.[/COLOR]")
				wiz.log('[Installed Check] Guifix url no funciona: %s' % gui, xbmc.LOGNOTICE)
	else:
		wiz.log('[Installed Check] La instalacion parece estar completada correctamente', xbmc.LOGNOTICE)
	if not wiz.getS('pvrclient') == "":
		wiz.toggleAddon(wiz.getS('pvrclient'), 1)
		wiz.ebi('StartPVRManager')
	wiz.addonUpdates('reset')
	if KEEPTRAKT == 'true': traktit.traktIt('restore', 'all'); wiz.log('[Installed Check] Restaurando datos de Trakt', xbmc.LOGNOTICE)
	if KEEPREAL  == 'true': debridit.debridIt('restore', 'all'); wiz.log('[Installed Check] Restaurando Datos Real Debrid', xbmc.LOGNOTICE)
	if KEEPLOGIN == 'true': loginit.loginIt('restore', 'all'); wiz.log('[Installed Check] Restaurar datos de inicio de sesion', xbmc.LOGNOTICE)
	wiz.clearS('install')
else: wiz.log("[Installed Check] No disponible", xbmc.LOGNOTICE)

if FAILED == False:
	wiz.log("[Build Check] Iniciando", xbmc.LOGNOTICE)
	if not WORKING:
		wiz.log("[Build Check] No es una URL valida para el archivo wizard: %s" % BUILDFILE, xbmc.LOGNOTICE)
	elif BUILDCHECK == '' and BUILDNAME == '':
		wiz.log("[Build Check] Primer intento", xbmc.LOGNOTICE)
		notify.firstRunSettings()
		xbmc.sleep(500)
		notify.firstRun()
		xbmc.sleep(500)
		wiz.setS('lastbuildcheck', str(NEXTCHECK))
	elif not BUILDNAME == '':
		wiz.log("[Build Check] Wizard instalado", xbmc.LOGNOTICE)
		if SKIN in ['skin.confluence', 'skin.estuary'] and not DEFAULTIGNORE == 'true':
			checkSkin()
			wiz.log("[Build Check] Wizard instalado: Buscando Updates", xbmc.LOGNOTICE)
			wiz.setS('lastbuildcheck', str(NEXTCHECK))
			checkUpdate()
		elif BUILDCHECK <= str(TODAY):
			wiz.log("[Build Check] Wizard instalado: Buscando Updates", xbmc.LOGNOTICE)
			wiz.setS('lastbuildcheck', str(NEXTCHECK))
			checkUpdate()
		else: 
			wiz.log("[Build Check] Wizard instalado: verificacion dentro de: %s / Hoy es: %s" % (BUILDCHECK, str(TODAY)), xbmc.LOGNOTICE)

wiz.log("[Trakt Data] Iniciando", xbmc.LOGNOTICE)
if KEEPTRAKT == 'true':
	if TRAKTSAVE <= str(TODAY):
		wiz.log("[Trakt Data] Guardando todos los datos", xbmc.LOGNOTICE)
		traktit.autoUpdate('all')
		wiz.setS('traktlastsave', str(THREEDAYS))
	else: 
		wiz.log("[Trakt Data] El siguiente Auto Guardar no es hasta: %s / Hoy es: %s" % (TRAKTSAVE, str(TODAY)), xbmc.LOGNOTICE)
else: wiz.log("[Trakt Data] No disponible", xbmc.LOGNOTICE)

wiz.log("[Real Debrid Data] Iniciando", xbmc.LOGNOTICE)
if KEEPREAL == 'true':
	if REALSAVE <= str(TODAY):
		wiz.log("[Real Debrid Data] Guardando todos los datos", xbmc.LOGNOTICE)
		debridit.autoUpdate('all')
		wiz.setS('debridlastsave', str(THREEDAYS))
	else: 
		wiz.log("[Real Debrid Data] El siguiente Auto Guardar no es hasta: %s / Hoy es: %s" % (REALSAVE, str(TODAY)), xbmc.LOGNOTICE)
else: wiz.log("[Real Debrid Data] No disponible", xbmc.LOGNOTICE)

wiz.log("[Login Data] Iniciando", xbmc.LOGNOTICE)
if KEEPLOGIN == 'true':
	if LOGINSAVE <= str(TODAY):
		wiz.log("[Login Data] Guardando todos los datos", xbmc.LOGNOTICE)
		loginit.autoUpdate('all')
		wiz.setS('loginlastsave', str(THREEDAYS))
	else: 
		wiz.log("[Login Data] El siguiente Auto Guardar no es hasta: %s / Hoy es: %s" % (LOGINSAVE, str(TODAY)), xbmc.LOGNOTICE)
else: wiz.log("[Login Data] No disponible", xbmc.LOGNOTICE)

wiz.setS('kodi17iscrap', '')