pyinstaller ^
--noconfirm ^
--onedir ^
--windowed ^
--add-data "C:/Users/1589l/AppData/Local/Programs/Python/Python310/Lib/site-packages/customtkinter;customtkinter/" ^
--icon "%cd%/icon.ico" ^
--add-data "%cd%/icon.ico;."  "%cd%/app.pyw" ^
--add-data "%cd%/assets;assets/"

pause