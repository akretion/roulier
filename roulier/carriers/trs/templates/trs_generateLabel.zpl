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
^FO40,270^GB180,120,3^FS

^FX Adresse
^FO300,130^FD{{ to_address.name }}^FS
^FO300,190^FD{{ to_address.street1 }}^FS
^FO300,250^FD{{ to_address.street2 }}^FS
^FO300,310^FD{{ to_address.zipCode }}^FS
^FO400,310^FD{{ to_address.city }}^FS
^FO280,90^GB500,300,3^FS

^FO300,410^FDTel: {{ to_address.phone }}^FS

^FX Ref, commentaires
^FO60,700^FDReference / Commentaires: ^FS
^FO60,740^FD{{ service.reference3 }} ^FS
^FO30,680^GB800,0,3^FS


^FX Code barre
^BY3,1,150
^FO60,480^B3^FD{{ service.shippingId }}^FS


^FX Departement
^CF0,160
^FO60,100^FD{{ to_address.dept }}^FS
^FO40,90^GB180,150,3^FS

^XZ
