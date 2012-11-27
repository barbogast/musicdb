import psycopg2

#conn = psycopg2.connect(database='musicdb', user='musicdb')
#cur = conn.cursor()
#cur.execute('insert into musicdb.person_alias (name) values (%s) returning id', ('Maynard James Keenan435',))

#cur = conn.cursor()
#cur.execute('select id from musicdb.person_alias where name = %s', ('Maynard James Keenan435', ))
##print cur.mogrify('select id from musicdb.person_alias where name = %s', ('Maynard James Keenan', ))
#print cur.fetchone()[0]
#conn.rollback()

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
    def getPersonID(self, cur, name):
        cur.execute("select id from musicdb.person_alias where name = %s", (name, ))
        if cur.rowcount != 1:
            return None
        return cur.fetchone()[0]

    def getArtistID(self, cur, name):
        cur.execute("select id from musicdb.artist where name = %s", (name, ))
        if cur.rowcount != 1:
            return None
        return cur.fetchone()[0]
    
    def insertPersonAlias(self, cur, name):
        cur.execute("insert into musicdb.person_alias (name) values (%s) returning id", (name,))
        res = cur.fetchone()[0]
        return res
        
    def insertArtist(self, cur, name):
        cur.execute("insert into musicdb.artist (name) values (%s) returning id", (name,))
        return cur.fetchone()[0]
    
    def insertRecord(self, cur, name):
        cur.execute("insert into musicdb.record (name) values (%s) returning id", (name,))
        return cur.fetchone()[0]

       
    def mapPersonAliasToArtist(self, cur, artistID, personAliasID):
        args = {'artist_id': artistID, 'person_alias_id': personAliasID}
        cur.execute("""insert into musicdb.artist__person_alias 
        (artist_id, person_alias_id) values (%(artist_id)s, %(person_alias_id)s)""", args)
        
        
    def mapArtistToRecord(self, cur, artistID, recordID):
        args = {'artist_id': artistID, 'record_id': recordID}
        cur.execute("""insert into musicdb.artist__record
        (artist_id, record_id) values (%(artist_id)s, %(record_id)s)""", args)


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
        isID = A().insertPersonAlias(cur, name)
        cur.execute("select id from musicdb.person_alias where name = %s", (name,))
        shouldBeID = cur.fetchone()[0]
        self.assertEqual(isID, shouldBeID)
        
    def test_insertArtist(self):
        name = 'test_insertArtist'
        cur = self.conn.cursor()
        isID = A().insertArtist(cur, name)
        cur.execute("select id from musicdb.artist where name = %s", (name,))
        shouldBeID = cur.fetchone()[0]
        self.assertEqual(isID, shouldBeID)
        
    def test_mapPersonAliasToArtist(self):
        cur = self.conn.cursor()
        artistID = A().insertArtist(cur, 'testArtist')
        personID = A().insertPersonAlias(cur, 'testPerson')
        A().mapArtistToPersonAlias(cur, artistID, personID)
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
    def personAlias__artist():
        conn = psycopg2.connect(database='musicdb', user='musicdb')
        cur = conn.cursor()
        
        maynard = A().insertPersonAlias(cur, 'Maynard James Keenan')
        james = A().insertPersonAlias(cur, 'James Iha')
        
        tool = A().insertArtist(cur, 'Tool')
        circle = A().insertArtist(cur, 'A Perfect Circle')
        pumpkins = A().insertArtist(cur, 'Smashing Pumpkins')
        
        A().mapPersonAliasToArtist(cur, maynard, tool)
        A().mapPersonAliasToArtist(cur, maynard, circle)
        A().mapPersonAliasToArtist(cur, james, circle)
        A().mapPersonAliasToArtist(cur, james, pumpkins)

        cur.execute("""
        select a.name, count(*) from 
        musicdb.person_alias as p, 
        musicdb.artist as a, 
        musicdb.artist__person_alias as pb
        where pb.artist_id = a.id and pb.person_alias_id = p.id
        group by a.name""")
        pprint.pprint( cur.fetchall() )
        
        cur.execute("""
        select p.name || ' spielt in ' || b.name as artistmembers from 
        musicdb.person_alias as p, 
        musicdb.artist as b, 
        musicdb.artist__person_alias as pb
        where (b.id = pb.artist_id and p.id = pb.person_alias_id) """)
        pprint.pprint( cur.fetchall())
        
    def artist__record():
        conn = psycopg2.connect(database='musicdb', user='musicdb')
        cur = conn.cursor()
        metallica = A().insertArtist(cur, 'Metallica')
        symphony = A().insertArtist(cur, 'San Francisco Symphony')
        sm = A().insertRecord(cur, 'S&M')
        A().mapArtistToRecord(cur, metallica, sm)
        A().mapArtistToRecord(cur, symphony, sm)
    personAlias__artist()

