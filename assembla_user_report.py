# -*- coding: utf-8 *-*
from assembla.models import API
from settings.auth import assembla_auth, sendgrid_auth
import sendgrid
from datetime import datetime, timedelta
from dateutil import tz
from dateutil.parser import parse
from settings.mail import email_to, email_subject, colors, email_from

#run this code once at the end of day, or setup a crontab.


def get_assembla_summary():
    # Retrieve the Stream Events.
    # These are similar to those appearing on http://www.assembla.com/start (right side)

    api = API(assembla_auth)
    events = api.events()
    spaces = api.spaces()
    local_zone = tz.tzlocal()

    # Retrieve the events happened in all spaces for an Organization, for a day.

    tday = datetime.now()
    tday = tday.replace(tzinfo=local_zone)
    this_day = (tday - timedelta(hours=48)).date()
    plain_body = ""
    user_activity = {}

    for event in events:
        edt = parse(event.date)
        event_date_time = edt.astimezone(local_zone)
        event_date = event_date_time.date()
        if not event_date > this_day:
            break
        for space in spaces:
            for user in space.users():
                if user.name not in user_activity.keys():
                    user_activity[user.name] = plain_body
                if user.id == event.author['id'] and event.space['id'] == space.id:
                    plain_body += "<hr/> <b>{0}</b> @ <font color=".format(
                        event_date_time.strftime("%H:%M"),
                        event.author['name']
                        ) + \
                    colors.get(event.space['name'], 'red') + ">{0}</font> <a href='{3}'>{1}</a> <br/> {2} <br/>".format(
                        event.space['name'],
                        event.operation,
                        event.title,
                        event.url,
                        #event.whatchanged,
                        #event.comment_or_description,
                        )
                    if event.object == 'Ticket' and event.operation != 'created':
                        if getattr(event, 'whatchanged', None):
                            plain_body += "<font color='violet'>" + event.whatchanged + "</font><br/>"
                        elif getattr(event, 'comment_or_description', None):
                            plain_body += "<font color='violet'>" + event.comment_or_description + "</font><br/>"
                    if plain_body:
                        user_activity[user.name] += plain_body
                    plain_body = ""

    html = "<html><body>"
    holiday = True
    for k, v in user_activity.iteritems():
        #display summary per each user.
        if v:
            html += "<div>" + "<h3>" + k + "</h3>" + v + "</div>"
            holiday = False
    html += "</body></html>"
    return html, holiday
    
    

def main():
    html, holiday = get_assembla_summary()
    sender = sendgrid.Sendgrid(sendgrid_auth[0], sendgrid_auth[1], secure=True)
    if not holiday:
        tday = datetime.now()
        subject = "%s %s" % (email_subject, tday.strftime("%b %d %Y"))
        message = sendgrid.Message(email_from, subject, "", "<div>" + html + "</div>")
        for person in email_to:
            message.add_to(person[0], person[1])
        sender.smtp.send(message)

if __name__ == '__main__':
    main()
