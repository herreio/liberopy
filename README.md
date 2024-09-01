# `liberopy`

This Python package provides a Libero Web Services SOAP API client.

## Setup

Depending on your preferred installation scope, you may need to use `sudo` or pip’s `--user` flag when running the following setup commands. However, it is recommended to use a virtual environment that does not require either:

```sh
python3 -m venv env
. env/bin/activate
```

### ... via SSH

```sh
pip install -e git+ssh://git@github.com/herreio/liberopy.git#egg=liberopy
```

### ... or via HTTPS

```sh
pip install -e git+https://github.com/herreio/liberopy.git#egg=liberopy
```

## Platform

- [Libero LMS](https://libero.com.au) (tested on 6.3.22 and 6.4.1)

### API Packages

> These webservices are provided to be used by third parties to design and write their own applications based on the Libero platform. (SOAP Protocol, Rev. 39)

## Classes and Methods

- Authenticate
    - Login
    - PatronLogin
    - Logout
- CatalogueSearcher
    - Catalogue (Type=newitem)
    - Search
    - SearchCount
    - GetTitle (Deprecated)
    - GetRsnByRID
- LibraryAPI
    - GetTitleDetails
    - GetItemDetails
    - GetMemberDetails
    - OrderStatus
    - OrderInformation
    - OrderLineInformation
    - Branch
- OnlineCatalogue
    - GetItemByBarcode
    - GetALLItemsByRID
    - GetMABBlock
    - GetMARCBlock
- OnlineILLService
    - GetMemberInformation

## Usage Example

```py
import liberopy
# Initialize client instance
libero = liberopy.WebServices("http://www.library.ACME.gov/libero", db="ACM")
# Retrieve items via barcode
item = libero.item("123456")
# Retrieve titles via RSN
title = libero.title("123456")
# Search for items by given term
result = libero.search("Harry Potter")
# Result count for given search term
result_count = libero.search_count("Harry Potter")
# Retrieve MAB data of titles via RID
mab = libero.mabblock("123456")
# Retrieve MARC data of titles via RID
marc = libero.marcblock("123456")
# Retrieve list of titles with new items
newlist = libero.newitems()
# Get RSN of title from the provided RID
rsn = libero.rid2rsn("123456")
# Get barcodes of items from the provided RID
bcs = libero.rid2bc("123456")
# Get information on member via member code
member = libero.memberinfo("10189")
# Log in before using methods of LibraryAPI
libero.login("GuestUser", "GuestPassword")
# Retrieve title details via RSN
titledetails = libero.titledetails("123456")
# Retrieve item details via barcode
itemdetails = libero.itemdetails("123456")
# Retrieve member details via member code (or ID of member)
memberdetails = libero.memberdetails(mc="10157")
# Retrieve header information for an order
orderinfo = libero.orderinfo("725")
# Retrieve the order’s line number information
orderlineinfo = libero.orderlineinfo("9", "1")
# Retrieve the current order status
orderstatus = libero.orderstatus("1", "1")
# Retrieve list of branches
branches = libero.branches()
```

## Public Instances

According to the company’s [website](https://libero.com.au/company/why-libero/), the library management system Libero has more than 2,500 users worldwide. Some examples of users can be found in the following list.

- [Bach Archiv Leipzig](https://bacharchiv.libero-is.de/libero/WebOpac.cls)
- [Hochschule für Grafik und Buchkunst Leipzig](https://hgb.libero-is.de/libero/WebOpac.cls)
- [Kunsthaus Zürich](https://opac.kunsthaus.ch/libero/WebOpac.cls)
- [Parlamentsbibliothek Bern](https://biblio.parlament.ch/libero/WebOpac.cls)
- [Richmond – Upper Clarence Regional Library](https://richmondvalley.libero.com.au/libero/WebOpac.cls)
- [Stadtbibliothek Saarbrücken](https://opac.saarbruecken.de/libero/WebOpac.cls)
- [Stadtbücherei Heinsberg](https://heinsberg.libero-is.de/libero/WebOpac.cls)
- [Stadt- und Regionalbibliothek Cottbus](https://web-opac.bibliothek-cottbus.de/libero/WebOpac.cls)
- [Università Pontificia Salesiana - Biblioteca Don Bosco](https://webopacups.urbe.it/libero/WebOpac.cls)
- [Universität Konstanz - KIM](https://libero.ub.uni-konstanz.de/libero/WebOpac.cls)
- [University of Mauritius - Library](https://library.uom.ac.mu/libero/WebOpac.cls)

cf. https://duckduckgo.com/?q=libero+webopac / https://www.google.com/search?q=libero+webopac

### Run Tests

```sh
python -m unittest
```
