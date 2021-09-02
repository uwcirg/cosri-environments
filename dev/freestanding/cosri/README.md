# Cosri
Sets up a copy of the Cosri SMART-on-FHIR app


## Setup
Copy the default env files:

    for file in *.default; do
        cp "$file" "${file%%.default}"
    done

Copy the .env file default:

    cp default.env .env

Modify each newly copied env file as necessary. Lines that are not commented-out are required, commented lines are optional.

Copy PDMP public certificate and private key into [./config/pdmp/certs](./config/pdmp/certs)
