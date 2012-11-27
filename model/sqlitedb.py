import sqlite3

createSQL = [                       
"""CREATE TABLE person_alias
(
  id                serial NOT NULL,
  name              text NOT NULL,
  UNIQUE (name),
  PRIMARY KEY (id)
);""",

"""CREATE TABLE band
(
  id                serial NOT NULL,
  name              text NOT NULL,
  UNIQUE (name),
  PRIMARY KEY (id)
);""",

"""CREATE TABLE person_alias_band
(
  id_person_alias   integer REFERENCES person_alias,
  id_band           integer REFERENCES band,
  PRIMARY KEY (id_person_alias, id_band)
);""",
]
     
     
conn = sqlite3.connect('test_01.db')
c = conn.cursor()


for stmt in createSQL:
    print c.execute(stmt)
    
conn.commit()
c.close()

conn.close()