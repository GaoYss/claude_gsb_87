"""演示数据：仅当水库台账为空时灌入，便于本地 / 容器一键体验。"""

import logging
from datetime import date, timedelta

from sqlalchemy import func, select

from app.db.base import now_local
from app.db.session import SessionLocal
from app.models import Hazard, HazardRectification, Inspection, InspectionItem, Reservoir

logger = logging.getLogger("app.seed")

# 水库台账演示数据
RESERVOIRS: list[dict] = [
    {
        "code": "SK-3301001",
        "name": "青龙湾水库",
        "region": "临江区",
        "basin": "清溪流域",
        "dam_type": "homogeneous_earth",
        "safety_class": "class_one",
        "status": "normal",
        "total_capacity": 1280.0,
        "normal_level": 86.5,
        "flood_limit_level": 84.0,
        "dam_height": 32.0,
        "dam_length": 480.0,
        "build_year": 1978,
        "manager": "临江区水利工程管理所",
        "manager_phone": "0571-88880001",
        "location": "临江区青溪镇青龙湾村",
        "remark": "小(1)型水库，坝顶道路畅通，设有渗流观测设施。",
    },
    {
        "code": "SK-3301002",
        "name": "石门坎水库",
        "region": "临江区",
        "basin": "清溪流域",
        "dam_type": "earth_rock",
        "safety_class": "class_two",
        "status": "normal",
        "total_capacity": 620.0,
        "normal_level": 128.0,
        "flood_limit_level": 126.0,
        "dam_height": 24.5,
        "dam_length": 320.0,
        "build_year": 1985,
        "manager": "临江区石门镇水利管理站",
        "manager_phone": "0571-88880002",
        "location": "临江区石门镇坎下村",
        "remark": "坝后设有排水棱体，汛期需加密巡查。",
    },
    {
        "code": "SK-3302001",
        "name": "白鹤塘水库",
        "region": "云岭县",
        "basin": "大溪流域",
        "dam_type": "homogeneous_earth",
        "safety_class": "class_two",
        "status": "attention",
        "total_capacity": 356.0,
        "normal_level": 210.5,
        "flood_limit_level": 208.0,
        "dam_height": 18.0,
        "dam_length": 260.0,
        "build_year": 1992,
        "manager": "云岭县白鹤塘水库管理站",
        "manager_phone": "0572-66660003",
        "location": "云岭县白鹤乡塘边村",
        "remark": "背水面坝脚曾出现渗水，已列入重点观察名单。",
    },
    {
        "code": "SK-3302002",
        "name": "长岭脚水库",
        "region": "云岭县",
        "basin": "大溪流域",
        "dam_type": "rockfill",
        "safety_class": "class_one",
        "status": "normal",
        "total_capacity": 890.0,
        "normal_level": 164.2,
        "flood_limit_level": 162.0,
        "dam_height": 28.0,
        "dam_length": 300.0,
        "build_year": 2003,
        "manager": "云岭县水利投资有限公司",
        "manager_phone": "0572-66660004",
        "location": "云岭县长岭乡脚村",
        "remark": "除险加固后运行良好。",
    },
    {
        "code": "SK-3303001",
        "name": "双溪口水库",
        "region": "平原区",
        "basin": "双溪流域",
        "dam_type": "masonry",
        "safety_class": "class_three",
        "status": "danger",
        "total_capacity": 148.0,
        "normal_level": 96.4,
        "flood_limit_level": 94.5,
        "dam_height": 12.6,
        "dam_length": 180.0,
        "build_year": 1972,
        "manager": "平原区双溪口水库管理所",
        "manager_phone": "0573-55550005",
        "location": "平原区双溪口村",
        "remark": "三类坝，已上报除险加固计划，汛期限制蓄水运行。",
    },
    {
        "code": "SK-3303002",
        "name": "黄泥岗水库",
        "region": "平原区",
        "basin": "双溪流域",
        "dam_type": "homogeneous_earth",
        "safety_class": "class_two",
        "status": "normal",
        "total_capacity": 268.0,
        "normal_level": 78.6,
        "flood_limit_level": 76.5,
        "dam_height": 15.2,
        "dam_length": 210.0,
        "build_year": 1996,
        "manager": "平原区黄泥岗水库管理站",
        "manager_phone": "0573-55550006",
        "location": "平原区黄泥岗村",
        "remark": "",
    },
    {
        "code": "SK-3303003",
        "name": "上垟塘水库",
        "region": "平原区",
        "basin": "双溪流域",
        "dam_type": "homogeneous_earth",
        "safety_class": "class_three",
        "status": "out_of_service",
        "total_capacity": 78.0,
        "normal_level": 62.0,
        "flood_limit_level": 60.5,
        "dam_height": 9.8,
        "dam_length": 140.0,
        "build_year": 1968,
        "manager": "平原区上垟塘村村民委员会",
        "manager_phone": "0573-55550007",
        "location": "平原区上垟塘村",
        "remark": "已报废停用，库区封闭管理，仅保留台账。",
    },
]

