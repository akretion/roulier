"""Implementation of Laposte Api."""
from roulier.api import BaseApi
from roulier.api import ApiPackingSlip
from roulier.api import ApiParcelDocument
from roulier.api import ApiParcel

LAPOSTE_LABEL_FORMAT = (
    "ZPL_10x15_203dpi",
    "ZPL_10x15_300dpi",
    "DPL_10x15_203dpi",
    "DPL_10x15_300dpi",
    "PDF_10x15_300dpi",
    "PDF_A4_300dpi",
)


class LaposteFrApiParcel(ApiParcel):
    def _service(self):
        schema = super()._service()
        schema["labelFormat"]["allowed"] = list(LAPOSTE_LABEL_FORMAT) + [
            "PDF",
            "ZPL",
            "DPL",
        ]
        schema["labelFormat"]["default"] = "ZPL_10x15_203dpi"
        schema["labelFormat_x"] = {"default": 0}
        schema["labelFormat_y"] = {"default": 0}
        schema["labelFormat"].update({"required": True, "empty": False})
        schema["product"].update({"required": True, "empty": False})
        schema["pickupLocationId"] = {
            "default": "",
            # 'description': """Si productCode = A2P, BPR, ACP, CDI, CMT, BDP. "
            # "Identifiant du point de retrait "
            # "(dans le cas d’une livraison Colissimo hors domicile)"""
        }
        schema["orderNumber"] = {"default": ""}
        schema["commercialName"] = {
            "default": "",
            # 'description':
            # """Obligatoire pour les produits DOM, DOS, BPR, A2P. "
            # "Nom commercial du chargeur qui sera affiché dans "
            # "les notifications par email aux destinataires des colis"""
        }
        schema["returnTypeChoice"] = {
            "default": "",
            # 'description':
            # """Obligatoire pour certains colis à l’international, "
            # "selon les zones tarifaires applicables. Indique si "
            # "le colis doit être retourné à l’expéditeur en cas de "
            # "non distribution du colis"""
        }
        schema["returnType"] = {
            "default": "",
            # 'description':
            # """Utilisé pour le Colissimo Retour uniquement. "
            # "Définit le mode de transmission de l’étiquette"""
        }
        # schema['reference1'].update({
        #     'description': """Référence expediteur ('Réf client')"""
        # })
        # schema['reference2'].update({
        #     'description': """Référence destinataire ('Réf destinataire')"""
        # })
        return schema

    def _address(self):
        schema = super()._address()
        schema["country"].update({"required": True, "empty": False})
        schema["zip"].update({"required": True, "empty": False})
        schema["city"].update({"required": True, "empty": False})
        schema["street0"] = {
            "required": False,
            "empty": True,
            # 'description': """Entrée, bâtiment, immeuble, résidence. """
            #                """Non utilisé pour la Belgique."""
        }
        schema["street2"].update(
            {
                "default": ""
                # , 'description': 'Etage, couloir, escalier, appart.'
            }
        )
        schema["street1"].update(
            {
                "required": True,
                "empty": False,
                # 'description': 'Numéro et libellé de voie. Ex : 5 rue du Bellay'
            }
        )
        schema["street3"] = {
            "default": "",
            # 'description': """Lieu dit ou autre mention. """
            #                """Non utilisé pour la Belgique."""
        }
        # 'description': """Code porte 1"""
        schema["door1"] = {"default": ""}
        # 'description': """Code porte 2"""
        schema["door2"] = {"default": ""}
        # 'description': """Interphone"""
        schema["intercom"] = {"default": ""}

        return schema

    def _from_address(self):
        schema = super()._from_address()
        return schema

    def _to_address(self):
        schema = super()._to_address()
        schema["firstName"] = {
            "default": "",
        }
        # 'description': """Prénom. Obligatoire pour So Colissimo"""
        return schema

    def _parcel(self):
        schema = super()._parcel()
        schema["nonMachinable"] = {
            "type": "boolean",
            "default": False,
            # 'description': """Passer à true pour indiquer que le "
            # "format du colis est non standard"""
        }
        schema["instructions"] = {
            "default": "",
            # 'description': """Indications complémentaires pour la livraison"""
        }
        schema["insuranceValue"] = {
            "type": "number",
            "default": 0,
            # 'description': """Valeur assurée. Max= 1500€ "
            # "Passer 1230 pour 12,30€ Cette valeur sera arrondie "
            # "à l’entier le plus proche (Ex : 12 euros si 1232 est envoyé) "
            # "Par défaut, renseigner « 0 » (zéro)"""
        }
        schema["recommendationLevel"] = {
            "default": "",
            # 'description': """Niveau de recommandation "
            # "(cf. III.2) Peut valoir « R1 », ou « R2 », ou « R3 »"""
        }
        schema["cod"] = {
            "type": "boolean",
            "default": False,
            # 'description': """Passer à true si la livraison doit se faire contre remboursement."""
        }
        schema["codAmount"] = {
            "type": "number",
            "default": 0,
            # 'description': """Montant attendu lors de la "
            # "livraison contre remboursement. Par défaut, renseigner "
            # "« 0 » (zéro)"""
        }
        schema["ftd"] = {
            "type": "boolean",
            "default": False,
            # 'description': """Pour les envois vers "
            # "l’Outre-Mer uniquement Indique si le colis est franc de taxes "
            # "et de droits."""
        }
        schema["totalAmount"] = {
            "default": "",
            # 'description': 'Needed for cn23'
        }
        schema["customs"] = {"type": "dict", "schema": self._customs()}
        schema["pickupLocationId"] = {
            "default": "",
            # 'description': """Si productCode = A2P, BPR, ACP, CDI, CMT, BDP. "
            # "Identifiant du point de retrait "
            # "(dans le cas d’une livraison Colissimo hors domicile)"""
        }
        return schema

    def _auth(self):
        schema = super()._auth()
        schema["login"].update({"required": True, "empty": False})
        schema["password"]["required"] = False
        return schema

    def _customs(self):
        schema = {
            "articles": {
                "type": "list",
                "schema": {
                    "type": "dict",
                    "schema": {
                        "description": {"default": "", "maxlength": 64},
                        "quantity": {"default": ""},
                        "weight": {"type": "float", "default": 0.0},
                        "value": {"default": ""},
                        "hsCode": {
                            "regex": "^(\\d{6}|\\d{8}|\\d{10})$",
                            "required": False,
                        },
                        "originCountry": {
                            "type": "string",
                            "required": False,
                            "default": "",
                            "regex": "^[a-zA-Z]{2}$",
                        },
                        "currency": {"default": "EUR", "regex": "^\\w{3}$"},
                        "artref": {"regex": "^\\w{1,44}$"},
                        "originalIdent": {"type": "string", "regex": "^[a-zA-Z]{1}$"},
                        "vatAmount": {"type": "float", "required": False},
                        "customsFees": {"type": "float", "required": False},
                    },
                },
                "default": [],
            },
            "category": {
                "required": True,
                "type": "integer",
                "maxlength": 1,
            },
            "explanations": {"required": False, "type": "string", "regex": "^.{0,35}$"},
            "original": {
                "type": "dict",
                "schema": {
                    "originalIdent": {"type": "string", "regex": "^[a-zA-Z]{1}$"},
                    "originalInvoiceNumber": {"type": "string", "regex": "^.{1,35}$"},
                    "originalInvoiceDate": {
                        "type": "string",
                        "regex": "^\\d{4}-\\d{2}-\\d{2}$",
                    },
                    "originalParcelNumber": {"type": "string", "regex": "^.{1,35}$"},
                },
            },
            "importersReference": {"type": "string", "regex": "^.{0,35}$"},
            "importersContact": {
                "type": "string",
                "regex": "^.{0,35}$",
                "required": False,
            },
            "officeOrigin": {"type": "string", "regex": "^.{0,35}$", "required": False},
            "comments": {"type": "string", "regex": "^.{0,35}$", "required": False},
            "description": {
                "type": "string",
                "regex": "^.{1,}$",
            },
            "invoiceNumber": {
                "type": "string",
                "regex": "^.{0,35}$",
                "required": False,
            },
            "licenceNumber": {
                "type": "string",
                "regex": "^.{0,35}$",
                "required": False,
            },
            "certificatNumber": {
                "type": "string",
                "regex": "^.{0,35}$",
                "required": False,
            },
            "importerAddress": {
                "type": "dict",
                "schema": {
                    "company": {
                        "type": "string",
                        "regex": "^.{0,35}$",
                        "required": False,
                    },
                    "lastName": {"regex": "^[a-zA-Z]{0,35}$", "required": False},
                    "fistName": {"regex": "^[a-zA-Z]{0,29}$", "required": False},
                    "street0": {
                        "type": "string",
                        "regex": "^.{0,35}$",
                        "required": False,
                    },
                    "street1": {
                        "type": "string",
                        "regex": "^.{0,35}$",
                        "required": False,
                    },
                    "street2": {
                        "type": "string",
                        "regex": "^.{0,35}$",
                        "required": False,
                    },
                    "street3": {
                        "type": "string",
                        "regex": "^.{0,35}$",
                        "required": False,
                    },
                    "country": {
                        "type": "string",
                        "regex": "^[a-zA-Z]{2}$",
                        "required": False,
                    },
                    "city": {"type": "string", "regex": "^.{0,35}$", "required": False},
                    "zip": {
                        "type": "string",
                        "regex": "^[a-z-A-Z0-9]{5}$",
                        "required": False,
                    },
                    "phone": {
                        "type": "string",
                        "regex": "^.{0,15}$",
                        "required": False,
                    },
                    "mobile": {
                        "type": "string",
                        "regex": "^(.{0}|.{10})$",
                        "required": False,
                    },
                    "door1": {
                        "type": "string",
                        "regex": "^.{0,8}$",
                        "required": False,
                    },
                    "door2": {
                        "type": "string",
                        "regex": "^.{0,8}$",
                        "required": False,
                    },
                    "email": {
                        "type": "string",
                        "regex": "^\\w*@\\w*\.\\w*$",
                        "required": False,
                        "maxlength": 80,
                    },
                    "intercom": {
                        "type": "string",
                        "regex": "^.{0,30}$",
                        "required": False,
                    },
                    "language": {
                        "type": "string",
                        "regex": "^[a-zA-Z]{2}$",
                        "required": False,
                        "default": "FR",
                    },
                },
            },
        }
        return schema

    def _schemas(self):
        schemas = super()._schemas()
        return schemas


