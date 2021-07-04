import datetime as dt

from dateutil.tz import tzlocal
from freezegun import freeze_time

from utils import Util

FAKE_TIME = dt.datetime(2021, 11, 1, 21, 0, 59)


@freeze_time(FAKE_TIME)
def test_now():
    assert Util.now() == FAKE_TIME


@freeze_time(FAKE_TIME)
def test_today():
    assert Util.today() == dt.datetime(2021, 11, 1, tzinfo=tzlocal())


@freeze_time(FAKE_TIME)
def test_offset_date():
    tz = tzlocal()
    today = Util.today()

    assert Util.offset_date(0) == today

    tomorrow = dt.datetime(2021, 11, 2, tzinfo=tz)
    assert Util.offset_date(1) == tomorrow
    assert Util.offset_date(1, start=today) == tomorrow

    yesterday = dt.datetime(2021, 10, 31, tzinfo=tz)
    assert Util.offset_date(-1) == yesterday

    assert Util.offset_date(2, yesterday) == tomorrow


# TODO: test_as_timestamp
# TODO: test_uuid
