from datetime import datetime
import re
from time import strptime

from click import group

# from symbol import not_test
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
def extract_salary(file_content):
    try:
        salary_pattern = r'\$(\d{1,3}(?:,\d{3})+).+?to.+\$(\d{1,3}(?:,\d{3})+)(?:\s+and\s+\$(\d{1,3}(?:,\d{3})+)\s+to\s+\$(\d{1,3}{?:,\d{3})+))?'
        salary_match = re.search(salary_pattern,file_content)
        if salary_match:
            salary_start = float(salary_match.group(1).replace(',' ,''))
            salary_end = float(salary_match.group(4).replace(',','')) 
            # else float(salary_match.group(2).replace(',',''))
            
        else:
            salary_start,salary_end = None,None
        return salary_start,salary_end           
    except Exception as e:
        raise ValueError(f' Error extracting salary:{str(e)}')
        

def extract_requirement(file_content):
    try:
        requirement_match = re.search(r'(REQUIREMENTS?/\s?MINIMUM_QUALIFICATIONS?)(.*)(PROCESS_NOTES?)',file_content,
                                      re.DOTALL)
        REQ = requirement_match.group(2).strip() if requirement_match else None
        return REQ
    except Exception as e:
        raise ValueError(f'Error extracting requirements: {str(e)}')

def extract_notes(file_content):
    try:
        notes_match = re.search(r'(DUTIES?):(:*?)(?DUTIES)',file_content,re.DOTALL | re.IGNORECASE)
        notes  = notes_match.group(2).strip() if notes_match else None
        return notes
    except Exception as e:
        raise ValueError(f'Error extracting notes:{str(e)}')

def extract_duties(file_content):
    try:
        duties_match = re.search(r'(NOTES?):(:*?)(REQ[A-Z])',file_content,re.DOTALL)
        duties  = duties_match.group(2).strip() if duties_match else None
        return duties
    except Exception as e:
        raise ValueError(f'Error extracting notes:{str(e)}')

def extract_selection(file_content):
    try:
        selection_match = re.findall(r'([A-Z][a-z]+)(\s\.\s)',file_content)
        selection = [z[0] for z in selection_match] if selection_match else None
        return selection 
    except Exception as e:
        raise ValueError(f'Error extracting selection:{str(e)}')

def extract_experience_length(file_content):
    try:
        experience_length_match = re.search(r'(One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|one|two|three|four|five)\s(years?)\s(of\sfull(-|\s)time)',file_content)
        experience_length = experience_length_match.group(1) if experience_length_match else None
        return experience_length
    except Exception as e:
        raise ValueError(f'Error extracting selection:{str(e)}')
        

def extract_jobtype():
    pass


def extract_education_length(file_content):
    try:
        education_length_match = re.search(r'(One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten|one|two|three|four|five)(\s|-)(years?)\s(college|university)',file_content)
        education_length = education_length_match.group(1) if education_length_match else None
        return education_length
    except Exception as e:
        raise ValueError(f'Error extracting selection:{str(e)}')
    

def extract_schooltype():
    pass


def extract_application_location(file_content):
    try:
        app_loc_match = re.search(r'(Applications? will only be accepted on-?line)',file_content,re.IGNORECASE)
        app_loc ='Online' if app_loc_match else 'Mail or In Person'
        return app_loc
    except Exception as e:
        raise ValueError(f'Error extracting selection:{str(e)}')
    