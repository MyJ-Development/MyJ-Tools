import radius

r = radius.Radius('ispcube2014', host='172.16.174.2')

try:
    print('success' if r.authenticate('carnescarampangue', '123456') else 'failure')
    sys.exit(0)
except radius.ChallengeResponse as e:
    pass
# The ChallengeResponse exception has `messages` and `state` attributes
# `messages` can be displayed to the user to prompt them for their
# challenge response. `state` must be echoed back as a RADIUS attribute.

# Send state as an attribute _IF_ provided.
attrs = {'State': e.state} if e.state else {}

# Finally authenticate again using the challenge response from the user
# in place of the password.
print('success' if r.authenticate(username, response, attributes=attrs)
                else 'failure')