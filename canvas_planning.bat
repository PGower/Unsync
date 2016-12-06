ECHO off
python main.py ptf9_course_import -i source\timetable_planning.ptf9 -d ptf9_courses ^
               regex_filter -s ptf9_courses -m exclude -f course_id "^[BGLR]{1}[1-9]{1}$" ^
                                                  -f Code "^GP-[0-9]{2}ACT.*$" ^
                                                  -f Code "^ASM-.*$" ^
                                                  -f Code "^.+QCS.+$" ^
                                                  -f Code "^PAS-.*$" ^
                                                  -f Code "^BREAK-.*$" ^
                                                  -f Code "^[0-9]{2}ASM.*$" ^
                                                  -f Code "^ACT$" ^
                                                  -f Code "^[0-9]{2}ACT$" ^
                                                  -f Code "^.+WRK.*$" ^
                                                  -f Code "^[0-9]{2}WRK.*$" ^
                                                  -f Code "^[0-9]{2}(STU|LAN).*$" ^
               copy_columns -s ptf9_courses -d temp_courses -c Code -c Name ^
               rename_columns -s temp_courses -r Code course_id -r Name long_name ^
               copy_columns -s temp_courses -d courses -c course_id -c long_name ^
               fill_column -s courses -c short_name -v "course_id" ^
               fill_column -s courses -c status -v "'active'" ^

               csv_import -i account_lookup_table.csv -d account_lookup_table ^
               print -s account_lookup_table -n 5


