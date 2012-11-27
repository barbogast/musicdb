-- psql --dbname=musicdb --username=musicdb --file=createdb3.sql
DROP SCHEMA musicdb CASCADE;
CREATE SCHEMA musicdb;




CREATE TABLE musicdb.person_alias
(
  id                serial,
  name              text NOT NULL,
  UNIQUE (name),
  PRIMARY KEY (id)
);

CREATE TABLE musicdb.artist
(
  id                serial,
  name              text NOT NULL,
  UNIQUE (name),
  PRIMARY KEY (id)
);

CREATE TABLE musicdb.artist__person_alias
(
  person_alias_id         integer,
  artist_id           integer,
  FOREIGN KEY (person_alias_id)
    REFERENCES musicdb.person_alias(id),
  FOREIGN KEY (artist_id)
    REFERENCES musicdb.artist(id),
  PRIMARY KEY (person_alias_id, artist_id)
);


CREATE TABLE musicdb.record
(
  id                serial,
  name              text NOT NULL,
  UNIQUE (name),
  PRIMARY KEY (id)
);

CREATE TABLE musicdb.artist__record
(
  record_id         integer,
  artist_id           integer,
  FOREIGN KEY (record_id)
    REFERENCES musicdb.record(id),
  FOREIGN KEY (artist_id)
    REFERENCES musicdb.artist(id),
  PRIMARY KEY (record_id, artist_id)
);



CREATE TABLE musicdb.volume
(
  id                serial,
  number			integer NOT NULL,
  name              text,
  record_id			integer,
  UNIQUE (name),
  PRIMARY KEY (id),
  FOREIGN KEY (record_id)
    REFERENCES musicdb.record(id)
);

CREATE TABLE musicdb.song
(
  id                serial,
  name              text NOT NULL,
  record_id			integer,
  variation_id		integer,
  PRIMARY KEY (id),
  FOREIGN KEY (variation_id)
    REFERENCES musicdb.song(id)
);

CREATE TABLE musicdb.song__volume
(
  song_id	         integer,
  volume_id           integer,
  FOREIGN KEY (song_id)
    REFERENCES musicdb.song(id),
  FOREIGN KEY (volume_id)
    REFERENCES musicdb.volume(id),
  PRIMARY KEY (song_id, volume_id)
);

CREATE TABLE musicdb.role
(
  id                serial,
  name              text NOT NULL,
  UNIQUE (name),
  PRIMARY KEY (id)
);
insert into musicdb.role (name) values ('First guitar');
insert into musicdb.role (name) values ('Second guitar');
insert into musicdb.role (name) values ('Drums');
insert into musicdb.role (name) values ('Voice');


CREATE TABLE musicdb.person_alias__song__role
(
  person_alias_id	integer,
  song_id           integer,
  role_id			integer,
  FOREIGN KEY (person_alias_id)
    REFERENCES musicdb.person_alias(id),
  FOREIGN KEY (song_id)
    REFERENCES musicdb.song(id),
  FOREIGN KEY (role_id)
    REFERENCES musicdb.role(id),
  PRIMARY KEY (person_alias_id, song_id, role_id)
);







