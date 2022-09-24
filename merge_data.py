from dataclasses import dataclass
import os
from csv import DictReader, reader
from collections import defaultdict
from dataclasses  import asdict, dataclass
from typing import List, Dict

DATA_DIR = 'data'
ADDRESSES_DATA = os.path.join(DATA_DIR, 'Addresses.csv')
CONSTITUENTS_DATA = os.path.join(DATA_DIR, 'Constituents.csv')
CONTACTS_DATA = os.path.join(DATA_DIR, 'Contacts.csv')

@dataclass
class Address:
    type: str
    isPrimary: bool
    line1: str
    line2: str
    line3: str
    line4: str
    city: str
    stateCode: str
    zipcode: str


def parse_address(address: List) -> Dict:
    return {
        "type": address[3],
        "isPrimary": True if address[4] == 'X' else False,
        "line1": address[6],
        "line2": address[7],
        "line3": address[8],
        "line4": address[9],
        "city": address[10],
        "stateCode": address[11],
        "zipcode": address[12]
        }


addresses = defaultdict(list)
with open(ADDRESSES_DATA, 'r') as f:
    address_reader = reader(f)
    # skip header row
    _ = next(address_reader)
    for address in address_reader:
        constituent_id = address[1]
        _address = parse_address(address)
        # will fail on duplicate constituent_id
        addresses[constituent_id] += [asdict(Address(**_address))]

contacts = defaultdict(dict)
with open(CONTACTS_DATA, 'r') as f:
    fieldnames = ['record_type', 'constituent_id', 'type', 'text']
    contact_reader = DictReader(f, fieldnames=fieldnames)
    _ = next(contact_reader)
    for contact in contact_reader:
        constituent_id = contact['constituent_id']
        if contact['type'] == 'EMAIL':
            try:
                contacts[constituent_id]['emails'] += [contact['text']]
            except KeyError:
                contacts[constituent_id]['emails'] = [contact['text']]
        else:
            try:
                contacts[constituent_id]['phones'] += [contact['text']]
            except KeyError:
                contacts[constituent_id]['phones'] = [contact['text']]

@dataclass
class Constituent:
    constituentId: int
    fullName: str
    birthday: str
    isDeceased: bool
    isNoMail: bool


def parse_constituent(constituent: List) -> Dict:
    _birthday = str(int(float(constituent[10]))) if constituent[10] else ''
    _birthday_year = _birthday[:4]
    _birthday_month = _birthday[4:6]
    _birthday_day = _birthday[6:8]
    return {
        "constituentId": constituent[1],
        "fullName": ' '.join([
            constituent[4],
            constituent[5],
            constituent[6]
        ]),
        "birthday": "-".join([_birthday_year, _birthday_month, _birthday_month]),
        "isDeceased": True if constituent[11] == 'X' else False,
        "isNoMail": True if constituent[12] == 'X' else False,
        }


constituents = defaultdict(dict)
with open(CONSTITUENTS_DATA, 'r') as f:
    constituent_reader = reader(f)
    # skip header row
    _ = next(constituent_reader)
    for constituent in constituent_reader:
        constituent_id = constituent[1]
        _constituent = parse_constituent(constituent)
        # will fail on duplicate constituent_ids
        constituents[constituent_id] = asdict(Constituent(**_constituent))

# merging not tested, consider pseudocode
for k, v in addresses:
    constituents[k]['addresses'] = v

for k, v in contacts:
    constituents[k] = v
