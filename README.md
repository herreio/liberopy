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

> These webservices are provided to be used by third parties to design and write their own applications based on the Libero platform. (SOAP Protocol, Rev. 39)

## Classes and Methods

- Authenticate
    - Login
    - PatronLogin
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

## Public Instances

According to the company’s [website](https://libero.com.au/company/our-partners/), the library management system has more than 450 users worldwide. Some examples of users can be found in the following list whose links point to the `WebOpac` class. Each link is followed by the base URL (`domain`) of the Libero instance which can be used to initialize a client.

- [Bach-Archiv](https://bacharchiv.libero-is.de/libero/WebOpac.cls)
    - `https://bacharchiv.libero-is.de/libero`
- [Cairns Regional Council - Libraries](https://lib.cairnslibrary.com.au/libero/WebOpac.cls)
    - `https://lib.cairnslibrary.com.au/libero`
- [Central Coast Council - Library Service](https://centralcoast.libero.com.au/libero/WebOpac.cls)
    - `https://centralcoast.libero.com.au/libero`
- [Deutsche Bundesbank - Bibliothek](http://www.libit.de/bbkwo/WebOpac.cls)
    - `http://www.libit.de/bbkwo`
- [Hochschule Bochum](https://opac.hs-bochum.de/libero/WebOpac.cls)
    - `https://opac.hs-bochum.de/libero`
- [Hochschule für Grafik und Buchkunst Leipzig](https://hgb.libero-is.de/libero/WebOpac.cls)
    - `https://hgb.libero-is.de/libero`
- [Kunsthaus Zürich](https://opac.kunsthaus.ch/libero/WebOpac.cls)
    - `https://opac.kunsthaus.ch/libero`
- [Landesamt für Schule und Bildung Sachsen - Bibliothek](https://portal.smk.sachsen.de/sbal-webopac/libero/WebOpac.cls)
    - `https://portal.smk.sachsen.de/sbal-webopac/libero`
- [University of Mauritius - Library](https://library.uom.ac.mu/libero/WebOpac.cls)
    - `https://library.uom.ac.mu/libero`
- [Saarländische Universitäts- und Landesbibliothek](https://opac.sulb.uni-saarland.de/libero/WebOpac.cls)
    - `https://opac.sulb.uni-saarland.de/libero`
- [Stadtbibliothek Aachen](https://webopac.stadtbibliothek-aachen.de/libero/WebOpac.cls)
    - `https://webopac.stadtbibliothek-aachen.de/libero`
- [Stadtbibliothek Saarbrücken](https://opac.saarbruecken.de/libero/WebOpac.cls)
    - `https://opac.saarbruecken.de/libero`
- [Stadt- und Regionalbibliothek Cottbus](https://web-opac.bibliothek-cottbus.de/libero/WebOpac.cls)
    - `https://web-opac.bibliothek-cottbus.de/libero`
- [Università Pontificia Salesiana - Biblioteca Don Bosco](https://webopacups.urbe.it/libero/WebOpac.cls)
    - `https://webopacups.urbe.it/libero`
- [Universität Konstanz - KIM](https://libero.ub.uni-konstanz.de/libero/WebOpac.cls)
    - `https://libero.ub.uni-konstanz.de/libero`
- [Universitätsbibliothek Chemnitz](https://opac.bibliothek.tu-chemnitz.de/libero/WebOpac.cls)
    - `https://opac.bibliothek.tu-chemnitz.de/libero`
- [Universitätsbibliothek TU Bergakademie Freiberg](https://webopac.ub.tu-freiberg.de/libero/WebOpac.cls)
    - `https://webopac.ub.tu-freiberg.de/libero`
- [Waverley Library](https://library.waverley.nsw.gov.au/libero/WebOpac.cls)
    - `https://library.waverley.nsw.gov.au/libero`

cf. https://www.google.com/search?q=libero+webopac
