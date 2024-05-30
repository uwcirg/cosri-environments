#!/usr/bin/env python3
'''
This script generates a file that's an analysis of FHIR Patient resources.
Input: PainTracker.created.Patient.resources.through2024-05-29AM.txt, which is
a list of FHIR resource IDs, parsed from an elk log of ID's created by PainTracker.
More info at https://uwnetid-my.sharepoint.com/:w:/r/personal/mcjustin_uw_edu/_layouts/15/doc.aspx?sourcedoc=%7B068d55a9-d4ce-4c48-a8d3-a5b865b1f7eb%7D&action=edit
It's intended to be run from nihonium:/srv/www/cosri-uwmc-prod/cosri-environments/prod/freestanding/femr :
sudo python3 ./fhir_patient_analysis.py
It requires no modification to be run from that location.
It accepts no arguments.
'''

import subprocess
import json
import requests
import csv
import urllib.parse

base_url = "http://fhir-internal:8080/fhir"
NOT_PRESENT = "NOT_PRESENT"
INITIALS_OR_DOB_MISSING = "INITIALS_OR_DOB_MISSING"
FAMILY_NAME_STARTS_WITH_SPACE = "FAMILY_NAME_STARTS_WITH_SPACE"
GIVEN_NAME_STARTS_WITH_SPACE = "GIVEN_NAME_STARTS_WITH_SPACE"
FAMILY_NAME_ENDS_WITH_SPACE = "FAMILY_NAME_ENDS_WITH_SPACE"
GIVEN_NAME_ENDS_WITH_SPACE = "GIVEN_NAME_ENDS_WITH_SPACE"
FAMILY_NAME_ALL_WHITESPACE = "FAMILY_NAME_ALL_WHITESPACE"
GIVEN_NAME_ALL_WHITESPACE = "GIVEN_NAME_ALL_WHITESPACE"


def get_fhir_resource(url):

    print(f"get_fhir_resource({url}), just entered.")

    command = f"docker-compose exec dashboard curl -X GET '{url}'"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    print(f"get_fhir_resource({url}), subprocess has been run.")

    if result.returncode != 0:
        raise Exception(f"get_fhir_resource({url}), command failed with exit code {result.returncode}: {result.stderr}")

    print(f"get_fhir_resource({url}), result.stdout:{result.stdout}")

    # Assuming the output is JSON, parse it
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise Exception(f"get_fhir_resource({url}), failed to parse JSON from command output")

#    response = requests.get(url)
#    response.raise_for_status()  # Ensure we stop on HTTP errors
#    return response.json()

def construct_next_url(next_url):
    # Parse the query parameters from the next URL
    next_query_params = urllib.parse.urlparse(next_url).query
    #print(f"construct_next_url({next_url}), here's next_query_params:{next_query_params}")
    next_params = urllib.parse.parse_qs(next_query_params)

    # Extract needed parameters
    getpages = next_params.get('_getpages', [''])[0]
    getpagesoffset = next_params.get('_getpagesoffset', [''])[0]
    count = next_params.get('_count', [''])[0]
    bundletype = next_params.get('_bundletype', [''])[0]

    # Construct the new URL
    new_url = f"{base_url}\?_getpages={getpages}\&_getpagesoffset={getpagesoffset}\&_count={count}\&_bundletype={bundletype}"
    return new_url

def get_patient_isacc_id(patient_reference, patient_cache):
    # Check if we already have the ISACC ID for this patient
    if patient_reference in patient_cache:
        return patient_cache[patient_reference]

    patient_url = f"{base_url}/{patient_reference}"
    patient_data = get_fhir_resource(patient_url)

    # Initialize ISACC ID as empty string
    isacc_id = ""

    # Search for ISACC ID in the patient's identifiers
    for identifier in patient_data.get('identifier', []):
        if identifier.get('system') == "http://isacc.app/user-id":
            isacc_id = identifier.get('value', "")
            break

    # Cache the ISACC ID for future use
    patient_cache[patient_reference] = isacc_id
    return isacc_id

def extract_type(communication):
    for category in communication.get('category', []):
        for coding in category.get('coding', []):
            if coding.get('system') == "https://isacc.app/CodeSystem/communication-type":
                return coding.get('code')
    return None

