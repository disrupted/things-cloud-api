from datetime import date, datetime, timedelta, timezone

from shortuuid import ShortUUID


class Util:
    @staticmethod
    def now() -> datetime:
        return datetime.utcnow()

    @staticmethod
    def today() -> datetime:
        return datetime.combine(date.today(), datetime.min.time())

    @staticmethod
    def offset_date(days: int, start: datetime | None = None) -> datetime:
        if start is None:
            start = Util.today()
        return start + timedelta(days=days)

    @staticmethod
    def as_timestamp(dt: datetime) -> int:
        return int(dt.replace(tzinfo=timezone.utc).timestamp())

    @staticmethod
    def uuid(length: int = 22) -> str:
        return ShortUUID().random(length=length)
