SET APP_SETTINGS=config.ProductionConfig
SET SECRET_KEY="\x00\x1e\xa2\x0f\xcbs&\xad\xc8\xa6q[\xee\xcc.\xa7oG7&\xac\xdfh\xa1"
SET DATABASE_URL=postgresql://seller:123@127.0.0.1/flask_db

python -m venv flask_env
call flask_env\Scripts\activate.bat
pip install -r requirements\development.txt
python manage.py run --debug
call flask_env\Scripts\deactivate.bat
pause

