import psycopg2

"""
DN: 
 * 3 joins um alle lieder von einem artist zu bekommen
 * kann ich volume irgendwie weglassen. wegen den records mit nur einem volume
 * ist song.variation_id und record.edition_id ok?
 * wie gehen db tests? wie teil 1 oder wie teil2? mit ergebnissen vergleichen? wie dokumentation?
 * was bringen schemas? wie wird aufgeteilt
 * views?
 * was is mit sqlite? schmemas und foreignkeys?
"""

"""
TODO: sql commentare
"""

class Transaction(object):
    def setConnection(self, connection):
        self.conn = connection

    def runInTransaction(self, func):
        def newF(self, *args, **kwArgs):
            cur = self.conn.cursor()
            try:
                func(self, cur, *args, **kwArgs)
            except Exception, e:
                self.conn.rollback()
                raise e
            else:
                self.conn.commit()
            finally:
                cur.close()
        return newF
        

class A(object):
    def setCursor(self, cursor):
        self.cur = cursor
        
    def getPersonID(self, name):
        self.cur.execute("select id from musicdb.person_alias where name = %s", (name, ))
        if self.cur.rowcount != 1:
            return None
        return self.cur.fetchone()[0]

    def getArtistID(self, name):
        self.cur.execute("select id from musicdb.artist where name = %s", (name, ))
        if self.cur.rowcount != 1:
            return None
        return self.cur.fetchone()[0]
    
    def insertPersonAlias(self, name):
        self.cur.execute("insert into musicdb.person_alias (name) values (%s) returning id", (name,))
        res = self.cur.fetchone()[0]
        return res
        
    def insertArtist(self, name):
        self.cur.execute("insert into musicdb.artist (name) values (%s) returning id", (name,))
        return self.cur.fetchone()[0]
    
    def insertRecord(self, name, editionID=None):
        args = {'name': name, 'edition_id': editionID}
        self.cur.execute("""insert into musicdb.record (name, edition_id) 
        values (%(name)s, %(edition_id)s) returning id""", args)
        return self.cur.fetchone()[0]
    
    def insertVolume(self, number, name=None, recordID=None):
        args = {'name': name, 'number': number, 'record_id': recordID}
        self.cur.execute("""insert into musicdb.volume
        (number, name, record_id) values (%(number)s, %(name)s, %(record_id)s) returning id""", args)
        return self.cur.fetchone()[0]
        
    def insertSong(self, name, variationID=None):
        args = {'name': name, 'variation_id': variationID}
        self.cur.execute("""insert into musicdb.song
        (name, variation_id) values (%(name)s, %(variation_id)s) returning id""", args)
        return self.cur.fetchone()[0]
        
       
    def mapArtistToPersonAlias(self, artistID, personAliasID):
        args = {'artist_id': artistID, 'person_alias_id': personAliasID}
        self.cur.execute("""insert into musicdb.artist__person_alias 
        (artist_id, person_alias_id) values (%(artist_id)s, %(person_alias_id)s)""", args)
        
        
    def mapArtistToRecord(self, artistID, recordID):
        args = {'artist_id': artistID, 'record_id': recordID}
        self.cur.execute("""insert into musicdb.artist__record
        (artist_id, record_id) values (%(artist_id)s, %(record_id)s)""", args)
        
    def mapSongToVolume(self, songID, volumeID, tracknumber=None):
        args = {'song_id': songID, 'volume_id': volumeID, 'tracknumber': tracknumber}
        self.cur.execute("""insert into song__volume 
        (song_id, volume_id, tracknumber) values (%(song_id)s, %(volume_id)s, %(tracknumber)s)""", args)
        
    def mapPersonAliasToRecordToRole(self, personAliasID, recordID, roleID):
        args = {'person_alias_id': personAliasID, 'record_id': recordID, 'role_id': roleID}
        self.cur.execute("""insert into person_alias__record__role
        (person_alias_id, record_id, role_id) values (%(person_alias_id)s, %(record_id)s, %(role_id)s)""", args)
    
    def mapPersonAliasToRoleToSong(self, personAliasID, roleID, songID):
        args = {'person_alias_id': personAliasID, 'role_id': roleID, 'song_id': songID}
        self.cur.execute("""insert into person_alias__role__song
        (person_alias_id, role_id, song_id) values (%(person_alias_id)s, %(role_id)s, %(song_id)s)""", args)
        
    def getRoleID(self, name):
        self.cur.execute("""select id from musicdb.role where name = %s""", (name,))
        return self.cur.fetchone()[0]

