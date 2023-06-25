rem Программа по созданию директории с именем в формате текущей даты

rem В переменной directory указать путь к директории, в которой следует создавать папки по датам
set directory=E:\Test\

rem Основная программа
set directory_name=%DATE:~-4%_%DATE:~3,2%_%DATE:~0,2%
mkdir %directory%%directory_name%
