from pyquery import PyQuery
from icalendar import Calendar, Event
from dateutil import parser
from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from datetime import datetime, date, time
import calendar
import argparse
from pytz import timezone
from dateutil.tz import tzutc

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

def main():
  parser = argparse.ArgumentParser(description='Create schedule iCalendar file')
  parser.add_argument('--input', help='The input HTML file we use to generate the schedule', type=str)
  parser.add_argument('--output', help='The output ics file we write to', type=str)
  args = parser.parse_args()
  if args.input is not None and args.output is not None:
    calendar = Calendar()
    try:
      document = PyQuery(filename=args.input)
      for event in parse_calendar(document):
        calendar.add_component(event)
      with open(args.output, 'wb') as f:
        f.write(calendar.to_ical())
    except:
      print 'Bad shit happened'
  else:
    parser.print_help()

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
    fields['start_date'] = datetime.combine(start_date, start_time)
    end_time = parser.parse(start_and_end[1].strip()).time()
    fields['end_time'] = datetime.combine(start_date, end_time)
    fields['end_date'] = datetime.combine(end_date, end_time)
    fields['location'] = cell[10].text_content()
    fields['professor'] = cell[11].text_content()
    return create_event(fields)
  else:
    return None

def create_event(fields):
  if fields is None:
    return
  event = Event()
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
