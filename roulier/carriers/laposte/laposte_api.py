# -*- coding: utf-8 -*-
"""Implementation of Laposte Api."""
from roulier.api import Api

LAPOSTE_LABEL_FORMAT = (
    'ZPL_10x15_203dpi',
    'ZPL_10x15_300dpi',
    'DPL_10x15_203dpi',
    'DPL_10x15_300dpi',
    'PDF_10x15_300dpi',
    'PDF_A4_300dpi',
)


class LaposteApi(Api):
    def _service(self):
        schema = super(LaposteApi, self)._service()
        schema['labelFormat']['allowed'] = (
            list(LAPOSTE_LABEL_FORMAT) + ["PDF", "ZPL", "DPL"])
        schema['labelFormat']['default'] = 'ZPL_10x15_203dpi'
        schema['labelFormat_x'] = {'default': 0}
        schema['labelFormat_y'] = {'default': 0}
        schema['labelFormat'].update({'required': True, 'empty': False})
        schema['product'].update({'required': True, 'empty': False})
        schema['pickupLocationId'] = {
            'default': '', 'description':
            """Si productCode = A2P, BPR, ACP, CDI, CMT, BDP. "
            "Identifiant du point de retrait "
            "(dans le cas d’une livraison Colissimo hors domicile)"""}
        schema['totalAmount'] = {
            'default': '', 'description': 'Needed for cn23'}
        schema['orderNumber'] = {'default': ''}
        schema['commercialName'] = {
            'default': '', 'description':
            """Obligatoire pour les produits DOM, DOS, BPR, A2P. "
            "Nom commercial du chargeur qui sera affiché dans "
            "les notifications par email aux destinataires des colis"""}
        schema['returnTypeChoice'] = {
            'default': '', 'description':
            """Obligatoire pour certains colis à l’international, "
            "selon les zones tarifaires applicables. Indique si "
            "le colis doit être retourné à l’expéditeur en cas de "
            "non distribution du colis"""}
        schema['returnType'] = {
            'default': '', 'description':
            """Utilisé pour le Colissimo Retour uniquement. "
            "Définit le mode de transmission de l’étiquette"""}
        schema['reference1'].update({
            'description': """Référence expediteur ('Réf client')"""
        })
        schema['reference2'].update({
            'description': """Référence destinataire ('Réf destinataire')"""
        })
        return schema

    def _address(self):
        schema = super(LaposteApi, self)._address()
        schema['country'].update({'required': True, 'empty': False})
        schema['zip'].update({'required': True, 'empty': False})
        schema['city'].update({'required': True, 'empty': False})
        schema['street0'] = {
            'required': False, 'empty': True,
            'description': """Entrée, bâtiment, immeuble, résidence. """
                           """Non utilisé pour la Belgique."""}
        schema['street2'].update({
            'default': '', 'description': 'Etage, couloir, escalier, appart.'})
        schema['street1'].update({
            'required': True, 'empty': False,
            'description': 'Numéro et libellé de voie. Ex : 5 rue du Bellay'})
        schema['street3'] = {
            'default': '',
            'description': """Lieu dit ou autre mention. """
                           """Non utilisé pour la Belgique."""}
        schema['door1'] = {'default': '', 'description': """Code porte 1"""}
        schema['door2'] = {'default': '', 'description': """Code porte 2"""}
        schema['intercom'] = {'default': '', 'description': """Interphone"""}

        return schema

    def _from_address(self):
        schema = super(LaposteApi, self)._from_address()
        return schema

    def _to_address(self):
        schema = super(LaposteApi, self)._to_address()
        schema['firstName'] = {
            'default': '',
            'description': """Prénom. Obligatoire pour So Colissimo"""}
        return schema

    def _parcel(self):
        schema = super(LaposteApi, self)._parcel()
        schema['nonMachinable'] = {
            'type': 'boolean', 'default': False,
            'description': """Passer à true pour indiquer que le "
            "format du colis est non standard"""}
        schema['instructions'] = {
            'default': '', 'description': """Indications complémentaires "
            "pour la livraison"""}
        schema['insuranceValue'] = {
            'type': 'number', 'default': 0,
            'description': """Valeur assurée. Max= 1500€ "
            "Passer 1230 pour 12,30€ Cette valeur sera arrondie "
            "à l’entier le plus proche (Ex : 12 euros si 1232 est envoyé) "
            "Par défaut, renseigner « 0 » (zéro)"""}
        schema['recommendationLevel'] = {
            'default': '', 'description': """Niveau de recommandation "
            "(cf. III.2) Peut valoir « R1 », ou « R2 », ou « R3 »"""}
        schema['cod'] = {
            'type': 'boolean', 'default': False,
            'description': """Passer à true si la livraison doit se "
            "faire contre remboursement."""}
        schema['codAmount'] = {
            'type': 'number', 'default': 0,
            'description': """Montant attendu lors de la "
            "livraison contre remboursement. Par défaut, renseigner "
            "« 0 » (zéro)"""}
        schema['ftd'] = {
            'type': 'boolean', 'default': False,
            'description': """Pour les envois vers "
            "l’Outre-Mer uniquement Indique si le colis est franc de taxes "
            "et de droits."""}
        return schema

    def _auth(self):
        schema = super(LaposteApi, self)._auth()
        schema['login'].update({'required': True, 'empty': False})
        schema['password']['required'] = False
        return schema

    def _customs(self):
        schema = {
            'category': {'default': ''},
            'articles': {
                'type': 'list',
                'schema': {
                    'quantity': {'default': ''},
                    'weight': {'type': 'float', 'default': 0.0},
                    'description': {'default': ''},
                    'hs': {'default': ''},
                    'value': {'default': ''},
                    'originCountry': {'default': ''}
                },
                'default': []
            }
        }
        return schema

    def _schemas(self):
        schemas = super(LaposteApi, self)._schemas()
        schemas['customs'] = self._customs()
        return schemas
