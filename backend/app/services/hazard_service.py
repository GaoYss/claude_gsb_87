"""隐患登记与整改跟踪业务逻辑（含状态流转规则）。"""

from dataclasses import dataclass
from datetime import date

from sqlalchemy import and_, func, or_, select, update as sa_update
from sqlalchemy.orm import Session, selectinload

from app.core.errors import ConflictError, InvalidOperationError, NotFoundError
from app.db.base import now_local
from app.models import Hazard, HazardRectification, Inspection
from app.models.enums import HazardStatus, RectificationAction
from app.schemas.hazard import (
    HazardCreate,
    HazardRectificationCreate,
    HazardTransitionOption,
    HazardTransitionRequest,
    HazardUpdate,
)
from app.services import reservoir_service
from app.services.helpers import enum_to_value, next_code


@dataclass(frozen=True)
class TransitionRule:
    """一条允许的状态流转。"""

    target: HazardStatus
    label: str
    action: RectificationAction
    require_content: bool = False
    require_acceptance_opinion: bool = False
    require_closed_on: bool = False


def _rule(
    target: HazardStatus,
    label: str,
    action: RectificationAction,
    require_content: bool = False,
    require_acceptance_opinion: bool = False,
    require_closed_on: bool = False,
) -> TransitionRule:
    return TransitionRule(
        target=target,
        label=label,
        action=action,
        require_content=require_content,
        require_acceptance_opinion=require_acceptance_opinion,
        require_closed_on=require_closed_on,
    )


# 销号类流转的共同要求：必须同时具备验收意见与销号日期
_CLOSE_RULE_KWARGS = {
    "require_acceptance_opinion": True,
    "require_closed_on": True,
}

# 隐患整改状态机：待整改 -> 整改中 -> 待验收 -> 已销号（已销号为终态）
TRANSITION_RULES: dict[str, list[TransitionRule]] = {
    HazardStatus.REGISTERED.value: [
        _rule(HazardStatus.RECTIFYING, "开始整改", RectificationAction.MEASURE),
        _rule(
            HazardStatus.CLOSED,
            "直接销号（立行立改）",
            RectificationAction.CLOSE,
            **_CLOSE_RULE_KWARGS,
        ),
    ],
    HazardStatus.RECTIFYING.value: [
        _rule(
            HazardStatus.PENDING_ACCEPTANCE,
            "提交验收",
            RectificationAction.PROGRESS,
            require_content=True,
        ),
        _rule(
            HazardStatus.CLOSED,
            "直接销号",
            RectificationAction.CLOSE,
            **_CLOSE_RULE_KWARGS,
        ),
    ],
    HazardStatus.PENDING_ACCEPTANCE.value: [
        _rule(
            HazardStatus.CLOSED,
            "验收通过并销号",
            RectificationAction.VERIFY,
            **_CLOSE_RULE_KWARGS,
        ),
        _rule(
            HazardStatus.RECTIFYING,
            "验收不通过，退回整改",
            RectificationAction.VERIFY,
            require_content=True,
        ),
    ],
    HazardStatus.CLOSED.value: [],
}


def available_transitions(status: str) -> list[HazardTransitionOption]:
    return [
        HazardTransitionOption(
            target_status=rule.target,
            label=rule.label,
            require_content=rule.require_content,
            require_acceptance_opinion=rule.require_acceptance_opinion,
            require_closed_on=rule.require_closed_on,
        )
        for rule in TRANSITION_RULES.get(status, [])
    ]


def _find_rule(current: str, target: str) -> TransitionRule | None:
    for rule in TRANSITION_RULES.get(current, []):
        if rule.target.value == target:
            return rule
    return None


def get_hazard(db: Session, hazard_id: int) -> Hazard:
    stmt = (
        select(Hazard)
        .options(
            selectinload(Hazard.reservoir),
            selectinload(Hazard.rectifications),
        )
        .where(Hazard.id == hazard_id)
    )
    hazard = db.scalar(stmt)
    if hazard is None:
        raise NotFoundError(f"隐患不存在：id={hazard_id}")
    return hazard


