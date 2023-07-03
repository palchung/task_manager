# Notes:
# Use the following username and password to access the admin rights
# username: admin
# password: password

# ===== importing libraries =====
import fileinput
import os
from datetime import datetime, date
DATETIME_STRING_FORMAT = "%Y-%m-%d"

# === Variables ===
default_account = "admin;password"
user_file = "./user.txt"
task_file = "./tasks.txt"
task_overview_file = "./task_overview.txt"
user_overview_file = "./user_overview.txt"
today = datetime.today()
logged_in = False
return_previous_menu = False


# ===== helper functions =====


# Show overview file content
def show_statistic(file):
    with open(file) as f:
        for line in f:
            print(line.strip())


# create a report and save as file
def output_report(file, report_str):
    with open(file, "w+") as report:
        report.write(report_str)

    print(f"{file} is generated.")


# convert items into a dictionary
def convert_to_dict(items):
    dict = {}
    for item in items:
        key, data = item.split(';')
        dict[key] = data
    return dict


# display a task
def show_tasks(task):
    disp_str = ""
    # check if the key "ref" exist in task dictionary
    if "ref" in task:
        disp_str += f"Task reference: \t {task['ref']}\n"
    disp_str += f"Task: \t\t\t {task['title']}\n"
    disp_str += f"Completed: \t\t {'Yes' if task['completed'] else 'No'}\n"
    disp_str += f"Assigned to: \t\t {task['username']}\n"
    disp_str += f"Date Assigned: \t\t {task['assigned_date'].strftime(DATETIME_STRING_FORMAT)}\n"
    disp_str += f"Due Date: \t\t {task['due_date'].strftime(DATETIME_STRING_FORMAT)}\n"
    disp_str += f"Task Description: \n{task['description']}\n"

    print(disp_str)


# Search texts in a file and replace it with new texts
def replace_text_in_file(file, text_to_search, replacement_text):
    fin = open(file, "rt")
    data = fin.read()
    data = data.replace(text_to_search, replacement_text)
    fin.close()
    fin = open(file, "wt")
    fin.write(data)
    fin.close()


# === functions ===


# Generate task overview file
def generate_task_overview(task_overview_file, task_list):
    completed_num = uncompleted_num = uncompleted_and_overdue = 0

    total_tasks_num = len(task_list)

    # Handle no task in the system.
    if total_tasks_num == 0:
        report = "Task overview file is blank. No task in the system."

    else:

        for t in task_list:
            if t["completed"] == True:
                completed_num += 1
            if t["completed"] == False:
                uncompleted_num += 1
            if t["completed"] == False and t['due_date'] < today:
                uncompleted_and_overdue += 1

        report = f"\n======= Task Overview =======\n\n"
        report += f"Total number of tasks: \t\t\t\t {total_tasks_num}\n"
        report += f"Total number of completed tasks: \t\t {completed_num}\n"
        report += f"Total number of uncompleted tasks: \t\t {uncompleted_num}\n"
        report += f"Total number of overdue tasks: \t\t\t {uncompleted_and_overdue}\n"
        report += f"Percentage of incompleted tasks: \t\t {round(uncompleted_num / total_tasks_num * 100, 2)}%\n"
        report += f"Percentage of overdued tasks: \t\t\t {round(uncompleted_and_overdue / total_tasks_num * 100 ,2)}%\n"

    # create report and save as file
    output_report(task_overview_file, report)

    return task_list


