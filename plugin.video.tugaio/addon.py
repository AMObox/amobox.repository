#!/usr/bin/python
# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Tuga.io v3.0.3
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# 
# Author: AdrXbmc | Copyright 2015 
#------------------------------------------------------------


import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmcaddon,xbmc,os,json,threading
from bs4 import BeautifulSoup
from resources.lib import Downloader 
from resources.lib import TVDB
#from resourses.lib import MovieDB


addon_id    = xbmcaddon.Addon().getAddonInfo("id")
selfAddon	= xbmcaddon.Addon(addon_id)
addonfolder	= selfAddon.getAddonInfo('path')
getSetting	= xbmcaddon.Addon().getSetting
artfolder	= os.path.join(addonfolder,'resources','img')
fanart 		= os.path.join(addonfolder,'fundo.png')

pastaFilmes = xbmc.translatePath(selfAddon.getSetting('bibliotecaFilmes'))
pastaSeries = xbmc.translatePath(selfAddon.getSetting('bibliotecaSeries'))


tv = TVDB.TVDB('D2E52B80062E3EE0', 'pt')
#movie = MovieDB.MovieDB('3421e679385f33e2438463e286e5c918')

site = 'http://tuga.io/'
sitekids = 'http://kids.tuga.io/'

def getLiguaMetaDados():
	lang = ''
	lingua = selfAddon.getSetting('linguaMetaDados')
	if lingua == '0': lang = 'pt'
	elif lingua == '1': lang = 'en'

	return lang

def categorias():
	if getSetting("pref_site") == 'Geral' or getSetting("pref_site") == 'Ambos':
		addDir('Filmes', site+'filmes', 1, os.path.join(artfolder,'filmes.png'), 0)
		addDir('Series', site+'series', 2, os.path.join(artfolder,'series.png'), 0)
		addDir('Pesquisa', site, 6, os.path.join(artfolder,'pesquisa.png'), 0)
		if "confluence" in xbmc.getSkinDir(): addDir('', '', '', os.path.join(artfolder,'nada.png'), 0)
	if getSetting("pref_site") == 'Kids' or getSetting("pref_site") == 'Ambos':
		addDir('Filmes KIDS', sitekids+'filmes', 1, os.path.join(artfolder,'filmes_kids.png'), 0)
		addDir('Pesquisa KIDS', sitekids, 6, os.path.join(artfolder,'pesquisa_kids.png'), 0)
	if "confluence" in xbmc.getSkinDir(): addDir('', '', '', os.path.join(artfolder,'nada.png'), 0)
	addDir('Filmes por Genero', site, 8, os.path.join(artfolder,'filmes.png'), 0)
	addDir('Series por Genero', site, 9, os.path.join(artfolder,'series.png'), 0)
	addDir('Filmes IMDB Rating', site+'filmes?orderby=1', 1, os.path.join(artfolder,'filmes.png'), 0)
	addDir('Series IMDB Rating', site+'series?orderby=1', 2, os.path.join(artfolder,'series.png'), 0)
	if "confluence" in xbmc.getSkinDir(): addDir('', '', '', os.path.join(artfolder,'nada.png'), 0)
	addDir('Definicoes', site, 1000, os.path.join(artfolder,'nanda.png'), 0)
	#setVista('menu')
	vista_menu()

