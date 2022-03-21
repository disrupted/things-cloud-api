from datetime import datetime, timedelta, timezone

from freezegun import freeze_time

from things_cloud.utils import Util

FAKE_TIME = datetime(2021, 11, 1, 21, 0, 59, tzinfo=timezone(timedelta(hours=2)))


@freeze_time(FAKE_TIME)
def test_now():
    assert Util.now() == datetime(2021, 11, 1, 19, 0, 59)


@freeze_time(FAKE_TIME)
def test_today():
    assert Util.today() == datetime(2021, 11, 1)


@freeze_time(FAKE_TIME)
def test_offset_date():
    today = Util.today()

    assert Util.offset_date(0) == today

    tomorrow = datetime(2021, 11, 2)
    assert Util.offset_date(1) == tomorrow
    assert Util.offset_date(1, start=today) == tomorrow

    yesterday = datetime(2021, 10, 31)
    assert Util.offset_date(-1) == yesterday

    assert Util.offset_date(2, yesterday) == tomorrow


@freeze_time(FAKE_TIME)
def test_as_timestamp():
    assert Util.as_timestamp(datetime(2022, 1, 1)) == 1640995200
    assert Util.as_timestamp(datetime(2022, 1, 1, tzinfo=timezone.utc)) == 1640995200
    assert Util.as_timestamp(Util.today()) == 1635724800


def test_uuid():
    uuid = Util.uuid()
    assert len(uuid) == 22
    assert uuid.isalnum()
    assert uuid != Util.uuid()
