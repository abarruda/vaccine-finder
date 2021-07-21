#!/bin/bash

set -e

docker build ../. -t vax-finder:test

# k3d registry create vax-cluster-registry.localhost --port 58736
# docker tag vax-finder:test k3d-vax-cluster-registry.localhost:58736/vax-finder:test
# docker push k3d-vax-cluster-registry.localhost:58736/vax-finder:test

k3d cluster create --config k3d.yaml
k3d image import vax-finder:test -c vax-cluster

helm upgrade --install --debug \
--set image.tag=vax-finder:test \
--set twilio.accountSid=${TWILIO_ACCOUNT_SID} \
--set twilio.authToken=${TWILIO_AUTH_TOKEN} \
--set twilio.toPhone=${TWILIO_TO_PHONE} \
--set twilio.fromPhone=${TWILIO_FROM_PHONE} \
--set location.longitude=${LOCATION_LONGITUDE} \
--set location.latitude=${LOCATION_LATITUDE} \
vaccine-finder ../helm/.

kubectl get nodes
kubectl get cronjob

# k3d registry delete k3d-vax-cluster-registry.localhost
#k3d cluster delete vax-cluster