echo off
if not exist ..\\ITI (
    echo Folder ITI not found
    exit /b
)

if exist ..\\ITI\\backend\\data rmdir /s /q ..\\ITI\\backend\\data
if exist ..\\ITI\\backend\\templates rmdir /s /q ..\\ITI\\backend\\templates
mkdir ..\\ITI\\backend\\data
mkdir ..\\ITI\\backend\\templates

copy flask_app.py ..\\ITI\\flask_app.py
copy passenger_wsgi.py ..\\ITI\\passenger_wsgi.py
copy .env ..\\ITI\\.env
copy database.db ..\\ITI\\backend\\database.db
xcopy /s /e data ..\\ITI\\backend\\data
xcopy /s /e templates ..\\ITI\\backend\\templates

echo The files were copied