def list_hazards(
    db: Session,
    *,
    reservoir_id: int | None = None,
    inspection_id: int | None = None,
    category: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    source: str | None = None,
    keyword: str | None = None,
    overdue_only: bool = False,
    open_only: bool = False,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Hazard], int]:
    conditions = []
    if reservoir_id:
        conditions.append(Hazard.reservoir_id == reservoir_id)
    if inspection_id:
        conditions.append(Hazard.inspection_id == inspection_id)
    if category:
        conditions.append(Hazard.category == category)
    if severity:
        conditions.append(Hazard.severity == severity)
    if status:
        conditions.append(Hazard.status == status)
    if source:
        conditions.append(Hazard.source == source)
    if open_only:
        conditions.append(Hazard.status != HazardStatus.CLOSED.value)
    if overdue_only:
        conditions.append(
            and_(
                Hazard.status != HazardStatus.CLOSED.value,
                Hazard.deadline.is_not(None),
                Hazard.deadline < date.today(),
            )
        )
    if keyword:
        like = f"%{keyword.strip()}%"
        conditions.append(
            or_(
                Hazard.title.like(like),
                Hazard.code.like(like),
                Hazard.description.like(like),
                Hazard.assignee.like(like),
            )
        )

    total = db.scalar(select(func.count()).select_from(Hazard).where(*conditions)) or 0
    rows = db.scalars(
        select(Hazard)
        .options(selectinload(Hazard.reservoir))
        .where(*conditions)
        .order_by(
            Hazard.status.desc(),
            Hazard.deadline.is_(None),
            Hazard.deadline.asc(),
            Hazard.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(rows), total


def create_hazard(db: Session, payload: HazardCreate) -> Hazard:
    reservoir_service.get_reservoir(db, payload.reservoir_id)
    data = enum_to_value(payload.model_dump())

    inspection_id = data.get("inspection_id")
    if inspection_id:
        inspection = db.get(Inspection, inspection_id)
        if inspection is None:
            raise NotFoundError(f"来源巡查记录不存在：id={inspection_id}")
        if inspection.reservoir_id != data["reservoir_id"]:
            raise InvalidOperationError("来源巡查记录与所选水库不一致，请重新选择")

    discovered_on = data.get("discovered_on") or date.today()
    hazard = Hazard(
        code=next_code(db, Hazard, Hazard.code, prefix="YH", on=discovered_on),
        **{**data, "discovered_on": discovered_on},
    )
    # 登记即写一条流水，保证整改跟踪时间轴从发现开始可追溯
    hazard.rectifications.append(
        HazardRectification(
            action=RectificationAction.REGISTER.value,
            content=f"隐患登记：{hazard.title}",
            operator=data.get("discoverer"),
            status_from=None,
            status_to=HazardStatus.REGISTERED.value,
        )
    )
    db.add(hazard)
    db.commit()
    return get_hazard(db, hazard.id)


def update_hazard(db: Session, hazard_id: int, payload: HazardUpdate) -> Hazard:
    hazard = get_hazard(db, hazard_id)

    if payload.status is not None and payload.status.value != hazard.status:
        raise InvalidOperationError(
            "状态变更请使用 POST /api/v1/hazards/{id}/transition 接口，以便记录整改流水"
        )

    data = enum_to_value(payload.model_dump(exclude_unset=True, exclude={"status"}))
    if "inspection_id" in data and data["inspection_id"]:
        inspection = db.get(Inspection, data["inspection_id"])
        if inspection is None:
            raise NotFoundError(f"来源巡查记录不存在：id={data['inspection_id']}")
        if inspection.reservoir_id != hazard.reservoir_id:
            raise InvalidOperationError("来源巡查记录与隐患所属水库不一致")

    for key, value in data.items():
        setattr(hazard, key, value)
    db.commit()
    return get_hazard(db, hazard_id)


def _latest_verify_record(db: Session, hazard_id: int) -> HazardRectification | None:
    """该隐患最近一条单独登记的验收意见流水（直接销号时作为依据关联）。

    只取未驱动状态流转（status_to 为空）的验收记录：「验收不通过退回整改」的
    否决记录本身带 status_to=rectifying，不能作为销号依据；「验收通过并销号」
    的意见就在本次销号流水里，无需再回指。
    """
    return db.scalar(
        select(HazardRectification)
        .where(
            HazardRectification.hazard_id == hazard_id,
            HazardRectification.action == RectificationAction.VERIFY.value,
            HazardRectification.status_from.is_(None),
            HazardRectification.status_to.is_(None),
        )
        .order_by(HazardRectification.recorded_at.desc(), HazardRectification.id.desc())
        .limit(1)
    )


def _latest_close_record(db: Session, hazard_id: int) -> HazardRectification | None:
    return db.scalar(
        select(HazardRectification)
        .where(
            HazardRectification.hazard_id == hazard_id,
            HazardRectification.status_to == HazardStatus.CLOSED.value,
        )
        .order_by(HazardRectification.id.desc())
        .limit(1)
    )


def _already_closed_message(db: Session, hazard: Hazard) -> str:
    """并发 / 重复销号失败时，明确告知先完成销号的一方信息，而不是静默覆盖。"""
    winner = _latest_close_record(db, hazard.id)
    who = winner.operator if winner and winner.operator else "其他经办人"
    when = winner.closed_on or hazard.closed_on or date.today()
    opinion = (winner.acceptance_opinion if winner else None) or ""
    opinion_hint = f"，验收意见：「{opinion}」" if opinion else ""
    return (
        f"该隐患已由{who}于 {when.isoformat()} 完成销号{opinion_hint}；"
        "本次操作未生效，请刷新后查看最新状态"
    )


def _execute_transition(
    db: Session,
    hazard: Hazard,
    payload: HazardTransitionRequest,
    rule: TransitionRule,
    target: str,
) -> None:
    """校验通过后在单事务内完成「状态推进 + 流水写入」。

    状态推进使用带原状态条件的 UPDATE：只有数据库中的状态仍等于读取时的
    status_from 才会命中一行。两个经办人同时销号时，数据库串行化两条 UPDATE，
    后执行的一条命中 0 行，据此回滚并提示冲突，保证只生效一次。
    """
    content = (payload.content or "").strip()
    if rule.require_content and not content:
        raise InvalidOperationError(f"变更为「{rule.label}」需要填写处理说明")

    is_close = target == HazardStatus.CLOSED.value
    acceptance_opinion = (payload.acceptance_opinion or "").strip()
    closed_on = None

    # 销号前置校验：验收意见与销号日期缺一不可，一次性提示全部缺项
    if is_close:
        missing: list[str] = []
        if rule.require_acceptance_opinion and not acceptance_opinion:
            missing.append("验收意见")
        if rule.require_closed_on and payload.closed_on is None:
            missing.append("销号日期")
        if missing:
            raise InvalidOperationError(
                f"销号失败：缺少{'、'.join(missing)}，补齐后才能销号"
            )
        closed_on = payload.closed_on
        if closed_on > date.today():
            raise InvalidOperationError("销号日期不能晚于今天")
        if closed_on < hazard.discovered_on:
            raise InvalidOperationError("销号日期不能早于隐患发现日期")

    status_from = hazard.status
    now = now_local()

    # 原子条件更新：状态仍是读取时的原值才推进，杜绝并发下的重复销号 / 丢失更新
    result = db.execute(
        sa_update(Hazard)
        .where(Hazard.id == hazard.id, Hazard.status == status_from)
        .values(
            status=target,
            closed_on=closed_on if is_close else None,
            updated_at=now,
        )
    )
    if result.rowcount != 1:
        # 未抢到状态推进：回滚本事务，不写流水、不留半成品，并重新读取给出明确提示
        db.rollback()
        fresh = db.get(Hazard, hazard.id)
        if fresh is not None and fresh.status == HazardStatus.CLOSED.value:
            raise ConflictError(_already_closed_message(db, fresh))
        fresh_label = HazardStatus.label_of(fresh.status if fresh else status_from)
        raise ConflictError(
            f"隐患状态刚被其他人更新为「{fresh_label}」，本次操作未生效，请刷新后重试"
        )

    record = HazardRectification(
        hazard_id=hazard.id,
        action=rule.action.value,
        content=content or acceptance_opinion or rule.label,
        operator=(payload.operator or "").strip() or None,
        status_from=status_from,
        status_to=target,
        recorded_at=now,
    )
    if is_close:
        # 销号审计三要素随流水固化：验收意见、销号日期、系统时点（recorded_at）
        record.acceptance_opinion = acceptance_opinion
        record.closed_on = closed_on
        record.acceptance_record_id = (
            latest.id if (latest := _latest_verify_record(db, hazard.id)) else None
        )

    db.add(record)
    db.commit()


def transition_hazard(db: Session, hazard_id: int, payload: HazardTransitionRequest) -> Hazard:
    """按状态机流转隐患状态，并自动写入整改跟踪流水。"""
    hazard = get_hazard(db, hazard_id)
    target = payload.target_status.value

    if hazard.status == HazardStatus.CLOSED.value:
        raise ConflictError(_already_closed_message(db, hazard))

    rule = _find_rule(hazard.status, target)
    if rule is None:
        raise ConflictError(
            f"不允许从「{HazardStatus.label_of(hazard.status)}」变更为"
            f"「{HazardStatus.label_of(target)}」"
        )

    _execute_transition(db, hazard, payload, rule, target)
    db.expire_all()
    return get_hazard(db, hazard_id)


def add_rectification(
    db: Session, hazard_id: int, payload: HazardRectificationCreate
) -> Hazard:
    """追加整改跟踪记录；记录整改措施时自动从「待整改」进入「整改中」。"""
    hazard = get_hazard(db, hazard_id)
    if hazard.status == HazardStatus.CLOSED.value:
        raise ConflictError("隐患已销号，不能再追加整改记录")

    record = HazardRectification(
        action=payload.action.value,
        content=payload.content,
        operator=payload.operator,
        recorded_at=payload.recorded_at or now_local(),
    )
    if (
        payload.action == RectificationAction.MEASURE
        and hazard.status == HazardStatus.REGISTERED.value
    ):
        record.status_from = HazardStatus.REGISTERED.value
        record.status_to = HazardStatus.RECTIFYING.value
        hazard.status = HazardStatus.RECTIFYING.value

    hazard.rectifications.append(record)
    db.commit()
    return get_hazard(db, hazard_id)


def delete_hazard(db: Session, hazard_id: int) -> None:
    hazard = get_hazard(db, hazard_id)
    db.delete(hazard)
    db.commit()


def overdue_hazard_count(db: Session) -> int:
    stmt = (
        select(func.count())
        .select_from(Hazard)
        .where(
            Hazard.status != HazardStatus.CLOSED.value,
            Hazard.deadline.is_not(None),
            Hazard.deadline < date.today(),
        )
    )
    return db.scalar(stmt) or 0
