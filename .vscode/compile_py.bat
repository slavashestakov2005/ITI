set FileName=%1
if not x%FileName:main.py=%==x%FileName% (
    start cmd /k "py main.py & echo. & pause & exit"
)
