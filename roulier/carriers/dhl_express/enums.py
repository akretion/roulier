# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from enum import Enum

from ...enums import UoM


class Format(Enum):
    PDF = "PDF"
    ZPL = "ZPL"
    DPL = "LP2"
    EPL = "EPL"


class DocumentFormat(Enum):
    PDF = "PDF"
    PNG = "PNG"
    GIF = "GIF"
    TIFF = "TIFF"
    JPEG = "JPEG"


class AccountType(Enum):
    SHIPPER = "shipper"
    PAYER = "payer"
    DUTIES_AND_TAXES = "duties-taxes"


class ReferenceType(Enum):
    AAO = "AAO"
    CU = "CU"
    FF = "FF"
    FN = "FN"
    IBC = "IBC"
    LLR = "LLR"
    OBC = "OBC"
    PRN = "PRN"
    ACP = "ACP"
    ACS = "ACS"
    ACR = "ACR"
    CDN = "CDN"
    STD = "STD"
    CO = "CO"
    AFM = "AFM"


class UoMType(Enum):
    METRIC = "metric"
    IMPERIAL = "imperial"


class ProductUoM(Enum):
    BOX = "BOX"
    _2GM = "2GM"
    M3 = "M3"
    DPR = "DPR"
    DOZ = "DOZ"
    PCS = "PCS"
    GM = "GM"
    GRS = "GRS"
    KG = "KG"
    M = "M"
    _3GM = "3GM"
    X = "X"
    NO = "NO"
    PRS = "PRS"
    CM2 = "CM2"
    _2M2 = "2M2"
    _3M2 = "3M2"
    M2 = "M2"
    _4M2 = "4M2"
    CM = "CM"
    CONE = "CONE"
    CT = "CT"
    EA = "EA"
    LBS = "LBS"
    RILL = "RILL"
    ROLL = "ROLL"
    SET = "SET"
    TU = "TU"
    KM = "KM"
    IN = "IN"
    FT = "FT"
    YD = "YD"
    MI = "MI"
    LTR = "LTR"
    MMQ = "MMQ"
    CM3 = "CM3"
    DMQ = "DMQ"
    MLT = "MLT"
    CLT = "CLT"
    DLT = "DLT"
    INQ = "INQ"
    FT3 = "FT3"
    YD3 = "YD3"
    GLI = "GLI"
    GLL = "GLL"
    PT = "PT"
    PTI = "PTI"
    QTI = "QTI"
    PTL = "PTL"
    QTL = "QTL"
    PTD = "PTD"
    OZI = "OZI"
    J57 = "J57"
    NM3 = "NM3"
    SM3 = "SM3"
    TNE = "TNE"
    LB = "LB"
    ONZ = "ONZ"
    CEL = "CEL"

    @staticmethod
    def from_uom(uom: UoM) -> "ProductUoM":
        return {
            UoM.CGM: ProductUoM._2GM,
            UoM.MTQ: ProductUoM.M3,
            UoM.DPR: ProductUoM.DPR,
            UoM.DZN: ProductUoM.DOZ,
            UoM.C62: ProductUoM.PCS,
            UoM.GRM: ProductUoM.GM,
            UoM.GRO: ProductUoM.GRS,
            UoM.KGM: ProductUoM.KG,
            UoM.MTR: ProductUoM.M,
            UoM.MGM: ProductUoM._3GM,
            UoM.NAR: ProductUoM.NO,
            UoM.PR: ProductUoM.PRS,
            UoM.CMK: ProductUoM.CM2,
            UoM.FTK: ProductUoM._2M2,
            UoM.INK: ProductUoM._3M2,
            UoM.MTK: ProductUoM.M2,
            UoM.YDK: ProductUoM._4M2,
            UoM.CMT: ProductUoM.CM,
            UoM.CJ: ProductUoM.CONE,
            UoM.CTM: ProductUoM.CT,
            UoM.LBR: ProductUoM.LBS,
            UoM.RO: ProductUoM.ROLL,
            UoM.KTM: ProductUoM.KM,
            UoM.INH: ProductUoM.IN,
            UoM.FOT: ProductUoM.FT,
            UoM.YRD: ProductUoM.YD,
            UoM.SMI: ProductUoM.MI,
            UoM.FTQ: ProductUoM.FT3,
            UoM.YDQ: ProductUoM.YD3,
            UoM.LBR: ProductUoM.LB,
        }.get(uom, getattr(ProductUoM, uom.value, ProductUoM.PCS))


class ExportType(Enum):
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    RETURN = "return"
    USED_EXHIBITION_GOODS_TO_ORIGIN = "used_exhibition_goods_to_origin"
    INTERCOMPANY_USE = "intercompany_use"
    COMMERCIAL_PURPOSE_OR_SALE = "commercial_purpose_or_sale"
    PERSONAL_BELONGINGS_OR_PERSONAL_USE = "personal_belongings_or_personal_use"
    SAMPLE = "sample"
    GIFT = "gift"
    RETURN_TO_ORIGIN = "return_to_origin"
    WARRANTY_REPLACEMENT = "warranty_replacement"
    DIPLOMATIC_GOODS = "diplomatic_goods"
    DEFENCE_MATERIAL = "defence_material"
