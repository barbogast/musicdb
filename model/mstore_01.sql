-- psql --dbname=musicdb --username=musicdb --file=createdb5.sql
-- postgresql_autodoc -d musicdb
-- dot -Tpng -o musicdb.png musicdb.dot

drop schema mstore cascade;
create schema mstore;

create table mstore.element (
  id                serial,
  name              text not null,
  is_folder         boolean,
  parent_id         int
    references mstore.element(id),
  unique (name, parent_id),
  primary key (id),
  
  artist_id         int
    references musicdb.artist(id),
  record_id         int
    references musicdb.record(id),
  volume_id         int
    references musicdb.volume(id),
  song_id           int
    references musicdb.song(id)
);
