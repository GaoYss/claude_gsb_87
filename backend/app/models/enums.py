"""领域枚举与中文标签。

前端下拉字典统一由 /api/v1/meta/options 下发，避免前后端各维护一份。
"""

from enum import Enum


class LabeledEnum(str, Enum):
    """带中文标签的字符串枚举，子类只需实现 labels()。"""

    @classmethod
    def labels(cls) -> dict[str, str]:
        """值 -> 中文标签。"""
        raise NotImplementedError

    @classmethod
    def choices(cls) -> list[dict[str, str]]:
        """供前端下拉使用的 [{value, label}] 列表。"""
        return [{"value": value, "label": label} for value, label in cls.labels().items()]

    @classmethod
    def label_of(cls, value: str | None) -> str:
        if value is None:
            return ""
        return cls.labels().get(value, value)


class ReservoirStatus(LabeledEnum):
    """水库运行状态。"""

    NORMAL = "normal"
    ATTENTION = "attention"
    DANGER = "danger"
    OUT_OF_SERVICE = "out_of_service"

    @classmethod
    def labels(cls) -> dict[str, str]:
        return {
            cls.NORMAL.value: "运行正常",
            cls.ATTENTION.value: "需要关注",
            cls.DANGER.value: "存在险情",
            cls.OUT_OF_SERVICE.value: "停用报废",
        }


class SafetyClass(LabeledEnum):
    """大坝安全类别。"""

    CLASS_ONE = "class_one"
    CLASS_TWO = "class_two"
    CLASS_THREE = "class_three"

    @classmethod
    def labels(cls) -> dict[str, str]:
        return {
            cls.CLASS_ONE.value: "一类坝",
            cls.CLASS_TWO.value: "二类坝",
            cls.CLASS_THREE.value: "三类坝",
        }


class DamType(LabeledEnum):
    """坝型。"""

    HOMOGENEOUS_EARTH = "homogeneous_earth"
    EARTH_ROCK = "earth_rock"
    ROCKFILL = "rockfill"
    MASONRY = "masonry"
    CONCRETE = "concrete"
    OTHER = "other"

    @classmethod
    def labels(cls) -> dict[str, str]:
        return {
            cls.HOMOGENEOUS_EARTH.value: "均质土坝",
            cls.EARTH_ROCK.value: "土石坝",
            cls.ROCKFILL.value: "堆石坝",
            cls.MASONRY.value: "浆砌石坝",
            cls.CONCRETE.value: "混凝土坝",
            cls.OTHER.value: "其他坝型",
        }


class StructurePart(LabeledEnum):
    """检查部位 / 隐患类别：巡查项与隐患共用一套分类。"""

    DAM_BODY = "dam_body"
    SPILLWAY = "spillway"
    OUTLET = "outlet"
    SEEPAGE = "seepage"
    SLOPE = "slope"
    FACILITY = "facility"
    OTHER = "other"

    @classmethod
    def labels(cls) -> dict[str, str]:
        return {
            cls.DAM_BODY.value: "坝体",
            cls.SPILLWAY.value: "溢洪道",
            cls.OUTLET.value: "放水设施",
            cls.SEEPAGE.value: "渗流观测",
            cls.SLOPE.value: "库岸边坡",
            cls.FACILITY.value: "管理设施",
            cls.OTHER.value: "其他",
        }


class InspectionType(LabeledEnum):
    """巡查类型。"""

    DAILY = "daily"
    FLOOD_SEASON = "flood_season"
    SPECIAL = "special"
    EMERGENCY = "emergency"

    @classmethod
    def labels(cls) -> dict[str, str]:
        return {
            cls.DAILY.value: "日常巡查",
            cls.FLOOD_SEASON.value: "汛期巡查",
            cls.SPECIAL.value: "专项巡查",
            cls.EMERGENCY.value: "应急巡查",
        }


class Weather(LabeledEnum):
    """天气情况。"""

    SUNNY = "sunny"
    CLOUDY = "cloudy"
    OVERCAST = "overcast"
    DRIZZLE = "drizzle"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    SNOW = "snow"

    @classmethod
    def labels(cls) -> dict[str, str]:
        return {
            cls.SUNNY.value: "晴",
            cls.CLOUDY.value: "多云",
            cls.OVERCAST.value: "阴",
            cls.DRIZZLE.value: "小雨",
            cls.RAIN.value: "中雨",
            cls.HEAVY_RAIN.value: "大雨及以上",
            cls.SNOW.value: "降雪",
        }


class InspectionStatus(LabeledEnum):
    """巡查结论，由巡查项自动推导。"""

    NORMAL = "normal"
    ABNORMAL = "abnormal"

    @classmethod
    def labels(cls) -> dict[str, str]:
        return {
            cls.NORMAL.value: "全部正常",
            cls.ABNORMAL.value: "发现异常",
        }


class ItemResult(LabeledEnum):
    """单个部位的检查结果。"""

    NORMAL = "normal"
    ABNORMAL = "abnormal"

    @classmethod
    def labels(cls) -> dict[str, str]:
        return {
            cls.NORMAL.value: "正常",
            cls.ABNORMAL.value: "异常",
        }


class HazardSeverity(LabeledEnum):
    """隐患等级。"""

    GENERAL = "general"
    SERIOUS = "serious"
    MAJOR = "major"

    @classmethod
    def labels(cls) -> dict[str, str]:
        return {
            cls.GENERAL.value: "一般隐患",
            cls.SERIOUS.value: "较大隐患",
            cls.MAJOR.value: "重大隐患",
        }


class HazardSource(LabeledEnum):
    """隐患来源。"""

    INSPECTION = "inspection"
    SUPERVISION = "supervision"
    MASS_REPORT = "mass_report"
    MAINTENANCE = "maintenance"

    @classmethod
    def labels(cls) -> dict[str, str]:
        return {
            cls.INSPECTION.value: "巡查发现",
            cls.SUPERVISION.value: "上级检查",
            cls.MASS_REPORT.value: "群众反映",
            cls.MAINTENANCE.value: "日常维护发现",
        }


class HazardStatus(LabeledEnum):
    """隐患整改状态。"""

    REGISTERED = "registered"
    RECTIFYING = "rectifying"
    PENDING_ACCEPTANCE = "pending_acceptance"
    CLOSED = "closed"

    @classmethod
    def labels(cls) -> dict[str, str]:
        return {
            cls.REGISTERED.value: "待整改",
            cls.RECTIFYING.value: "整改中",
            cls.PENDING_ACCEPTANCE.value: "待验收",
            cls.CLOSED.value: "已销号",
        }


class RectificationAction(LabeledEnum):
    """整改跟踪记录类型。"""

    REGISTER = "register"
    MEASURE = "measure"
    PROGRESS = "progress"
    VERIFY = "verify"
    CLOSE = "close"

    @classmethod
    def labels(cls) -> dict[str, str]:
        return {
            cls.REGISTER.value: "登记发现",
            cls.MEASURE.value: "整改措施",
            cls.PROGRESS.value: "整改进展",
            cls.VERIFY.value: "验收意见",
            cls.CLOSE.value: "销号说明",
        }
