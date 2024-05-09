-- Discharge data
-- TODO: Add the new columns (summarised)
CREATE TABLE public.discharge_data (
    note_id character varying(15) NOT NULL,
    subject_id character varying(8) NOT NULL,
    hadm_id character varying(8) NOT NULL,
    note_type character(2) NOT NULL,
    note_seq numeric(3, 0) NOT NULL,
    charttime date,
    storetime date,
    text text NOT NULL,
    name text,
    dob date,
    complaint text NOT NULL,
    patient_sex character varying(6) NOT NULL,
    PRIMARY KEY (note_id)
);

-- Radiology data
CREATE TABLE public.radiology_data (
    note_id character varying(15) NOT NULL,
    subject_id character varying(8) NOT NULL,
    hadm_id double precision,
    note_type character varying(5) NOT NULL,
    note_seq integer NOT NULL,
    charttime date,
    storetime date,
    text text,
    examination text NOT NULL,
    summarised text NOT NULL
);