import unittest as ut
class TestA(ut.TestCase):
    def setUp(self):
        self.conn = psycopg2.connect(database='musicdb', user='musicdb')

    def test_getPersonID(self):
        name = 'testperson'
        a = A()
        cur = self.conn.cursor()
        cur.execute("insert into musicdb.person_alias (name) values (%s) returning id", (name, ))
        personID = cur.fetchone()[0]
        self.assertEqual(a.getPersonID(cur, name), personID)

    def test_getArtistID(self):
        name = 'testartist'
        a = A()
        cur = self.conn.cursor()
        cur.execute("insert into musicdb.artist (name) values (%s) returning id", (name, ))
        ID = cur.fetchone()[0]
        self.assertEqual(a.getArtistID(cur, name), ID)
        
    def test_insertPersonAlias(self):
        name = 'test_insertPersonAlias'
        cur = self.conn.cursor()
        isID = a.insertPersonAlias(cur, name)
        cur.execute("select id from musicdb.person_alias where name = %s", (name,))
        shouldBeID = cur.fetchone()[0]
        self.assertEqual(isID, shouldBeID)
        
    def test_insertArtist(self):
        name = 'test_insertArtist'
        cur = self.conn.cursor()
        isID = a.insertArtist(cur, name)
        cur.execute("select id from musicdb.artist where name = %s", (name,))
        shouldBeID = cur.fetchone()[0]
        self.assertEqual(isID, shouldBeID)
        
    def test_mapArtistToPersonAlias(self):
        cur = self.conn.cursor()
        artistID = a.insertArtist(cur, 'testArtist')
        personID = a.insertPersonAlias(cur, 'testPerson')
        a.mapArtistToPersonAlias(cur, artistID, personID)
        cur.execute("""select a.name
        from musicdb.person_alias as p, musicdb.artist as a, musicdb.artist__person_alias as ap
        where p.name = 'testPerson' and p.id = ap.person_alias_id and ap.artist_id = a.id""")
        res = cur.fetchone()[0]
        self.assertEqual(res, 'testArtist')

    def tearDown(self):
        self.conn.rollback()
        self.conn.close()
    