# Generate user overview file
def generate_user_overview(user_file, user_overview_file, task_list):
    # Read in user_data
    user_data = read_user_data(user_file, default_account)

    # Convert to a dictionary
    username_password = convert_to_dict(user_data)

    total_user_num = len(username_password.keys())
    total_tasks_num = len(task_list)
    total_user_tasks = total_user_completed_tasks = total_user_incompleted_tasks = total_user_incompleted_overdued = 0

    report = "\n======= User Overview =======\n\n"
    report += f"Total number of users : \t\t\t {total_user_num}\n"

    if total_tasks_num == 0:
        print(
            f"\nNo task in the system, no task related statistic show in user overview file.")

    else:

        for user in username_password.keys():
            report += f"\nUser : \t\t\t\t\t\t {user}\n"

            for task in task_list:
                if user == task["username"]:
                    total_user_tasks += 1

                    if task["completed"] == True:
                        total_user_completed_tasks += 1

                    elif task["completed"] == False:
                        total_user_incompleted_tasks += 1

                    if task["completed"] == False and task['due_date'] < today:
                        total_user_incompleted_overdued += 1

            if total_user_tasks == 0:
                report += f"Total number of tasks assigned : \t\t 0\n"

            else:

                report += f"Total number of tasks assigned : \t\t {total_user_tasks}\n"
                report += f"Percentage of tasks assigned : \t\t\t {round(total_user_tasks / total_tasks_num * 100, 2)}\n"
                report += f"Percentage of completed tasks assigned : \t {round(total_user_completed_tasks / total_user_tasks * 100, 2)}\n"
                report += f"Percentage of incompleted tasks assigned : \t {round(total_user_incompleted_tasks / total_user_tasks * 100, 2)}\n"
                report += f"Percentage of incompleted overdued tasks : \t {round(total_user_incompleted_overdued / total_user_tasks * 100, 2)}\n"

            # reset parameter for next user data
            total_user_tasks = total_user_completed_tasks = total_user_incompleted_tasks = total_user_incompleted_overdued = 0

    output_report(user_overview_file, report)


# edit a task
def edit_task(task, mark_as_completed, task_file, username_password):

    the_task = f"{task['username']};{task['title']};{task['description']};{task['due_date'].strftime(DATETIME_STRING_FORMAT)};{task['assigned_date'].strftime(DATETIME_STRING_FORMAT)}"
    task_to_search = f"{the_task};No"

    # if mark as completed for a task
    if mark_as_completed:
        replacement_task = f"{the_task};Yes"
        replace_text_in_file(task_file, task_to_search, replacement_task)

    # if user edit a task
    else:
        # custom exception for assigning a task to non-exist user.
        class UserExist(Exception):
            pass
        # check if user name exist.
        while True:
            try:
                new_username = input("New user to assign for this task ? ")

                if new_username == "":
                    new_username = task['username']

                # - Check duplicate user name
                elif new_username not in username_password.keys():
                    raise UserExist

                break
            except UserExist:
                print("Username is not found. Please enter another username")

        while True:
            try:
                task_due_date = input("New due date of task (YYYY-MM-DD): ")

                if task_due_date == "":
                    new_due_date = task['due_date']

                else:
                    new_due_date = datetime.strptime(
                        task_due_date, DATETIME_STRING_FORMAT)

                break

            except ValueError:
                print("Invalid datetime format. Please use the format specified")

        replacement_task = f"{new_username};{task['title']};{task['description']};{new_due_date.strftime(DATETIME_STRING_FORMAT)};{task['assigned_date'].strftime(DATETIME_STRING_FORMAT)};No"

        replace_text_in_file(task_file, task_to_search, replacement_task)


# Read in user_data or create user.txt if not exist
def read_user_data(file, default_account):
    # If no user.txt file, write one with a default account
    if not os.path.exists(file):
        with open(file, "w") as default_file:
            default_file.write(default_account)

    # Read in user_data
    with open(file, 'r') as user_file:
        user_data = user_file.read().split("\n")

    return (user_data)


# open or create tasks file
def open_tasks_file(file):
    if not os.path.exists(file):
        with open(file, "w") as default_file:
            pass

    with open(file, 'r') as task_file:
        task_data = task_file.read().split("\n")
        task_data = [t for t in task_data if t != ""]
    return (task_data)


