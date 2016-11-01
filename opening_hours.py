# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

DAY_NAMES = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
             'saturday', 'sunday']


def parse_opening_hours(hours_data):
    """Parses opening hours dictionary from separate open and close times
    to a unified list of ordered opening time tuples per day.

    Features:
    - Adds missing weekdays
    - Returns days in the correct order
    - Joins consecutive opening and closing time pairs to a continuous span.
    - Supports closing time occuring in the following day by adding the closing
      time inside the previous day.

    :param hours_data: opening hours in Opening Hours format
    :type hours_data: dict
    :return: list of dictionaries where every dict has keys "name" and
      "hours". Value of the "name" key is the name of the weekday. Value of
      the "hours" key is a list of time tuples "(start time in seconds,
      end time in seconds)" in order.
    :rtype: list

    >>> parse_opening_hours({})
    [{u'hours': None, u'day': u'monday'}, \
{u'hours': None, u'day': u'tuesday'}, \
{u'hours': None, u'day': u'wednesday'}, \
{u'hours': None, u'day': u'thursday'}, \
{u'hours': None, u'day': u'friday'}, \
{u'hours': None, u'day': u'saturday'}, \
{u'hours': None, u'day': u'sunday'}]
    >>> parse_opening_hours({"monday":[{"type": "open","value": 36000},\
    {"type": "close","value": 86399}]})
    [{u'hours': [(36000, 86399)], u'day': u'monday'}, \
{u'hours': None, u'day': u'tuesday'}, \
{u'hours': None, u'day': u'wednesday'}, \
{u'hours': None, u'day': u'thursday'}, \
{u'hours': None, u'day': u'friday'}, \
{u'hours': None, u'day': u'saturday'}, \
{u'hours': None, u'day': u'sunday'}]
    >>> parse_opening_hours({"monday":[{"type": "close","value": 3600}],\
    "sunday": [{"type": "open", "value": 61200}]})
    [{u'hours': None, u'day': u'monday'}, \
{u'hours': None, u'day': u'tuesday'}, \
{u'hours': None, u'day': u'wednesday'}, \
{u'hours': None, u'day': u'thursday'}, \
{u'hours': None, u'day': u'friday'}, \
{u'hours': None, u'day': u'saturday'}, \
{u'hours': [(61200, 3600)], u'day': u'sunday'}]
    """
    # First sort the time entries inside every day
    for day, hour_entries in hours_data.items():
        hours_data[day] = sorted(hour_entries, key=lambda x: x['value'])

    all_days = []
    sunday_close = None

    for day_name in DAY_NAMES:
        # Add missing days to the result
        if day_name not in hours_data or not len(hours_data[day_name]):
            all_days.append({
                "day": day_name,
                "hours": None,
            })
            continue

        hours = []
        current_start = None

        for item in hours_data[day_name]:
            if "type" not in item:
                continue

            if item['type'] == 'open':
                if current_start:
                    raise RuntimeError(
                            'New open time "{}" in day "" before '
                            'previous time "{}" closed'.format(
                                    item['value'], day_name, current_start))

                current_start = item['value']
                # Consolidate separate consecutive hours if this start time
                # is the same as the previous end time
                if len(hours) and current_start == hours[-1][1]:
                    current_start = hours[-1][0]
                    del hours[-1]
            elif item['type'] == 'close':
                # If this is a closing time to the previous days opening time
                # add the time there
                if current_start is None and not len(hours):
                    if len(all_days) and all_days[-1].get('hours'):
                        all_days[-1]['hours'][-1] = (
                            all_days[-1]['hours'][-1][0], item['value'])
                    else:
                        # Special case where we sundays closing
                        # time in defined in monday. We keep it in a temporary
                        # variable because sunday is handled last.
                        if day_name == 'monday':
                            sunday_close = item['value']
                        else:
                            raise RuntimeError('Invalid close time "{}" '
                                               'in day "{}"'.format(
                                                   item['value'], day_name))
                else:
                    if current_start is None:
                        raise RuntimeError(
                                'New close time "{}" in day "{}" without an '
                                'opening time'.format(item['value'], day_name))
                    else:
                        hours.append((current_start, item['value']))
                        current_start = None

        if current_start is not None:
            if day_name == 'sunday' and sunday_close:
                hours.append((current_start, sunday_close))
            else:
                hours.append((current_start, None))
        elif day_name == 'sunday' and sunday_close:
            raise RuntimeError('Lingering sunday close time detected')

        all_days.append({
            "day": day_name,
            "hours": hours if hours else None,
        })

    for day in all_days:
        try:
            if day.get('hours') and day.get('hours')[-1][1] is None:
                raise RuntimeError(
                        'Lingering opening time "{}" in day "{}"'.format(
                                day.get('hours')[-1][0], day.get('day')))
        except IndexError:
            pass

    return all_days