"""
insert into musicdb.record (name) values ('Thirteenth Step');
insert into musicdb.artist__record(record_id, artist_id) values (
  (select id from musicdb.record where name = 'Thirteenth Step'),
  (select id from musicdb.artist where name = 'A Perfect Circle')
);

insert into musicdb.record (name) values ('S&M');
insert into musicdb.artist (name) values ('Metallica');
insert into musicdb.artist (name) values ('San Francisco Symphony');
insert into musicdb.artist__record(record_id, artist_id) values (
  (select id from musicdb.record where name = 'S&M'),
  (select id from musicdb.artist where name = 'Metallica')
);  
insert into musicdb.artist__record(record_id, artist_id) values (
  (select id from musicdb.record where name = 'S&M'),
  (select id from musicdb.artist where name = 'San Francisco Symphony')
);  

select a.name || ' spielt ' || r.name from 
  musicdb.record as r,
  musicdb.artist as a,
  musicdb.artist__record as ar
where r.id = ar.record_id and a.id = ar.artist_id;

select p.name || ' spielt in Band ' || a.name || ' das Album ' || r.name from
  musicdb.person_alias as p,
  musicdb.artist as a,
  musicdb.record as r,
  musicdb.artist__person_alias as ap,
  musicdb.artist__record as ar
where r.id = ar.record_id and a.id = ar.artist_id and a.id = ap.artist_id and p.id = ap.person_alias_id;
"""

"""
insert into musicdb.volume(number, name, record_id) values (
  1,
  'One',
  (select id from musicdb.record where name = 'S&M')
);

insert into musicdb.volume(number, name, record_id) values (
  2,
  'Two',
  (select id from musicdb.record where name = 'S&M')
);
"""

"""
insert into musicdb.song (name) values ('The Ecstasy of Gold');
insert into musicdb.song (name) values ('The Call of Ktulu');
insert into musicdb.song (name) values ('Nothing Else Matters (live)');
insert into musicdb.song (name) values ('Until It Sleeps');

insert into musicdb.song__volume(song_id, volume_id) values (
  (select id from musicdb.song where name = 'The Ecstasy of Gold'),
  (select id from musicdb.volume where number = 1)
);
insert into musicdb.song__volume(song_id, volume_id) values (
  (select id from musicdb.song where name = 'The Call of Ktulu'),
  (select id from musicdb.volume where number = 1)
);  
insert into musicdb.song__volume(song_id, volume_id) values (
  (select id from musicdb.song where name = 'Nothing Else Matters (live)'),
  (select id from musicdb.volume where number = 2)
);
insert into musicdb.song__volume(song_id, volume_id) values (
  (select id from musicdb.song where name = 'Until It Sleeps'),
  (select id from musicdb.volume where number = 2)
);

select 'The volume '||v.name||' of the record '||r.name||' from '||a.name||' contains the song '||s.name from
  musicdb.artist as a,
  musicdb.record as r,
  musicdb.volume as v,
  musicdb.song as s,
  musicdb.artist__record as ar,
  musicdb.song__volume as sv
  where a.id = ar.artist_id and ar.record_id = r.id and r.id = v.record_id and v.id = sv.volume_id and sv.song_id = s.id
  order by v.name;
  
insert into musicdb.record (name) values ('Metallica');
insert into musicdb.artist__record (artist_id, record_id) values (
  (select id from musicdb.artist where name = 'Metallica'),
  (select id from musicdb.record where name = 'Metallica')
);
insert into volume (number, record_id) values (
  1,
  (select id from musicdb.record where name = 'Metallica')
);
insert into song (name) values ('Nothing Else Matters');
insert into song__volume (song_id, volume_id) values (
  (select id from musicdb.song where name = 'Nothing Else Matters'),
  (select id from musicdb.volume where record_id = 
	(select id from musicdb.record where name = 'Metallica'))
);

select 'Das Lied '||s.name||' von der CD Nr '||v.number||' des Albums '||r.name||' ist von '||a.name from
  musicdb.artist as a,
  musicdb.record as r,
  musicdb.volume as v,
  musicdb.song as s,
  musicdb.artist__record as ar,
  musicdb.song__volume as sv
  where a.id = ar.artist_id and ar.record_id = r.id and r.id = v.record_id and v.id = sv.volume_id and sv.song_id = s.id
  order by s.name;  

update musicdb.song set variation_id = 
  (select id from musicdb.song where name = 'Nothing Else Matters')
where name = 'Nothing Else Matters (live)';

select s2.name||' ist eine Variation von '||s1.name 
  from musicdb.song as s1, musicdb.song as s2
  where s1.id = s2.variation_id;
"""

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