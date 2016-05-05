from flask import Flask, request, redirect
import twilio.twiml, datetime, urllib, json

# author : Brian Mejia
app = Flask(__name__)

url_gop = "http://elections.huffingtonpost.com/pollster/api/charts.json?topic=2016-president-gop-primary"
url_dem = "http://elections.huffingtonpost.com/pollster/api/charts.json?topic=2016-president-dem-primary"

gop_response = urllib.urlopen(url_gop)
dem_response = urllib.urlopen(url_dem)

gop_data = json.loads(gop_response.read())
dem_data = json.loads(dem_response.read())

gop_choices = ['trump', 'cruz', 'kasich', 'rubio', 'huckabee', 'palin', 'carson', 'bush', 'walker', 'ryan', 'paul', 'perry', 'graham', 'jindal', 'santorum']
dem_choices = ["clinton", "sanders", "o'malley"]
other_choices = ['undecided', 'other']

@app.route("/", methods=['GET', 'POST'])
def search_candidate():

    body = request.values.get('Body', None)
    resp = twilio.twiml.Response()

    data = None
    if body.lower() == "!help":
        resp.message("Hello! I search for data on the 2016 US Presidential Primaries and Caucuses!\n" +
            "Please use this format to get a proper response: <gop/dem> <state> [candidate(s)].\n" +
            "Example: dem MI Sanders\nThank you!\n")
        return '<h1>This sends messages to phones. Text the # (862) 256-2358</h1>';
    elif body.lower() == "!data":
        resp.message("All data is received from the HuffPost Pollster API.\nPython and Twilio were used to create this!\nCreated by Brian Mejia")
        return '<h1>This sends messages to phones. Text the # (862) 256-2358</h1>';
    
    body = body.split()
    if len(body) >= 2:
        party = body[0].lower()
        state = body[1].upper()
        choices = []
        c = []
    else:
        resp.message("Error: Not enough parameters. Use <party> <state> [choice(s)].")
        return '<h1>This sends messages to phones. Text the # (862) 256-2358</h1>';
    if len(body) >= 3:
        c = body[2:]
    elif len(body) == 2:
        choices = dem_choices if (party == "dem") else gop_choices
        choices += other_choices
        c = choices
    choices = [choice.lower() for choice in c]

    print party, state, choices

    if party == "dem" and (any(choice.lower() in choices for dchoice in dem_choices) or any(c.lower() in choices for ochoice in other_choices)):
        data = dem_data
    elif party == "gop" and (any(choice.lower() in choices for gchoice in gop_choices) or any(c.lower() in choices for ochoice in other_choices)):
        data = gop_data
    if data is not None:
        for item in data:
            if state == item['state']:
                if not item['estimates']:
                    message_str = "Error: There are no estimates for the %s. Try another primary/caucus." %item['title']
                    resp.message(message_str)
                    return '<h1>This sends messages to phones. Text the # (862) 256-2358</h1>';
                already_chosen = []
                choice_scores = []
                for estimate in item['estimates']:
                    if (estimate['choice'].lower()) in choices and (estimate['choice'].lower()) not in already_chosen:
                        already_chosen.append(estimate['choice'].lower())
                        today = datetime.datetime.today().strftime('%Y-%m-%d')
                        score = "%s: %.1f%%\n" %(estimate['choice'], estimate['value'])
                        choice_scores.append(score)
                if already_chosen:
                    message_str = "%s\n" %item['title']
                    for chosen in choice_scores:
                        message_str += chosen
                    if item['election_date'] > today:
                        message_str += "NOTE: These numbers are poll numbers as the election hasn't started yet.\n"
                else:
                    message_str = "Error: There are no estimates for candidates. Try again."
                resp.message(message_str)
                return '<h1>This sends messages to phones. Text the # (862) 256-2358</h1>';
        resp.message("Error: State is not in data.\n")
    else:
        resp.message("Error: Party or Choice is not in data.\n")
    return '<h1>This sends messages to phones. Text the # (862) 256-2358</h1>';

if __name__ == "__main__":
    app.run(debug=True)