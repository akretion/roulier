^XA
^DFR:ALLOIN.ZPL^FS
^PR3
^POI
^MD12
^MNY

^FO30,30^GFA,3230,3230,38,,{{ service.labelLogo or ''}}^FS

^LH9,9^FS

^PR3
^POI
^MD12
^MNY

^LH14,14^FS
^FO14,14^XGLOGOKN.GRF,1,1^FS
^FO0,130^GB780,2^FS
^FO0,177^GB780,2^FS
^FO0,260^GB785,2^FS
^FO592,105^A0N,30,30^FDEtiquette CLIENT^FS
^FO5,145^A0N,32,32^FD{{ service.kuehneOfficeName }}^FS
^FO5,192^A0N,32,32^FDEXP :^FS
^FO75,192^A0N,32,32^FD{{ sender_address.name }}^FS
^FO75,222^A0N,32,32^FD{{ "%s / %s / %s" % (sender_address.country.upper(), sender_address.zip, sender_address.city) }}^FS
^FO5,275^A0N,32,32^FD{{ service.labelShippingDate }}^FS
^FO669,314^A0N,30,30^FD{% if service.epalQuantity %}EUR {{ service.epalQuantity }}{% endif %}^FS
^FO67,310^A0N,130,130^FD{{ service.shippingOffice }}^FS
^FO320,310^A0N,130,130^FD{{ service.shippingRound }}^FS


^FO19,450^A0N,32,32^FDDest:^FS
^FO85,450^A0N,32,32^FD{{ recipient_address.name }}^FS

^FO19,480^A0N,32,32^FD{{ recipient_address.street1 }}^FS
^FO19,510^A0N,32,32^FD{{ recipient_address.street2 }}^FS
^FO19,540^A0N,32,32^FD{{ recipient_address.country.upper() }} {{ recipient_address.zip }} {{ recipient_address.city }}^FS
^FO19,570^A0N,32,32^FDNo Exp :                /^FS
^FO19,600^A0N,32,32^FDRef Exped.: {{ service.shippingName }}^FS
^FO19,630^A0N,32,32^FDDesc.: {{ service.goodsName }}^FS

^FO36,660^A0N,32,32^FD"

^FO19,680^A0N,42,42^FDNo commande : {{ service.orderName }}^FS

^FO19,760^A0N,32,32^FDNb Colis: {{ service.mhuQuantity }}^FS
^FO19,790^A0N,32,32^FDPoids: {{ service.weight }} Kg^FS
^FO19,820^A0N,32,32^FDVol. Decl.: {{ service.volume }} m3^FS
^FO436,572^A0N,32,32^FDEtiquette :^FS
^FO280,1038^GB504,2^FS
^FO280,1038^GB2,126^FS
^FO280,1164^GB504,2^FS
^FO532,1038^GB2,126^FS
^FO785,1038^GB2,127^FS
{% if service.labelDeliveryContract == 'EXPORT' %}^FO28,1067^A0N,62,62^FD{{ service.exportHub }}^FS{% endif %}
{% if service.labelDeliveryContract in ['C', 'D'] %}
^FO290,1067^A0N,75,75^FD{{ service.labelDeliveryContract }}^FS
^FO385,1097^A0N,60,60^FD{% if service.labelDeliveryContract == 'D' %}{{ service.wishedDate }}{% endif %}^FS
^FO532,1038^GB252,126,116^FS
{% else %}
^FO280,1038^GB252,126,116^FS
^FO555,1084^A0N,65,65^FD{{ service.labelDeliveryContract }}^FS
{% endif %}

^PQ1,0,1,Y
^XZ


^XA

^XFALLOIN.ZPL^FS

^FO519,612^A0N,52,52^FD{{ parcel.number }}^FS
^BY3^FO67,890^BCN,100,Y,N,N,A^FD{{ parcel.barcode }}^FS
^BY3^FO670,330^BCR,90,Y,N,N,A^FD{{ parcel.barcode }}^FS


^XZ