class LaposteFrApiPackingSlip(ApiPackingSlip):
    def _auth(self):
        schema = super()._auth()
        schema["login"].update({"required": True, "empty": False})
        schema["password"]["required"] = False
        return schema


class LaposteFrApiParcelDocument(ApiParcelDocument):
    def _auth(self):
        schema = super()._auth()
        schema["app_key"] = {
            "type": "string",
            "regex": "^.{0,8}$",
            "required": False,
        }
        schema["password"]["required"] = False
        return schema

    def _document_type(self):
        schema = super()._document_type()
        schema["allowed"] = [
            # for creation:
            "CERTIFICATE_OF_ORIGIN",  # Certificat d'origine
            "EXPORT_LICENSE",  # Licence d'exportation
            "COMMERCIAL_INVOICE",  # Facture du colis
            "OTHER",  # Autre
            # existing documents can have those types below too, but encoder is only for creation
            # "C50",  # C50
            # "COMPENSATION",  # Bilan d’indemnisation
            # "DAU",  # Facture de droits et taxes
            # "DELIVERY_CERTIFICATE",  # Attestation de livraison
            # "SIGNATURE",  # Preuve de livraison
        ]
        return schema

    def _schemas(self):
        schemas = super()._schemas()
        schemas["service"]["language"] = {
            "default": "fr_FR",
            "type": "string",
            "allowed": [
                "fr_FR",
                "en_GB",
                "es_ES",
                "de_DE",
                "it_IT",
            ],
            "required": False,
        }
        if self.current_action in ("create_document", "update_document"):
            schemas["service"]["account_number"] = {
                "schema": {"type": "string", "empty": False, "default": ""},
                "required": True,
            }
            # Liste des colis suiveurs du colis maître dans le cas des expéditions
            # multi colis. les colis sont séparés par une virgule
            schemas["service"]["parcelNumberList"] = {
                "schema": {"type": "string", "empty": True, "default": ""},
                "required": False,
            }
        return schemas