def main():
    urlGeneralPatient = f"{base_url}/Patient"
    patient_cache = {}

    with open('PatientResourceAnalysis.csv', 'w', newline='') as fileOut:
        writer = csv.writer(fileOut)
        writer.writerow(["ID", "family name", "given name", "birthDate", "cproId", "lastUpdated", "number of matches on name & DOB", 'IDs for matches on name & DOB', "number of matches on initials & dob", 'IDs for matches on initials & DOB', "notes"])

    with open('/home/mcjustin/PainTracker.created.Patient.resources.through2024-05-29AM.txt', 'r') as fileIn:
        for line in fileIn:
            resourceId = line.rstrip()

            #urlById = urlGeneralPatient + '?_id=' + resourceId
            urlById = urlGeneralPatient + '/' + resourceId
            patient = get_fhir_resource(urlById)
            #dataPatient = get_fhir_resource(urlById)
            #for entry in dataPatient.get('entry', []):
            #patient = entry['resource']
            #patient = dataPatient
            print(f"patient:{patient}")
            #print(f"get_fhir_resource({url}), result.stdout:{result.stdout}")
            name_list = patient.get('name', [])
            family = NOT_PRESENT
            given = NOT_PRESENT
            notes = ''
            if name_list:
                family = name_list[0].get('family', '')
                given = name_list[0].get('given', [''])[0]
            print(f"family:{family}")
            print(f"given:{given}")
            birthDate = patient.get('birthDate')
            if birthDate is None:
                birthDate = NOT_PRESENT
            print(f"birthDate:{birthDate}")
            #cproId = patient.get('identifier', [])[0].get('value', '')
            cproId = NOT_PRESENT
            identifier_list = patient.get('identifier', [])
            if identifier_list:
                cproId = identifier_list[0].get('value', '')
            print(f"cproId:{cproId}")
            lastUpdated = patient.get('meta', {}).get('lastUpdated')
            print(f"lastUpdated:{lastUpdated}")

            # Find resources matching these names & birthDate exactly. This scenario might happen if cPRO finds more than one Patient matching... in that case, it creates yet another Patient resource.
            urlByDemog = urlGeneralPatient + '?family:exact=' + urllib.parse.quote_plus(family) + '&given:exact=' + urllib.parse.quote_plus(given) + '&birthdate=' + birthDate
            dataPatientMatchingDemog = get_fhir_resource(urlByDemog)
            numMatchesOnDemog = dataPatientMatchingDemog.get('total')
            #numMatchesOnDemog = 0
            idsMatchesOnDemog = ''
            for entry in dataPatientMatchingDemog.get('entry', []):
                #numMatchesOnDemog += 1
                patient = entry['resource']
                resourceIdMatchOnDemog = patient.get('id')
                idsMatchesOnDemog = idsMatchesOnDemog + resourceIdMatchOnDemog + ' '

            # Find all Patients matching these initials & birthDate
            numMatchingInitialsDob = INITIALS_OR_DOB_MISSING
            idsMatchingInitialsDob = INITIALS_OR_DOB_MISSING
            if family != NOT_PRESENT and given != NOT_PRESENT:

                familyInitial = family[0]
                familyNoWs = family.strip()
                if familyInitial.isspace():
                    notes = notes + ' ' + FAMILY_NAME_STARTS_WITH_SPACE
                    if familyNoWs == '':
                        notes = notes + ' ' + FAMILY_NAME_ALL_WHITESPACE;
                familyLastChar = family[len(family) - 1]
                if familyLastChar.isspace():
                    notes = notes + ' ' + FAMILY_NAME_ENDS_WITH_SPACE

                givenInitial = given[0]
                givenNoWs = given.strip()
                if givenInitial.isspace():
                    notes = notes + ' ' + GIVEN_NAME_STARTS_WITH_SPACE
                    if givenNoWs == '':
                        notes = notes + ' ' + GIVEN_NAME_ALL_WHITESPACE;
                givenLastChar = given[len(given) - 1]
                if givenLastChar.isspace():
                    notes = notes + ' ' + GIVEN_NAME_ENDS_WITH_SPACE

                if familyNoWs != '' and givenNoWs != '' and birthDate != NOT_PRESENT:
                    urlByInitialsDob = urlGeneralPatient + '?family=' + familyNoWs[0] + '&given=' + givenNoWs[0] + '&birthdate=' + birthDate
                    dataPatientMatchingInitialsDob = get_fhir_resource(urlByInitialsDob)
                    numMatchingInitialsDob = dataPatientMatchingInitialsDob.get('total')
                    idsMatchingInitialsDob = ''
                    for entry in dataPatientMatchingInitialsDob.get('entry', []):
                        patient = entry['resource']
                        resourceIdMatchingInitialsDob = patient.get('id')
                        idsMatchingInitialsDob = idsMatchingInitialsDob + resourceIdMatchingInitialsDob + ' '

            with open('PatientResourceAnalysis.csv', 'a', newline='') as fileOut:
                writer = csv.writer(fileOut)
                writer.writerow([resourceId, family, given, birthDate, cproId, lastUpdated, numMatchesOnDemog, idsMatchesOnDemog, numMatchingInitialsDob, idsMatchingInitialsDob, notes])


if __name__ == "__main__":
    main()

