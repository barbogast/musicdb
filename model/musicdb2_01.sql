-- psql --dbname=musicdb --username=musicdb --file=createdb5.sql
-- postgresql_autodoc -d musicdb
-- dot -Tpng -o musicdb.png musicdb.dot

DROP SCHEMA musicdb CASCADE;
CREATE SCHEMA musicdb;


CREATE TABLE musicdb.artist (
  id                serial,
  name              text NOT NULL,
  UNIQUE (name),
  PRIMARY KEY (id)
);

CREATE TABLE musicdb.record (
  id                serial,
  name              text NOT NULL,
  edition_id        int
    REFERENCES musicdb.record(id),
  PRIMARY KEY (id)   
);
COMMENT ON COLUMN musicdb.record.edition_id IS 'This id points to another tuple
of record. It allows to connect different versions of a record ("Deluxe Version")';


CREATE TABLE musicdb.volume (
  id                serial,
  number			int NOT NULL,
  name              text,
  record_id			int
    REFERENCES musicdb.record(id),
  PRIMARY KEY (id),
  UNIQUE (name),
  UNIQUE(number, record_id)
);

CREATE TABLE musicdb.song (
  id                serial,
  name              text NOT NULL,
  record_id			int,
  variation_id		int
    REFERENCES musicdb.song(id),
  PRIMARY KEY (id)  
);
COMMENT ON COLUMN musicdb.song.variation_id IS 'This id points to another tuple
of song. It allows to connect different versions of a song (Live, Covers, ...)';


CREATE TABLE musicdb.song_map (
  song_id           int
    REFERENCES musicdb.song(id),
  volume_id         int
    REFERENCES musicdb.volume(id),
  record_id         int
    REFERENCES musicdb.record(id),
  artist_id         int
    REFERENCES musicdb.artist(id)
);
    

CREATE TABLE musicdb.person_alias
(
  id                serial,
  name              text NOT NULL,
  UNIQUE (name),
  PRIMARY KEY (id)
);


CREATE TABLE musicdb.role
(
  id                serial,
  name              text NOT NULL,
  UNIQUE (name),
  PRIMARY KEY (id)
);
insert into musicdb.role (name) values ('Guitar');
insert into musicdb.role (name) values ('Drums');
insert into musicdb.role (name) values ('Voice');
insert into musicdb.role (name) values ('Producer');


CREATE TABLE musicdb.person_alias__record__role
(
  person_alias_id	int
    REFERENCES musicdb.person_alias(id),
  record_id           int
    REFERENCES musicdb.record(id),
  role_id			int
    REFERENCES musicdb.role(id),
  PRIMARY KEY (person_alias_id, record_id, role_id)
);

CREATE TABLE musicdb.person_alias__role__song
(
  person_alias_id	int
    REFERENCES musicdb.person_alias(id),
  song_id           int
    REFERENCES musicdb.song(id),
  role_id			int
    REFERENCES musicdb.role(id),
  PRIMARY KEY (person_alias_id, song_id, role_id)
);

CREATE TABLE musicdb.artist__person_alias__role
(
  person_alias_id    int
    REFERENCES musicdb.person_alias(id),
  artist_id          int
    REFERENCES musicdb.artist(id),
  role_id            int
    REFERENCES musicdb.role(id),
  PRIMARY KEY (person_alias_id, artist_id, role_id)
);