# 巡查记录演示数据：items 为 (部位, 结果, 异常描述)
INSPECTIONS: list[dict] = [
    {
        "reservoir": 0,
        "days_ago": 1,
        "hour": 9,
        "inspect_type": "daily",
        "inspector": "陈立",
        "weather": "sunny",
        "water_level": 84.8,
        "rainfall": 0.0,
        "route": "坝顶→迎水面→坝脚→溢洪道→放水涵管",
        "summary": "各项设施运行正常，坝顶无裂缝、无沉陷。",
        "items": [
            ("dam_body", "normal", "坝顶、迎水面、背水面均无裂缝"),
            ("spillway", "normal", "进口无淤堵，边坡完好"),
            ("outlet", "normal", "闸门启闭正常，涵管无渗漏"),
            ("seepage", "normal", "坝脚无水渍，观测孔水位平稳"),
            ("facility", "normal", "观测设施、警示牌完好"),
        ],
    },
    {
        "reservoir": 1,
        "days_ago": 2,
        "hour": 10,
        "inspect_type": "daily",
        "inspector": "王海涛",
        "weather": "cloudy",
        "water_level": 126.4,
        "rainfall": 0.0,
        "route": "坝顶→背水面→坝脚排水棱体→溢洪道",
        "summary": "巡查未发现异常，排水棱体出水清澈。",
        "items": [
            ("dam_body", "normal", ""),
            ("seepage", "normal", "排水棱体出水清澈无异味"),
            ("spillway", "normal", ""),
            ("outlet", "normal", ""),
        ],
    },
    {
        "reservoir": 2,
        "days_ago": 3,
        "hour": 15,
        "inspect_type": "flood_season",
        "inspector": "李文倩",
        "weather": "rain",
        "water_level": 208.6,
        "rainfall": 18.5,
        "route": "坝顶→背水面→坝脚渗流观测点→溢洪道",
        "summary": "背水面坝脚出现轻微湿润，已加密观测频次并上报。",
        "items": [
            ("dam_body", "normal", ""),
            ("seepage", "abnormal", "坝脚排水棱体附近出现湿润区，范围约 2 平方米，渗水清澈"),
            ("spillway", "normal", ""),
            ("outlet", "normal", ""),
            ("facility", "normal", ""),
        ],
    },
    {
        "reservoir": 3,
        "days_ago": 5,
        "hour": 9,
        "inspect_type": "daily",
        "inspector": "赵明",
        "weather": "overcast",
        "water_level": 162.8,
        "rainfall": 0.0,
        "route": "坝顶→上游坝坡→下游坝坡→溢洪道",
        "summary": "库区运行正常。",
        "items": [
            ("dam_body", "normal", ""),
            ("slope", "normal", "上游坝坡砌石护坡完好"),
            ("spillway", "normal", ""),
            ("outlet", "normal", ""),
        ],
    },
    {
        "reservoir": 4,
        "days_ago": 2,
        "hour": 8,
        "inspect_type": "emergency",
        "inspector": "周建国",
        "weather": "heavy_rain",
        "water_level": 95.2,
        "rainfall": 46.0,
        "route": "坝顶→溢洪道→放水涵管",
        "summary": "强降雨期间加密巡查，溢洪道进口有杂草淤堵，已安排清理。",
        "items": [
            ("dam_body", "normal", ""),
            ("spillway", "abnormal", "溢洪道进口堆积树枝杂草，过流断面减少约 20%"),
            ("outlet", "abnormal", "放水涵管闸门启闭机外壳锈蚀，启闭尚可"),
        ],
    },
    {
        "reservoir": 5,
        "days_ago": 6,
        "hour": 10,
        "inspect_type": "daily",
        "inspector": "孙婷",
        "weather": "sunny",
        "water_level": 76.9,
        "rainfall": 0.0,
        "route": "坝顶→迎水面→溢洪道→放水设施",
        "summary": "巡查正常。",
        "items": [
            ("dam_body", "normal", ""),
            ("spillway", "normal", ""),
            ("outlet", "normal", ""),
        ],
    },
    {
        "reservoir": 0,
        "days_ago": 12,
        "hour": 9,
        "inspect_type": "daily",
        "inspector": "陈立",
        "weather": "sunny",
        "water_level": 85.1,
        "rainfall": 0.0,
        "route": "坝顶→迎水面→坝脚→溢洪道",
        "summary": "巡查正常。",
        "items": [
            ("dam_body", "normal", ""),
            ("spillway", "normal", ""),
            ("outlet", "normal", ""),
        ],
    },
    {
        "reservoir": 1,
        "days_ago": 9,
        "hour": 14,
        "inspect_type": "special",
        "inspector": "王海涛",
        "weather": "drizzle",
        "water_level": 126.1,
        "rainfall": 3.2,
        "route": "专项检查：坝体、溢洪道、放水设施、观测设施",
        "summary": "专项检查未发现结构性异常。",
        "items": [
            ("dam_body", "normal", ""),
            ("spillway", "normal", ""),
            ("outlet", "normal", ""),
            ("facility", "normal", "渗流观测孔标识清晰，数据记录完整"),
        ],
    },
    {
        "reservoir": 2,
        "days_ago": 15,
        "hour": 9,
        "inspect_type": "daily",
        "inspector": "李文倩",
        "weather": "cloudy",
        "water_level": 207.9,
        "rainfall": 0.0,
        "route": "环库道路→库岸边坡→坝顶",
        "summary": "库区边坡植被完好，无塌方迹象。",
        "items": [
            ("slope", "normal", ""),
            ("dam_body", "normal", ""),
        ],
    },
    {
        "reservoir": 4,
        "days_ago": 20,
        "hour": 11,
        "inspect_type": "flood_season",
        "inspector": "周建国",
        "weather": "rain",
        "water_level": 93.8,
        "rainfall": 22.0,
        "route": "坝顶→溢洪道→坝脚",
        "summary": "汛期巡查正常，溢洪道过流顺畅。",
        "items": [
            ("dam_body", "normal", ""),
            ("spillway", "normal", ""),
        ],
    },
    {
        "reservoir": 6,
        "days_ago": 30,
        "hour": 10,
        "inspect_type": "daily",
        "inspector": "郑宏",
        "weather": "sunny",
        "water_level": 61.2,
        "rainfall": 0.0,
        "route": "库区围栏→坝顶→坝脚",
        "summary": "已停用水库，库区封闭管理，坝体无异常。",
        "items": [
            ("dam_body", "normal", ""),
            ("facility", "normal", "围栏及警示牌完好"),
        ],
    },
    {
        "reservoir": 0,
        "days_ago": 45,
        "hour": 9,
        "inspect_type": "daily",
        "inspector": "陈立",
        "weather": "sunny",
        "water_level": 84.2,
        "rainfall": 0.0,
        "route": "坝顶→迎水面→坝脚",
        "summary": "巡查正常。",
        "items": [
            ("dam_body", "normal", ""),
            ("seepage", "normal", ""),
        ],
    },
]

