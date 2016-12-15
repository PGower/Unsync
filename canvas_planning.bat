ECHO off
REM REM What does this do?
REM REM Imports all of the courses from a ptf9 file.
REM REM Removes any course that has an ID that matches an ignored course ()
REM python main.py ptf9_course_import -i source\timetable_planning.ptf9 -d ptf9_courses ^
REM                petl_cut -s ptf9_courses --field Code --field Name --field ClassID^
REM                petl_rename -s ptf9_courses -t Code course_id -t Name long_name -t ClassID ptf9_id ^
REM                petl_searchcomplement -s ptf9_courses -f course_id "^[BGLR]{1}[1-9]{1}$" ^
REM                                                      -f course_id "^GP-[0-9]{2}ACT.*$" ^
REM                                                      -f course_id "^ASM-.*$" ^
REM                                                      -f course_id "^.+QCS.+$" ^
REM                                                      -f course_id "^PAS-.*$" ^
REM                                                      -f course_id "^BREAK-.*$" ^
REM                                                      -f course_id "^[0-9]{2}ASM.*$" ^
REM                                                      -f course_id "^ACT$" ^
REM                                                      -f course_id "^[0-9]{2}ACT$" ^
REM                                                      -f course_id "^.+WRK.*$" ^
REM                                                      -f course_id "^[0-9]{2}WRK.*$" ^
REM                                                      -f course_id "^[0-9]{2}(STU|LAN).*$" ^
REM                csv_import -i source\merged_courses_source.csv -d merge_data ^
REM                canvas_merge_courses --courses ptf9_courses --merge-data merge_data ^
REM                csv_import -i source\account_lookup_source.csv -d account_lookup_data ^
REM                canvas_course_account_lookup --courses ptf9_courses --account-data account_lookup_data ^
REM                csv_import -i source\lifecycle_defaults.csv -d lifecycle_defaults ^
REM                csv_import -i source\lifecycle_mappings.csv -d lifecycle_mappings ^
REM                canvas_add_course_lifecycle_type --courses ptf9_courses ^
REM                csv_import -i source\enrollment_defaults.csv -d enrollment_defaults ^
REM                csv_import -i source\enrollment_mappings.csv -d enrollment_mappings ^
REM                canvas_add_course_enrollment_type --courses ptf9_courses ^
REM                petl_addfield -s ptf9_courses -f short_name -v "{course_id}" ^
REM                petl_addfield -s ptf9_courses -f old_course_id -v "{course_id}" ^
REM                csv_import -i source\time_periods.csv -d terms ^
REM                canvas_generate_full_course_ids --courses ptf9_courses --terms terms --target-date "2017-01-25T00:00:00" ^
REM                petl_cutout -s ptf9_courses --field ptf9_id ^
REM                petl_addfield -s ptf9_courses --field status --value "'active'" ^
REM                csv_export -o generated_courses.csv -s ptf9_courses ^
REM                csv_export -o removed_courses.csv -s removed_merged_course_data
REM 
REM REM Prepare enrollments for processing, staff and students enrollments are stored differently. Make them the same and update identifiers.
REM python main.py ptf9_student_enrollment_import -i source\timetable_planning.ptf9 -d ptf9_student_enrollments ^
REM                ptf9_student_import -i source\timetable_planning.ptf9 -d temp_ptf9_students ^
REM                ptf9_staff_enrollment_import -i source\timetable_planning.ptf9 -d ptf9_staff_enrollments ^
REM                ptf9_course_import -i source\timetable_planning.ptf9 -d temp_ptf9_courses ^
REM                ptf9_staff_import -i source\timetable_planning.ptf9 -d temp_ptf9_staff ^
REM                csv_import -i source\teacher_id_map.csv -d teacher_id_map ^
REM                csv_import -i source\extra_enrollments.csv -d extra_enrollments ^
REM                canvas_prep_student_enrollments --ptf9-enrollments ptf9_student_enrollments --ptf9-students temp_ptf9_students --destination student_enrollments ^
REM                canvas_prep_staff_enrollments --ptf9-enrollments ptf9_staff_enrollments --ptf9-staff temp_ptf9_staff --ptf9-courses temp_ptf9_courses --teacher-id-map teacher_id_map --destination staff_enrollments ^
REM                petl_cat -s student_enrollments -s staff_enrollments -s extra_enrollments -d combined_enrollments ^
REM                petl_addfield -s combined_enrollments -f status -v "'active'" ^
REM                csv_export -s combined_enrollments -o processed_enrollments.csv

REM Process enrollments, change identifiers as required.
REM python main.py csv_import -i processed_enrollments.csv -d enrollments ^
REM                csv_import -i generated_courses.csv -d courses ^
REM                csv_import -i removed_courses.csv -d merged_courses ^
REM                csv_import -i source\time_periods.csv -d terms ^
REM                canvas_process_enrollments --enrollments enrollments --courses courses --merged-courses merged_courses --terms terms --target-date "2017-01-25T00:00:00" ^
REM                csv_export -o generated_enrollments.csv -s enrollments

REM Using the generated enrollments create appropriate sections
REM python main.py csv_import -i generated_enrollments.csv -d enrollments ^
REM                petl_cut -s enrollments -d sections --field course_id --field section_id ^
REM                petl_distinct -s sections --key section_id ^
REM                petl_addfield -s sections --field status --value "'active'" ^
REM                petl_addfield -s sections --field name --value "{section_id}.replace('_', ' ').replace(' COMBINED', '_COMBINED').replace(' 2017', '')" ^
REM                csv_export -s sections -o generated_sections.csv

REM Get users from LDAP and then filter based on enrollments.
REM TODO: Relief Teachers
python main.py ldap_import --server 10.192.11.56 ^
                           --user "CN=SMC Canvas Service Account,OU=Service Accounts,OU=SMC,OU=Resources,DC=cairns,DC=catholic,DC=edu,DC=au" ^
                           --password "5alM0n5wiM" ^
                           --base-ou "OU=SMC,OU=Automated Objects,DC=cairns,DC=catholic,DC=edu,DC=au" ^
                           --query "(objectClass=user)" ^
                           -a sAMAccountName -a mail -a givenName -a sn -a employeeID -d ldap_users ^
               petl_rename -s ldap_users -t sAMAccountName login_id -t givenName first_name -t sn last_name -t mail email -t employeeID user_id ^
               petl_cat -s ldap_users -s users -d users ^
               csv_export -s users -o generated_users.csv

REM Submit the generated data to the Canvas Instance
python main.py csv_import -i generated_users.csv -d users ^
               csv_import -i generated_courses.csv -d courses ^
               csv_import -i generated_enrollments.csv -d enrollments ^
               csv_import -i generated_sections.csv -d sections ^
               canvas_upload_csv_set --url "stmonicas.test.instructure.com" ^
                                     --api-key "6523~CCjKiAk61nJgNASmvwnuAOJTl8fduaQIYeWof25EkInXvV6NXW9f8hHczUvJ8ymj" ^
                                     --data-set-id "2017_testing" 



