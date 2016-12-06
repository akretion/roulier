^XA
^DFR:ALLOIN.ZPL^FS
^PR3
^POI
^MD12
^MNY

^LH9,9^FS

^PR3
^POI
^MD12
^MNY

^LH14,14^FS
^FO14,14^XGLOGOKN.GRF,1,1^FS
^FO0,135^GB640,2^FS
^FO0,174^GB640,2^FS
^FO640,135^GB2,116^FS
^FO0,212^GB785,2^FS
^FO640,252^GB145,2^FS
^FO436,105^A0N,30,30^FDEtiquette CLIENT^FS
^FO19,147^A0N,30,30^FD{{ service.kuehneOfficeName }}^FS
^FO19,186^A0N,30,30^FDEXP.: {{ sender_address.company }}^FS
^FO655,184^A0N,30,30^FD{{ service.labelShippingDate }}^FS
^FO669,284^A0N,30,30^FD{% if service.epalQuantity %}EUR {{ service.epalQuantity }}{% endif %}^FS
^FO67,261^A0N,139,139^FD{{ service.shippingOffice }}^FS
^FO387,261^A0N,75,75^FD{{ service.shippingRound }}^FS


^FO19,422^A0N,30,30^FDDest:^FS
^FO88,422^A0N,32,32^FD{{ recipient_address.name }}^FS

^FO19,450^A0N,32,32^FD{{ recipient_address.street1 }}^FS
^FO19,479^A0N,32,32^FD{{ recipient_address.street2 }}^FS
^FO19,513^A0N,32,32^FD{{ recipient_address.country.upper() }} {{ recipient_address.zip }} {{ recipient_address.city }}^FS
^FO19,542^A0N,30,30^FDNo Exp :                /^FS
^FO19,576^A0N,30,30^FDRef Exped.: {{ service.shippingName }}^FS
^FO19,615^A0N,30,30^FDDesc.: {{ service.goodsName }}^FS

^FO36,644^A0N,30,30^FD"
^FO19,678^A0N,30,30^FDNb Colis: {{ service.mhuQuantity }}^FS
^FO19,712^A0N,32,32^FDPoids: {{ service.weight }} Kg^FS
^FO19,746^A0N,30,30^FDVol. Decl.: {{ service.volume }} m3^FS
^FO436,542^A0N,30,30^FDEtiquette :^FS
^FO280,1008^GB504,2^FS
^FO280,1008^GB2,126^FS
^FO280,1134^GB504,2^FS
^FO532,1008^GB2,126^FS
^FO785,1008^GB2,127^FS
{% if service.labelDeliveryContract == 'EXPORT' %}^FO28,1037^A0N,62,62^FD{{ service.exportHub }}^FS{% endif %}
{% if service.labelDeliveryContract in ['C', 'D'] %}
^FO290,1037^A0N,75,75^FD{{ service.labelDeliveryContract }}^FS
^FO385,1067^A0N,60,60^FD{% if service.labelDeliveryContract == 'D' %}{{ service.wishedDate }}{% endif %}^FS
^FO532,1008^GB252,126,116^FS
{% else %}
^FO280,1008^GB252,126,116^FS
^FO555,1054^A0N,65,65^FD{{ service.labelDeliveryContract }}^FS
{% endif %}

^PQ1,0,1,Y
^XZ


^XA

^XFALLOIN.ZPL^FS

^FO519,582^A0N,52,52^FD{{ parcel.number }}^FS
^BY3^FO67,804^BCN,154,Y,N,N,A^FD{{ parcel.barcode }}^FS
^BY3^FO670,300^BCR,90,Y,N,N,A^FD{{ parcel.barcode }}^FS


^XZ
