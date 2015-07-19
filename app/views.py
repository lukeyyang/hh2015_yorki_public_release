# imports
from flask import Flask, request, redirect, render_template
from twilio.rest import TwilioRestClient
from twilio_config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from twilio_config import TWILIO_FROM_NUMBER
from app import app, db, models
import requests
import twilio.twiml
import random

# config
twilio_client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Twilio - voice endpoint
@app.route('/voice', methods=['GET', 'POST'])
def voice():
  response = twiml.Response()
  response.say("Welcome to Yorki! You can visit us at replaceme.io\
                to sign up for our texts. ")
  return str(response)

# Twilio - sms endpoint
@app.route('/sms', methods=['GET', 'POST'])
def sms():
  # parse SMS
  msg = request.values.get('Body', None).lower()
  from_number = request.values.get('From', None)[2:] 
  # "10-digit string"
  if msg is not None:
    if 'info' in msg:
      tosend = 'Welcome to yorki, Text back with more or invite.'
    elif 'join' in msg:
      code = msg.replace('join','').strip()
      # make new user - copy properties from code
      # look for model user from code
      # print "duplicating user code " + code
      user_old = models.Subscriber.query.\
                      filter_by(id = code).first()
      user_new = models.Subscriber(phone = from_number,\
                                   time = user_old.time,\
                                   num_events = user_old.num_events,\
                                   neighborhood = user_old.neighborhood)

      db.session.add(user_new)
      db.session.commit()
      tosend = 'You have joined yorki. To modify settings, \
                      text back with "settings"'
    elif 'more' in msg:
      tosend = 'Here are more events in your area: '
      user_origin = models.Subscriber.query.\
                      filter_by(phone = from_number).first()
      user_area = models.Neighborhood.query.\
                      filter_by(id = user_origin.neighborhood).first()
      tosend += msg_pretty(search_for_event(area = user_area.zipcode,\
                                            number = 1))
    elif 'invite' in msg:
      invite_code = models.Subscriber.query.\
                    filter_by(phone = from_number).first().id
      tosend = 'Your invite code is ' + str(invite_code)
    elif 'settings' in msg:
      userid = models.Subscriber.query.\
                    filter_by(phone = from_number).first().id
      base_url = 'replaceme.ngrok.io/settings/'
      short_url = str(userid)
      # TODO prepare url in Flask
      tosend = "Go to " + base_url + short_url + \
               " to change delivery settings."
    else:
      tosend = "Unknown Command. Use the commands - \
                settings, info, join, more, or invite"
  else:
    tosend = 'Invalid'
  response = twilio.twiml.Response()
  response.sms(tosend)
  return str(response)

# Twilio - send sms
def send_message(number, message):
  message = twilio_client.messages.create(body = message,\
                                          to = number,\
                                          from_ = TWILIO_FROM_NUMBER)

# HTML - static HTML
@app.route('/')
def landing_page():
  return render_template('main.html')

# HTML - settings static HTML
@app.route('/settings')
def settings_page():
  return render_template('settings.html')

@app.route('/settings/')
def settings_page():
  return render_template('settings.html')

# HTML - static HTML
@app.route('/settings/<id>')
def user_settings(id):
  textTime = models.Subscriber.query.filter_by(id = id).first().time
  eventAmount = models.Subscriber.query.filter_by(id = id).first().num_events
  neighborhoodadjust = models.Neighborhood.query.\
    filter_by(id = models.Subscriber.query.filter_by(id = id).first().neighborhood).first().name
  return render_template('settings2.html', textTime=textTime, eventAmount=eventAmount, neighborhoodadjust=neighborhoodadjust)

# HTML - new user
@app.route('/adduser', methods=['POST'])
def add_user():
  phone = request.form['phone-initial']
  location = request.form['neighborhood-initial']
  neighborhood_to_add = \
    models.Neighborhood.query.filter_by(name = location).first()
  new_user = models.Subscriber(phone = phone, \
                               time = 1000, \
                               num_events = 3, \
                               neighborhood = neighborhood_to_add.id)
  db.session.add(new_user)
  db.session.commit()
  send_message(number = phone, message = "welcome!")

  return render_template('main.html')


# prepare events
def search_for_event(start_time = 1000, \
                     end_time = 2300, \
                     area = "", \
                     number = 3):
  payload = {"app_key":"REPLACE", \
             "app_id":"REPLACE", \
             "categories" : "Education"}
  payload["startTime"] = str(start_time / 100)
  payload["endTime"] = str(end_time / 100)
  payload["zip"] = area
  r = requests.get('https://api.cityofnewyork.us/calendar/v1/search.htm', \
                   params = payload)
  events_dict  = r.json()['items']
	
  result = []
  i = 0
  while i < number:
    index = random.randrange(0,len(events_dict))
    item = events_dict[index]
    
    if item['allDay'] != True:
      dct = {}
      dct['Event_Name'] = item['name']
      dct['Start_Time'] = item['startDate'].strip().split("T")[1].\
                          strip().split(".")[0]
      dct['Address'] = item['address']
      temp = ""

      for count in range(80) :
        if item['desc'][count] == "" :
          break;
        else:
          temp += item['desc'][count]
          if count == 79 :
            temp += "..."
      dct['Description'] = temp
      result.append(dct)
      i = i + 1
  return result

def msg_pretty(event_list): 
  msg = ""
  for i in event_list:
    msg += i['Event_Name'] + ", " + i['Address'] + \
          ", " + i['Start_Time'] + ", " + i['Description'] + "\n"
  return msg