def getFilmes(url, pagina):

	siteAux = ''

	if 'kids.' in url: siteAux = sitekids
	else: siteAux = site
	
	mensagemprogresso = xbmcgui.DialogProgress()
	mensagemprogresso.create('Tuga.io', 'A abrir lista de filmes','Por favor aguarde...')

	i=1
	mensagemprogresso.update(i)

	codigo_fonte_listaFilmes=abrir_url(url)
	match_filmes=re.compile('<li>\n<a href="(.+?)">\n<div class="thumb">\n<div class="img" style="background-image: url\(\'(.+?)\'\);"></div>\n</div>\n<div class="info">\n<div class="title">(.+?)</div>\n<div class="infos">\n<div class="year">(.+?)</div>\n<div class="imdb">(.+?)</div>\n</div>\n</div>\n</a>\n</li>\n').findall(codigo_fonte_listaFilmes)

	tamanhoArray = len(match_filmes)+0.0

	for link,imagem,nome,ano,imdb in match_filmes:
		percentagem = int((i/tamanhoArray)*100)
		link = link[1:]
		codigo_fonte=abrir_url(siteAux+link)
		
		idIMDb = link.split('/')[-1]

		mediaInfo = getInfoIMDB(idIMDb)
		nome = mediaInfo['Title'].encode('utf8')
		ano = mediaInfo['Year'].encode('utf8')
		infoLabels = {'Title':name, 'Year': ano, 'Genre':mediaInfo['Genre'], 'Plot':mediaInfo['Plot']}
		poster = mediaInfo['Poster']
		
		#match=re.compile('jwplayer\(\'player_get_hard\'\).setup\(\{\n                            file: \'(.+?)\',\n                            aspectratio: \'.+?\',\n                            width: \'.+?\',\n                            height: \'.+?\',\n                            skin: \'.+?\',\n                            primary: ".+?",\n                            androidhls:.+?,\n                            logo : \{\n                                file: ".+?",\n                                link: ".+?",\n                                hide: .+?\n                            \},\n                            tracks:\n                                    \[\n                                        \{\n                                            file: "(.+?)",\n                                            default: ".+?"\n                                        \}\n                                    \],\n                            captions: \{\n                                backgroundOpacity: .+?                            \}\n\n                        \}\);').findall(codigo_fonte)
		getStream=re.compile('file: \'(.+?)\'').findall(codigo_fonte) 
		getLegenda=re.compile('file: \"(.+?)\"').findall(codigo_fonte)
		stream = ''
		legenda = ''
		mensagemprogresso.update(percentagem, "", nome, "")
		for streamAux in getStream: stream = streamAux
		for legendaAux in getLegenda: legenda = legendaAux 
		addVideo(nome + ' ('+ano+')', stream, 3, siteAux+imagem, siteAux+legenda, 'filme', infoLabels, poster)
		if mensagemprogresso.iscanceled(): break
		i+=1
		
	if pagina==0:
		match_prox=re.compile('<a href=\"(.+?)\" class=\"r\">Pr').findall(codigo_fonte_listaFilmes)
		pagina+=1
		for proximo in match_prox:
			proximo = proximo[1:]
			addDir('Proximo >>', siteAux+proximo, 1, os.path.join(artfolder,'proximo.png'), pagina)
		
	elif pagina>=1:
		match_prox_ant=re.compile('<a href=\".+?\" class="l"><i class="fa fa-arrow-left"></i> Anterior</a><a href="(.+?)" class="r">Pr').findall(codigo_fonte_listaFilmes)
		pagina+=1
		for proximo in match_prox_ant:
			proximo = proximo[1:]
			addDir('Proximo >>', siteAux+proximo, 1, os.path.join(artfolder,'proximo.png'), pagina)
	
	mensagemprogresso.close()
	#setVista('filmesSeries')
	vista_filmesSeries()

def getSeries(url, pagina):
	codigo_fonte_listaSeries = abrir_url(url)
	match_series=re.compile('<li>\n<a href="(.+?)">\n<div class="thumb">\n<div class="img" style="background-image: url\(\'(.+?)\'\);"></div>\n</div>\n<div class="info">\n<div class="title">(.+?)</div>\n<div class="infos">\n<div class="year">(.+?)</div>\n<div class="imdb">(.+?)</div>\n</div>\n</div>\n</a>\n</li>\n').findall(codigo_fonte_listaSeries)
	for link,imagem,nome,ano,imdb in match_series:
		link = link[1:]
		
		idIMDb = link.split('/')[-1]
		
		mediaInfo = json.loads(tv.getSerieInfo(idIMDb))

		infoLabels = {'Title':nome, 'Aired':mediaInfo['aired'], 'Plot':mediaInfo['plot']}
		addDir(nome+ ' ('+ano+')', site+link, 4, site+imagem, pagina, 'serie', infoLabels, site+imagem)

	if pagina==0:
		match_prox=re.compile('<a href=\"(.+?)\" class=\"r\">Pr').findall(codigo_fonte_listaSeries)
		pagina+=1
		for proximo in match_prox:
			proximo = proximo[1:]
			addDir('Proximo >>', site+proximo, 2, artfolder+'proximo.png', pagina)	
	elif pagina>=1:
		match_prox_ant=re.compile('<a href=\".+?\" class="l"><i class="fa fa-arrow-left"></i> Anterior</a><a href="(.+?)" class="r">Pr').findall(codigo_fonte_listaSeries)
		pagina+=1
		for proximo in match_prox_ant:
			proximo = proximo[1:]
			addDir('Proximo >>', site+proximo, 2, os.path.join(artfolder,'proximo.png'), pagina)
	#setVista('filmesSeries')
	vista_filmesSeries()

