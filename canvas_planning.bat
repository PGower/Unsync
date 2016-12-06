ECHO off
python main.py ptf9_course_import -i source\timetable_planning.ptf9 -d ptf9_courses ^
               copy_columns -s ptf9_courses -d temp_courses -c Code -c Name ^
               rename_columns -s temp_courses -r Code course_id -r Name long_name ^
               copy_columns -s temp_courses -d courses -c course_id -c long_name ^
               fill_column -s courses -c short_name -v "course_id" ^
               fill_column -s courses -c status -v "'active'" ^
               regex_filter -s courses -m exclude -f course_id "^[BGLR]{1}[1-9]{1}$" ^
                                                  -f course_id "^GP-[0-9]{2}ACT.*$" ^
                                                  -f course_id "^ASM-.*$" ^
                                                  -f course_id "^.+QCS.+$" ^
                                                  -f course_id "^PAS-.*$" ^
                                                  -f course_id "^BREAK-.*$" ^
                                                  -f course_id "^[0-9]{2}ASM.*$" ^
                                                  -f course_id "^ACT$" ^
                                                  -f course_id "^[0-9]{2}ACT$" ^
                                                  -f course_id "^.+WRK.*$" ^
                                                  -f course_id "^[0-9]{2}WRK.*$" ^
                                                  -f course_id "^[0-9]{2}(STU|LAN).*$" ^
               print -s courses -n 5


