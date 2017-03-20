^XA

^FX Grand cadre
^FO30,15^GB800,1200,3^FS

^FX Expediteur
^CF0,40
^FO50,30^FD{{ from_address.company }}^FS
^FO30,15^GB800,50,3^FS

^FX Num colis et poids
^FO60,290^FDColis  {{ service.reference2 }}^FS
^FO60,340^FDPoids  {{ parcel.weight }}^FS
^FO40,270^GB200,120,3^FS

^FX Adresse
^FO300,130^TB,480,120^FD{{ to_address.name }}^FS
^FO300,220^TB,480,90^FD^FD{{ to_address.street1 }}^FS
^FO300,300^TB,480,90^FD^FD{{ to_address.street2 }}^FS
^FO300,380^FD{{ to_address.zip }}^FS
^FO400,420^FD{{ to_address.city }}^FS
^FO280,90^GB500,400,3^FS

^FO300,510^FDTel: {{ to_address.phone }}^FS

^FX Ref, commentaires
^FO60,800^FDReference / Commentaires: ^FS
^FO60,840^FD{{ service.reference1 }} ^FS
^FO60,880^FD{{ service.reference3 }} ^FS
^FO30,780^GB800,0,3^FS


^FX Code barre
^BY3,1,150
^FO60,580^B3^FD{{ service.shippingId }}^FS


^FX Departement
^CF0,160
^FO60,100^FD{{ to_address.dept }}^FS
^FO40,90^GB200,150,3^FS

^XZ