if __name__ == '__main__':
    #ut.main()
    import pprint
    
    def makeAwithConnAndCur():
        conn = psycopg2.connect(database='musicdb', user='musicdb')
        #conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        a = A()
        a.setCursor(cur)
        return a
    
    def person__personAlias():
        # TODO: Add table "person" with 1:N person:personAliasJoin 
        # examples: bob marley: 'Robert Nesta Marley'
        # TODO: is 1:N required? need to find a example for one musician having multiple aliases
        pass
        
    def personAlias__artist():
        a = makeAwithConnAndCur()
        
        maynard = a.insertPersonAlias('Maynard James Keenan')
        james = a.insertPersonAlias('James Iha')
        bob = a.insertPersonAlias('Bob Marley')
        
        
        tool = a.insertArtist('Tool')
        circle = a.insertArtist('A Perfect Circle')
        pumpkins = a.insertArtist('Smashing Pumpkins')
        
        a.mapArtistToPersonAlias(tool, maynard)
        a.mapArtistToPersonAlias(circle, maynard)
        a.mapArtistToPersonAlias(circle, james)
        a.mapArtistToPersonAlias(pumpkins, james)

        a.cur.execute("""
        select a.name, count(*) from 
        musicdb.person_alias as p, 
        musicdb.artist as a, 
        musicdb.artist__person_alias as pb
        where pb.artist_id = a.id and pb.person_alias_id = p.id
        group by a.name""")
        pprint.pprint( a.cur.fetchall() )
        
        a.cur.execute("""
        select p.name || ' spielt in ' || b.name as artistmembers from 
        musicdb.person_alias as p, 
        musicdb.artist as b, 
        musicdb.artist__person_alias as pb
        where (b.id = pb.artist_id and p.id = pb.person_alias_id) """)
        pprint.pprint( a.cur.fetchall())
        
    def artist__record():
        a = makeAwithConnAndCur()
        metallica = a.insertArtist('Metallica')
        symphony = a.insertArtist('San Francisco Symphony')
        sm = a.insertRecord('S&M')
        master = a.insertRecord('Master Of Puppets')
        a.mapArtistToRecord(metallica, master)
        a.mapArtistToRecord(metallica, sm)
        a.mapArtistToRecord(symphony, sm)
        
        a.cur.execute("""select a.name, r.name from 
        musicdb.record as r,
        musicdb.artist as a,
        musicdb.artist__record as ar
        where r.id = ar.record_id and a.id = ar.artist_id;
        """)
        pprint.pprint(a.cur.fetchall())
        
    def record__volume():
        a = makeAwithConnAndCur()
        sm = a.insertRecord('S&M')
        mellon = a.insertRecord('Mellon Collie and the Infinite Sadness')
        sm1 = a.insertVolume(1, recordID=sm)
        sm1 = a.insertVolume(2, recordID=sm)
        mellon1 = a.insertVolume(1, 'dawn to dusk', mellon)
        mellon1 = a.insertVolume(2, 'twilight to starlight', mellon)        
        
        a.cur.execute("""select r.name, v.number, v.name from
        musicdb.record as r, musicdb.volume as v
        where r.id = v.record_id""")
        pprint.pprint(a.cur.fetchall())
        
    def record__record():
        # "I'm yours" is a single
        a = makeAwithConnAndCur()
        jason = a.insertArtist('Jason Mraz')
        orig = a.insertRecord("I'm yours")
        uk = a.insertRecord("I'm yours UK", editionID=orig)
        
        a.mapArtistToRecord(jason, orig)
        a.mapArtistToRecord(jason, uk)
        
        orig1 = a.insertVolume(1, recordID=orig)
        uk1 = a.insertVolume(1, recordID=uk)
        
        im = a.insertSong("I'm yours")
        imradio = a.insertSong("I'm yours (Radio Edit)", variationID=im)
        kills = a.insertSong('If It Kills Me')
        
        a.mapSongToVolume(imradio, orig1, 1)
        a.mapSongToVolume(im, orig1, 2)

        a.mapSongToVolume(im, uk1, 1)
        a.mapSongToVolume(kills, uk1, 2)
        
        a.cur.execute("""select r2.name||' is a edition of '||r1.name from 
          musicdb.record as r1,
          musicdb.record as r2
        where r1.id = r2.edition_id""")
        pprint.pprint(a.cur.fetchall())
        
        a.cur.execute("""select s.name, r.name, sv.tracknumber from 
          musicdb.song as s,
          musicdb.volume as v,
          musicdb.record as r,
          musicdb.song__volume as sv
        where s.id = sv.song_id and sv.volume_id = v.id and v.record_id = r.id""")
        pprint.pprint(a.cur.fetchall())
          
        
    def song__volume():
        a = makeAwithConnAndCur()
        rammstein = a.insertArtist('Rammstein')
        bravo = a.insertArtist('Bravo Hits')
        sehnsucht = a.insertRecord('Sehnsucht')
        bravo17 = a.insertRecord('17')
        sehnsucht1 = a.insertVolume(1, recordID=sehnsucht)
        bravo1 = a.insertVolume(2, recordID=bravo17)
        engel = a.insertSong('Engel')
        du = a.insertSong('Du hast')
        a.mapArtistToRecord(rammstein, sehnsucht)
        a.mapArtistToRecord(bravo, bravo17)
        a.mapSongToVolume(engel, bravo1)
        a.mapSongToVolume(engel, sehnsucht1)
        a.mapSongToVolume(du, sehnsucht1)
        
        a.cur.execute("""select a.name, r.name, v.number, s.name from
          musicdb.artist as a,
          musicdb.record as r,
          musicdb.song as s, 
          musicdb.volume as v,
          musicdb.artist__record as ar,
          musicdb.song__volume as sv
        where a.id = ar.artist_id and ar.record_id = r.id and r.id = v.record_id and sv.volume_id = v.id and s.id = sv.song_id""")
        pprint.pprint(a.cur.fetchall())
        
    def song__song():
        a = makeAwithConnAndCur()
        sm = a.insertRecord('S&M')
        justice = a.insertRecord('...And Justice For All')
        sm2 = a.insertVolume(2, recordID=sm)
        justice1 = a.insertVolume(1, recordID=justice)
        one = a.insertSong('One')
        oneSm = a.insertSong('One', variationID=one)
        a.mapSongToVolume(one, justice1)
        a.mapSongToVolume(oneSm, sm2)
        a.cur.execute("""select s1.name as songname, r1.name as albumOfOriginal, r2.name as albumOfVariation from 
        musicdb.song as s1, 
        musicdb.song as s2,
        musicdb.volume as v1,
        musicdb.volume as v2,
        musicdb.record as r1,
        musicdb.record as r2,
        musicdb.song__volume as sv1,
        musicdb.song__volume as sv2
        where s1.id = s2.variation_id and s1.id = sv1.song_id and sv1.volume_id = v1.id and v1.record_id = r1.id
          and s2.id = sv2.song_id and sv2.volume_id = v2.id and v2.record_id = r2.id""")
        print 'SongName, AlbumOriginal, AlbumVariation'
        pprint.pprint(a.cur.fetchall())
        
    def personAlias_record_role():
        a = makeAwithConnAndCur()
        opeth = a.insertArtist('Opeth')
        tree = a.insertArtist('Porcupine Tree')
        mikael = a.insertPersonAlias('Mikael Akerfeldt')
        steven = a.insertPersonAlias('Steven Wilson')
        a.mapArtistToPersonAlias(opeth, mikael)
        a.mapArtistToPersonAlias(tree, steven)
        
        damn = a.insertRecord('Damnation')
        dead = a.insertRecord('Deadwing')
        damn1 = a.insertVolume(1, recordID=damn)
        dead1 = a.insertVolume(1, recordID=dead)
        
        a.mapArtistToRecord(opeth, damn)
        a.mapArtistToRecord(tree, dead)
        
        lazarus = a.insertSong('Lazarus')
        a.mapSongToVolume(lazarus, dead1)
        
        voice = a.getRoleID('Voice')
        producer = a.getRoleID('Producer')
        
        a.mapPersonAliasToRecordToRole(steven, damn, producer)
        a.mapPersonAliasToRecordToRole(steven, damn, voice)
        a.mapPersonAliasToRoleToSong(mikael, voice, lazarus)
    
    personAlias__role__song = personAlias_record_role
                    
    def compilation():
        a = makeAwithConnAndCur()
        bravo = a.insertArtist('Bravo Hits')
        rammstein = a.insertArtist('Rammstein')
        depeche = a.insertArtist('Depeche Mode')
        nodoubt = a.insertArtist('No Doubt')
        
        bravo16 = a.insertRecord('16')
        bravo17 = a.insertRecord('17')
        sehnsucht = a.insertRecord('Sehnsucht')
        ultra = a.insertRecord('Ultra')
        tragic = a.insertRecord('Tragic Kingdom')
        
        
        bravo16_1 = a.insertVolume(1, recordID=bravo16)
        bravo16_2 = a.insertVolume(2, recordID=bravo16)
        bravo17_1 = a.insertVolume(1, recordID=bravo17)
        bravo17_2 = a.insertVolume(2, recordID=bravo17)
        sehnsucht1 = a.insertVolume(1, recordID=sehnsucht)
        ultra1 = a.insertVolume(1, recordID=ultra)
        tragic1 = a.insertVolume(1, recordID=tragic)
        
        engel = a.insertSong('Engel')
        barrel = a.insertSong('Barrel Of A Gun')
        dont = a.insertSong("Don't Speak")
        nogood = a.insertSong("It's no good")

        a.mapArtistToRecord(rammstein, sehnsucht)
        a.mapArtistToRecord(depeche, ultra)
        a.mapArtistToRecord(nodoubt, tragic)
        a.mapArtistToRecord(bravo, bravo16)
        a.mapArtistToRecord(bravo, bravo17)
        
        a.mapSongToVolume(barrel, bravo16_1, 10)
        a.mapSongToVolume(dont, bravo16_2, 1)
        a.mapSongToVolume(nogood, bravo17_1, 10)
        a.mapSongToVolume(engel, bravo17_2, 3)

        a.mapSongToVolume(barrel, ultra1)
        a.mapSongToVolume(nogood, ultra1)
        a.mapSongToVolume(engel, sehnsucht1)
        a.mapSongToVolume(dont, tragic1)        
        
        a.cur.execute("""select a.name, r.name, v.number, sv.tracknumber, s.name from
          musicdb.artist as a,
          musicdb.record as r,
          musicdb.song as s, 
          musicdb.volume as v,
          musicdb.artist__record as ar,
          musicdb.song__volume as sv
        where a.id = ar.artist_id and ar.record_id = r.id and r.id = v.record_id and sv.volume_id = v.id and s.id = sv.song_id""")
        pprint.pprint(a.cur.fetchall())
    
    single = record__record
        
    def classicalMusic():
        pass
    
    def soundtrack():
        pass
    
    def score():
        pass
    
    personAlias__artist()
    artist__record()
    record__volume()
    record__record()
    song__volume()
    song__song()
    compilation()    
    personAlias_record_role()
 


