from nevow import inevow, rend, flat, loaders, static, tags as T, entities as E
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

    
class Toolset(object):
    def setModel(self, model):
        self.model = model
    
    def addRecentPage(self, page):
        self.recentPages.append(page)
        
    def makeBreadcrump(self):
        return T.p['> ', ListJoin(' > ').join(self.recentPages)]
    
    def render2TableJoin(self, dbResult, target):
        li = []
        for p in dbResult:
            name = p[0]
            url = URL.fromString(target).add('name', name)
            li.append(T.li[T.a(href=url)[name]])
        return li
            
    def render3tableJoin(self, dbResult, outerTarget, innerTarget):
        d = {}
        for i in dbResult:
            d.setdefault(i[0], []).append(i[1])

        outerLi = []
        for el in sorted(d.keys()):
            innerLi = []
            for r in sorted(d[el]):
                url = URL.fromString(innerTarget).add('name', r)
                innerLi.append(T.a(href=url)[r])
            url = URL.fromString(outerTarget).add('name', el)
            outerLi.append(T.li[ T.a(href=url)[el], ': ', ListJoin(', ').join(innerLi)])
        return outerLi
    

class BasePage(rend.Page, Toolset):
    docFactory = loaders.xmlfile('index.tmpl', templateDir='templates')
    child_public = static.File('public')
    
    def __init__(self, model, debug=False):
        self.model = model
        self.debug = debug
    
    def render_topnav(self, ctx, data):
        seg = inevow.ICurrentSegments(ctx)[0]
        seg = '/' if seg == '' else seg
        elements = [
            ('/', 'Home'),
            ('person', 'Personen'),
            ('artist', 'Interpreten'),
            ('record', 'Alben'),
            ('song', 'Lieder'),
            ('role', 'Rollen'),
            ('songtable', 'Liedtabelle')
        ]
        
        if self.debug:
            elements.append(('/public', '[Debug] public'))
        
        li = []
        for el in elements:
            if el[0] == seg:
                li.append(T.li(class_='active')[T.a(href=el[0])[el[1]]])
            else:
                li.append(T.li[T.a(href=el[0])[el[1]]])
                
        return T.ul[li]

class OneOrAllPage(BasePage):
    def render_content(self, ctx, data):
        try:
            name = inevow.IRequest(ctx).args['name'][0]
            return self.one(name)
        except (KeyError, AttributeError):
            return self.all()
        
class Person(OneOrAllPage):
    def all(self):
        dbResult = self.model.getPersonen()
        li = self.render2TableJoin(dbResult, '/person')
        return [
            #T.h2['Personen'],
            T.ul[li]
        ]
        
    def one(self, name):
        s = [T.h2[name]]
        dbResult = self.model.getPersonArtists(name)
        if dbResult:
            s.append(T.a(href='interpreten')[T.h3['Bands:']])
            s.append(self.render3tableJoin(dbResult, '/artist', '/role'))

        dbResult = self.model.getPersonSongs(name)
        if dbResult:
            s.append(T.a(href='lieder')[T.h3['Lieder:']])
            s.append(self.render3tableJoin(dbResult, '/song', '/role'))
            
        return s

        
class Artist(OneOrAllPage):
    def all(self):
        dbResult = self.model.getArtists()
        li = self.render2TableJoin(dbResult, '/artist')
        return [
            T.ul[li]
        ]

    def one(self, name):
        s = [T.h2[name]]
        dbResult = self.model.getArtistPersons(name)
        if dbResult:
            s.append(T.a(href='person')[T.h3['Personen:']])
            s.append(self.render3tableJoin(dbResult, '/person', '/role'))
                
        dbResult = self.model.getArtistRecords(name)
        if dbResult:
            s.append(T.a(href='record')[T.h3['Alben:']])
            s.append(self.render2TableJoin(dbResult, '/record'))
        
        return s
       
    
