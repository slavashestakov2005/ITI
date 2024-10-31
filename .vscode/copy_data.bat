if not exist ..\\ITI-data (
    ..\\ITI-data
    cd ..
    cd ITI-data
    git init
    cd ..
    cd ITI
)

if exist ..\\ITI-data\\data rmdir /s /q ..\\ITI-data\\data
if exist ..\\ITI-data\\templates rmdir /s /q ..\\ITI-data\\templates
mkdir ..\\ITI-data\\data
mkdir ..\\ITI-data\\templates

copy flask_app.py ..\\ITI-data\\flask_app.py
copy passenger_wsgi.py ..\\ITI-data\\passenger_wsgi.py
copy .env ..\\ITI-data\\.env
copy backend\\database.db ..\\ITI-data\\database.db
xcopy /s /e backend\\data ..\\ITI-data\\data
xcopy /s /e backend\\templates ..\\ITI-data\\templates
