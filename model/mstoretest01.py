import psycopg2

class MStore(object):
    def setCursor(self, cursor):
        self.cur = cursor
    
    def addElement(self, name, isFolder, parentID=None, artistID=None, 
                recordID=None, volumeID=None, songID=None):
        # Check if the element already is in the db
        if parentID is None:
            self.cur.execute("""select id from mstore.element where name = %s 
            and parent_id is null""", (name,) )
        else:
            self.cur.execute("""select id from mstore.element where name = %(name)s 
            and parent_id = %(parent_id)s""", {'name': name, 'parent_id': parentID})
        
        res = self.cur.fetchone()
        if res:
            return res[0]
        
        # Check if more than one value is set
        b = (artistID is not None) + (recordID is not None) + \
          (volumeID is not None) + (songID is not None)
        if b > 1:
            raise ValueError('Only one id is allowed to be set')
        
        args = {
            'name': name,
            'is_folder': isFolder,
            'parent_id': parentID,
            'artist_id': artistID,
            'record_id': recordID,
            'volume_id': volumeID,
            'song_id': songID
        }
        self.cur.execute("""insert into mstore.element
        (name, is_folder, parent_id, artist_id, record_id, volume_id, song_id)
        values ( %(name)s, %(is_folder)s, %(parent_id)s, %(artist_id)s, %(record_id)s, %(volume_id)s, %(song_id)s )
        returning id""", args)
        return self.cur.fetchone()[0]
    

import os
class Importer(object):
    def setMStore(self, mstore):
        self.mstore = mstore
        
    def setMusicdb(self, musicdb):
        self.musicdb = musicdb
        
    def importFolderRecursive(self, path):
        """
        TODO: If /home/benjamin/meins is in the DB and you add
        /home/benjamin/meins/musicdb, musicdb is correctly recognized as already
        present. But if you add /home/karl/musicdb, it is wrongly found as /home/benjamin/meins/musicdb
        """
        dirname =  path.split(os.path.sep)[-1]
        root_id = self.mstore.addElement(dirname, True)
        
        # Cashing is required to avoid reselecting the ID of dirs when they are 
        # visited and the ID is required as parent id for the children
        dirIDCash = {path: root_id}
        
        for root, dirs, files in os.walk(path):
            parentID = dirIDCash[root]
            for d in dirs:
                dirID = self.mstore.addElement(d, True, parentID=parentID)
                dirIDCash[os.path.join(root, d)] = dirID
            
            for f in files:
                self.mstore.addElement(f, False, parentID=parentID)
                
    def getRecursive():
        """with recursive rec(name, is_folder, path, path_name, parent_id, id) as 
        (select el.name, el.is_folder, array[el.id], '/'||el.name, el.parent_id, el.id from mstore.element el where el.parent_id is null
        union all

        select el.name, el.is_folder, rec.path||array[el.id], rec.path_name||'/'||el.name, el.parent_id, el.id
        from mstore.element el, rec
        where el.parent_id = rec.id
        )
        select * from rec"""
        
    def importSong(self, path, musicBrainz_id):
        songId = self.musicdb.getByMusicbrainz('song', musicBrainz_id)
        if not songId:
            raise ValueError('No db entry found')
        self.model.addElement(name, False, song_id=song_id)
    


if __name__ == '__main__':
    print 'start'

    def makeModelWithConnAndCur():
        conn = psycopg2.connect(database='musicdb', user='musicdb')
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        m = MStore()
        m.setCursor(cur)
        return m

    m = makeModelWithConnAndCur()
    #print m.addElement('asdfasdf2.txt', False)
    i = Importer()
    i.setMStore(m)
    i.importFolderRecursive('/home/benjamin/music')
    print 'finish'
    
    