# 隐患演示数据：records 为 (记录类型, 内容, 记录人, 距今天数, 变更前状态, 变更后状态)
HAZARDS: list[dict] = [
    {
        "reservoir": 1,
        "inspection": 1,
        "title": "背水面坝脚局部渗水",
        "category": "seepage",
        "severity": "serious",
        "status": "rectifying",
        "source": "inspection",
        "discovered_days_ago": 12,
        "deadline_offset": 18,
        "discoverer": "王海涛",
        "assignee": "王海涛",
        "description": "坝脚排水棱体右侧 3 米处出现湿润区，渗水清澈，无明显携砂。",
        "plan": "开挖导渗沟并设置反滤层，完成后连续观测 15 天确认渗流量稳定。",
        "records": [
            ("measure", "采用导渗沟加反滤层处理，已上报镇水利站备案", "王海涛", 10, "registered", "rectifying"),
            ("progress", "导渗沟已开挖 40 米，反滤料进场 60 立方米", "王海涛", 4, None, None),
        ],
    },
    {
        "reservoir": 4,
        "inspection": 4,
        "title": "溢洪道进口淤堵影响泄流",
        "category": "spillway",
        "severity": "serious",
        "status": "pending_acceptance",
        "source": "inspection",
        "discovered_days_ago": 8,
        "deadline_offset": 2,
        "discoverer": "周建国",
        "assignee": "周建国",
        "description": "溢洪道进口堆积树枝、杂草及淤泥，过流断面减少约 20%。",
        "plan": "人工清淤并砍伐进口两侧杂草，清理后复核过流断面。",
        "records": [
            ("measure", "组织 6 人清淤，砍伐进口两侧杂木", "周建国", 6, "registered", "rectifying"),
            ("progress", "清淤完成，过流断面已恢复，申请验收", "周建国", 3, "rectifying", "pending_acceptance"),
        ],
    },
    {
        "reservoir": 2,
        "inspection": None,
        "title": "坝顶路面局部沉陷",
        "category": "dam_body",
        "severity": "general",
        "status": "closed",
        "source": "supervision",
        "discovered_days_ago": 40,
        "deadline_offset": -12,
        "closed_days_ago": 12,
        "discoverer": "李文倩",
        "assignee": "云岭县白鹤塘水库管理站",
        "description": "坝顶靠右岸约 8 平方米范围路面下沉 3 至 5 厘米。",
        "plan": "清除松散层后回填夯实，恢复坝顶路面平整。",
        "records": [
            ("measure", "安排养护队回填碎石并夯实", "李文倩", 30, "registered", "rectifying"),
            ("progress", "回填夯实完成，申请验收", "李文倩", 18, "rectifying", "pending_acceptance"),
            (
                "verify",
                "现场复核路面平整，无积水，验收通过",
                "云岭县水利局",
                12,
                "pending_acceptance",
                "closed",
                "现场复核路面平整、无积水，回填部位与周边路面衔接平顺，同意销号",
                12,
            ),
        ],
    },
    {
        "reservoir": 4,
        "inspection": 4,
        "title": "放水涵管闸门启闭机锈蚀",
        "category": "outlet",
        "severity": "general",
        "status": "registered",
        "source": "inspection",
        "discovered_days_ago": 8,
        "deadline_offset": -3,
        "discoverer": "周建国",
        "assignee": "平原区双溪口水库管理所",
        "description": "启闭机外壳及丝杆锈蚀，启闭仍可进行但阻力偏大。",
        "plan": "除锈防腐并加注润滑脂，必要时更换丝杆。",
        "records": [],
    },
    {
        "reservoir": 0,
        "inspection": None,
        "title": "坝顶照明路灯损坏 2 盏",
        "category": "facility",
        "severity": "general",
        "status": "closed",
        "source": "maintenance",
        "discovered_days_ago": 60,
        "deadline_offset": -45,
        "closed_days_ago": 50,
        "discoverer": "陈立",
        "assignee": "临江区水利工程管理所",
        "description": "坝顶道路东侧 2 盏路灯不亮，夜间巡查存在安全隐患。",
        "plan": "更换灯具并检查线路。",
        "records": [
            ("measure", "采购同型号灯具并更换", "陈立", 52, "registered", "rectifying"),
            (
                "close",
                "灯具更换完成，线路测试正常，直接销号",
                "陈立",
                50,
                "rectifying",
                "closed",
                "灯具更换完成、线路测试正常，夜间照明恢复，立行立改符合销号条件",
                50,
            ),
        ],
    },
    {
        "reservoir": 3,
        "inspection": 3,
        "title": "库岸东侧边坡小块塌方",
        "category": "slope",
        "severity": "major",
        "status": "rectifying",
        "source": "inspection",
        "discovered_days_ago": 25,
        "deadline_offset": 5,
        "discoverer": "赵明",
        "assignee": "云岭县水利投资有限公司",
        "description": "库岸东侧约 12 立方米土体滑塌，坡面裸露，暂未影响大坝安全。",
        "plan": "清除松动土体，坡脚砌筑挡墙并恢复植被。",
        "records": [
            ("measure", "编制边坡处理方案，委托施工队进场", "赵明", 20, "registered", "rectifying"),
            ("progress", "松动土体已清除，坡脚挡墙砌筑完成 60%", "赵明", 8, None, None),
            ("progress", "挡墙砌筑完成，正在植草护坡", "赵明", 2, None, None),
        ],
    },
    {
        "reservoir": 2,
        "inspection": None,
        "title": "库区围栏破损存在垂钓风险",
        "category": "facility",
        "severity": "general",
        "status": "registered",
        "source": "mass_report",
        "discovered_days_ago": 5,
        "deadline_offset": 25,
        "discoverer": "白鹤乡村民",
        "assignee": "云岭县白鹤塘水库管理站",
        "description": "库区西侧围栏破损约 6 米，有人员进入库区垂钓。",
        "plan": "补装围栏并增设警示标志，纳入日常巡查内容。",
        "records": [
            ("progress", "已现场核实并向村民宣传禁止入库垂钓", "李文倩", 4, None, None),
        ],
    },
    {
        "reservoir": 6,
        "inspection": None,
        "title": "坝体杂草丛生且有白蚁活动迹象",
        "category": "dam_body",
        "severity": "serious",
        "status": "pending_acceptance",
        "source": "supervision",
        "discovered_days_ago": 18,
        "deadline_offset": -6,
        "discoverer": "平原区水利局检查组",
        "assignee": "平原区上垟塘村村民委员会",
        "description": "已停用水库坝体长期未清理，发现白蚁蚁路，存在坝体隐患。",
        "plan": "全面清除杂草并结合白蚁防治药剂处理，完成后申请验收。",
        "records": [
            ("measure", "委托白蚁防治机构进场处理，同步清除杂草", "郑宏", 14, "registered", "rectifying"),
            ("progress", "杂草清除完毕，白蚁药剂处理完成，申请验收", "郑宏", 6, "rectifying", "pending_acceptance"),
        ],
    },
]


