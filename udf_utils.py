from datetime import datetime
from time import strptime
def extract_file_name(file_content):
    file_content = file_content.strip()
    position = file_content.split('/n')[0]
    return position

def extract_postion(file_content):
    file_content = file_content.strip()
    position = file_content.split('/n')[0]
    return position


def extract_classcode(file_content):
    try:
        classcodde_match = re.search(r'(Class Code:)\s+(\d+)',file_content)
        classcode = classcodde_match.group(2) if classcodde_match else None
        return classcode
    except Exception as a:
        raise ValueError(f'Error extracting class node: {a}')


def extract_start_date(file_content):
    try:
        opendate_match = re.search(r'(Open [Date]:)\s+(\d\d-\d\d-\d\d)',file_content)
        start_date = datetime.strptime(opendate_match.group(2),'%m-%d-%y') if opendate_match else None

        return start_date
    except Exception as a:
        raise ValueError(f'Error extracting class node: {a}')

def extract_end_date(file_content):
    enddate_match = re.search(
    r'(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s(\d{1,2},\s\d{4})',file_content)
    enddate = enddate_match.group() if enddate_match else None
    enddatee = datetime.strptime(enddate,'%B %d, %y') if enddate_match else None
    return enddatee
def extract_salary():
    pass


def extract_requirement():
    pass

def extract_notes():
    pass

def extract_duties():
    pass

def extract_selection():
    pass

def extract_experince_length():
    pass

def extract_jobtype():
    pass


def extract_education_length():
    pass

def extract_schooltype():
    pass


def extract_application_location():
    pass