#!/usr/local/bin/python3

# https://api.us.castlighthealth.com/vaccine-finder/v1/medications
# [
# {
# guid: "779bfe52-0dd8-4023-a183-457eb100fccc",
# name: "Moderna COVID Vaccine"
# },
# {
# guid: "a84fb9ed-deb4-461c-b785-e17c782ef88b",
# name: "Pfizer-BioNTech COVID Vaccine"
# },
# {
# guid: "784db609-dc1f-45a5-bad6-8db02e79d44f",
# name: "Johnson & Johnson's Janssen COVID Vaccine"
# }
# ]

import os
import urllib.request
import urllib.parse
import gzip
import json
import datetime
import time
from twilio.rest import Client

vaxMap = {"779bfe52-0dd8-4023-a183-457eb100fccc": "Moderna", 
"a84fb9ed-deb4-461c-b785-e17c782ef88b": "Pfizer",
"784db609-dc1f-45a5-bad6-8db02e79d44f": "J & J"}

# Your Account SID from twilio.com/console
twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
# Your Auth Token from twilio.com/console
twilio_auth_token  = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_to_phone = os.environ.get('TWILIO_TO_PHONE')
twilio_from_phone = os.environ.get('TWILIO_FROM_PHONE')

vaxIds = os.environ.get('VAX_IDS').split(",")
print(vaxIds)
longitude = os.environ.get('LOCATION_LONGITUDE')
lattitude = os.environ.get('LOCATION_LATITUDE')
radius = os.environ.get('LOCATION_RADIUS')

def sendTextMessage(text):
	truncatedText = text[0:1599] # 1600 characters max
	client = Client(twilio_account_sid, twilio_auth_token)

	message = client.messages.create(
    to=twilio_to_phone, 
    from_=twilio_from_phone,
    body=text)

	print("Sending text message (%s)" % message.sid)

def constructRequest(url):
	request = urllib.request.Request(url)
	request.add_header('Accept', 'application/json, text/plain')
	request.add_header('Accept-Encoding', 'gzip, deflate, br')
	request.add_header('Accept-Language', 'en-US,en;q=0.9')
	request.add_header('Connection', 'keep-alive')
	request.add_header('Host', 'api.us.castlighthealth.com')
	request.add_header('Origin', 'https://vaccinefinder.org')
	request.add_header('Referer', 'https://vaccinefinder.org/')
	request.add_header('sec-ch-ua', '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"')
	request.add_header('sec-ch-ua-mobile', '?0')
	request.add_header('Sec-Fetch-Dest', 'empty')
	request.add_header('Sec-Fetch-Mode', 'cors')
	request.add_header('Sec-Fetch-Site', 'cross-site')
	request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36')
	return request

def locationRequest():
	params = urllib.parse.urlencode({'medicationGuids': ",".join(vaxIds), 'lat': lattitude, 'long': longitude, 'radius': radius})
	url = "https://api.us.castlighthealth.com/vaccine-finder/v1/provider-locations/search?%s" % params
	print(url)
	return constructRequest(url)

def locationDetailRequest(locationGuid):
	url = "https://api.us.castlighthealth.com/vaccine-finder/v1/provider-locations/%s" % locationGuid
	return constructRequest(url)

def processResponse(response):
	content = gzip.decompress(response.read())
	return json.loads(content)

def timeSinceLastUpdate(locationDetailJson):
	lastUpdateTime = datetime.datetime.strptime(locationDetailJson['last_updated'], '%Y-%m-%dT%H:%M:%SZ')
	return (datetime.datetime.utcnow() - lastUpdateTime).seconds

def processVaxData(json):
	recentlyUpdated = []

	lastUpdateSeconds = timeSinceLastUpdate(json)
	if (lastUpdateSeconds <= 300):
		print("***** %s (%s) last updated %s minutes ago" % (locationDetailJsonData['name'], locationDetailJsonData['guid'], lastUpdateSeconds / 60))

	for vax in json['inventory']:
		if vax['guid'] in vaxIds and vax['supply_level'] != 'NO_SUPPLY' and vax['supply_level'] != 'NO_REPORT':
			nameAddressText = "%s (%s, %s, %s %s)" % (json['name'], json['address1'], json['city'], json['state'], json['zip'])
			print(nameAddressText)
			print("vax: %s" % vax['name'])
			print("Supply level: %s" % vax['supply_level'])
			if (lastUpdateSeconds <= 300):
				print("**** last updated %s minutes ago" % (lastUpdateSeconds / 60))
				recentlyUpdated.append({"name_address": nameAddressText, "vaxId": vax['guid'], "supply": vax['supply_level']})
			else:
				print("last updated %s minutes ago" % (lastUpdateSeconds / 60))
	return recentlyUpdated

recentlyUpdated = []
print("(%s) Checking for vaccines..." % datetime.datetime.now())
with urllib.request.urlopen(locationRequest()) as response:
	print("location response code: %s" % response.status)
	jsonData = processResponse(response)
	for location in jsonData['providers']:
		if (location['in_stock']):
			guid = location['guid']
			print("requesting location detail (%s)" % guid)
			with urllib.request.urlopen(locationDetailRequest(guid)) as locationDetailResponse:
				print("location detail response code: %s" % (response.status))
				locationDetailJsonData = processResponse(locationDetailResponse)
				recentlyUpdated+=processVaxData(locationDetailJsonData)
					
				print()
				time.sleep(1)

if len(recentlyUpdated) > 0:
	textMessage = ""
	for location in recentlyUpdated:
		textMessage+="%s\n%s\nSupply: %s\n\n" % (location['name_address'], vaxMap[location["vaxId"]], location['supply'])
	sendTextMessage(textMessage)
exit()

