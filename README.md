# `liberopy`

This Python package provides a Libero Web Services SOAP API client.

## Setup

### ... via SSH

```sh
pip install -e git+ssh://git@github.com/herreio/liberopy.git#egg=liberopy
```

### ... via HTTPS

```sh
pip install -e git+https://github.com/herreio/liberopy.git#egg=liberopy
```

## Platform

- [Libero LMS](https://libero.com.au) (tested on 6.3.22)

### API Packages

> These webservices are provided to be used by third parties to design and write their own applications based on the Libero platform. (SOAP Protocol)

## Classes and Methods

- Authenticate
    - Login
    - Logout
- CatalogueSearcher
    - Catalogue (Type=newitem)
    - GetRsnByRID
- LibraryAPI
    - GetTitleDetails
    - GetItemDetails
    - OrderStatus
    - OrderInformation
    - OrderLineInformation

## Usage Example

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
# Get RSN of title from the provided RID
rsn = libero.rid2rsn("123456")
# Retrieve header information for an order
orderinfo = libero.orderinfo("725")
# Retrieve the order’s line number information
orderlineinfo = libero.orderlineinfo("9", "1")
# Retrieve the current order status
orderstatus = libero.orderstatus("1", "1")
```