def getSeasons(url):
	codigo_fonte = abrir_url(url)
	temporadaN = 0
	soup = BeautifulSoup(codigo_fonte)
	idIMDb = url.split('/')[-1]
	
	for temporada in soup.findAll('h2'):
		addDirSeason(temporada.text, url, 5, os.path.join(artfolder,'temporadas','temporada'+str(temporadaN+1)+'.png'), 0, temporadaN, idIMDb)
		temporadaN+=1
	#setVista('temporadas')
	vista_temporadas()


def getEpisodes(url, temporadaNumero, idIMDb):
	codigo_fonte = abrir_url(url)
	soup = BeautifulSoup(codigo_fonte)

	temporadas = soup.findAll('div', attrs={'class':'temporadas'})

	i = 0
	match_episodios=re.compile('<li>\n<a href="(.+?)">\n<div class="thumb">\n<div class="img" style="background-image: url\(\'(.+?)\'\);"></div>\n</div>\n<div class="info">\n<div class="title">(.+?)</div>\n<div class="infos">\n<div class="year">(.+?)</div>\n<div class="imdb">(.+?)</div>\n</div>\n</div>\n</a>\n</li>\n').findall(str(temporadas[temporadaNumero]))
	for link,imagem,nomeOriginal,ano,imdb in match_episodios:
		codigo_fonte=abrir_url(site+link)

		episodioNumero = nomeOriginal.split('.')[1]
		episodioNomeSplit = episodioNumero.split('|')
		episodioNumero = episodioNomeSplit[0]
		
		codigoIMDb = link.split('/')[-1]
		
		
		if int(episodioNumero) == 0:
			i+=1

		episodioNumero = int(episodioNumero)+i
		mediaInfo = json.loads(tv.getSeasonEpisodio(idIMDb,(temporadaNumero+1),episodioNumero))
		nome = 'Ep. '+str(episodioNumero)+' - '+mediaInfo['name'].encode('utf8')
		ano = mediaInfo['aired'].encode('utf8')
		infoLabels = {'Title':nome, 'Aired': mediaInfo['aired'], 'Actors':mediaInfo['actors'], 'Plot':mediaInfo['plot'], 'Season':temporadaNumero, 'Episode':episodioNumero, 'Writer': mediaInfo['writer'], 'Director':mediaInfo["director"], "Code":codigoIMDb }

		poster = site+imagem

		getStream=re.compile('file: \'(.+?)\'').findall(codigo_fonte) 
		getLegenda=re.compile('file: \"(.+?)\"').findall(codigo_fonte)
		stream = ''
		legenda = ''
		for streamAux in getStream: stream = streamAux
		for legendaAux in getLegenda: legenda = legendaAux 
		addVideo(nome, stream, 3, site+imagem, site+legenda, 'episodio', infoLabels, poster)
	#setVista('episodios')
	vista_episodios()

