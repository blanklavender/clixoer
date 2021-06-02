from gnowsys_ndf.settings import GSTUDIO_INSTITUTE_ID
from gnowsys_ndf.ndf.models import node_collection
from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.models import Session
class UserDetails(MiddlewareMixin):
    ''' Set's cookie. Gstudio supports following cookies along with django defalut:
    - `institute_id`: contains value of `GSTUDIO_INSTITUTE_ID`
    - `user_id`
    - `buddy_ids`: seperated by '&'
    - `user_and_buddy_ids`: seperated by '&'. first id will be logged in user's id followed by buddy-ids.
    '''
    # desired cookie will be available in every django view
    def process_request(self, request):
        # will only add cookie if request does not have it already
        try:
            # if not request.COOKIES.get('user_id'):
            print("inside UserDetails process_request")
            print(request.COOKIES)
            print(request.LANGUAGE_CODE)
            request.session.set_test_cookie()
            # Not using following cookie as we are not using cookie in views
            # 'user_and_buddy_ids'
        except Exception as e:
            pass

    # desired cookie will be available in every HttpResponse parser like browser but not in django view
    def process_response(self, request, response):
        try:
            print("inside UserDetails process_response")
            #request.session.delete_test_cookie()
            #from django.contrib.sessions.backends.db.models import Session
            print("Length:",str(len(request.session)))
            s = Session.objects.get(pk = request.COOKIES['sessionid'])
            #print("sadasddsdf")
            for each, val in s.get_decoded():
                print(each,":",val)
        except Exception as e:
            pass
        return response
    
class Author(MiddlewareMixin):
    ''' Set's data named "author". '''
    def process_request(self, request):
        #print "inside Author process_request"
        request.author = node_collection.find_one({'_type': 'Author', 'created_by': request.user.id})
        return 


class AdditionalDetails(MiddlewareMixin):
    """ Additional details can be added in this class """
    def process_response(self, request, response):
        #print "inside AdditionalDetails process_response"
        response.set_cookie('institute_id', GSTUDIO_INSTITUTE_ID)
        response.set_cookie('language_code', request.LANGUAGE_CODE)
        return response
