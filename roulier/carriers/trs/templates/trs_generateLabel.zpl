^XA

^FX Grand cadre
^FO50,10^GB1000,1200,3^FS

^FX Expediteur
^CF0,40
^FO70,20^FD{{ sender_address.company }}^FS
^FO50,10^GB1000,50,3^FS

^FX Num colis et poids
^FO100,290^FDColis  {{ service.reference2 }}^FS
^FO100,340^FDPoids  {{ parcel.weight }}^FS
^FO80,270^GB180,120,3^FS

^FX Adresse
^FO320,130^FD{{ receiver_address.name }}^FS
^FO320,190^FD{{ receiver_address.street1 }}^FS
^FO320,250^FD{{ receiver_address.street2 }}^FS
^FO320,310^FD{{ receiver_address.zipCode }}^FS
^FO620,310^FD{{ receiver_address.city }}^FS
^FO300,90^GB750,300,3^FS

^FO320,410^FDTel: {{ receiver_address.phone }}^FS

^FX Ref, commentaires
^FO80,700^FDReference / Commentaires: ^FS
^FO80,720^FD{{ service.reference3 }} ^FS
^FO50,680^GB1000,0,3^FS


^FX Code barre
^BY3,1,150
^FO80,480^B3^FD{{ service.reference1 }}^FS


^FX Departement
^CF0,160
^FO100,120^FD{{ receiver_address.dept }}}^FS
^FO80,90^GB180,150,3^FS

^XZ
