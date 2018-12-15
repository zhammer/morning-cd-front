from datetime import date, datetime

from behave import given


@given('I live in new york')  # noqa: F811
def step_impl(context):
    context.iana_timezone = 'America/New_York'


@given('today\'s date is November 12th, 2018')  # noqa: F811
def step_impl(context):
    context.todays_date = date(2018, 11, 12)


@given('my name is "{name}"')  # noqa: F811
def step_impl(context, name):
    context.name = name


@given('it\'s daytime at 10:30am on November 12th 2018')  # noqa: F811
def step_impl(context):
    context.current_time_utc = datetime(2018, 11, 12, 15, 30)  # utc
    context.is_day = True


@given('it\'s nighttime at 6pm on November 12th 2018')  # noqa: F811
def step_impl(context):
    context.current_time_utc = datetime(2018, 11, 12, 23, 0)  # utc time
    context.is_day = False
