import requests
import json
import logging
import os

# Migration script to add SearchParameter for next appointment extension
revision = '985f4e1e-29f5-4911-bc9c-2c774b685289'
down_revision = 'None'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the FHIR server base URL
FHIR_SERVER_URL = os.getenv('FHIR_URL')

# Headers for FHIR requests
HEADERS = {
    'Content-Type': 'application/fhir+json'
}
SP_ID = "NextAppointmentTimeSearchParameter"


def upgrade():
    # Insert new SearchParameter
    sp_resource = {
        "resourceType": "SearchParameter",
        "id": SP_ID,
        "name": "NextAppointmentTimeSearchParameter",
        "status": "active",
        "description": "Search by patient extension for next appointment",
        "code": "date-time-of-next-appointment",
        "base": [ "Patient" ],
        "type": "date",
        "expression": "Patient.extension('http://www.uwmedicine.org/time_of_next_appointment').valueDateTime"
    }
    response = requests.put(f'{FHIR_SERVER_URL}SearchParameter/{SP_ID}', headers=HEADERS, data=json.dumps(sp_resource))
    response.raise_for_status()


def downgrade():
    # Reverse upgrade by deleting new SearchParameter
    response = requests.delete(f'{FHIR_SERVER_URL}SearchParameter/{SP_ID}', headers=HEADERS)
    response.raise_for_status()
