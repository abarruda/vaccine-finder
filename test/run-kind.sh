#!/bin/bash

set -e

docker build ../. -t vax-finder:test

kind create cluster --config=kind.yaml

kind load docker-image vax-finder:test --name vax-cluster

docker exec -it vax-cluster-control-plane crictl images

helm upgrade --install --debug \
--set image.tag=vax-finder:test \
--set twilio.accountSid=${TWILIO_ACCOUNT_SID} \
--set twilio.authToken=${TWILIO_AUTH_TOKEN} \
--set twilio.toPhone=${TWILIO_TO_PHONE} \
--set twilio.fromPhone=${TWILIO_FROM_PHONE} \
--set location.longitude=${LOCATION_LONGITUDE} \
--set location.latitude=${LOCATION_LATITUDE} \
vaccine-finder ../helm/.

# kind delete cluster --name vax-cluster