from flask import Flask, request, render_template, after_this_request
import schedule_parse

app = Flask(__name__)
ALLOWED_EXTENSIONS = ['html', 'htm']

@app.route('/', methods=['GET', 'POST'])
def home():
  if request.method == 'GET':
    return render_template('index.html')
  elif request.method == 'POST':
    @after_this_request
    def alter_response_type(response):
      response.headers['Content-Type'] = 'text/calendar'
      response.headers['Content-Disposition'] = 'attachment; filename="schedule.ics"'
      return response
    schedule = request.files['schedule']
    if schedule and valid_filename(schedule.filename):
      cal = schedule_parse.build_calendar(schedule.filename)
      return cal.to_ical()
    return '404 Something went wrong'
  else:
    raise Exception('Invalid request type')

def valid_filename(fname):
  return fname.split('.')[-1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
  app.run(debug=True)