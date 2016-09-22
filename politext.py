from flask import Flask, request, redirect
import twilio.twiml, datetime, json
import jinja2
import os
import urllib.request as url
import requests

# author : Brian Mejia
app = Flask(__name__)

"""
Potential responses:
President NY
Senate AK
Favorable Rating Romney
Job Approval MN
EU Referendum
Primary NV DEM
"""

topics = {"president": "2016-president", "senate": "2016-senate", "house": "2016-house", 
			"favorable rating": "favorable-ratings", "job approval": "obama-job-approval"}
states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "US"]
obama_approval_sectors = {"independents": "-independents", "rep": "-republicans", 
		"dem": "-democrats", "adults": "-adults", "foreign policy": "-foreign-policy", 
		"health": "-health", "economy": "-economy"}
favorable_rating_sectors = {"stein": "jill-stein", "johnson": "gary-johnson", "kaine": "tim-kaine",
		"pence": "mike-pence", "o'malley": "martin-o-malley", "pataki": "george-pataki",
		"graham": "lindsey-graham", "jindal": "bobby-jindal", "gilmore": "jim-gilmore",
		"chafee": "lincoln-chafee", "fiorina": "carly-fiorina", "kasich": "john-kasich",
		"trump": "donald-trump", "perry": "rick-perry", "sanders": "bernie-sanders",
		"carson": "ben-carson", "warren": "elizabeth-warren", "huckabee": "mike-huckabee",
		"walker": "scott-walker", "cruz": "ted-cruz", "cuomo": "andrew-cuomo",
		"santorum": "rick-santorum", "bush": "jeb-bush", "paul": "rand-paul", "christie": "chris-christie",
		"pelosi": "nancy-pelosi", "reid": "harry-reid", "mcconnell": "mitch-mcconnell", 
		"boehner": "john-boehner", "rubio": "marco-rubio", "rep": "republican-party", "dem": "democratic-party",
		"clinton": "hillary-clinton", "biden": "joe-biden", "ryan": "paul-ryan", 
		"obama": "obama"}

def build_criteria(msg):
	msg_body = msg.lower().split()
	sector = ''
	potential_topics = [msg_body[0]]
	if len(msg_body) > 1: 
		potential_topics.append(msg_body[0] + " " + msg_body[1])
	if potential_topics[0] in topics:
		topic = topics[potential_topics[0]]
		if len(msg_body) == 1:
			state = 'US'
		elif msg_body[1].upper() not in states:
			return 'Error: State not recognized. Enter abbreviation or US.'
		else:
			state = msg_body[1].upper()
	elif len(msg_body) > 1 and potential_topics[1] in topics:
		topic = topics[potential_topics[1]]
		if len(msg_body) == 2:
			if topic == 'favorable-ratings':
				return 'Error: No candidate selected. Please enter their last name.'
			elif topic == 'eu-uk-referendum':
				state = 'UK'
			else:
				state = 'US'
		if topic == 'obama-job-approval' and len(msg_body) > 2:
			criteria = msg.lower().split(' ', 2)[2]
			if criteria.upper() in states:
				state = criteria.upper()
				sector = ''
			elif criteria in obama_approval_sectors:
				sector = 'obama-job-approval' + obama_approval_sectors[criteria]
				state = 'US'
			else:
				return 'Error: Job Approval criteria not recognized.'
		elif topic == 'favorable-ratings':
			if msg_body[2] in favorable_rating_sectors:
				sector = favorable_rating_sectors[msg_body[2]] + "-favorable-rating"
				state = 'US'
			else:
				return 'Error: Candidate not recognized. Enter another candidate.'
	else:
		return "Error: Topic is not recognized."

	chart_url = "http://elections.huffingtonpost.com/pollster/api/charts.json?topic=" + topic + "&state=" + state
	polls_url = "http://elections.huffingtonpost.com/pollster/api/polls.json?topic=" + topic + "&state=" + state

	chart_response = url.urlopen(chart_url)
	polls_response = url.urlopen(polls_url)

	chart_data = json.loads(chart_response.read().decode('utf-8'))
	polls_data = json.loads(polls_response.read().decode('utf-8'))

	search_data = [chart_data, polls_data, state, sector]

	return find_estimate(search_data, topic)

def find_estimate(search_data, topic):
	selected_data = None
	chart_data = search_data[0]
	if topic == 'obama-job-approval' or topic == 'favorable-ratings':
		for item in chart_data:
			if item['slug'] == search_data[3] or (search_data[3] == '' and item['state'] == search_data[2]):
				if len(item['estimates']) > 0:
					selected_data = [item, 'chart']
				else:
					selected_data = find_descriptive_poll(search_data, topic)
				break
	elif len(chart_data) == 0 or len(chart_data[0]['estimates']) == 0:
		selected_data = find_descriptive_poll(search_data, topic)
	else:
		selected_data = [chart_data[0], 'chart']

	if selected_data[0] is None:
		return "Error: There are no charts/data on this topic."
		
	return build_response(selected_data)


def find_descriptive_poll(search_data, topic):
	selected_poll = None
	item_count = 0
	poll_data = search_data[1]
	state = search_data[2]
	sector = search_data[3]
	for item in poll_data:
		for question in item['questions']:
			if question['topic'] == topic and question['state'] == state:
				for subpopulation in question['subpopulations']:
					sub_len = len(subpopulation['responses'])
					if sub_len > item_count:
						item_count = sub_len
						selected_poll = question
						selected_poll['source'] = item['pollster']
	return [selected_poll, 'poll']

def build_response(estimate):
	response = ""
	data = estimate[0]
	if estimate[1] == 'poll':
		response += data['name'] + "\n\n"
		response += str(data['subpopulations'][0]['observations']) + " " + \
			data['subpopulations'][0]['name'] + ":" + "\n"
		for choice in data['subpopulations'][0]['responses']:
			response += choice['choice'] + ": " + "{:.3g}%".format(float(choice['value'])) + "\n"
		response += "\nPoll Source: " + data['source']
	elif estimate[1] == 'chart':
		response += data['title'] + "\n\n"
		response += "Based on " + str(data['poll_count']) + " Polls:" + "\n"
		for choice in data['estimates']:
			party = '(U) '
			if (choice['party'] == 'Dem'):
				party = '(D) '
			elif (choice['party'] == 'Rep'):
				party = '(R) '
			response += party + choice['choice'] + ": " + "{:.3g}%".format(float(choice['value'])) + "\n"
		gurl = goo_shorten_url(data['url'])
		response += "\nSee the chart here: " + gurl
	return response

def goo_shorten_url(url):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyCzJlU2BF46intOo179nMKstgemnbxBxsk'
    params = json.dumps({'longUrl': url})
    response = requests.post(post_url,params,headers={'Content-Type': 'application/json'})
    return response.json()['id']

@app.route('/')
def show_homepage():
 	return app.send_static_file('index.html')

if __name__ == "__main__":
	#user_input = input("Enter search: ")
	#print(build_criteria(user_input))
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)