import urllib, os, xbmc, xbmcgui

addon_id = 'plugin.video.stalker'
data_folder = 'special://userdata/addon_data/' + addon_id
Url = 'http://adrxbmc.site90.net/stalker.fix/'
File = ['settings.xml', 'http_portal_iptvprivateserver_tv-genres', 'http_portal_iptvprivateserver_tv']

def download(url, dest, dp = None):
    if not dp:
        dp = xbmcgui.DialogProgress()
        dp.create("Fixing IPTV Stalker","Downloading & Copying File",' ', ' ')
    dp.update(0)
    urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
 
def _pbhook(numblocks, blocksize, filesize, url, dp):
    try:
        percent = min((numblocks*blocksize*100)/filesize, 100)
        dp.update(percent)
    except:
        percent = 100
        dp.update(percent)
    if dp.iscanceled(): 
        raise Exception("Canceled")
        dp.close()

for file in File:
	url = Url + file
	fix = xbmc.translatePath(os.path.join( data_folder, file))
	download(url, fix)
	
d = xbmcgui.Dialog()
d.ok('Fix IPTV Stalker', 'IPTV Stalker Fixed')