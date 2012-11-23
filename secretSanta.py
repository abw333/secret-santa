import random
import smtplib

# Amount of times this program will try to randomly create correct assignments
# before giving up.
MAX_NUM_ASSIGNMENT_TRIES = 10

# Email address from which all messages will be sent.
FROM_EMAIL_ADDRESS = 'YOUR_SECRET_SANTA_EMAIL_ACCOUNT@gmail.com'

# Message used to notify people of their assignment.
MESSAGE = 'Subject: Your Secret Santa Assignment\n\n\
	   Dear %s,\n\n\
           Your assigned Secret Santa recipient is %s.\n\n\
           Sincerely,\n\
           Secret Santa'

# Message to all those who decide not to participate.
DID_NOT_PARTICIPATE_MESSAGE = 'Subject: You should participate in Secret Santa!'

# If true, prints all the emails instead of sending them.
DEBUG = False

# This is a dictionary from the filepaths to all the relevant csv files to a list
# containing the names of the people within that csv that will not be participating.
# The format of csv files is described in the comment above parse_csv.
csv_filepaths_to_ignore_list = {'/path/to/file/file1.csv' : ['Amy', 'Bill'],
                                '/path/to/file/file2.csv' : ['Carlos'],
                                '/path/to/file/file3.csv' : ['David', 'Ernest', 'Felix'],
                                '/path/to/file/file4.csv' : []}

# Secret Santa service for a group of people.
# Format of csv files is described in parse_csv.
def secret_santa(csv_filepaths_to_ignore_list):
    # Start up the server if not in debug mode.
    if DEBUG:
        server = None
    else:
        password = raw_input('Please enter the password to your Secret Santa email account: ')
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(FROM_EMAIL_ADDRESS, password)

    # Create assignments, update the csvs, and send emails for all groups.
    for csv_filepath in csv_filepaths_to_ignore_list:
        ignore_list = csv_filepaths_to_ignore_list[csv_filepath]
        (emails, possible_assignments) = parse_csv(csv_filepath, ignore_list)
        assignments = generate_assignments(possible_assignments)
        update_csv(csv_filepath, assignments)
        send_emails(emails, assignments, ignore_list, server)

    # Shut down the server if not in debug mode.
    if not DEBUG:
        server.quit()

# *input
#   *is a filepath to a csv file
#       *the file exists
#       *each line of the file represents a person
#          *first column is the name of the person
#          *second column is the person's email
#          *all other columns are the names of people
#           that the person has already had as an assignment
#   *ignore list contains people that will not be participating
# *output is a dictionary
#   *keys are the names of all the people
#   *value for a key is a list of people that that key
#    can receive as an assignment (you can't get someone
#    assigned to you if you have had them before)
def parse_csv(csv_filepath, ignore_list):
    # Get the text from the csv file.
    csv_file = open(csv_filepath)
    lines = csv_file.readlines()
    csv_file.close()

    # Get all the people, their email addresses,
    # and the people they've already had as assignments.
    people = {}
    emails = {}
    for line in lines:
        columns = line.rstrip('\n').split(',')
        # We'll need everyone's email, even if they're not participating.
        emails[columns[0]] = columns[1]
        # Only people participating will be considered for assignments.
        if columns[0] not in ignore_list:
            people[columns[0]] = columns[2:]

    # Build up a map from each person to who they can get as an assignment.
    possible_assignments = {}
    for person in people:
        # A person can have anyone but himself and anyone he has had before.
        possible_assignments[person] = \
        [possible_assignment for possible_assignment in people
         if possible_assignment != person
         and possible_assignment not in people[person]]

    return (emails, possible_assignments)

# *input is a dictionary
#   *keys are the names of all the people
#   *value for a key is a list of people that that key
#    can receive as an assignment
# *output is a dictionary
#   *keys are the names of all the people
#   *value for a key is that key's assignment
def generate_assignments(possible_assignments):
    # Try to create an assignment a few times.
    for try_num in range(MAX_NUM_ASSIGNMENT_TRIES):
        assignments = {}
        # Try to get an assignment for each person.
        for person in possible_assignments:
            # All the people that this person can get as an assignment.
            eligibles = [eligible for eligible in possible_assignments[person]
                         if eligible not in assignments.values()]
            # If there are no possible assignments, stop trying.
            if not eligibles:
                break

            # Choose randomly among the possible assignments.
            assignments[person] = eligibles[random.randint(0, len(eligibles) - 1)]

        # If everyone has received an assignment, we are done.           
        if len(assignments) == len(possible_assignments):
            break

    # If not everyone received an assignment, error out.
    if len(assignments) != len(possible_assignments):
        print 'ERROR: A valid assignment could not be found.'
        exit()

    return assignments

# *input
#   *filepath to a csv file
#       *same format as in parse_csv
#   *dictionary containing secret santa assignments
#    for the people in the csv file
# *there is no output
# *effects
#   *creates a backup of the csv file
#       *if the original is called mycsv.csv,
#        the backup is called mycsvbackup[RAND].csv,
#        where [RAND] represents a random number
#   *updates the csv file to reflect the new assignments
def update_csv(csv_filepath, assignments):
    # Get the csv text.
    csv_file = open(csv_filepath)
    lines = csv_file.readlines()
    csv_file.close()

    # Create a backup file.
    backup_filepath = ('backup' + str(random.randint(1, 333)) + '.csv').join(csv_filepath.rsplit('.csv', 1))
    backup_file = open(backup_filepath, 'w')

    # Open the original file for writing.
    csv_file = open(csv_filepath, 'w')

    for line in lines:
        # Write the original contents of the csv to the backup.
        backup_file.write(line)

        # Write the updated contents to the original csv file.
        columns = line.rstrip('\n').split(',')
        if columns[0] in assignments:
            csv_file.write(','.join(columns) + ',' + assignments[columns[0]] + '\n')
        else:
            csv_file.write(line)

    # Close both files.
    backup_file.close()
    csv_file.close()

# *input
#   *emails is a dictionary mapping people to their emails
#   *assignments is a dictionary mapping people to their assignments
#   *ignore_list is a list of people that are not participating
#   *server is used to send mail
# *there is no output
# *effects
#   *sends an email to each person notifying them of their assignment
#   *people who did not participate get a special message
def send_emails(emails, assignments, ignore_list, server):
    # Send out emails to everyone participating.
    for person in assignments:
        message = MESSAGE % (person, assignments[person])
        # If in debug mode, just print out the emails.
        if DEBUG:
            print message
            print
            print
        else:
            if person in emails:
                server.sendmail(FROM_EMAIL_ADDRESS, emails[person], message)
            else:
                print 'ERROR: No email for %s.' % (person)

    # Send out emails to everyone not participating.
    for person in ignore_list:
        # If in debug mode, just print out the emails.
        if DEBUG:
            print DID_NOT_PARTICIPATE_MESSAGE
            print
            print
        else:
            if person in emails:
                server.sendmail(FROM_EMAIL_ADDRESS, emails[person], DID_NOT_PARTICIPATE_MESSAGE)
            else:
                print 'ERROR: No email for %s.' % (person)

# Runs the program.
secret_santa(csv_filepaths_to_ignore_list)
    