def seconds_to_hours_and_minutes(seconds):
    """Converts seconds to a tuple with hours and minutes. Discards seconds.

    >>> seconds_to_hours_and_minutes(0)
    (0, 0)
    >>> seconds_to_hours_and_minutes(60)
    (0, 1)
    >>> seconds_to_hours_and_minutes(75600)
    (21, 0)
    >>> seconds_to_hours_and_minutes(86399)
    (23, 59)
    """
    minutes = seconds // 60
    hours = minutes // 60
    minutes %= 60

    return hours, minutes


def hours_and_minutes_as_string(hours_and_minutes):
    """Converts 24-hour and minutes tuple to a human readable 12-hour
    and minute string.

    :param hours_and_minutes: Hours and minutes tuple (hours, minutes)
    :type hours_and_minutes: tuple
    :return: Human readable time
    :rtype: basestring

    >>> hours_and_minutes_as_string((0, 0))
    u'0 am'
    >>> hours_and_minutes_as_string((10, 0))
    u'10 am'
    >>> hours_and_minutes_as_string((18, 0))
    u'6 pm'
    >>> hours_and_minutes_as_string((10, 15))
    u'10:15 am'
    >>> hours_and_minutes_as_string((23, 59))
    u'11:59 pm'
    """
    (hours, minutes) = hours_and_minutes

    am_or_pm = 'am'
    if hours >= 12:
        am_or_pm = 'pm'
        if hours > 12:
            hours -= 12

    return '{}{} {}'.format(
            hours, ':{:02d}'.format(minutes) if minutes else '', am_or_pm)


def opening_hours_to_string(day_data):
    """Converts list of opening hours and days to a human readable string.

    :param day_data: list of day dictionaries from parse_opening_hours
    :type day_data: list of dict
    :return: Opening hours as a human readable string
    :rtype: basestring

    >>> opening_hours_to_string([{"day": "monday", "hours":None}])
    u'Monday: Closed\\n'
    >>> opening_hours_to_string([{"day": "monday", "hours":[(36000, 64800)]}])
    u'Monday: 10 am - 6 pm\\n'
    >>> opening_hours_to_string([{"day": "monday", "hours":[(36000, 64800)]}, \
        {"day": "tuesday", "hours":[(43200, 75600)]}])
    u'Monday: 10 am - 6 pm\\nTuesday: 12 pm - 9 pm\\n'
    """
    result = ""
    for day in day_data:
        opening_hours = []
        if day['hours']:
            for start_time, end_time in day['hours']:
                opening_hours.append(
                        "{} - {}".format(
                                hours_and_minutes_as_string(
                                    seconds_to_hours_and_minutes(start_time)),
                                hours_and_minutes_as_string(
                                    seconds_to_hours_and_minutes(end_time))))
        else:
            opening_hours.append("Closed")

        result += "{}: {}\n".format(day['day'].capitalize(),
                                    ", ".join(opening_hours))

    return result

if __name__ == '__main__':
    import sys
    import json
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="the filename of the JSON file from "
                                         "where the opening hours are read")
    parser.add_argument("--validate", help="validate the opening hours data",
                        action="store_true")
    args = parser.parse_args()

    try:
        with open(args.filename) as data_file:
            try:
                data = json.load(data_file)
            except ValueError:
                print('Could not parse file "{}" as JSON.'.format(
                        args.filename))
                sys.exit(-1)

    except IOError:
        print('Could not read file "{}".'.format(args.filename))
        sys.exit(-1)

    if args.validate:
        try:
            from voluptuous import (Invalid, Schema, Required, All, Range,
                                    Any, In)
        except ImportError:
            print('Validating requires voluptuous library. Please install it '
                  'by running "pip install voluptuous".')
            sys.exit(-1)

        schema = Schema({
            In(DAY_NAMES): [{
                Required('type'): Any('open', 'close'),
                Required('value'): All(int, Range(min=0, max=86399))
            }]
        })

        try:
            data = schema(data)
        except Invalid as e:
            print("Data is not well-formed. Error: {}".format(e))
            sys.exit(-1)

    try:
        day_times = parse_opening_hours(data)
        opening_hours_string = opening_hours_to_string(day_times)
        print(opening_hours_string)
    except RuntimeError as e:
        print(e.message)
