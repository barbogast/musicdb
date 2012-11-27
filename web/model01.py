import psycopg2


class Model(object):
    def setCursor(self, cursor):
        self.cur = cursor
        
    def getPersonen(self):
        self.cur.execute("select name from musicdb.person_alias order by name")
        return self.cur.fetchall()
    
    def getPersonArtists(self, name):
        self.cur.execute("""select a.name, r.name from 
        musicdb.person_alias p
        join musicdb.artist__person_alias__role apr on (p.id = apr.person_alias_id)
        join musicdb.artist a on (apr.artist_id = a.id)
        join musicdb.role r on (apr.role_id = r.id)
        where p.name = %s""", (name,))
        return self.cur.fetchall()
        
    def getPersonSongs(self, name):
        self.cur.execute("""select s.name, r.name from 
        musicdb.person_alias p
        join musicdb.person_alias__role__song prs on (p.id = prs.person_alias_id)
        join musicdb.song s on (prs.song_id = s.id)
        join musicdb.role r on (prs.role_id = r.id)
        where p.name = %s""", (name,))
        return self.cur.fetchall()
    
    def getArtists(self):
        self.cur.execute("select name from musicdb.artist order by name")
        return self.cur.fetchall()
    
    def getArtistPersons(self, artist):
        self.cur.execute("""select p.name, r.name from 
        musicdb.artist a
        join musicdb.artist__person_alias__role apr on (a.id = apr.artist_id)
        join musicdb.person_alias as p on (p.id = apr.person_alias_id)
        join musicdb.role r on (apr.role_id = r.id)
        where a.name = %s order by p.name, r.name""", (artist, ))
        return self.cur.fetchall()
    
    def getArtistRecords(self, artist):
        self.cur.execute("""select r.name from 
        musicdb.artist a
        join musicdb.artist__record ar on (a.id = ar.artist_id)
        join musicdb.record r on (ar.record_id = r.id)
        where a.name = %s order by r.name""", (artist, ))
        return self.cur.fetchall()
    
    def getRecordArtists(self, record):
        self.cur.execute("""select a.name from 
        musicdb.record r
        join musicdb.artist__record ar on (r.id = ar.record_id)
        join musicdb.artist a on (ar.artist_id = a.id)
        where r.name = %s order by a.name""", (record,) )
        return self.cur.fetchall()
    
    def getRecordPersonRole(self, record):
        self.cur.execute("""select p.name, ro.name from 
        musicdb.record re
        join musicdb.person_alias__record__role prr on (re.id = prr.record_id)
        join musicdb.person_alias p on (p.id = prr.person_alias_id)
        join musicdb.role ro on (ro.id = prr.role_id)
        where re.name = %s order by p.name, ro.name""", (record,) )
        return self.cur.fetchall()

    def getRecordSongs(self, record):
        self.cur.execute("""select s.name, v.number, sv.tracknumber from 
        musicdb.song s
        join musicdb.song__volume sv on (s.id = sv.song_id)
        join musicdb.volume v on (sv.volume_id = v.id)
        join musicdb.record r on (r.id = v.record_id)
        where r.name = %s
        order by v.number, sv.tracknumber""", (record,) )
        return self.cur.fetchall()
    
    def getSongArtists(self, song):
        self.cur.execute("""select a.name, r.name from 
        musicdb.song s
        join musicdb.song__volume sv on (s.id = sv.song_id)
        join musicdb.volume v on (v.id = sv.volume_id)
        join musicdb.record r on (v.record_id = r.id)
        join musicdb.artist__record ar on (r.id = ar.record_id)
        join musicdb.artist a on (a.id = ar.artist_id)
        where s.name = %s
        order by a.name, r.name""", (song, ))
        return self.cur.fetchall()
    
    def getSongPersons(self, song):
        self.cur.execute("""select p.name, r.name from
        musicdb.song s
        join musicdb.person_alias__role__song prs on (s.id = prs.song_id)
        join musicdb.person_alias p on (p.id = prs.person_alias_id)
        join musicdb.role r on (r.id = prs.role_id)
        where s.name = %s
        order by p.name, r.name""", (song, ))
        return self.cur.fetchall()
    
    def getArtistsRecords(self):
        self.cur.execute("""select a.name, r.name from
        musicdb.record r
        join musicdb.artist__record ar on (ar.record_id = r.id)
        join musicdb.artist a on (ar.artist_id = a.id)
        order by a.name, r.name""")
        return self.cur.fetchall()
    
    def getSongs(self):
        self.cur.execute("""select s.name from musicdb.song s order by s.name""")
        return self.cur.fetchall()
    
    def getRoleArtists(self, role):
        self.cur.execute("""select p.name, a.name from
        musicdb.role r
        join musicdb.artist__person_alias__role apr on (r.id = apr.role_id)
        join musicdb.person_alias p on (p.id = apr.person_alias_id)
        join musicdb.artist a on (a.id = apr.artist_id)
        where r.name = %s
        order by p.name, a.name""", (role, ))
        return self.cur.fetchall()
        
    def getRoleSongs(self, song):
        self.cur.execute("""select p.name, s.name from
        musicdb.role r
        join musicdb.person_alias__role__song prs on (r.id = prs.role_id)
        join musicdb.person_alias p on (p.id = prs.person_alias_id)
        join musicdb.song s on (s.id = prs.song_id)
        where r.name = %s
        order by p.name, s.name""", (song,) )
        return self.cur.fetchall()
        
    def getSongTable(self):
        self.cur.execute("""select s.name, sv.tracknumber, v.number, v.name, r.name, a.name from
        musicdb.song s
        full join musicdb.song__volume sv on (s.id = sv.song_id)
        full join musicdb.volume v on (v.id = sv.volume_id)
        full join musicdb.record r on (v.record_id = r.id)
        full join musicdb.artist__record ar on (ar.record_id = r.id)
        full join musicdb.artist a on (ar.artist_id = a.id)
        where s.name is not NULL
        order by a.name, r.name, v.number, sv.tracknumber""")
        return self.cur.fetchall()
        
    def getRolePersonArtist(self):
        self.cur.execute("""select r.name, a.name, p.name from
        musicdb.role r
        join musicdb.artist__person_alias__role apr on (r.id = apr.role_id)
        join musicdb.artist a on (apr.artist_id = a.id)
        join musicdb.person_alias p on (p.id = apr.person_alias_id)
        order by r.name, a.name, p.name""")
        return self.cur.fetchall()
    
    def getRolePersonSong(self):
        self.cur.execute("""select r.name, s.name, p.name from
        musicdb.role r
        join musicdb.person_alias__role__song prs on (r.id = prs.role_id)
        join musicdb.song s on (prs.song_id = s.id)
        join musicdb.person_alias p on (p.id = prs.person_alias_id)
        order by r.name, s.name, p.name""")
        return self.cur.fetchall()
    
    def getByMusicbrainz(self, table, musicbrainz_id):
        if not table in ('artist', 'record', 'song'):
            raise ValueError('Table not allowed')
        
        sql = "select id from musicdb."+table+" where musicbrainz_id = %s"
        self.cur.execute(sql, (musicbrainz_id,))
        res = self.cur.fetchone()
        if res:
            return res[0]
        else:
            return None
    
        