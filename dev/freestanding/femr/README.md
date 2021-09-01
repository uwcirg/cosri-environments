# fEMR

Sets up a copy of the fEMR


## Setup

Copy the default env files:
    for file in *.default; do
        cp "$file" "${file%%.default}"
    done

Copy the .env file default
    cp default.env .env

Modify each newly copied env file as necessary. Lines that are not commented-out are required, commented lines are optional.
