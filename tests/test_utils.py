import datetime as dt

from freezegun import freeze_time

from things_cloud.utils import Util

FAKE_TIME = dt.datetime(2021, 11, 1, 21, 0, 59)


@freeze_time(FAKE_TIME)
def test_now():
    assert Util.now() == FAKE_TIME


@freeze_time(FAKE_TIME)
def test_today():
    assert Util.today() == dt.datetime(2021, 11, 1)


@freeze_time(FAKE_TIME)
def test_offset_date():
    today = Util.today()

    assert Util.offset_date(0) == today

    tomorrow = dt.datetime(2021, 11, 2)
    assert Util.offset_date(1) == tomorrow
    assert Util.offset_date(1, start=today) == tomorrow

    yesterday = dt.datetime(2021, 10, 31)
    assert Util.offset_date(-1) == yesterday

    assert Util.offset_date(2, yesterday) == tomorrow


def test_as_timestamp():
    assert Util.as_timestamp(dt.datetime(2022, 1, 1)) == 1640995200


def test_uuid():
    uuid = Util.uuid()
    assert len(uuid) == 22
    assert uuid.isalnum()
    assert uuid != Util.uuid()
