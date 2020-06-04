from os import sep, makedirs
from os.path import exists
from csv import writer


def write_file(name, data):
    directory = sep.join(name.split(sep)[:-1])
    if not exists(directory):
            makedirs(directory)
    with open(name, "a") as f:
        f.write(str(data))
        f.write("\n")

def write_file_csv(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)