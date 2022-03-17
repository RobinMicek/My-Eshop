import datetime


# This function return current date and time
# It's made a separate function so i won't need
# write it over and over again. 
def current_date():
    now = datetime.datetime.now()

    return(now.strftime("%Y-%m-%d %H:%M:%S"))