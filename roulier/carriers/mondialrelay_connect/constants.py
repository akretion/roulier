"""Constants for Mondial Relay Connect API (Web Service Dual Carrier).

Reference: Mondial Relay "Connect" REST API, ShipmentCreationRequest.
"""

# XML namespace declared in the Connect API request XSD.
NS_REQUEST = "http://www.example.org/Request"

# API version sent in the request Context.
VERSION_API = "1.0"

# Delivery modes (DeliveryMode@Mode). Non exhaustive, the most common ones.
DELIVERY_HOME = "HOM"  # home delivery
DELIVERY_HOME_PLUS = "HOC"  # home delivery, heavy/bulky
DELIVERY_POINT_RELAIS = "24R"  # pickup point (requires a Location, e.g. "FR-66974")
DELIVERY_LOCKER = "24L"  # locker
DELIVERY_DRIVE = "DRI"  # drive

DELIVERY_MODES = (
    DELIVERY_HOME,
    DELIVERY_HOME_PLUS,
    DELIVERY_POINT_RELAIS,
    DELIVERY_LOCKER,
    DELIVERY_DRIVE,
)

# Collection modes (CollectionMode@Mode).
COLLECTION_MERCHANT = "CCC"  # collected at the merchant
COLLECTION_POINT_RELAIS = "REL"  # dropped at a pickup point

COLLECTION_MODES = (
    COLLECTION_MERCHANT,
    COLLECTION_POINT_RELAIS,
)

# Output types (OutputOptions/OutputType).
OUTPUT_PDF_URL = "PdfUrl"
OUTPUT_ZPL = "ZplCode"
OUTPUT_IPL = "IplCode"

OUTPUT_TYPES = (
    OUTPUT_PDF_URL,
    OUTPUT_ZPL,
    OUTPUT_IPL,
)

# Output formats (OutputOptions/OutputFormat). The accepted values depend on the
# output type; these are the most common ones documented for the dual carrier API.
OUTPUT_FORMATS = (
    "10x15",
    "A4",
    "A5",
    "Generic_PDF_10x15_300dpi",
    "Generic_ZPL_10x15_203dpi",
    "Generic_ZPL_10x15_300dpi",
    "Generic_IPL_10x15_203dpi",
    "Generic_IPL_10x15_300dpi",
)