class Record(OneOrAllPage):
    def one(self, name):
        s = [T.h2[name]]
        dbResult = self.model.getRecordArtists(name)
        if dbResult:
            s.append(T.a(href='/artist')[T.h3['Interpreten:']])
            s.append(self.render2TableJoin(dbResult, '/artist'))
                    
        songs = self.model.getRecordSongs(name)
        if songs:
            volumes = {}
            for song in songs:
                volumes.setdefault(song[1], []).append((song[0], song[2]))
            liVolumes = []
            for v in sorted(volumes.keys()):
                if len(volumes) > 1:
                    liVolumes.append(T.li['CD ', v])
                liSongs = []
                for song in volumes[v]:
                    songName = song[0]
                    url = URL.fromString('/song').add('name', songName)
                    number = '' if song[1] is None else [song[1], ': ']
                    liSongs.append(T.li[number, T.a(href=url)[songName]])
                liVolumes.append(T.ul[liSongs])
            
            s.append(T.a(href='/song')[T.h3['Lieder:']])
            s.append(liVolumes)
            
        
        dbResult = self.model.getRecordPersonRole(name)
        if dbResult:
            s.append(T.a(href='/person')[T.h3['Personen:']])
            s.append(self.render3tableJoin(dbResult, '/person', '/role'))
                
        return s
    
    def all(self):
        dbResult = self.model.getArtistsRecords()
        liRecords = self.render3tableJoin(dbResult, '/artist', '/record')
                
        return T.ul[liRecords]
    
class Song(OneOrAllPage):
    def one(self, name):
        s = [T.h2[name]]
        dbResult = self.model.getSongArtists(name)
        if dbResult:
            s.append(T.a(href='/artist')[T.h3['Interpreten:']])
            s.append(self.render3tableJoin(dbResult, '/artist', '/record'))
        
        dbResult = self.model.getSongPersons(name)
        if dbResult:
            s.append(T.a(href='person')[T.h3['Personen:']])
            s.append(self.render3tableJoin(dbResult, '/person', '/role')    )
        
        return s
    
    def all(self):
        dbResult = self.model.getSongs()
        li = []
        for r in dbResult:
            url = URL.fromString('/song').add('name', r)
            li.append(T.li[T.a(href=url)[r]])
            
        return T.ul[li]
    
    
## TODO: bei Song ist der artist link kapuut    
class Role(OneOrAllPage):
    def all(self):
        dbResult = self.model.getRolePersonArtist()
        roleDict = {}
        for role, artist, person in dbResult:
            roleDict.setdefault(role, {})
            roleDict[role].setdefault(artist, []).append(person)

        roleArtist = []
        for role in sorted(roleDict.keys()):
            artistLi = []
            for artist in sorted(roleDict[role].keys()):
                persons = []
                for person in roleDict[role][artist]:
                    url = URL.fromString('/person').add('name', person)
                    persons.append(T.a(href=url)[person])
                url = URL.fromString('/artist').add('name', artist)
                artistLi.append(T.li[T.a(href=url)[artist], ': ', ListJoin(', ').join(persons)])
            url = URL.fromString('/role').add('name', role)
            roleArtist.append( [T.a(href=url)[role], T.ul[ artistLi ]] )
       
            
        dbResult = self.model.getRolePersonSong()
        roleDict = {}
        for role, song, person in dbResult:
            roleDict.setdefault(role, {})
            roleDict[role].setdefault(song, []).append(person)

        roleSong = []
        for role in sorted(roleDict.keys()):
            songLi = []
            for song in sorted(roleDict[role].keys()):
                persons = []
                for person in roleDict[role][song]:
                    url = URL.fromString('/person').add('name', person)
                    persons.append(T.a(href=url)[person])
                url = URL.fromString('/song').add('name', song)
                songLi.append(T.li[T.a(href=url)[song], ': ', ListJoin(', ').join(persons)])
            url = URL.fromString('/role').add('name', role)
            roleSong.append( [T.a(href=url)[role], T.ul[ songLi ]] )
        
        return [
            T.h3['Rollen in Bands'],
            roleArtist,
            T.h3['Rollen in Liedern'],
            T.ul[roleSong],
        ]
            

