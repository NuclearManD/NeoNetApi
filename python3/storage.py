try:
    import discord
    import discordAccess as dis
except:
    discord = False
import ast
import os
DISCORD_META_DIR = "discord-meta"
AUTORUN_RES_DIR = "autorun/res"
# NOTE: This function CANNOT save complex objects.
def saveList(fn,l,mode='w'):
    f=open(fn,mode)
    for i in l:
        if type(i)==str:
            i=repr(i)
        f.write(str(i)+'\n')
    f.close()
def loadList(fn):
    f=open(fn,'r')
    data = f.read().replace('\r','\n').split('\n')
    olist = []
    for i in data:
        if i.isspace():
            continue
        try:
            olist.append(ast.literal_eval(i))
        except:
            olist.append(i)
    while '' in olist:
        olist.remove('')
    return olist

# NOTE: This function CANNOT save complex objects.
def saveDict(fn, d):
    f=open(fn,'w')
    f.write(repr(d))
    f.close()
def loadDict(fn):
    f=open(fn, 'r')
    d = ast.literal_eval(f.read())
    f.close()
    return d
# because saving dict and obj is the same
saveObj = saveDict
loadObj = loadDict

if discord!=False:
    def listKnownDiscordServerIds():
        if not os.path.isdir(DISCORD_META_DIR):
            os.mkdir(DISCORD_META_DIR)
        if not os.path.isfile(DISCORD_META_DIR+"/servers.lst"):
            saveList(DISCORD_META_DIR+"/servers.lst", [])
            return []
        return loadList(DISCORD_META_DIR+"/servers.lst")
    def listKnownDiscordServers():
        lis=[]
        for i in listKnownDiscordServerIds():
            try:
                lis.append(DiscordServerStorage(DISCORD_META_DIR+"/"+i+".server"))
            except:
                print("Warning: failed to load discord server with ID "+i)
        return lis
    class DiscordServerStorage():
        def __init__(self, server):
            if type(server)==str:
                self.load(server)
            else:
                self.id = server.id
                self.owner_id = server.owner_id
                self.owner_name = server.owner.name
                self.owner_discriminator = server.owner.discriminator
                self.name = server.name
        def save(self,fn=None):
            if fn==None:
                fn=DISCORD_META_DIR+"/"+self.id+".server"
            data={}
            data["id"]=self.id
            data["o_id"]=self.owner_id
            data["o_name"]=self.owner_name
            data["o_dis"]=self.owner_discriminator
            data["name"]=self.name
            saveDict(fn, data)
        def load(self,fn):
            if fn==None:
                fn=DISCORD_META_DIR+"/"+self.id+".server"
            data=loadDict(fn)
            self.id=data["id"]
            self.owner_id=data["o_id"]
            self.owner_name=data["o_name"]
            self.owner_discriminator=data["o_dis"]
            self.name=data["name"]
    def updateKnownDiscordServers():
        allServers = dis.allServers()
        newServers = []
        knownServers = listKnownDiscordServerIds()
        for i in allServers:
            if not i.id in knownServers:
                newServers.append(i)
        new_servers = []
        for i in newServers:
            server = DiscordServerStorage(i)
            server.save()
            knownServers.append(i.id)
            new_servers.append(i)
        saveList(DISCORD_META_DIR+"/servers.lst",knownServers)
        return new_servers
def saveObjAutorun(pgmname, fn, obj):
    if not os.path.isdir(AUTORUN_RES_DIR):
        os.makedirs(AUTORUN_RES_DIR)
    saveObj(AUTORUN_RES_DIR+"/"+pgmname+"_"+fn, obj)
def loadObjAutorun(pgmname, fn):
    return loadObj(AUTORUN_RES_DIR+"/"+pgmname+"_"+fn)
