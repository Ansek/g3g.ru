USE flask_db;

INSERT INTO public."user" (id, login, "password", telephone, email, is_admin)
VALUES(nextval('user_id_seq'::regclass), 'admin', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', '9211234567', 'admin@mail.ru', true);