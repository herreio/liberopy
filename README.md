# `liberopy`

This Python package provides a Libero Web Services SOAP API client.

## Requirements

- [Libero LMS](http://www.libero.com.au/) (tested on 6.3.22)

## Setup

```sh
# ... via SSH:
pip install -e git+ssh://git@github.com/herreio/liberopy.git#egg=liberopy
# ... or via HTTPS:
pip install -e git+https://github.com/herreio/liberopy.git#egg=liberopy
```

## Classes and Methods

- Authenticate: Login / Logout
- Catalogue Searcher: Catalogue (Type=newitem)
- Library API: GetTitleDetails
- Library API: GetItemDetails

## Usage

```py
import liberopy
# Initialize client instance
libero = liberopy.WebServices("http://www.library.ACME.gov/libero")
# Log in by passing username and password
libero.login("GuestUser", "GuestPassword")
# Retrieve titles via RSN
title = libero.titledetails("123456")
# Retrieve items via Barcode
item = libero.itemdetails("123456")
# Retrieve list of titles with new items
newlist = libero.newitems()
```
