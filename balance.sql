CREATE TABLE IF NOT EXISTS session
(
    id serial NOT NULL PRIMARY KEY,
    hash text NOT NULL,
    ts integer NOT NULL
)

CREATE TABLE IF NOT EXISTS balance
(
    id serial NOT NULL PRIMARY KEY,
    iduser integer NOT NULL,
    idoperation integer,
    ts integer,
    amount money,
    CONSTRAINT balance_pkey PRIMARY KEY (id)
)