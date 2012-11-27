-- psql --dbname=musicdb --username=musicdb --file=createdb.sql
DROP SCHEMA musicdb CASCADE;
CREATE SCHEMA musicdb;


CREATE TABLE musicdb.artist
(
  id                serial NOT NULL,
  name              text NOT NULL,
  UNIQUE (name),
  PRIMARY KEY (id)
);


CREATE TABLE musicdb.album
(
  id                serial NOT NULL,
  artist_id         integer,
  name              text NOT NULL,
  release_date      timestamp,
  UNIQUE (name),
  PRIMARY KEY (id),
  FOREIGN KEY (artist_id) 
    REFERENCES musicdb.artist(id)
);


CREATE TABLE musicdb.song
(
  id                serial NOT NULL,
  artist_id         integer,
  album_id          integer,
  name              text NOT NULL,
  UNIQUE (name),
  PRIMARY KEY (id),
  FOREIGN KEY (artist_id) 
    REFERENCES musicdb.artist(id),
  FOREIGN KEY (album_id) 
    REFERENCES musicdb.album(id)
);



CREATE TABLE musicdb.folder
(
  id                serial NOT NULL,
  artist_id         integer,
  album_id          integer,
  path              text NOT NULL,
  UNIQUE (path),
  PRIMARY KEY (id),
  FOREIGN KEY (artist_id) 
    REFERENCES musicdb.artist(id),
  FOREIGN KEY (album_id) 
    REFERENCES musicdb.album(id)
);

CREATE TABLE musicdb.file
(
  id                serial NOT NULL,
  name              text NOT NULL,
  folder_id         integer NOT NULL,
  song_id           integer,
  hash              text NOT NULL,
  UNIQUE (hash),
  UNIQUE (folder_id, name),
  PRIMARY KEY (id),
  FOREIGN KEY (folder_id)
    REFERENCES musicdb.folder(id),
  FOREIGN KEY (song_id)
    REFERENCES musicdb.song(id)
);


--------
-- artist
insert into musicdb.artist (name) values ('Tool');

-- album
insert into musicdb.album (name) values ('Tales of the Inexpressible');

--album with artist
insert into musicdb.album (artist_id, name) values (
  (select id from musicdb.artist where name = 'Tool'),
  'Lateralus'
);

-- song
insert into musicdb.song (name) values ('Castleriggs');
  
-- song with artist and album
insert into musicdb.song (name, artist_id, album_id) values (
  'Schism',
  (select id from musicdb.artist where name = 'Tool'),
  (select id from musicdb.album where name = 'Lateralus')
);

-- song with artist
insert into musicdb.song (name, artist_id) values (
  'Opiate',
  (select id from musicdb.artist where name = 'Tool')
);
  
-- song with album
insert into musicdb.song (name, album_id) values (
  'Star Shpongled Banner',
  (select id from musicdb.album where name = 'Tales of the Inexpressible')
);

-- folder
insert into musicdb.folder (path) values ('/home/benjamin/music/Iona/Open sky');

-- folder with artist
insert into musicdb.folder(path, artist_id) values (
  '/home/benjamin/music/Tool',
  (select id from musicdb.artist where name = 'Tool')
);
  
-- folder with album
insert into musicdb.folder(path, album_id) values (
  '/home/benjamin/music/Shpongle/Tales of the Inexpressible',
  (select id from musicdb.album where name = 'Tales of the Inexpressible')
);
  
-- folder with artist and album
insert into musicdb.folder(path, artist_id, album_id) values (
  '/home/benjamin/music/Tool/Lateralus',
  (select id from musicdb.artist where name = 'Tool'),
  (select id from musicdb.album where name = 'Lateralus')
);
  
-- file
insert into musicdb.file(name, folder_id, hash) values (
  'Iona - Castlerigg.mp3',
  (select id from musicdb.folder where path = '/home/benjamin/music/Iona/Open sky'),
    '45KJK43KJ34KJ#4'
);

-- file with song
insert into musicdb.file(name, folder_id, song_id, hash) values (
  'Tool - Schism.mp3',
  (select id from musicdb.folder where path = '/home/benjamin/music/Shpongle/Tales of the Inexpressible'),
  (select id from musicdb.song where name = 'Star Shpongled Banner'),
  '45KJK43KJ34KJ#5'
);
  

