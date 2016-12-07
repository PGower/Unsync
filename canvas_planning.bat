ECHO off
python main.py ptf9_course_import -i source\timetable_planning.ptf9 -d ptf9_courses ^
               petl_cut -s ptf9_courses --field Code --field Name ^
               petl_rename -s ptf9_courses -t Code course_id -t Name long_name ^
               petl_searchcomplement -s ptf9_courses -f course_id "^[BGLR]{1}[1-9]{1}$" ^
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
               csv_import -i merged_courses_source.csv -d merge_data ^
               canvas_merge_courses --courses ptf9_courses --merge-data merge_data ^
               csv_import -i account_lookup_source.csv -d account_lookup_data ^
               canvas_course_account_lookup --courses ptf9_courses --account-data account_lookup_data ^
               petl_tail -s ptf9_courses -n 30 ^
               utils_print -s ptf9_courses ^
               utils_stats -s ptf9_courses




