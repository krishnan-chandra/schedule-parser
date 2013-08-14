from pyquery import PyQuery
from icalendar import Calendar, Event, Timezone, TimezoneStandard, TimezoneDaylight
from dateutil import parser
from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from datetime import datetime, date, time, timedelta
import calendar
import argparse
from pytz import timezone
from dateutil.tz import tzutc
import traceback

UTC = tzutc()

DAY_MAP = {
  "M": calendar.MONDAY, 
  "T": calendar.TUESDAY,
  "W": calendar.WEDNESDAY,
  "R": calendar.THURSDAY,
  "F": calendar.FRIDAY 
}

ABBR_MAP = {
  "M": "MO",
  "T": "TU",
  "W": "WE",
  "R": "TH",
  "F": "FR"
}

CLASS_TIMEZONE = 'US/Central'

def main():
  parser = argparse.ArgumentParser(description='Create schedule iCalendar file')
  parser.add_argument('--input', help='The input HTML file we use to generate the schedule', type=str)
  parser.add_argument('--output', help='The output ics file we write to', type=str)
  args = parser.parse_args()
  calendar = Calendar()
  calendar.add('uid', 'Krishnan-Calendar-0')
  calendar.add_component(create_timezone())
  if args.input is not None and args.output is not None:
    try:
      document = PyQuery(filename=args.input)
      for event in parse_calendar(document):
        calendar.add_component(event)
      with open(args.output, 'wb') as f:
        f.write(calendar.to_ical())
    except:
      traceback.print_exc();
  else:
    parser.print_help()

def create_timezone():
  central = Timezone()
  central.add('tzid', CLASS_TIMEZONE)
  central.add('x-lic-location', CLASS_TIMEZONE)
  tzs = TimezoneStandard()
  tzs.add('tzname', 'CST')
  tzs.add('dtstart', datetime(1970, 10, 25, 3, 0, 0))
  tzs.add('rrule', {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su'})
  tzs.add('TZOFFSETFROM', timedelta(hours=-5))
  tzs.add('TZOFFSETTO', timedelta(hours=-6))
  tzd = TimezoneDaylight()
  tzd.add('tzname', 'CDT')
  tzd.add('dtstart', datetime(1970, 3, 29, 2, 0, 0))
  tzd.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '-1su'})
  tzd.add('TZOFFSETFROM', timedelta(hours=-6))
  tzd.add('TZOFFSETTO', timedelta(hours=-5))
  central.add_component(tzs)
  central.add_component(tzd)
  return central

def parse_calendar(document):
  ddtable = document(".datadisplaytable")
  ddtable = PyQuery(ddtable[-1])
  ddrows = ddtable("tr")
  for row in ddrows.items():
    cell = row.find('.dddefault')
    if len(cell) != 12:
      continue
    event = parse_cell(cell)
    if event is not None:
      yield event

def parse_cell(cell):
  central = timezone(CLASS_TIMEZONE)
  fields = dict()
  fields['class_name'] = cell[1].text_content()
  fields['class_title'] = cell[2].text_content()
  fields['credit_hours'] = float(cell[4].text_content().strip())
  start_date = parser.parse(cell[6].text_content()).date()
  end_date = parser.parse(cell[7].text_content()).date()
  fields['days'] = tuple(cell[8].text_content().strip())
  time_range = cell[9].text_content()
  start_and_end = time_range.split("-")
  if len(start_and_end) == 2:
    start_time = parser.parse(unicode(start_and_end[0]).strip()).time()
    first_day = fields['days'][0]
    fields['start_date'] = central.localize(datetime.combine(start_date, start_time))
    fields['start_date'] = fix_start(fields['start_date'], first_day)
    end_time = parser.parse(start_and_end[1].strip()).time()
    fields['end_time'] = central.localize(datetime.combine(fields['start_date'].date(), end_time))
    fields['end_date'] = central.localize(datetime.combine(end_date, end_time))
    fields['location'] = cell[10].text_content()
    fields['professor'] = cell[11].text_content()
    return create_event(fields)
  else:
    return None

def fix_start(start_date, first_day):
  delta = {
    'M': timedelta(days=0),
    'T': timedelta(days=1),
    'W': timedelta(days=2),
    'R': timedelta(days=3),
    'F': timedelta(days=4)
  }.get(first_day, timedelta(days=0))
  new_date = start_date + delta
  return new_date

def create_event(fields):
  if fields is None:
    return
  event = Event()
  event.add('uid', fields['class_name'] + fields['class_title'])
  event.add('summary', fields['class_name'] + ", " + fields['class_title'])
  event.add('location', fields['location'])
  event.add('dtstart', fields['start_date'])
  event.add('dtend', fields['end_time'])
  dates = tuple([ABBR_MAP[day] for day in fields['days']])
  rr = dict()
  rr['FREQ'] = 'WEEKLY'
  rr['UNTIL'] = fields['end_date'].date()
  rr['WKST'] = 'SU'
  rr['BYDAY'] = dates
  event.add('rrule', rr)
  return event

def serialize_date(dt):
  """
  Serialize a date/time value into an ISO8601 text representation
  adjusted (if needed) to UTC timezone.

  For instance:
  >>> serialize_date(datetime(2012, 4, 10, 22, 38, 20, 604391))
  '2012-04-10T22:38:20.604391Z'
  """
  if dt.tzinfo:
      dt = dt.astimezone(UTC).replace(tzinfo=None)
  return dt.isoformat() + 'Z'

if __name__ == "__main__":
  main()
