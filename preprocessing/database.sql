CREATE TABLE public.discharge_data(
    note_id character varying(15) NOT NULL,
    subject_id character varying(8) NOT NULL,
    hadm_id character varying(8) NOT NULL,
    note_type character(2) NOT NULL,
    note_seq numeric(3, 0) NOT NULL,
    charttime date ,
    storetime date ,
    text text NOT NULL,
    PRIMARY KEY (note_id)
);

CREATE TABLE public.radiology_data (
    note_id character varying(15) NOT NULL PRIMARY KEY,
    subject_id character varying(8) NOT NULL,
    hadm_id FLOAT,
    note_type character varying(5)  NOT NULL,
    note_seq INT NOT NULL,
    charttime date,
    storetime date,
    text TEXT
);