def pesquisa(url):
	siteAux = ''

	if 'kids.' in url: siteAux = sitekids
	else: siteAux = site

	url =  siteAux + 'procurar'

	teclado = xbmc.Keyboard('', 'O que quer pesquisar?')
	teclado.doModal()

	if(teclado.isConfirmed()):
		strPesquisa = teclado.getText()
		
		codigo_fonte_pesquisa = abrir_url(url, strPesquisa)
		soup = BeautifulSoup(codigo_fonte_pesquisa)
		filmes_series = soup.findAll('div', attrs={'class':'list'})

		if(filmes_series[0].find('ul').text != ''):
			addLink('Filmes:', '', artfolder+'filmes.png')
			match_filmes=re.compile('<li>\n<a href="(.+?)">\n<div class="thumb">\n<div class="img" style="background-image: url\(\'(.+?)\'\);"></div>\n</div>\n<div class="info">\n<div class="title">(.+?)</div>\n<div class="infos">\n<div class="year">(.+?)</div>\n<div class="imdb">(.+?)</div>\n</div>\n</div>\n</a>\n</li>\n').findall(str(filmes_series[0]))
			for link,imagem,nome,ano,imdb in match_filmes:
				link = link[1:]
				codigo_fonte=abrir_url(siteAux+link)

				idIMDb = link.split('/')[-1]
				mediaInfo = getInfoIMDB(idIMDb)
				nome = mediaInfo['Title'].encode('utf8')
				ano = mediaInfo['Year'].encode('utf8')
				infoLabels = {'Title':name, 'Year': ano, 'Genre':mediaInfo['Genre'], 'Plot':mediaInfo['Plot']}
				poster = mediaInfo['Poster']
				
				getStream=re.compile('file: \'(.+?)\'').findall(codigo_fonte) 
				getLegenda=re.compile('file: \"(.+?)\"').findall(codigo_fonte)
				stream = ''
				legenda = ''
				for streamAux in getStream: stream = streamAux
				for legendaAux in getLegenda: legenda = legendaAux 
				addVideo(nome + ' ('+ano+')', stream, 3, siteAux+imagem, siteAux+legenda,'filme', infoLabels, poster)

		addDir('', '', '', artfolder+'nada.png', 0)

		if(filmes_series[1].find('ul').text != ''):
			addLink('Series:', '', artfolder+'series.png')
			match_series=re.compile('<li>\n<a href="(.+?)">\n<div class="thumb">\n<div class="img" style="background-image: url\(\'(.+?)\'\);"></div>\n</div>\n<div class="info">\n<div class="title">(.+?)</div>\n<div class="infos">\n<div class="year">(.+?)</div>\n<div class="imdb">(.+?)</div>\n</div>\n</div>\n</a>\n</li>\n').findall(str(filmes_series[1]))
			for link,imagem,nome,ano,imdb in match_series:
				link = link[1:]
				idIMDb = link.split('/')[-1]

				mediaInfo = json.loads(tv.getSerieInfo(idIMDb))
				print mediaInfo
				infoLabels = {'Title':name, 'Released':mediaInfo['aired'], 'Plot':mediaInfo['plot']}
				poster = mediaInfo['poster']
				addDir(nome + ' ('+ano+')', siteAux+link, 4, siteAux+imagem,'serie', infoLabels, poster)
		
		#setVista('filmesSeries')
		vista_filmesSeries()

def download(url,name,legenda):
	folder = selfAddon.getSetting('pastaDownloads')

	urlAux = clean(url.split('/')[-1])
	legendaAux = clean(legenda.split('/')[-1])

	extensaoMedia = clean(urlAux.split('.')[-1])
	extensaoLegenda = clean(legendaAux.split('.')[1])

	nomeMedia = name+'.'+extensaoMedia
	nomeLegenda = name+'.'+extensaoLegenda


	Downloader.Downloader().download( os.path.join(folder,nomeMedia), url, name)
	
	download_legendas(legenda, os.path.join(folder,nomeLegenda))

def download_legendas(url,path):
	contents = abrir_url(url)
	if contents:
		fh = open(path, 'w')
		fh.write(contents)
		fh.close()
	return

def getInfoIMDB(idIMDb):
	url = 'http://www.omdbapi.com/?i='+idIMDb+'&plot=short'
	data = json.loads(abrir_url(url))
	return data

def getGeneros(url, tipo):
	siteAux = ''
	mode = 1
	arte = ''

	if tipo == 'filmes':
		siteAux = url+'filmes'
		mode = 1
		arte = os.path.join(artfolder,'filmes.png')
	elif tipo == 'series':
		siteAux = url+'series'
		mode = 2
		arte = os.path.join(artfolder,'series.png')


	codigo_fonte=abrir_url(siteAux)

	soup = BeautifulSoup(codigo_fonte)
	generos = soup.find('select', attrs={'name':'genre'})

	listaGeneros = re.compile('<option value="(.+?)">(.+?)</option>').findall(str(generos))
	for value, text in listaGeneros:
		addDir(text, siteAux+'?genre='+value, mode, arte, 0)


###################################################################################
#                              DEFININCOES		                                  #
###################################################################################