"""
insert into musicdb.artist (name) values ('Rage Against The Machine');
insert into musicdb.record (name) values ('Rage Against The Machine');
insert into musicdb.artist__record(record_id, artist_id) values (
  (select id from musicdb.record where name = 'Rage Against The Machine'),
  (select id from musicdb.artist where name = 'Rage Against The Machine')
);
insert into volume (number, record_id) values (
  1,
  (select id from record where name = 'Rage Against The Machine')
);
insert into song (name) values ('Know Your Enemy');
insert into musicdb.song__volume (song_id, volume_id) values (
  (select id from musicdb.song where name = 'Know Your Enemy'),
  (select id from musicdb.volume where record_id = (
	select id from record where name = 'Rage Against The Machine'))
);

insert into person_alias__song__role (person_alias_id, song_id, role_id) values (
  (select id from musicdb.person_alias where name = 'Maynard James Keenan'),
  (select id from musicdb.song where name = 'Know Your Enemy'),
  (select id from musicdb.role where name = 'Voice')
);

select p.name||' spielt in '||s.name||' als '||r.name from
  musicdb.person_alias as p,
  musicdb.song as s,
  musicdb.role as r,
  musicdb.person_alias__song__role as psr
  where p.id = psr.person_alias_id and s.id = psr.song_id and r.id = psr.role_id;  
"""