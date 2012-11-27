-- psql --dbname=musicdb --username=musicdb --file=createdb.sql
DROP SCHEMA musicdb CASCADE;
CREATE SCHEMA musicdb;




CREATE TABLE musicdb.person_alias
(
  id                serial NOT NULL,
  name              text NOT NULL,
  UNIQUE (name),
  PRIMARY KEY (id)
);

CREATE TABLE musicdb.artist
(
  id                serial NOT NULL,
  name              text NOT NULL,
  UNIQUE (name),
  PRIMARY KEY (id)
);

CREATE TABLE musicdb.artist__person_alias
(
  person_alias_id         integer NOT NULL,
  artist_id           integer NOT NULL,
  FOREIGN KEY (person_alias_id)
    REFERENCES musicdb.person_alias(id),
  FOREIGN KEY (artist_id)
    REFERENCES musicdb.artist(id),
  PRIMARY KEY (person_alias_id, artist_id)
);




insert into musicdb.person_alias (name) values ('Maynard James Keenan');
insert into musicdb.person_alias (name) values ('James Iha');
insert into musicdb.artist (name) values ('Tool');
insert into musicdb.artist (name) values ('A Perfect Circle');
insert into musicdb.artist (name) values ('Smashing Pumpkins');

insert into musicdb.artist__person_alias (artist_id, person_alias_id) values (
  (select id from musicdb.artist where name = 'Tool'),
  (select id from musicdb.person_alias where name = 'Maynard James Keenan')
);

insert into musicdb.artist__person_alias (artist_id, person_alias_id) values (
  (select id from musicdb.artist where name = 'A Perfect Circle'),
  (select id from musicdb.person_alias where name = 'Maynard James Keenan')
);

insert into musicdb.artist__person_alias (artist_id, person_alias_id) values (
  (select id from musicdb.artist where name = 'A Perfect Circle'),
  (select id from musicdb.person_alias where name = 'James Iha')
);

insert into musicdb.artist__person_alias (artist_id, person_alias_id) values (
  (select id from musicdb.artist where name = 'Smashing Pumpkins'),
  (select id from musicdb.person_alias where name = 'James Iha')
);

select b.name, count(*) from 
	musicdb.person_alias as p, 
	musicdb.artist as b, 
	musicdb.artist__person_alias as pb
where pb.artist_id = b.id and pb.person_alias_id = p.id
group by b.name;


select p.name || ' spielt in ' || b.name as artistmembers from 
musicdb.person_alias as p, 
musicdb.artist as b, 
musicdb.artist__person_alias as pb
 where (b.id = pb.artist_id and p.id = pb.person_alias_id);  
  
  
  

CREATE TABLE musicdb.record
(
  id                serial NOT NULL,
  name              text NOT NULL,
  UNIQUE (name),
  PRIMARY KEY (id)
);

CREATE TABLE musicdb.artist__record
(
  record_id         integer NOT NULL,
  artist_id           integer NOT NULL,
  FOREIGN KEY (record_id)
    REFERENCES musicdb.record(id),
  FOREIGN KEY (artist_id)
    REFERENCES musicdb.artist(id),
  PRIMARY KEY (record_id, artist_id)
);


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

select p.name || ' spielt als Band ' || a.name || ' das Album ' || r.name from
  musicdb.person_alias as p,
  musicdb.artist as a,
  musicdb.record as r,
  musicdb.artist__person_alias as ap,
  musicdb.artist__record as ar
where r.id = ar.record_id and a.id = ar.artist_id and a.id = ap.artist_id and p.id = ap.person_alias_id;



CREATE TABLE musicdb.volume
(
  id                serial NOT NULL,
  number			integer NOT NULL,
  name              text,
  record_id			integer,
  UNIQUE (name),
  PRIMARY KEY (id),
  FOREIGN KEY (record_id)
    REFERENCES musicdb.record(id)
);

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




CREATE TABLE musicdb.song
(
  id                serial NOT NULL,
  name              text NOT NULL,
  record_id			integer,
  UNIQUE (name),
  PRIMARY KEY (id)
);

CREATE TABLE musicdb.song__volume
(
  song_id	         integer NOT NULL,
  volume_id           integer NOT NULL,
  FOREIGN KEY (song_id)
    REFERENCES musicdb.song(id),
  FOREIGN KEY (volume_id)
    REFERENCES musicdb.volume(id),
  PRIMARY KEY (song_id, volume_id)
);

insert into musicdb.song (name) values ('The Ecstasy of Gold');
insert into musicdb.song (name) values ('The Call of Ktulu');
insert into musicdb.song (name) values ('Nothing Else Matters');
insert into musicdb.song (name) values ('Until It Sleeps');