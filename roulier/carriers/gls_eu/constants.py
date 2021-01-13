SERVICE_STANDARD = "Standard"
"""
Concerne les livraisons pour la France et l’international sans aucun service additionnel,
notre système utilisera le produit adapté en fonction de la destination :
BP (Business Parcel), EBP (Euro Business Parcel) ou GBP (Global Business Parcel)
"""

SERVICE_FDS = "flexDeliveryService"
"""
Pour les livraisons aux particuliers, GLS communique par mail et SMS avec le
destinataire afin d’offrir une interaction avec les modalités de livraison
"""

SERVICE_SHD = "shopdeliveryservice"
"""
livraison du colis dans un point relais
"""

SERVICE_SRS = "shopreturnservice"
"""
Dépôt du colis par le destinataire dans un point relais colis pour une livraison
en retour à l’adresse du donneur d’ordre, identifié par le shipperId utilisé
"""

SERVICE_PandS = "Pick&ShipService"
"""
enlèvement du colis par GLS à une adresse indiquée pour une livraison à une
autre adresse que celle du compte GLS donneur de l’ordre.
ATTENTION, l’une des deux adresses doit être localisé en France
"""

SERVICE_PandR = "Pick&ReturnService"
"""
enlèvement du colis par GLS à une adresse indiquée pour une livraison en
retour à l’adresse du donneur de l’ordre, identifié par le shipperId utilisé.
ATTENTION, l’une des deux adresses doit être localisé en France
"""

SERVICE_CHOICES = {
    SERVICE_STANDARD,
    SERVICE_FDS,
    SERVICE_SHD,
    SERVICE_SRS,
    SERVICE_PandS,
    SERVICE_PandR,
}

FR_ONLY_SERVICES_CHOICES = SERVICE_CHOICES - {
    SERVICE_STANDARD,
}
