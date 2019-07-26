#!/bin/bash

# source me before trying to start Cores if you're running
# locally rather than in Docker. It gets very upset if you
# don't have some of these set.

export HOSTNAME=localhost
export SECRET_KEY=uhaegagoihierghaoeguiaeguiagr
export DEBUG=True

# database
export POSTGRES_HOST=localhost
export POSTGRES_PASSWORD=password
export POSTGRES_USER=django

# LDAP or Kerberos config
export LDAP_AUTH=False # enable LDAP
export LDAP_AUTH_DIRECT=False # enable direct bind LDAP (only if normal LDAP not enabled)
export LDAP_URI=ldap://dc01.contoso.com # where to bind to
export LDAP_BIND_DN=bind-user # creds for queries
export LDAP_BIND_PASS=password
export LDAP_SEARCH_PATH=OU=Users,OU=All Sites,DC=Contoso,DC=Com # where to search for users
export LDAP_LOGGING=False # extra debug logs
export KERBEROS_AUTH=False # enable (experimental) Kerberos authentication
export KERBEROS_REALM=contoso.com
export KERBEROS_SERVICE=dc02.contoso.com/FINANCE

# leave SMTP server blank if not in use
export SMTP_SERVER=False # set server here if you want emails
export SMTP_PORT=25
export SMTP_FROM=noreply@cores.local