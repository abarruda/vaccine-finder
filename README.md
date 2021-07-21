# vaccine-finder
A Python based Kubernetes Cronjob that provides SMS notifications for recent vaccine stock replenishments in the configured area.

## Requirements

- Twilio account
- Kubernetes Cluster

## Deployment

### K3d

```bash
$ cd test

$ TWILIO_ACCOUNT_SID=<Twilio account SID> \
TWILIO_AUTH_TOKEN=<Twilio auth token> \
TWILIO_TO_PHONE=+<phone number to notify> \
TWILIO_FROM_PHONE=+<twilio phone number> \
LOCATION_LONGITUDE=<lat> \
LOCATION_LATITUDE=<long> ./run-k3d.sh
```

### Kind

```bash
$ cd test 

$ TWILIO_ACCOUNT_SID=<Twilio account SID> \
TWILIO_AUTH_TOKEN=<Twilio auth token> \
TWILIO_TO_PHONE=+<phone number to notify> \
TWILIO_FROM_PHONE=+<twilio phone number> \
LOCATION_LONGITUDE=<lat> \
LOCATION_LATITUDE=<long> ./run-k3d.sh
```

### Helm

```bash
helm upgrade --install --debug \
--set image.tag=vax-finder:latest \
--set twilio.accountSid=<Twilio account SID> \
--set twilio.authToken=<Twilio auth token> \
--set twilio.toPhone=+<phone number to notify> \
--set twilio.fromPhone=+<twilio phone number> \
--set location.latitude=<lat> \
--set location.longitude=-<long> \
--set location.radius=50 \
vaccine-finder helm/.
```