def addBiblioteca(nome, url, tipo, temporada=False, episodio=False):
	updatelibrary=True

	if tipo == 'filme': 
		if not xbmcvfs.exists(pastaFilmes): xbmcvfs.mkdir(pastaFilmes)
	elif tipo == 'serie': 
		if not xbmcvfs.exists(pastaSeries): xbmcvfs.mkdir(pastaSeries)

	if type == 'filme': 
		try: file_folder = os.path.join(pastaFilmes,nome)
		except: pass
	elif type == 'serie':
		file_folder1 = os.path.join(pastaSeries,nome)
		if not xbmcvfs.exists(file_folder1): tryFTPfolder(file_folder1)
		file_folder = os.path.join(pastaSeries, nome+'/','S'+temporada)
		title =  nome + ' S'+temporada+'E'+episodio

	strm_contents = 'plugin://plugin.video.tugaio/?url=' + url +'&mode='+1+'&name=' + urllib.quote_plus(nome)
	savefile(urllib.quote_plus(title)+'.strm',strm_contents,file_folder)
	if updatelibrary: xbmc.executebuiltin("XBMC.UpdateLibrary(video)")
	return True


def abrirDefinincoes():
	selfAddon.openSettings()
	addDir('Entrar novamente','url',None,artfolder+'refresh.jpg',True)
	vista_menu()
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def vista_menu():
	opcao = selfAddon.getSetting('menuView')
	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51")

def vista_filmesSeries():
	opcao = selfAddon.getSetting('filmesSeriesView')
	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
	elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
	elif opcao == '3': xbmc.executebuiltin("Container.SetViewMode(501)")
	elif opcao == '4': xbmc.executebuiltin("Container.SetViewMode(508)")
	elif opcao == '5': xbmc.executebuiltin("Container.SetViewMode(504)")
	elif opcao == '6': xbmc.executebuiltin("Container.SetViewMode(503)")
	elif opcao == '7': xbmc.executebuiltin("Container.SetViewMode(515)")
	

def vista_temporadas():
	opcao = selfAddon.getSetting('temporadasView')
	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
	elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")

def vista_episodios():
	opcao = selfAddon.getSetting('episodiosView')
	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
	elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")

"""def setVista(vista):
	if vista == 'menu':
		opcao = selfAddon.getSetting('menuView')
		if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
		elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
    elif vista == 'filmesSeries':
    	opcao = selfAddon.getSetting('filmesSeriesView')
    	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
    	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
    	elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
    	elif opcao == '3': xbmc.executebuiltin("Container.SetViewMode(501)")
    	elif opcao == '4': xbmc.executebuiltin("Container.SetViewMode(508)")
    	elif opcao == '5': xbmc.executebuiltin("Container.SetViewMode(504)")
    	elif opcao == '6': xbmc.executebuiltin("Container.SetViewMode(503)")
    	elif opcao == '7': xbmc.executebuiltin("Container.SetViewMode(515)")
    elif vista == 'temporadas':
    	opcao = selfAddon.getSetting('temporadasView')
    	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
    	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
    	elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
    elif vista == 'episodios':
    	opcao = selfAddon.getSetting('episodiosView')
    	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
    	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
    	elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
"""
    

###################################################################################
#                               FUNCOES JA FEITAS                                 #
###################################################################################

#ABELHAS ADDON
def tryFTPfolder(file_folder):
	if 'ftp://' in file_folder:
		try:
			from ftplib import FTP		
			ftparg = re.compile('ftp://(.+?):(.+?)@(.+?):?(\d+)?/(.+/?)').findall(file_folder)
			ftp = FTP(ftparg[0][2],ftparg[0][0],ftparg[0][1])
			try: ftp.cwd(ftparg[0][4])
			except: ftp.mkd(ftparg[0][4])
			ftp.quit()
		except: print 'Nao conseguiu criar %s' % file_folder
	else: xbmcvfs.mkdir(file_folder)

def abrir_url(url,pesquisa=False):
	if pesquisa:
		data = urllib.urlencode({'procurar' : pesquisa})
		req = urllib2.Request(url,data)
	else: req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

def addLink(name,url,iconimage):
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setProperty('fanart_image', iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
	return ok

def addDir(name,url,mode,iconimage,pagina,tipo=False,infoLabels=False,poster=False):
	if infoLabels: infoLabelsAux = infoLabels
	else: infoLabelsAux = {'Title': name}

	if poster: posterAux = poster
	else: posterAux = iconimage

	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&pagina="+str(pagina)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True

	if tipo == 'filme':	
		xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
	elif tipo == 'serie':
		xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	elif tipo == 'episodio':
		xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
	else: 
		xbmcplugin.setContent(int(sys.argv[1]), 'Movies')

	liz=xbmcgui.ListItem(name, iconImage=posterAux, thumbnailImage=posterAux)
	liz.setProperty('fanart_image', posterAux)
	liz.setInfo( type="Video", infoLabels=infoLabelsAux )

	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok

def addFolder(name,url,mode,iconimage,folder):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="fanart.jpg", thumbnailImage=iconimage)
	liz.setProperty('fanart_image', iconimage)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=folder)
	return ok

