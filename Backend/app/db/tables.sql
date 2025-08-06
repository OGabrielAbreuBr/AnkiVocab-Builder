-- Entidades Fortes

CREATE TABLE User (
  id               SERIAL PRIMARY KEY,
  first_name       VARCHAR(100)   NOT NULL,
  last_name        VARCHAR(255)   NOT NULL,
  username         VARCHAR(255)   NOT NULL UNIQUE,
  email            VARCHAR(255)   NOT NULL UNIQUE,
  password_hash    VARCHAR(255)   NOT NULL,
  created_at       TIMESTAMP      NOT NULL DEFAULT now(),
  updated_at       TIMESTAMP      NOT NULL DEFAULT now()
);

CREATE TABLE Languages (
  id               SERIAL PRIMARY KEY,
  code             VARCHAR(10)    NOT NULL UNIQUE,
  name             VARCHAR(50)    NOT NULL
);

CREATE TABLE DLanguageeck (
  id                       SERIAL PRIMARY KEY,
  name                     VARCHAR(255) NOT NULL,
  is_public                BOOLEAN      NOT NULL DEFAULT FALSE,
  created_at               TIMESTAMP     NOT NULL DEFAULT now(),
  updated_at               TIMESTAMP     NOT NULL DEFAULT now(),
  language_word_id         INTEGER      NOT NULL
    REFERENCES languages(id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  language_explanation_id  INTEGER      NOT NULL
    REFERENCES languages(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE Word (
  id            SERIAL PRIMARY KEY,
  text          VARCHAR(100) NOT NULL,
  meaning       TEXT         NOT NULL,
  example       TEXT,
  cefr          CHAR(2)      NOT NULL
                   CHECK (cefr IN ('A1','A2','B1','B2','C1','C2')),
  phonetic      VARCHAR(50),
  language_id   INTEGER      NOT NULL
                   REFERENCES languages(id)
                   ON UPDATE CASCADE ON DELETE RESTRICT,
  created_at    TIMESTAMP    NOT NULL DEFAULT now(),
  updated_at    TIMESTAMP    NOT NULL DEFAULT now()
);


-- Entidades Fracas

CREATE TABLE Audio (
  word_id       INTEGER    NOT NULL
                   REFERENCES words(id)
                   ON UPDATE CASCADE ON DELETE CASCADE,
  format        VARCHAR(10) NOT NULL,
  path          VARCHAR(255) NOT NULL,
  duration_secs REAL,
  created_at    TIMESTAMP    NOT NULL DEFAULT now(),
  updated_at    TIMESTAMP    NOT NULL DEFAULT now(),
  PRIMARY KEY (word_id)
);

CREATE TABLE Images (
  word_id      INTEGER     NOT NULL
                  REFERENCES words(id)
                  ON UPDATE CASCADE ON DELETE CASCADE,
  image_type   VARCHAR(50) NOT NULL,
  path         VARCHAR(255) NOT NULL,
  format       VARCHAR(10)  NOT NULL,
  creator      VARCHAR(255),
  created_at   TIMESTAMP     NOT NULL DEFAULT now(),
  updated_at   TIMESTAMP     NOT NULL DEFAULT now(),
  PRIMARY KEY (word_id)
);

-- Relacionamentos M:N (tabelas de junção)

CREATE TABLE User_decks (
  user_id  INTEGER NOT NULL
             REFERENCES users(id)
             ON UPDATE CASCADE ON DELETE CASCADE,
  deck_id  INTEGER NOT NULL
             REFERENCES decks(id)
             ON UPDATE CASCADE ON DELETE CASCADE,
  PRIMARY KEY (user_id, deck_id)
);

CREATE TABLE User_languages (
  user_id     INTEGER NOT NULL
                REFERENCES users(id)
                ON UPDATE CASCADE ON DELETE CASCADE,
  language_id INTEGER NOT NULL
                REFERENCES languages(id)
                ON UPDATE CASCADE ON DELETE CASCADE,
  PRIMARY KEY (user_id, language_id)
);

CREATE TABLE eck_words (
  deck_id  INTEGER NOT NULL
             REFERENCES decks(id)
             ON UPDATE CASCADE ON DELETE CASCADE,
  word_id  INTEGER NOT NULL
             REFERENCES words(id)
             ON UPDATE CASCADE ON DELETE CASCADE,
  PRIMARY KEY (deck_id, word_id)
);
