^XA

^FO50,10^GB700,290,3^FS
^FO250,10^GB1,290,3^FS

^CF0,40
^FO400,20^FD{{ sender_address.company }}^FS
^FO250,50^GB500,1,3^FS

^FO280,060^FD{{ receiver_address.name }}^FS
^FO280,100^FD{{ receiver_address.street1 }}^FS
^FO280,140^FD{{ receiver_address.street2 }}^FS
^FO280,180^FD{{ receiver_address.zipCode }}^FS
^FO280,220^FD{{ receiver_address.city }}^FS
^FO280,260^FDRef: {{ service.reference1 }}^FS
^FO570,260^FDColi: {{ parcel.reference }}^FS

^CF0,190
^FO85,75^FD{{ receiver_address.dept }}^FS

^XZ