# get all tasks in tasks.txt
def get_all_tasks_from(file):
    task_list = []
    task_data = open_tasks_file(file)
    for t_str in task_data:
        curr_t = {}

        # Split by semicolon and manually add each component
        task_components = t_str.split(";")
        curr_t['username'] = task_components[0]
        curr_t['title'] = task_components[1]
        curr_t['description'] = task_components[2]
        curr_t['due_date'] = datetime.strptime(
            task_components[3], DATETIME_STRING_FORMAT)
        curr_t['assigned_date'] = datetime.strptime(
            task_components[4], DATETIME_STRING_FORMAT)
        curr_t['completed'] = True if task_components[5] == "Yes" else False

        task_list.append(curr_t)
    return (task_list)


# register a user
def reg_user(username_password, user_file):

    # - Request input of a new username
    while True:
        try:
            new_username = input("New Username: ")
            # - Check duplicate user name
            if new_username in username_password.keys():
                raise Exception()
            break
        except Exception:
            print("Username exist. Please enter another username")

    # - Request input of a new password
    new_password = input("New Password: ")

    # - Request input of password confirmation.
    confirm_password = input("Confirm Password: ")

    # - Check if the new password and confirmed password are the same.

    if new_password == confirm_password:
        # - If they are the same, add them to the user.txt file,
        print("New user added")
        username_password[new_username] = new_password

        with open(user_file, "w") as out_file:
            user_data = []
            for k in username_password:
                user_data.append(f"{k};{username_password[k]}")
            out_file.write("\n".join(user_data))

    # - Otherwise you present a relevant message.
    else:
        print("Passwords do no match")


# add a task
# Allow a user to add a new task to task.txt file
# Prompt a user for the following:
# - A username of the person whom the task is assigned to,
# - A title of a task,
# - A description of the task and
# - the due date of the task.
def add_task(username_password, task_list, task_file):

    while True:
        try:
            task_username = input("Name of person assigned to task: ")
            if task_username not in username_password.keys():
                raise Exception()
            break
        except Exception:
            print("User does not exist. Please enter a valid username")

    task_title = input("Title of Task: ")
    task_description = input("Description of Task: ")
    while True:
        try:
            task_due_date = input("Due date of task (YYYY-MM-DD): ")
            due_date_time = datetime.strptime(
                task_due_date, DATETIME_STRING_FORMAT)
            break

        except ValueError:
            print("Invalid datetime format. Please use the format specified")

    # Then get the current date.
    curr_date = date.today()
    # Add the data to the file task.txt and
    # Include 'No' to indicate if the task is complete.
    new_task = {
        "username": task_username,
        "title": task_title,
        "description": task_description,
        "due_date": due_date_time,
        "assigned_date": curr_date,
        "completed": False
    }

    task_list.append(new_task)
    with open(task_file, "w") as tasks_file:
        task_list_to_write = []
        for t in task_list:
            str_attrs = [
                t['username'],
                t['title'],
                t['description'],
                t['due_date'].strftime(DATETIME_STRING_FORMAT),
                t['assigned_date'].strftime(DATETIME_STRING_FORMAT),
                "Yes" if t['completed'] else "No"
            ]
            task_list_to_write.append(";".join(str_attrs))
        tasks_file.write("\n".join(task_list_to_write))
    print("Task successfully added.")


# View all tasks
# Reads the task from task.txt file and prints to the console in the
# format of Output 2 presented in the task pdf (i.e. includes spacing
# and labelling)
def view_all(task_list):
    print(f"\n=== All Tasks ===\n")
    for t in task_list:
        show_tasks(t)