def addDirSeason(name,url,mode,iconimage,pagina,temporada,idIMDbSerie,infoLabels=False,poster=False):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&pagina="+str(pagina)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&temporada="+str(temporada)+"&idIMDbSerie="+urllib.quote_plus(idIMDbSerie)
	ok=True
	xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
	liz=xbmcgui.ListItem(name, iconImage="fanart.jpg", thumbnailImage=iconimage)
	liz.setProperty('fanart_image', iconimage)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok

def addVideo(name,url,mode,iconimage,legenda,tipo,infoLabels=False,poster=False):
	if infoLabels: infoLabelsAux = infoLabels
	else: infoLabelsAux = {'Title': name}

	if poster: posterAux = poster
	else: posterAux = iconimage

	if tipo == 'filme':	
		xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
	elif tipo == 'serie':
		xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	elif tipo == 'episodio':
		xbmcplugin.setContent(int(sys.argv[1]), 'episodes')


	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&legenda="+urllib.quote_plus(legenda)+"&iconimage="+urllib.quote_plus(iconimage)
	ok=True
	contextMenuItems = []
	liz=xbmcgui.ListItem(name, iconImage=posterAux, thumbnailImage=posterAux)
	liz.setProperty('fanart_image', posterAux)
	liz.setInfo( type="Video", infoLabels=infoLabelsAux )
	contextMenuItems.append(('Download', 'XBMC.RunPlugin(%s?mode=7&name=%s&url=%s&iconimage=%s&legenda=%s)'%(sys.argv[0],urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(iconimage), urllib.quote_plus(legenda))))
	liz.addContextMenuItems(contextMenuItems, replaceItems=False)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	return ok

def clean(text):
	command={'&#8220;':'"','&#8221;':'"', '&#8211;':'-','&amp;':'&','&#8217;':"'",'&#8216;':"'"}
	regex = re.compile("|".join(map(re.escape, command.keys())))
	return regex.sub(lambda mo: command[mo.group(0)], text)

def player(name,url,iconimage,legenda):
	playlist = xbmc.PlayList(1)
	playlist.clear()
	listitem = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	listitem.setInfo("Video", {"title":name})
	listitem.setProperty('mimetype', 'video/x-msvideo')
	listitem.setProperty('IsPlayable', 'true')
	playlist.add(url, listitem)
	xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	xbmcPlayer.play(playlist)
	xbmc.Player().setSubtitles(legenda)

########################################################################################################
#                                               GET PARAMS                                                 #
############################################################################################################

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'): params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2: param[splitparams[0]]=splitparams[1]
	return param


params=get_params()
url=None
name=None
mode=None
iconimage=None
link=None
legenda=None
pagina=None
temporada=None
idIMDbSerie=None

try: url=urllib.unquote_plus(params["url"])
except: pass
try: link=urllib.unquote_plus(params["link"])
except: pass
try: legenda=urllib.unquote_plus(params["legenda"])
except: pass
try: name=urllib.unquote_plus(params["name"])
except: pass
try: temporada=int(params["temporada"])
except: pass
try: mode=int(params["mode"])
except: pass
try: pagina=int(params["pagina"])
except: pass
try: iconimage=urllib.unquote_plus(params["iconimage"])
except: pass
try: idIMDbSerie=urllib.unquote_plus(params["idIMDbSerie"])
except: pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "LINK. "+str(link)
print "Name: "+str(name)
print "Iconimage: "+str(iconimage)
print "PAGINA: "+str(pagina)
###############################################################################################################
#                                                   MODOS                                                     #
###############################################################################################################
if mode==None or url==None or len(url)<1: categorias()
elif mode==1: getFilmes(url, pagina)
elif mode==2: getSeries(url, pagina)
elif mode==3: player(name, url, iconimage, legenda)
elif mode==4: getSeasons(url)
elif mode==5: getEpisodes(url, temporada, idIMDbSerie)
elif mode==6: pesquisa(url)
elif mode==7: download(url, name, legenda)
elif mode==8: getGeneros(url, 'filmes')
elif mode==9: getGeneros(url, 'series')
elif mode==1000: abrirDefinincoes()
xbmcplugin.endOfDirectory(int(sys.argv[1]))