class SongTable(BasePage):
    def render_content(self, ctx, data):
        td = self.model.getSongTable()
        tRows = [T.tr[
            T.th['Interpret'],
            T.th['Album'], 
            T.th['CD-Nr'],
            T.th['CD-Name'], 
            T.th['Nr.'], 
            T.th['Lied'], 
        ]]
        for song, tracknumber, diskNumber, disk, record, artist in td:
            song = E.nbsp if song is None else T.a(href=URL.fromString('/song').add('name', song))[song]
            record = E.nbsp if record is None else T.a(href=URL.fromString('/record').add('name', record))[record]
            artist = E.nbsp if artist is None else T.a(href=URL.fromString('/artist').add('name', artist))[artist]
            tracknumber = E.nbsp if tracknumber is None else tracknumber
            disk = E.nbsp if disk is None else disk
            diskNumber = E.nbsp if diskNumber is None else diskNumber
            tRows.append( T.tr[ 
                T.td[artist], 
                T.td[record], 
                T.td[diskNumber],
                T.td[disk], 
                T.td[tracknumber], 
                T.td[song],
            ] )

        return [
            T.h1['Liedtabelle'],
            T.table(border=2)[tRows]
        ]
    
    
class IndexPage(BasePage):
    childPages = {
        'person': Person,
        'artist': Artist,
        'record': Record,
        'song': Song,
        'songtable': SongTable,
        'role': Role
        }
    
    
    
    def childFactory(self, ctx, name):
        try:
            return self.childPages[name](self.model)
        except KeyError:
            return self
    
    def render_content(self, ctx):
        return 'Hallo'
    
    #def locateChild(self, ctx, segments):
        #reload(simpleview)
        #m = self.mkModel()
        #self.simple.setModel(m)
        #args = inevow.IRequest(ctx).args
        #if 'name' in args:
            #url = URL.fromString(segments[0]).add('name', args['name'])
            #self.simple.addRecentPage(T.a(href=url)[args['name'][0]])
        #return self.simple, segments
        
        
