




## Need a database model to track sends

class Email(object):
    to = None
    cc = None
    bcc = None
    subject = 'Some text'
    body = 'emails/blah.html'

    def __init__(self):
        self._to = [] if self.to is None else list(self.to)
        self._cc = [] if self.cc is None else list(self.cc)
        self._bcc = [] if self.bcc is None else list(self.bcc)

    def many(self, attr, append=None):
        j = getattr(self, '_'+attr)
        if append is not None:
            j.append(append)
            return self
        return j

    def mto(self, append=None):
        return self.many('to', append)
    def mcc(self, append=None):
        return self.many('cc', append)
    def mbcc(self, append=None):
        return self.many('bcc', append)

    def context(self, **kwargs):
        self.context.update(kwargs)
        return self

    def send(self):
        pass


class DailyDeals(Notification):

    class textManager(Text):
        message = """
        Hello How are you?
        """

    class emailManager(Email):
        subject = "Hello"

    





if __name__ == '__main__':

    class FacilitySpecificEmail(Email):
        to = ['some@default.com']

    class GetDirectionsEmail(FacilitySpecificEmail):
        pass


    GetDirectionsEmail().mto('rajeev@alokin.in').context(key=10, **options).send()
    print GetDirectionsEmail().to


    DailyDeals.mobile('+919846088898').mto('rajeev@alokin.in', 'rajeev+test@alokin.in').context(blah="blah", **options).send()