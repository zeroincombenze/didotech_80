# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010-2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


class fiscalcode(object):

    def codicefiscale(self, cognome, nome, giornonascita,
                       mesenascita, annonascita, sesso, cittanascita):

        MESI = 'ABCDEHLMPRST'
        CONSONANTI = 'BCDFGHJKLMNPQRSTVWXYZ'
        VOCALI = 'AEIOU'
        LETTERE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

        REGOLECONTROLLO = {
            'A': (0, 1), 'B': (1, 0), 'C': (2, 5), 'D': (3, 7),
            'E': (4, 9), 'F': (5, 13), 'G': (6, 15), 'H': (7, 17),
            'I': (8, 19), 'J': (9, 21), 'K': (10, 2), 'L': (11, 4),
            'M': (12, 18), 'N': (13, 20), 'O': (14, 11), 'P': (15, 3),
            'Q': (16, 6), 'R': (17, 8), 'S': (18, 12), 'T': (19, 14),
            'U': (20, 16), 'V': (21, 10), 'W': (22, 22), 'X': (23, 25),
            'Y': (24, 24), 'Z': (25, 23),
            '0': (0, 1), '1': (1, 0), '2': (2, 5), '3': (3, 7),
            '4': (4, 9), '5': (5, 13), '6': (6, 15), '7': (7, 17),
            '8': (8, 19), '9': (9, 21)
        }

        """Funzioni per il calcolo del C.F."""
        def _surname(stringa):
            """Ricava, da stringa, 3 lettere in base alla convenzione dei C.F.
            """
            cons = [c for c in stringa if c in CONSONANTI]
            voc = [c for c in stringa if c in VOCALI]
            chars = cons + voc
            if len(chars) < 3:
                chars += ['X', 'X']
            return chars[:3]

        def _name(stringa):
            """Ricava, da stringa, 3 lettere in base alla convenzione dei C.F.
            """
            cons = [c for c in stringa if c in CONSONANTI]
            voc = [c for c in stringa if c in VOCALI]
            if len(cons) > 3:
                cons = [cons[0]] + [cons[2]] + [cons[3]]
            chars = cons + voc
            if len(chars) < 3:
                chars += ['X', 'X']
            return chars[:3]

        def _datan(giorno, mese, anno, sesso):
            """Restituisce il campo data del CF."""
            chars = (list(anno[-2:]) + [MESI[int(mese) - 1]])
            gn = int(giorno)
            if sesso == 'F':
                gn += 40
            chars += list("%02d" % gn)
            return chars

        def _codicecontrollo(c):
            """Restituisce il codice di controllo, l'ultimo carattere del C.F.
            """
            sommone = 0
            for i, car in enumerate(c):
                j = 1 - i % 2
                sommone += REGOLECONTROLLO[car][j]
            resto = sommone % 26
            return [LETTERE[resto]]

        """Restituisce il C.F costruito sulla base degli argomenti."""
        nome = nome.upper()
        cognome = cognome.upper()
        sesso = sesso.upper()
        cittanascita = cittanascita.upper()
        chars = (_surname(cognome) + 
                 _name(nome) + 
                 _datan(giornonascita, mesenascita, annonascita, sesso) + 
                 list(cittanascita))
        chars += _codicecontrollo(chars)
        return ''.join(chars)
