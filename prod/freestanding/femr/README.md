# fEMR

Sets up a copy of the fEMR


## Setup

Copy the default env files:

    for file in *.default; do
        cp "$file" "${file%%.default}"
    done

Copy the .env file default:

    cp default.env .env

Modify each newly copied env file as necessary. Lines that are not commented-out are required, commented lines are optional.

Copy PDMP public certificate and private key into [./config/pdmp/certs](./config/pdmp/certs)

### Keycloak

#### Rotating Keys
New keys should be generated, and old keys disabled.

Select **Realm Settings** from the left navigation bar, then select the **Keys** tab, then **Providers** sub-tab.

For every **Provider** type listed (`rsa-generated`, `hmac-generated`, `aes-generated`), perform the following:

1. Click the **Add keystore...** drop-down menu, then select the desired provider to open the **Add Keystore** dialog and a new key provider
2. Change **Priority** to `150`, higher than the default of `100`
3. Click **Save**

For every **Provider** type listed (`rsa-generated`, `hmac-generated`, `aes-generated`), with **Priority** of `100`, click **Delete**
