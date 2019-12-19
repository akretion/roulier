from .dpd_api import DpdApi

DPD_INFOS = {
   'createShipmentWithLabels': {
       'api': DpdApi,
       'endpoint': 'https://ws.dpd.fr/backend/api/integration/public/',
       'service': 'shipment/save/print',
   }
}