class SimpleView(BasePage):
    #docFactory = loaders.xmlfile('index.tmpl', templateDir='templates')
    
    def __init__(self):
        self.setModel(self.mkModel())
        super(SimpleView, self).__init__()
        
    #def locateChild
        
        def mkModel(self):
            reload(model)
            m = model.Model()
        m.setCursor(cur)
        return m
    
    def renderTitle(self):
        s = ListJoin(' | ').join([
            T.a(href='/')['Home'],
            T.a(href='personen')['Personen'],
            T.a(href='interpreten')['Interpreten'],
            T.a(href='alben')['Alben'],
            T.a(href='lieder')['Lieder'],
            T.a(href='songtable')['Liedtabelle']
        ])
        return flat.flatten(s)
    
    
    #def child_(self, ctx):       
        #return self.renderTitle()
    
    def child_personen(self, ctx):
        dbResult = self.model.getPersonen()
        li = self.render2TableJoin(dbResult, '/person')
        s = [
            self.renderTitle(),
            self.makeBreadcrump(),
            T.ul[li]
        ]
        return flat.flatten(s)
    

    def child_person(self, ctx):
        name = inevow.IRequest(ctx).args['name'][0]
        dbResult = self.model.getPersonArtists(name)
        liArtists = self.render3tableJoin(dbResult, '/interpret', '/rolle')

        dbResult = self.model.getPersonSongs(name)
        liSongs = self.render3tableJoin(dbResult, '/lied', '/rolle')
            
        s = [
            self.renderTitle(),
            self.makeBreadcrump(),
            T.h1[name],
            T.a(href='interpreten')['Bands:'],
            T.ul[liArtists],
            T.a(href='lieder')['Lieder:'],
            T.ul[liSongs]
        ]
        return flat.flatten(s)
    
    def child_interpreten(self, ctx):          
        dbResult = self.model.getArtists()
        li = self.render2TableJoin(dbResult, '/interpret')
        s = [
            self.renderTitle(),
            self.makeBreadcrump(),
            T.ul[li]
        ]
        return flat.flatten(s)
    
    def child_interpret(self, ctx):
        name = inevow.IRequest(ctx).args['name'][0]
        dbResult = self.model.getArtistPersons(name)
        liPersons = self.render3tableJoin(dbResult, '/person', '/rolle')
            
        dbResult = self.model.getArtistRecords(name)
        liRecords = self.render2TableJoin(dbResult, '/album')
        
        s = [
            self.renderTitle(),
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
        
        dbResult = self.model.getRecordArtist(name)
        liArtists = self.render2TableJoin(dbResult, '/interpret')
        
        songs = self.model.getRecordSongs(name)
        volumes = {}
        for s in songs:
            volumes.setdefault(s[1], []).append((s[0], s[2]))

        liVolumes = []
        for v in sorted(volumes.keys()):
            liVolumes.append(T.li['CD ', v])
            liSongs = []
            for s in volumes[v]:
                songName = s[0]
                url = URL.fromString('/lied').add('name', songName)
                number = '' if s[1] is None else [s[1], ': ']
                liSongs.append(T.li[number, T.a(href=url)[songName]])
            liVolumes.append(T.ul[liSongs])
                
        s = [
            self.renderTitle(),
            self.makeBreadcrump(),
            T.h1['Album: ', name],
            T.a(href='interpreten')['Interpreten:'],
            T.ul[liArtists],
            T.a(href='songs')['Lieder:'],
            T.ul[liVolumes]
        ]
        return flat.flatten(s)
    
    def child_lied(self, ctx):
        name = inevow.IRequest(ctx).args['name'][0]

        dbResult = self.model.getSongArtists(name)
        liArtists = self.render3tableJoin(dbResult, '/interpret', '/album')
        
        dbResult = self.model.getSongPersons(name)
        liPersons = self.render3tableJoin(dbResult, '/person', '/rolle')    
        
        s = [
            self.renderTitle(),
            T.h1['Lied: ', name],
            self.makeBreadcrump(),
            T.a(href='interpreten')['Interpreten:'],
            T.ul[liArtists],
            T.a(href='personen')['Personen:'],
            T.ul[liPersons],
        ]
        return flat.flatten(s)
    
    def child_alben(self, ctx):
        dbResult = self.model.getRecords()
        liRecords = self.render3tableJoin(dbResult, '/album', '/interpret')
        
        s = [
            self.renderTitle(),
            self.makeBreadcrump(),
            T.h1['Alben'],
            T.ul[liRecords]
        ]
        return flat.flatten(s)
    
    def child_lieder(self, ctx):
        dbResult = self.model.getSongs()
        li = []
        for r in dbResult:
            url = URL.fromString('/lied').add('name', r)
            li.append(T.li[T.a(href=url)[r]])
            
        s = [
            self.renderTitle(),
            self.makeBreadcrump(),
            T.h1['Lieder'],
            T.ul[li]
        ]
        return flat.flatten(s)
    
    def child_rolle(self, ctx):
        name = inevow.IRequest(ctx).args['name'][0]
        dbResult = self.model.getRoleArtists(name)
        liArtists = self.render3tableJoin(dbResult, '/person', '/interpret')
        
        dbResult = self.model.getRoleSongs(name)
        liSongs = self.render3tableJoin(dbResult, '/person', '/song')
        
        s = [
            self.renderTitle(),
            self.makeBreadcrump(),
            T.h1['Rolle: ', name],
            'Bands:',
            T.ul[liArtists],
            'Lieder: ',
            T.ul[liSongs]
        ]
        return flat.flatten(s)
    
    def child_songtable(self, ctx):
        td = self.model.getSongsWithInfo()
        tRows = [T.tr[
            T.th['Interpret'],
            T.th['Album'], 
            T.th['CD-Nr'],
            T.th['CD-Name'], 
            T.th['Nr.'], 
            T.th['Lied'], 
        ]]
        for song, tracknumber, diskNumber, disk, record, artist in td:
            song = E.nbsp if song is None else T.a(href=URL.fromString('/lied').add('name', song))[song]
            record = E.nbsp if record is None else T.a(href=URL.fromString('/album').add('name', record))[record]
            artist = E.nbsp if artist is None else T.a(href=URL.fromString('/interpret').add('name', artist))[artist]
            tracknumber = E.nbsp if tracknumber is None else tracknumber
            disk = E.nbsp if disk is None else disk
            diskNumber = E.nbsp if diskNumber is None else diskNumber
            tRows.append( T.tr[ 
                T.td[artist], 
                T.td[record], 
                T.td[diskNumber],
                T.td[disk], 
                T.td[tracknumber], 
                T.td[song],
            ] )

        s = [
            self.renderTitle(),
            self.makeBreadcrump(),
            T.h1['Liedtabelle'],
            T.table(border=1)[tRows]
        ]
        return flat.flatten(s)