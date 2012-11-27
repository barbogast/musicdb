from nevow import inevow, rend, flat, loaders, tags as T
from nevow.url import URL


class ListJoin(object):
    def __init__(self, s):
        self.s = s
        
    def join(self, l):
        if not l:
            return []
        
        res = [l[0]]
        if len(l) == 1:
            return res
        
        for j in l[1:]:
            res.append(self.s)
            res.append(j)
        return res

        
class SimpleView(rend.Page):
    def __init__(self):
        self.recentPages = []
        super(SimpleView, self).__init__()
        
    def setModel(self, model):
        self.model = model
    
    def addRecentPage(self, page):
        self.recentPages.append(page)
        
    def makeBreadcrump(self):
        return T.p[ListJoin(' >> ').join(self.recentPages)]
        
    def child_(self, ctx):
        s = T.ul[
            T.li[T.a(href='personen')['Personen']],
            T.li[T.a(href='interpreten')['Interpreten']],
            T.li[T.a(href='alben')['Alben']],
            T.li[T.a(href='lieder')['Lieder']],
            T.li[T.a(href='rollen')['Rollen']]
        ]
        return flat.flatten(s)
    
    def child_personen(self, ctx):
        li = []
        for p in self.model.getPersonen():
            name = p[0]
            url = URL.fromString('/person').add('name', name)
            li.append(T.li[T.a(href=url)[name]])
        s = [
            T.a(href='/')['Home'],
            self.makeBreadcrump(),
            T.ul[li]
        ]
        return flat.flatten(s)
    
    def render3tableJoin(self, dbResult, outerSegment, innerSegment):
        d = {}
        for i in dbResult:
            d.setdefault(i[0], []).append(i[1])

        outerLi = []
        for el in sorted(d.keys()):
            innerLi = []
            for r in sorted(d[el]):
                url = URL.fromString(innerSegment).add('name', r)
                innerLi.append(T.li[T.a(href=url)][r])
            url = URL.fromString(outerSegment).add('name', el)
            outerLi.append(T.li[ T.a(href=url)[el], ': ', T.ul[innerLi]])
        return outerLi

    
    def child_person(self, ctx):
        name = inevow.IRequest(ctx).args['name'][0]
        dbResult = self.model.getPersonArtists(name)
        liArtists = self.render3tableJoin(dbResult, '/interpret', '/role')
        #d = {}
        #for i in pInfo:
            #d.setdefault(i[0], []).append(i[1])

        #liArtists = []
        #for artist in sorted(d.keys()):
            #roles = []
            #for r in sorted(d[artist]):
                #url = URL.fromString('/role').add('name', r)
                #roles.append(T.li[T.a(href=url)][r])
            #liArtists.append(T.li[ T.a(href='interpret?name='+artist)[artist], ': ', T.ul[roles]])
            
        #sInfo = self.model.getPersonSongs(name)
        #d = {}
        #for i in sInfo:
            #d.setdefault(i[0], []).append(i[1])
        
        #liSongs = []
        #for song in sorted(d.keys()):
            #roles = []
            #for r in sorted(d[song]):
                #url = URL.fromString('/role').add('name', r)
                #roles.append(T.li[T.a(href=url)[r]] )
            #url = URL.fromString('/lied').add('name', song)
            #liSongs.append(T.li[ T.a(href=url)[song], ': ', T.ul[roles]])
        dbResult = self.model.getPersonSongs(name)
        liSongs = self.render3tableJoin(dbResult, '/lied', '/role')
            
        s = [
            T.a(href='/')['Home'], ' > ', T.a(href='personen')['Personen'],
            self.makeBreadcrump(),
            T.h1[name],
            T.a(href='interpreten')['Bands:'],
            T.ul[liArtists],
            T.a(href='lieder')['Lieder:'],
            T.ul[liSongs]
        ]
        return flat.flatten(s)
    
    def child_interpreten(self, ctx):
        li = []
        for p in self.model.getArtists():
            name = p[0]
            url = URL.fromString('/interpret').add('name', name)
            li.append(T.li[T.a(href=url)[name]])
        s = [
            T.a(href='/')['Home'],
            self.makeBreadcrump(),
            T.ul[li]
        ]
        return flat.flatten(s)
    
    def child_interpret(self, ctx):
        name = inevow.IRequest(ctx).args['name'][0]
        pInfo = self.model.getArtistPersons(name)
        d = {}
        for i in pInfo:
            d.setdefault(i[0], []).append(i[1])

        liPersons = []
        for person in sorted(d.keys()):
            roles = []
            for r in sorted(d[person]):
                url = URL.fromString('/role').add('name', r)
                roles.append( T.li[T.a(href=url)[r]] )
            url = URL.fromString('/person').add('name', person)
            liPersons.append(T.li[ T.a(href=url)[person], ': ', T.ul[roles]])
            
        records = self.model.getArtistRecords(name)
        records = [r[0] for r in records]
        
        liRecords = []
        for record in sorted(records):
            url = URL.fromString('/album').add('name', record)
            liRecords.append(T.li[ T.a(href=url)[record] ])
        
        s = [
            T.a(href='/')['Home'], ' > ', T.a(href='interpreten')['Interpreten'],
            self.makeBreadcrump(),
            T.h1[name],
            T.a(href='personen')['Personen:'],
            T.ul[liPersons],
            T.a(href='albums')['Alben:'],
            T.ul[liRecords]
        ]
        return flat.flatten(s)
    
    def child_album(self, ctx):
        name = inevow.IRequest(ctx).args['name'][0]
        artists = self.model.getRecordArtist(name)
        print artists
        artists = [a[0] for a in artists]
        
        liArtists = []
        for artist in sorted(artists):
            url = URL.fromString('/interpret').add('name', artist)
            liArtists.append(T.li[ T.a(href=url)[artist] ])
            
        
        songs = self.model.getRecordSongs(name)
        print songs
        volumes = {}
        for s in songs:
            volumes.setdefault(s[1], []).append((s[0], s[2]))

        liVolumes = []
        for v in sorted(volumes.keys()):
            liVolumes.append(T.li['CD ', v])
            liSongs = []
            for s in volumes[v]:
                name = s[0]
                url = URL.fromString('/lied').add('name', name)
                number = '-' if s[1] is None else s[1]
                liSongs.append(T.li[number, ': ', T.a(href=url)[name]])
            liVolumes.append(T.ul[liSongs])
                
        s = [
            T.a(href='/')['Home'], ' > ', T.a(href='alben')['Alben'],
            self.makeBreadcrump(),
            T.h1[name],
            T.a(href='interpreten')['Interpreten:'],
            T.ul[liArtists],
            T.a(href='songs')['Lieder:'],
            T.ul[liVolumes]
        ]
        return flat.flatten(s)
    
    def child_lied(self, ctx):
        name = inevow.IRequest(ctx).args['name'][0]

        liArtists = []
        artists = self.model.getSongArtists(name)
        aDict = {}
        for a in artists:
            aDict.setdefault(a[0], []).append(a[1])
        for a in sorted(aDict.keys()):
            liRecords = []
            for r in aDict[a]:
                url = URL.fromString('/album').add('name', r)
                liRecords.append(T.li[T.a(href=url)[r]])
            url = URL.fromString('/interpret').add('name', a)
            liArtists.append(T.li[T.a(href=url)[a], ': ', T.ul[ liRecords] ])
            
        liPersons = []
        persons = self.model.getSongPersons(name)
        pDict = {}
        for p in persons:
            pDict.setdefault(p[0], []).append(p[1])
        for p in sorted(pDict.keys()):
            liRoles = []
            for r in pDict[p]:
                url = URL.fromString('/rolle').add('name', r)
                liRoles.append(T.li[T.a(href=url)[r]])
            url = URL.fromString('/person').add('name', p)
            liPersons.append(T.li[ T.a(href=url)[p], ': ', T.ul[ liRoles ] ])
            
        liRecords = []
            
        
        s = [
            T.a(href='/')['Home'], ' > ', T.a(href='lieder')['Lieder'],
            self.makeBreadcrump(),
            T.h1[name],
            T.a(href='interpreten')['Interpreten:'],
            T.ul[liArtists],
            T.a(href='personen')['Personen'],
            T.ul[liPersons],
        ]
        return flat.flatten(s)