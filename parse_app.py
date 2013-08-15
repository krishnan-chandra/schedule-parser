from flask import Flask, request, render_template, after_this_request, make_response
import schedule_parse

app = Flask(__name__)
ALLOWED_EXTENSIONS = ['html', 'htm']

@app.errorhandler(404)
def error_handler(exception):
  return render_template('404.html'), 404

@app.route('/', methods=['GET', 'POST'])
def home():
  if request.method == 'GET':
    return render_template('index.html')
  elif request.method == 'POST':
    schedule = request.files['schedule']
    try:
      if schedule and valid_filename(schedule.filename):
        cal = schedule_parse.build_calendar(schedule.filename)
        response = make_response(cal.to_ical())
        response.headers['Content-Type'] = 'text/calendar'
        response.headers['Content-Disposition'] = 'attachment; filename="schedule.ics"'
        return response
      else:
        return render_template('index.html', error='Sorry, the file you gave could not be parsed.')
    except:
      return render_template('404.html'), 404
  else:
    return render_template('404.html')

def valid_filename(fname):
  return fname.split('.')[-1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
  app.run(debug=True)