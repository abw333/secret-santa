secret-santa
============

Generates Secret Santa assignments and notifies all participants by email.

Usage Instructions:

1) Fill in FROM_EMAIL_ADDRESS with an email address that you have control over.

2) Create a csv file for each group of people you want to run this program on. For example, suppose that there are five people, Alan, Ben, Carlos, David, and Eli. Your csv file might look like:

Alan,alan@gmail.com,Ben

Ben,ben@gmail.com,Carlos

Carlos,carlos@gmail.com,David

David,david@gmail.com,Eli

Eli,eli@gmail.com,Alan

This means that Alan has already had Ben as a secret santa assignment, Ben has already had Carlos, etc.

NOTE: Don't include empty lines in your csv file. I just put some here because github displays everything on a single line if I don't put an extra newline.

3) Modify csv_filepaths_to_ignore_list. The keys are just the filepaths to your csv files. The values are a list of people within the corresponding csv that are not participating. For example, if I put Ben into the list corresponding to the sample csv above, Ben will not get an assignment and nobody will get Ben as an assignment.

4) Run the program. Your csv will be modified to include the new assignments so that you don't have to update it next year. Furthermore, a backup of your csvs will be produced in case that something goes wrong. All participants will receive an email informing them of their assignment. All people who do not participate will get an email telling them that they should've participated.