def _code(prefix: str, day: date, counters: dict[str, int]) -> str:
    """与 services.helpers.next_code 保持同一编号规则。"""
    base = f"{prefix}{day:%Y%m%d}"
    counters[base] = counters.get(base, 0) + 1
    return f"{base}{counters[base]:03d}"


def seed_demo_data() -> None:
    """灌入演示数据（水库台账非空时直接跳过）。"""
    with SessionLocal() as db:
        existing = db.scalar(select(func.count()).select_from(Reservoir)) or 0
        if existing:
            return

        counters: dict[str, int] = {}
        today = now_local().date()

        reservoirs = [Reservoir(**item) for item in RESERVOIRS]
        db.add_all(reservoirs)
        db.flush()

        inspections: list[Inspection] = []
        for plan in INSPECTIONS:
            inspected_at = now_local().replace(
                hour=plan["hour"], minute=0, second=0, microsecond=0
            ) - timedelta(days=plan["days_ago"])
            items = [
                InspectionItem(part=part, result=result, description=description)
                for part, result, description in plan["items"]
            ]
            inspection = Inspection(
                code=_code("XC", inspected_at.date(), counters),
                reservoir_id=reservoirs[plan["reservoir"]].id,
                inspect_type=plan["inspect_type"],
                inspected_at=inspected_at,
                inspector=plan["inspector"],
                weather=plan["weather"],
                water_level=plan["water_level"],
                rainfall=plan["rainfall"],
                route=plan["route"],
                summary=plan["summary"],
                status="abnormal" if any(item.result == "abnormal" for item in items) else "normal",
                items=items,
            )
            inspections.append(inspection)
        db.add_all(inspections)
        db.flush()

        for plan in HAZARDS:
            discovered_on = today - timedelta(days=plan["discovered_days_ago"])
            hazard = Hazard(
                code=_code("YH", discovered_on, counters),
                reservoir_id=reservoirs[plan["reservoir"]].id,
                inspection_id=(
                    inspections[plan["inspection"]].id
                    if plan.get("inspection") is not None
                    else None
                ),
                title=plan["title"],
                category=plan["category"],
                severity=plan["severity"],
                status=plan["status"],
                source=plan["source"],
                discovered_on=discovered_on,
                discoverer=plan["discoverer"],
                deadline=(
                    today + timedelta(days=plan["deadline_offset"])
                    if plan.get("deadline_offset") is not None
                    else None
                ),
                assignee=plan["assignee"],
                description=plan["description"],
                plan=plan["plan"],
                closed_on=(
                    today - timedelta(days=plan["closed_days_ago"])
                    if plan.get("closed_days_ago") is not None
                    else None
                ),
            )
            hazard.rectifications.append(
                HazardRectification(
                    action="register",
                    content=f"隐患登记：{plan['title']}",
                    operator=plan["discoverer"],
                    recorded_at=now_local() - timedelta(days=plan["discovered_days_ago"]),
                    status_to="registered",
                )
            )
            for record in plan["records"]:
                # 元组前 6 项：记录类型、内容、记录人、距今天数、变更前状态、变更后状态；
                # 销号流水另有第 7、8 项：验收意见、销号日期（距今天数）
                action, content, operator, days_ago, status_from, status_to = record[:6]
                acceptance_opinion = record[6] if len(record) > 6 else None
                closed_offset = record[7] if len(record) > 7 else None
                rectification = HazardRectification(
                    action=action,
                    content=content,
                    operator=operator,
                    recorded_at=now_local() - timedelta(days=days_ago),
                    status_from=status_from,
                    status_to=status_to,
                )
                if acceptance_opinion:
                    rectification.acceptance_opinion = acceptance_opinion
                if closed_offset is not None:
                    rectification.closed_on = today - timedelta(days=closed_offset)
                hazard.rectifications.append(rectification)
            db.add(hazard)

        db.commit()
        logger.info(
            "已灌入演示数据：%s 座水库 / %s 条巡查记录 / %s 条隐患",
            len(reservoirs),
            len(inspections),
            len(HAZARDS),
        )