# View a user task
# Reads the task from task.txt file and prints to the console in the
# format of Output 2 presented in the task pdf (i.e. includes spacing
# and labelling)
def view_mine(task_file, curr_user):
    task_new_list = []
    match = False

    class TaskCompleted(Exception):
        pass

    task_list = get_all_tasks_from(task_file)
    print(f"\n=== Your assigned Task ===\n")
    for ref, t in enumerate(task_list):
        if t['username'] == curr_user:
            t['ref'] = ref
            show_tasks(t)
            task_new_list.append(t)

    while True:
        try:
            task_num = int(input(
                "Which task do you want to view ? (please input the task reference number, or '-1' return to previous menu) "))

            if task_num == -1:
                return True

            for curr_t in task_new_list:

                if task_num == curr_t['ref']:
                    match = True
                    print("\n=== You selected following task to edit. ===\n")
                    show_tasks(curr_t)

                    action = int(
                        input(f"Would you like to ?\n1 - mark the task as complete\n2 - edit the task\n: "))
                    if action == 1:
                        curr_t['completed'] = True
                        edit_task(
                            curr_t, curr_t['completed'], task_file, username_password)
                        print('\nThis task is marked as completed.')

                    elif action == 2 and curr_t['completed'] == True:
                        raise TaskCompleted(Exception)

                    elif action == 2 and curr_t['completed'] == False:
                        edit_task(
                            curr_t, curr_t['completed'], task_file, username_password)
                        print('\nThe task is edited.\n')
                    else:
                        raise ValueError

            if not match:
                raise ValueError

            break

        except ValueError:
            print("\nInvalid input, please try again.\n")

        except TaskCompleted:
            print(
                "\nThis task is already completed before. You cannot edit a completed task.\n")

    return True


# === main program ===


# ====Login Section====

# Read in user_data
user_data = read_user_data(user_file, default_account)

# Convert to a dictionary
username_password = convert_to_dict(user_data)

while not logged_in:

    print("LOGIN")
    curr_user = input("Username: ")
    curr_pass = input("Password: ")
    if curr_user not in username_password.keys():
        print("User does not exist")
        continue
    elif username_password[curr_user] != curr_pass:
        print("Wrong password")
        continue
    else:
        print("Login Successful!")
        logged_in = True


while logged_in:
    # presenting the menu to the user and
    # making sure that the user input is converted to lower case.
    print()
    menu = input('''Select one of the following Options below:
                    r - Registering a user
                    a - Adding a task
                    va - View all tasks
                    vm - View my task
                    gr - generate reports
                    ds - Display statistics
                    e - Exit
                    : ''').lower()

    if menu == 'r':
        # Add a new user to the user.txt file
        reg_user(username_password, user_file)

    elif menu == 'a':
        # Add task into task.txt file
        # Get all tasks from tasks.txt
        task_list = get_all_tasks_from(task_file)
        add_task(username_password, task_list, task_file)

    elif menu == 'va':
        # View all tasks

        # Always get tasks from file to ensure data consistancy.
        task_list = get_all_tasks_from(task_file)
        view_all(task_list)

    elif menu == 'vm':
        # View a user task
        while True:
            return_previous_menu = view_mine(task_file, curr_user)
            if return_previous_menu:
                break

    elif menu == 'gr':

        # Always genrate task_overview.txt and user_overview.txt from files, even they are already exist
        # This can keep data updated during user using the application.
        task_list = get_all_tasks_from(task_file)

        # generate task_overview.txt
        generate_task_overview(task_overview_file, task_list)

        # generate user_overview.txt
        generate_user_overview(user_file, user_overview_file, task_list)

    elif menu == 'ds' and curr_user == 'admin':
        # If the user is an admin they can display statistics about number of users
        # and tasks.

        # Always genrate task_overview.txt and user_overview.txt from files, even they are already exist
        # This can keep data updated during user using the application.
        task_list = get_all_tasks_from(task_file)

        # generate task_overview.txt
        generate_task_overview(task_overview_file, task_list)

        # generate user_overview.txt
        generate_user_overview(user_file, user_overview_file, task_list)

        # Display tasks statistic data from txt files
        show_statistic(task_overview_file)
        show_statistic(user_overview_file)

    elif menu == 'ds' and curr_user != 'admin':
        print("You have no right to view tasks and user statistic.")

    elif menu == 'e':
        print('Goodbye!!!')
        exit()

    else:
        print("You have made a wrong choice, Please Try again")
