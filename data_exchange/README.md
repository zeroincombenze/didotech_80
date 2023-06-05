Data Exchange
=============

Module gives possibility to exchange data between various Odoo installations


How it works
------------

Exchange data requires that there is a possibility to exchange partners and products between databases

    Search if partner exists in second database (the key is VAT number)
    If partner exists, write in local database the id of the partner on the other side.
    If not, add partner on the other side and write in local database the id of created partner


Purchase Order in db One became Sale Order in db Two



Contributors
------------

Andrei Levin <andrei.levin@didotech.com>
