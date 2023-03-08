''' -- imports from python libraries -- '''
import re
import json
#import ox
import mailbox
import email.utils
import datetime
import os
import socket
import multiprocessing as mp
# import shutil
# import magic

from collections import OrderedDict
from time import time
from bson import json_util

#for creating deault mailbox : Metabox
#from django_mailbox.models import Mailbox
from imaplib import IMAP4

''' -- imports from installed packages -- '''
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from django.core.exceptions import PermissionDenied

from django import template
from django.template import RequestContext,loader
from django.shortcuts import render_to_response, render
#from django_mailbox.models import Mailbox

# cache imports
from django.core.cache import cache
from django.db.models import *
#from mongokit import IS

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS as setting_gapps, GSTUDIO_DEFAULT_GAPPS_LIST, META_TYPE, CREATE_GROUP_VISIBILITY, GSTUDIO_SITE_DEFAULT_LANGUAGE,GSTUDIO_DEFAULT_EXPLORE_URL,GSTUDIO_EDIT_LMS_COURSE_STRUCTURE,GSTUDIO_WORKSPACE_INSTANCE
# from gnowsys_ndf.settings import GSTUDIO_SITE_LOGO,GSTUDIO_COPYRIGHT,GSTUDIO_GIT_REPO,GSTUDIO_SITE_PRIVACY_POLICY, GSTUDIO_SITE_TERMS_OF_SERVICE,GSTUDIO_ORG_NAME,GSTUDIO_SITE_ABOUT,GSTUDIO_SITE_POWEREDBY,GSTUDIO_SITE_PARTNERS,GSTUDIO_SITE_GROUPS,GSTUDIO_SITE_CONTACT,GSTUDIO_ORG_LOGO,GSTUDIO_SITE_CONTRIBUTE,GSTUDIO_SITE_VIDEO,GSTUDIO_SITE_LANDING_PAGE
from gnowsys_ndf.settings import *
try:
	from gnowsys_ndf.local_settings import GSTUDIO_SITE_NAME
except ImportError:
	pass

from gnowsys_ndf.ndf.models import *
#from gnowsys_ndf.ndf.views.methods import check_existing_group, get_gapps, get_all_resources_for_group, get_execution_time, get_language_tuple
#from gnowsys_ndf.ndf.views.methods import get_drawers, get_group_name_id, cast_to_data_type, get_prior_node_hierarchy, get_course_completetion_status
# from gnowsys_ndf.mobwrite.models import TextObj

from pymongo.errors import InvalidId as invalid_id
from django.contrib.sites.models import Site
from gnowsys_ndf.ndf.views import es_queries
# from gnowsys_ndf.settings import LANGUAGES
# from gnowsys_ndf.settings import GSTUDIO_GROUP_AGENCY_TYPES,GSTUDIO_AUTHOR_AGENCY_TYPES
from elasticsearch_dsl import *
from gnowsys_ndf.ndf.node_metadata_details import schema_dict
#from django_mailbox.models import Mailbox
import itertools

register = template.Library()
at_apps_list = node_collection.find_one({"_cls": "AttributeType", "name": "apps_list"})
translation_set=[]
check=[]

#@get_execution_time
@register.simple_tag
def get_site_registration_variable_visibility(registration_variable=None):
    """Returns dictionary variable holding variables defined in settings file
    for Author's class regarding their visibility in registration template

    If looking for value of single variable, then pass that variable name as
    string which will return it's corresponding value. For example,
        bool_val = get_site_registration_variable_visibility(
            registration_variable="GSTUDIO_REGISTRATION_AUTHOR_AGENCY_TYPE"
        )

    Otherwise, if no parameter is passed, then returns a dictionary variable.
    For example,
        site_dict = get_site_registration_variable_visibility()
    In order to fetch given variable's value from above dictionay use following:
        site_registration_dict["AUTHOR_AGENCY_TYPE"]
        site_registration_dict["AFFILIATION"]
    """
    if registration_variable:
        return eval(registration_variable)

    else:
        site_registration_variable_visibility = {}
        site_registration_variable_visibility["AUTHOR_AGENCY_TYPE"] = GSTUDIO_REGISTRATION_AUTHOR_AGENCY_TYPE
        site_registration_variable_visibility["AFFILIATION"] = GSTUDIO_REGISTRATION_AFFILIATION
    return site_registration_variable_visibility


#@get_execution_time
@register.simple_tag
def get_site_variables():

	result = cache.get('site_var')
	if result:
		return result

	site_var = {}
	site_var['ORG_NAME'] = GSTUDIO_ORG_NAME
	site_var['LOGO'] = GSTUDIO_SITE_LOGO
	site_var['SECONDARY_LOGO'] = GSTUDIO_SITE_SECONDARY_LOGO
	site_var['FAVICON'] = GSTUDIO_SITE_FAVICON
	site_var['COPYRIGHT'] = GSTUDIO_DEFAULT_COPYRIGHT
	site_var['GIT_REPO'] = GSTUDIO_GIT_REPO
	site_var['PRIVACY_POLICY'] = GSTUDIO_SITE_PRIVACY_POLICY
	site_var['TERMS_OF_SERVICE'] = GSTUDIO_SITE_TERMS_OF_SERVICE
	site_var['ORG_LOGO'] = GSTUDIO_ORG_LOGO
	site_var['ABOUT'] = GSTUDIO_SITE_ABOUT
	site_var['SITE_POWEREDBY'] = GSTUDIO_SITE_POWEREDBY
	site_var['PARTNERS'] = GSTUDIO_SITE_PARTNERS
	site_var['GROUPS'] = GSTUDIO_SITE_GROUPS
	site_var['CONTACT'] = GSTUDIO_SITE_CONTACT
	site_var['CONTRIBUTE'] = GSTUDIO_SITE_CONTRIBUTE
	site_var['SITE_VIDEO'] = GSTUDIO_SITE_VIDEO
	site_var['LANDING_PAGE'] = GSTUDIO_SITE_LANDING_PAGE
	site_var['LANDING_TEMPLATE'] = GSTUDIO_SITE_LANDING_TEMPLATE
	site_var['HOME_PAGE'] = GSTUDIO_SITE_HOME_PAGE
	site_var['SITE_NAME'] = GSTUDIO_SITE_NAME
	site_var['SECOND_LEVEL_HEADER'] = GSTUDIO_SECOND_LEVEL_HEADER
	site_var['MY_GROUPS_IN_HEADER'] = GSTUDIO_MY_GROUPS_IN_HEADER
	site_var['MY_COURSES_IN_HEADER'] = GSTUDIO_MY_COURSES_IN_HEADER
	site_var['MY_DASHBOARD_IN_HEADER'] = GSTUDIO_MY_DASHBOARD_IN_HEADER
	site_var['ISSUES_PAGE'] = GSTUDIO_SITE_ISSUES_PAGE
	site_var['ENABLE_USER_DASHBOARD'] = GSTUDIO_ENABLE_USER_DASHBOARD
	site_var['BUDDY_LOGIN'] = GSTUDIO_BUDDY_LOGIN
	site_var['INSTITUTE_ID'] = GSTUDIO_INSTITUTE_ID
	site_var['HEADER_LANGUAGES'] = HEADER_LANGUAGES
	site_var['GSTUDIO_DOC_FOOTER_TEXT'] = GSTUDIO_DOC_FOOTER_TEXT
	site_var['GSTUDIO_OER_GROUPS'] = GSTUDIO_OER_GROUPS
	cache.set('site_var', site_var, 60 * 30)

	return  site_var


#@get_execution_time
@register.simple_tag
def get_oid_variables():

	result = cache.get('oid_var')
	if result:
		return result

	oid_var = {}

	try:
		# oid_var['ABOUT'] 				= GSTUDIO_OID_ABOUT
		# oid_var['COPYRIGHT'] 			= GSTUDIO_OID_COPYRIGHT
		# oid_var['PRIVACY_POLICY'] 	= GSTUDIO_OID_SITE_PRIVACY_POLICY
		# oid_var['TERMS_OF_SERVICE'] 	= GSTUDIO_OID_SITE_TERMS_OF_SERVICE
		# oid_var['PARTNERS'] 			= GSTUDIO_OID_SITE_PARTNERS
		# oid_var['GROUPS'] 			= GSTUDIO_OID_SITE_GROUPS
		# oid_var['CONTACT'] 			= GSTUDIO_OID_SITE_CONTACT
		# oid_var['CONTRIBUTE'] 		= GSTUDIO_OID_SITE_CONTRIBUTE
		# oid_var['LANDING_PAGE'] 		= GSTUDIO_OID_SITE_LANDING_PAGE
		# oid_var['HOME_PAGE'] 			= GSTUDIO_OID_SITE_HOME_PAGE

		oid_var['tc']			 	= GSTUDIO_OID_TC
		oid_var['oer']				= GSTUDIO_OID_OER

	except Exception as e:
		pass

	cache.set('oid_var', oid_var, 60 * 30)

	return  oid_var


#@get_execution_time
@register.simple_tag
def get_author_agency_types():
   return GSTUDIO_AUTHOR_AGENCY_TYPES


#@get_execution_time
@register.simple_tag
def get_group_agency_types():
   return GSTUDIO_GROUP_AGENCY_TYPES


#@get_execution_time
@register.simple_tag
def get_copyright():
   return GSTUDIO_COPYRIGHT


#@get_execution_time
@register.simple_tag
def get_agency_type_of_group(group_id):
	'''
	Getting agency_type value of the group.
	'''
	group_obj = node_collection.one({"_id": ObjectId(group_id)})
	group_agency_type = group_obj.agency_type
	# print "group_agency_type : ", group_agency_type
	return group_agency_type


#@get_execution_time
@register.simple_tag
def get_node_type(node):
        if node:
                obj = node_collection.find_one({"_id": ObjectId(node._id)})
                nodetype=node.member_of_names_list[0]
                if "Group" == nodetype:
                        pe = get_sg_member_of(node._id)
                        if "ProgramEventGroup" in pe:
                                return "ProgramEventGroup"
                return nodetype
        else:
                return ""

@register.simple_tag
def get_download_preview_cnt(ndname):
        #from django.db.models import *
        if ndname:
                objs = hit_counters.objects.values('visitednode_name').annotate(total_downloadcnt = Sum('download_count')).annotate(total_previewcnt = Sum('preview_count')).annotate(total_visitcnt = Sum('visit_count'))
                obj = [nd for nd in objs if nd['visitednode_name'] == ndname]
                if obj:
                        #print("counts:",obj[0])
                        return obj[0]
                else:
                        return ""
        else:
                return ""

#@get_execution_time
@register.simple_tag
def get_node(node_id):
        if node_id:
                #from elasticsearch_dsl import *
                obj = node_collection.find_one({"_id": ObjectId(node_id)})
                if obj:
                        return obj
        else:
                return ""

@register.simple_tag
def get_unplatformpkg_node(node_id,lang):
    print("get unplatform pkg",node_id,lang)
    if node_id:
        domain = get_attribute_value(node_id,'educationalsubject')
        print("domain:",domain)
        if domain == 'Digital Literacy':
                return "",""
        else:
                if domain != 'English':
                        q = Q('bool',must=[Q('match_phrase',group_set = node_id),Q('match_phrase',language = lang),Q('match_phrase',tags = 'unplatform')])
                else:
                        q = Q('bool',must=[Q('match_phrase',group_set = node_id),Q('match_phrase',tags = 'unplatform')])
                s1 = Search(using=es, index='nodes',doc_type="node").query(q)
                s2 = s1.execute()
                #prinnplatform pkr url:",s2[0].id
                if s1.count() > 0:
                        print("unplatform pkg url:",s2[0].id)
                        return s2[0]
                else:
                        nd = get_translated_node(node_id)
                        q = Q('bool',must=[Q('match_phrase',group_set = nd),Q('match_phrase',language = 'en'),Q('match_phrase',tags = 'unplatform')])
                        s1 = Search(using=es, index='nodes',doc_type="node").query(q)
                        s2 = s1.execute()
                        print("unplatform pkr url:",s2[0].id)
                        return s2[0]
    else:
                return "",""

@register.simple_tag
def get_downloadpckg(domain,lang):
    print("get download pkg",domain,lang)
    if domain == 'english':
            q = Q('bool',must=[Q('match_phrase',language = 'en'),Q('match_phrase',tags = 'unplatform'),Q('match_phrase',tags = domain)])
    else:
            q = Q('bool',must=[Q('match_phrase',language = lang),Q('match_phrase',tags = 'unplatform'),Q('match_phrase',tags = domain)])
    s1 = Search(using=es, index='nodes',doc_type="node").query(q)
    s2 = s1.execute()
    print("unplatform pkr url:",s2[0].id)
    return s2[0]
    
        
@register.simple_tag
def get_translated_node(node_id):
    print(node_id)
    if node_id:
        q = Q('bool',must=[Q('match',id = node_id )])
        s1 = Search(using=es, index='nodes',doc_type="node").query(q)
        s2 = s1.execute()
        #print "unplatform pkr url:",s2[0].id                                                                                                                          
        if s1.count() > 0:
                print("trns id:",s2[0].relation_set)
                for each in list(s2[0].relation_set):
                        print(type(each))
                        for k,v in (each.to_dict()).items():
                                if k == 'translation_of':
                                        return v
        else:
                return ""
    else:
                return ""


#@get_execution_time
@register.simple_tag
def get_schema(node):
	if node:
		# obj = node_collection.find_one({"_id": ObjectId(node.member_of[0])}, {"name": 1})
		print("type of node in get_schema",type(node))
		#from elasticsearch_dsl import * 
		if isinstance(node,response.hit.Hit):
			q = Q('match',id = node.member_of[0])
			s1 = Search(using=es, index='nodes',doc_type="node").query(q)
			s2 = s1.execute()
			nam =s2[0]
		else:
			nam = node.member_of_names_list[0]
		if(nam == 'Page'):
			return [1,schema_dict[nam]]

		elif hasattr(node, 'mime_type') and (nam=='File'):
			mimetype_val = node.get_gsystem_mime_type()
			if( 'image' in node.mime_type):
				return [1,schema_dict['Image']]
			elif('video' in mimetype_val or 'Pandora_video' in mimetype_val):
				return [1,schema_dict['Video']]
			else:
				return [1,schema_dict['Document']]
		else:
			return [0,""]
	else:
		return [0,""]

@register.filter
def get_item(dictionary, key):
    print("combined key:",key,dictionary.get(key))
    return dictionary.get(key)


@register.filter
def get_key(li, key):
    #print "combined key:",key
    #print "dictionary,key",li, key                                                                                                                            
    for each in li:
            if isinstance(each, AttrDict):
                    #print "inside if", 
                    d = each.to_dict()
                    if key in d:
                            if key == 'educationallevel':
                                    st = d.get(key)[0]
                                    #print st
                                    return st
                            #print "key:value",key,d.get(key)
                            return d.get(key)

@register.filter
def get_date_format(val):
    dt = datetime.datetime.strptime(val, '%d/%m/%Y %H:%M:%S:%f')
    frmtDt = dt.strftime("%d %B %Y")
    return frmtDt

@register.simple_tag
def get_resource_img(rsrc_type):
    print("in get resource image:",rsrc_type.encode('utf-8'))
    
    #dt = datetime.datetime.strptime(val, '%d/%m/%Y %H:%M:%S:%f')
    if rsrc_type in ['Tool',u'\u091f\u0942\u0932',u'\u0c2a\u0c28\u0c3f\u0c2e\u0c41\u0c1f\u0c4d\u0c1f\u0c41',u'\u0b95\u0bb0\u0bc1\u0bb5\u0bbf',u'\u0a38\u0a70\u0a26']:
            img = 'noun_Gears_1111296.svg'
    elif rsrc_type in ['Simulation',u'\u0938\u093f\u092e\u094d\u092f\u0941\u0932\u0947\u0936\u0928',u'\u0c05\u0c28\u0c41\u0c15\u0c30\u0c23',u'\u0b89\u0bb0\u0bc1\u0bb5\u0b95\u0baa\u0bcd\u0baa\u0b9f\u0bc1\u0ba4\u0bcd\u0ba4\u0bc1\u0ba4\u0bb2\u0bcd']:
            img = 'noun_atom_954768.svg'
    elif rsrc_type in ['Hands-on',u'\u092a\u094d\u0930\u093e\u092f\u094b\u0917\u093f\u0915']:
            img = 'noun_Game_694760.svg'
    elif rsrc_type in ['Forum']:
            img = 'noun_forum_563603.png'
    else:
            img = 'noun_Gears_1111296.svg'
    return img

#@get_execution_time
@register.filter
def is_Page(node):
	Page = node_collection.find_one({"_cls": "GSystemType", "name": "Page"})
	if(Page._id in node.member_of):
		return 1
	else:
		return 0


#@get_execution_time
@register.filter
def is_Quiz(node):
	Quiz = node_collection.find_one({"_cls": "GSystemType", "name": "Quiz"})
	if(Quiz._id in node.member_of):
		return 1
	else:
		return 0


#@get_execution_time
@register.filter
def is_File(node):
	File = node_collection.find_one({"_cls": "GSystemType", "name": "File"})
	if(File._id in node.member_of):
		return 1
	else:
		return 0

#@get_execution_time
@register.simple_tag
def get_languages():
        return LANGUAGES


#@get_execution_time
@register.simple_tag
def get_node_ratings(request,node_id):
	try:
		user = request.user
		node_obj = node_collection.one({'_id': ObjectId(node_id)})
		total_score = 0
		total_rating = 0
		rating_by_user = 0
		counter_var = 0
		avg_rating = 0.0
		rating_data = {}
		for each in node_obj:
			if each['user_id'] == user.id:
				rating_by_user = each['score']
			if each['user_id'] == 0:
				counter_var += 1
			total_score = total_score + each['score']
		if len(node_obj.rating) == 1 and counter_var == 1:
			total_rating = 0
		else:
			if node_obj.rating:
				total_rating = len(node_obj.rating) - counter_var
			if total_rating:
				if type(total_rating) is float:
					total_rating = round(total_rating,1)
				avg_rating = float(total_score)/total_rating
				avg_rating = round(avg_rating,1)

		rating_data['avg'] = avg_rating
		rating_data['tot'] = total_rating
		rating_data['user_rating'] = rating_by_user
		return rating_data

	except Exception as e:
		print("Error in get_node_ratings " + str(e))

#@get_execution_time
@register.simple_tag
def get_group_resources(group):
	try:
		res=get_all_resources_for_group(group['_id'])
		return res.count
	except Exception as e:
		print("Error in get_group_resources "+str(e))


#@get_execution_time
@register.simple_tag
def all_gapps():
	try:
		return get_gapps()
	except Exception as expt:
		print("Error in get_gapps "+str(expt))


#@get_execution_time
@register.simple_tag
def get_group_gapps(group_id=None):

	# group_obj = node_collection.one({"_id": ObjectId(group_id) }, { "name": 1, "attribute_set.apps_list": 1, '_type': 1 })

	if ObjectId.is_valid(group_id):

		# group_attrs = group_obj.get_possible_attributes(group_obj._id)
		# print group_attrs

		# gapps_list = group_attrs.get('apps_list', [])
		at_apps_list = node_collection.find_one({'_cls': 'AttributeType', 'name': 'apps_list'})
		# attr_list = triple_collection.find({'_type': 'GAttribute', 'attribute_type': at_apps_list._id, 'subject':group_obj._id})
		# attr_list = triple_collection.one({
		# 									'_type': 'GAttribute',
		# 									'attribute_type': at_apps_list._id,
		# 									'subject': ObjectId(group_id),
		# 									'status': u'PUBLISHED'
		# 								},
		# 								{'_id': 0, 'object_value': 1}
		# 							)

		attr_list = triple_collection.find_one({
											'_cls': 'GAttribute',
											'attribute_type': at_apps_list._id,
											'subject': ObjectId(group_id),
											'status': u'PUBLISHED',
											'object_value': {'$exists': 1}
										},
										{'_id': 0, 'object_value': 1}
									)
		# print attr_list.count()," ---------- count "

		if attr_list:
			all_gapp_ids_list = [node_collection.find_one({'_id': g['_id']}) for g in attr_list['object_value']]
			# all_gapp_ids_list = attr_list
			# print "\n legnt==== ", all_gapp_ids_list
			return all_gapp_ids_list
		# group_name = group_obj.name
		# for attr in group_obj.attribute_set:
		# 	if attr and "apps_list" in attr:
		# 		gapps_list = attr["apps_list"]
		# 		# print "\n", gapps_list,"\n"

		# 		all_gapp_ids_list = [node_collection.one({'_id':ObjectId(g['_id'])}) for g in gapps_list]
		# 		# print all_gapp_ids_list,">>>>>>>>>>\n\n works like prior_node"
		# 		return all_gapp_ids_list


	return []


#@get_execution_time
@register.simple_tag
def get_create_group_visibility():
	if CREATE_GROUP_VISIBILITY:
		return True
	else:
		return False


#@get_execution_time
@register.simple_tag
def get_site_info():
	sitename = Site.objects.all()[0].name.__str__()
	return sitename


#@get_execution_time
@register.simple_tag
def check_is_user_group(group_id):
	try:
		res_group_obj = get_group_name_id(group_id, True)
		# print "\n\n res_group_obj",res_group_obj._type
		if res_group_obj._type == "Author":
			return True
		else:
			return False
		# lst_grps=[]
		# all_user_grps=get_all_user_groups()
		# grp = node_collection.one({'_id':ObjectId(group_id)})
		# for each in all_user_grps:
		# 	lst_grps.append(each.name)
		# if grp.name in lst_grps:
		# 	return True
		# else:
		# 	return False
	except Exception as exptn:
		print("Exception in check_user_group "+str(exptn))


#@get_execution_time
@register.simple_tag
def switch_group_conditions(user,group_id):
	try:
		ret_policy=False
		req_user_id=User.objects.get(username=user).id
		group = node_collection.one({'_id':ObjectId(group_id)})
		if req_user_id in group.author_set and group.group_type == 'PUBLIC':
			ret_policy=True
		return ret_policy
	except Exception as ex:
		print("Exception in switch_group_conditions"+str(ex))


#@get_execution_time
@register.simple_tag
def get_all_user_groups():
	try:
		return node_collection.find({'_cls':'Author'}).sort('name', 1)
		# return list(all_groups)
	except:
		print("Exception in get_all_user_groups")


#@get_execution_time
@register.simple_tag
def get_group_object(group_id = None):
	try:
		if group_id == None :
			group_object = node_collection.find_one({'$and':[{'_cls':u'Group'},{'name':u'home'}]})
		else:
			group_object = node_collection.find_one({'_id':ObjectId(group_id)})
		return group_object
	except invalid_id:
		group_object = node_collection.find_one({'$and':[{'_cls':u'Group'},{'name':u'home'}]})
		return group_object


#@get_execution_time
@register.simple_tag
def get_oer_groups():
   print("inside get_oer_groups")
   gst_group = node_collection.find_one({'_cls': "GSystemType", 'name': "Group"})
   oergroups_cur = node_collection.find({'member_of':gst_group._id, 'name':{'$in':GSTUDIO_OER_GROUPS}}) .sort('last_update',-1)
   print("oer_groups_list", oergroups_cur.count())
   return list(oergroups_cur)  

#@get_execution_time
@register.simple_tag
def get_states_object(request):
   group_object = node_collection.find_one({'$and':[{'_cls':u'Group'},{'name':u'State Partners'}]})
   return group_object


#@get_execution_time
@register.simple_tag
def get_all_users_to_invite():
	try:
		inv_users = {}
		users = User.objects.all()
		for each in users:
			inv_users[each.username.__str__()] = each.id.__str__()
		return str(inv_users)
	except Exception as e:
		print(str(e))


#@get_execution_time
@register.simple_tag
def get_all_users_int_count():
	'''
	get integer count of all the users
	'''
	all_users = len(User.objects.all())
	return all_users


#@get_execution_time
@register.inclusion_tag('ndf/twist_replies.html')
def get_reply(request, thread,parent,forum,token,user,group_id):
	return {'request':request, 'thread':thread,'reply': parent,'user':user,'forum':forum,'csrf_token':token,'eachrep':parent,'groupid':group_id}


#@get_execution_time
@register.simple_tag
def get_all_possible_languages():
	language = list(LANGUAGES)
	all_languages = language# + OTHER_COMMON_LANGUAGES
	return all_languages

#@get_execution_time
@register.simple_tag
def get_metadata_values(metadata_type=None):

	metadata = {"educationaluse": GSTUDIO_RESOURCES_EDUCATIONAL_USE, "interactivitytype": GSTUDIO_RESOURCES_INTERACTIVITY_TYPE, "curricular": GSTUDIO_RESOURCES_CURRICULAR,"educationallevel": GSTUDIO_RESOURCES_EDUCATIONAL_LEVEL, "educationalsubject": GSTUDIO_RESOURCES_EDUCATIONAL_SUBJECT,"timerequired": GSTUDIO_RESOURCES_TIME_REQUIRED, "audience": GSTUDIO_RESOURCES_AUDIENCE , "textcomplexity": GSTUDIO_RESOURCES_TEXT_COMPLEXITY,"age_range": GSTUDIO_RESOURCES_AGE_RANGE ,"readinglevel": GSTUDIO_RESOURCES_READING_LEVEL, "educationalalignment": GSTUDIO_RESOURCES_EDUCATIONAL_ALIGNMENT}
	if metadata_type and metadata_type in metadata:
		return metadata[metadata_type]
	return metadata


#@get_execution_time
@register.simple_tag
def get_attribute_value(node_id, attr_name, get_data_type=False, use_cache=True):
    print("in get_attribute_value")
    # if (cache_key in cache) and not get_data_type and use_cache:                                                                                                     
    #     #print "from cache in module detail:", cache_result                                                                                                          
    #     return cache_result                                                                                                                                          

    attr_val = ""
    node_attr = data_type = None
    if node_id:
        # print "\n attr_name: ", attr_name                                                                                                                            
        # gattr = node_collection.one({'_type': 'AttributeType', 'name': unicode(attr_name) })                                                                         

        q = eval("Q('bool',must =[Q('match', type = 'AttributeType'), Q('match', name = attr_name)])")

        # q = Q('match',name=dict(query='File',type='phrase'))                                                                                                         
        s1 = Search(using=es, index='nodes',doc_type="node").query(q)
        s2 = s1.execute()

        gattr = s2[0]

        if get_data_type:
            data_type = gattr.data_type
        if gattr: # and node  :                                                                                                                                        
            # node_attr = triple_collection.find_one({'_type': "GAttribute", "subject": ObjectId(node_id), 'attribute_type': gattr._id, 'status': u"PUBLISHED"})       
            #print node_id,gattr.id
            q = eval("Q('bool',must =[Q('match', type = 'GAttribute'), Q('match', subject = str(node_id)), Q('match',attribute_type = str(gattr.id))])")

            # q = Q('match',name=dict(query='File',type='phrase'))                                                                                                     
            s1 = Search(using=es, index='triples',doc_type="triple").query(q)
            s2 = s1.execute()
           # print "s2:",s2,q                                                                                                                                          
            if s1.count() > 0:
                node_attr = s2[0]
                attr_val = node_attr.object_value
                #print("\n here: ", attr_name, " : ", type(attr_val), " : ", attr_val)
                #print("node attr:",node_attr)
    return attr_val

#@get_execution_time
@register.simple_tag
def get_relation_value(node_id, grel, return_single_right_subject=False):
    # import ipdb; ipdb.set_trace()
    print("inside get relation value")
    return es_queries.get_relation_value(node_id,grel)


#@get_execution_time
@register.simple_tag
def get_site_name_from_settings():
	# print "GSTUDIO_SITE_NAME : ", GSTUDIO_SITE_NAME
	# print "site name",GSTUDIO_SITE_NAME
	return GSTUDIO_SITE_NAME


#@get_execution_time
@register.simple_tag
def get_group_policy(group_id,user):
	try:
		policy = ""
		colg = node_collection.find_one({'_id':ObjectId(group_id)})
		if colg:
			policy = str(colg.subscription_policy)
	except:
		pass
	return policy


#@get_execution_time
@register.simple_tag
def get_user_group(user, selected_group_name):
  """
  Returns first 10 group(s) to which logged-in user is subscribed to (sorted by last_update field in descending order)
  excluding the currently selected group if it comes under the searching criteria

  Keyword arguments:
  user -- django's user object

  selected_group_name -- name of the group which is currently selected

  Returns:
  list of group and/or author (logged-in) node(s) resulted after given searching criteria
  """
  group_list = []
  auth_group = None

  group_cur = node_collection.find({'_cls': "Group", 'name': {'$nin': ["home", selected_group_name]},
  									'$or': [{'group_admin': user.id}, {'author_set': user.id}],
  								}).sort('last_update', -1).limit(9)

  auth_group = node_collection.one({'_cls': "Author", '$and': [{'name': unicode(user.username)}, {'name': {'$ne': selected_group_name}}]})

  if group_cur.count():
    for g in group_cur:
      group_list.append(g)

  if auth_group:
    # Appends author node at the bottom of the list, if it exists
    group_list.append(auth_group)

  if not group_list:
    return "None"

  return group_list


#@get_execution_time
@register.simple_tag
def get_prior_node(node_id):
	obj = node_collection.find_one({'_id':ObjectId(node_id) })
	prior = []
	topic_GST = node_collection.find_one({'_cls': 'GSystemType', 'name': 'Topic'})
	if topic_GST._id in obj.member_of:

		if obj.prior_node:
	                prior=[(node_collection.one({'_id': ObjectId(each) })._id,node_collection.one({'_id': ObjectId(each) }).name) for each in obj.prior_node]
		return prior

	return prior


# method fist get all possible translations associated with current node &
# return the set of resources by using get_resources method
#@get_execution_time
@register.simple_tag
def get_all_resources(request,node_id):
        obj_set=[]
        keys=[] # set of keys used for creating the fieldset in template
        result_set=[]
        node=node_collection.one({'_id':ObjectId(node_id)})
        result_set=get_possible_translations(node)
        if node._id not in obj_set:
                obj_set.append(node._id)
                for item in result_set:
                        # print "\n=====",item.keys()
                        obj_set.extend(item.keys())
        resources={'Images':[],'Documents':[],'Audios':[],'Videos':[],'Interactives':[], 'eBooks':[]}
        for each in obj_set:
                n=node_collection.find_one({'_id':ObjectId(each)})
                resources_dict=get_resources(each,resources)
        res_dict={'Images':[],'Documents':[],'Audios':[],'Videos':[],'Interactives':[], 'eBooks':[]}

        for k,v in res_dict.items():
                res_dict[k]={'fallback_lang':[],'other_languages':[]}
        for key,val in resources_dict.items():
                if val:
                        keys.append(key)
                        for res in val:
                            if isinstance(res.language, (list, tuple)) and len(res.language) > 1 and (res.language[0] != request.LANGUAGE_CODE):
                                    res_dict[key]['other_languages'].append(res)
                            else:
                                    res_dict[key]['fallback_lang'].append(res)

        for k1,v1 in res_dict.items():
                if k1 not in keys :
                        del res_dict[k1]
        return res_dict
# method returns resources associated with node
#@get_execution_time
@register.simple_tag
def get_resources(node_id,resources):
        node = node_collection.find_one({'_id': ObjectId(node_id)})
        RT_teaches = node_collection.find_one({'_cls':'RelationType', 'name': 'teaches'})
        RT_translation_of = node_collection.find_one({'_cls':'RelationType','name': 'translation_of'})
        teaches_grelations = triple_collection.find({'_cls': 'GRelation', 'right_subject': node._id, 'relation_type': RT_teaches._id })
        AT_educationaluse = node_collection.find_one({'_cls': 'AttributeType', 'name': u'educationaluse'})
        for each in teaches_grelations:
                obj=node_collection.one({'_id':ObjectId(each.subject)})
                mime_type=triple_collection.one({'_cls': "GAttribute", 'attribute_type': AT_educationaluse._id, "subject":each.subject})
                for k,v in resources.items():
                        if mime_type and mime_type.object_value == k:
                                if obj.name not in resources[k]:
                                        resources.setdefault(k,[]).append(obj)

        return resources



'''this template function is used to get the user object from template'''
#@get_execution_time
@register.simple_tag
def get_user_object(user_id):
	user_obj=""
	try:
		user_obj=User.objects.get(id=user_id)
	except Exception as e:
		print("User Not found in User Table",e)
	return user_obj


#@get_execution_time
@register.filter
def get_username(user_id):
	try:
		return User.objects.get(id=user_id).username
	except:
		return user_id


#@get_execution_time
@register.simple_tag
def get_grid_fs_object(f):
    """
    Get the gridfs object by object id
    """
    grid_fs_obj = ""
    try:
        file_obj = node_collection.one({'_id': ObjectId(f['_id'])})
        if file_obj.mime_type == 'video':
            if len(file_obj.fs_file_ids) > 2:
                if (file_obj.fs.files.exists(file_obj.fs_file_ids[2])):
                    grid_fs_obj = file_obj.fs.files.get(ObjectId(file_obj.fs_file_ids[2]))
        else:
            grid_fs_obj = file_obj.fs.files.get(file_obj.fs_file_ids[0])
    except Exception as e:
        print("Object does not exist", e)
    return grid_fs_obj

#@get_execution_time
@register.simple_tag
def get_Object_count(key):
		try:
				return node_collection.find({'_cls':key}).count()
		except:
				return 'null'

#@get_execution_time
@register.simple_tag
def get_memberof_objects_count(request, key, group_id):
	try:
		lang = list(get_language_tuple(request.LANGUAGE_CODE))
		return node_collection.find({'member_of': {'$all': [ObjectId(key)]},'group_set': {'$all': [ObjectId(group_id)]}, 'language': lang}).count()
	except:
		return 'null'


'''Pass the ObjectId and get the name of it's first member_of element'''
#@get_execution_time
@register.simple_tag
def get_memberof_name(node_id):
	try:
		node_obj = node_collection.find_one({'_id': ObjectId(node_id)})
		member_of_name = ""
		if node_obj.member_of:
			member_of_name = node_collection.find_one({'_id': ObjectId(node_obj.member_of[0]) }).name
		return member_of_name
	except:
		return 'null'

#@get_execution_time
@register.filter
def get_dict_item(dictionary, key):
	return dictionary.get(key)


#@get_execution_time
@register.simple_tag
def get_policy(group, user):
  if group.group_type =='PUBLIC':
    return False
  elif user.is_superuser:
    return True
  elif user.id in group.author_set:
    return True
  elif user.id == group.created_by:
    return True
  else:
    return False


#@get_execution_time
@register.simple_tag
def group_type_info(groupid,user=0):
	cache_key = "group_type_" + str(groupid)
	cache_result = cache.get(cache_key)

	if cache_result:
		return cache_result

	# group_gst = node_collection.one({'_id': ObjectId(groupid)},
	# 	{'post_node': 1, 'prior_node': 1, 'group_type': 1})
	group_gst = get_group_name_id(groupid, get_obj=True)

	if group_gst.post_node:
		group_type = "BaseModerated"
	elif group_gst.prior_node:
		group_type = "Moderated"
	else:
		group_type = group_gst.group_type

	if cache_result != group_type:
		cache.set(cache_key, group_type)

	return group_type


#@get_execution_time
@register.simple_tag
def user_access_policy(node, user):
  """
  Returns status whether logged-in user is able to access any resource.

  Check is performed in given sequence as follows (sequence has importance):
  - If user is superuser, then he/she is allowed
  - Else if user is creator or admin of the group, then he/she is allowed
  - Else if group's edit-policy is "NON_EDITABLE" (currently "home" is such group), then user is NOT allowed
  - Else if user is member of the group, then he/she is allowed
  - Else user is NOT allowed!

  Arguments:
  node -- group's node that is currently selected by the user_access
  user -- user's node that is currently logged-in

  Returns:
  string value (allow/disallow), i.e. whether user is allowed or not!
  """
  user_access = False

  try:
    # Please make a note, here the order in which check is performed is IMPORTANT!

    if not user.is_authenticated:
        return "disallow"

    if user.is_superuser:
        user_access = True

    else:
      # group_node = node_collection.one({'_type': {'$in': ["Group", "Author"]}, '_id': ObjectId(node)})
      group_node = get_group_name_id(node, get_obj=True)
      # group_node = node_collection.one({"_id": ObjectId(group_id)})

      if user.id == group_node.created_by:
        user_access = True

      elif user.id in group_node.group_admin:
        user_access = True

      elif "PartnerGroup" in group_node.member_of_names_list:
        user_access = True

      elif group_node.edit_policy == "NON_EDITABLE":
        user_access = False

      elif user.id in group_node.author_set:
        user_access = True

      else:
        auth_obj = Author.get_author_by_userid(user.id)
        if auth_obj:
          if auth_obj.agency_type == 'Teacher':
            user_access = True
          elif auth_obj.agency_type == 'Student' and GSTUDIO_IMPLICIT_ENROLL:
            user_access = True

    if user_access:
      return "allow"

    else:
      return "disallow"

  except Exception as e:
    error_message = "\n UserAccessPolicyError: " + str(e) + " !!!\n"
    # raise Exception(error_message)
    return 'disallow'

#@get_execution_time
@register.simple_tag
def resource_info(node):
		col_Group=db[Group.collection_name]
		try:
			group_gst=col_Group.Group.one({'_id':ObjectId(node._id)})
		except:
			grname=re.split(r'[/=]',node)
			group_gst=col_Group.Group.one({'_id':ObjectId(grname[1])})
		return group_gst


#@get_execution_time
@register.simple_tag
def edit_policy(groupid,node,user):
	groupnode = node_collection.find_one({"_id":ObjectId(groupid)})
	# node=resource_info(node)
	#code for public Groups and its Resources
	resource_type = node_collection.find_one({"_id": {"$in":node.member_of}})
	if resource_type.name == 'Page':
		if node.type_of:
			resource_type_name = get_objectid_name(node.type_of[0])
			if resource_type_name == 'Info page':
				if user.id in groupnode.group_admin:
					return "allow"
			elif resource_type_name == 'Wiki page':
				return "allow"
			elif resource_type_name == 'Blog page':
				if user.id ==  node.created_by:
					return "allow"
		else:
			return "allow"
	else:
		return "allow"

#@get_execution_time
@register.simple_tag
def get_prior_post_node(group_id):
	col_Group = db[Group.collection_name]
	prior_post_node=col_Group.Group.one({'_cls': 'Group',"_id":ObjectId(group_id)})
	#check wheather we got the Group name
	if prior_post_node is not  None:
			 #first check the prior node id  and take the id
			 Prior_nodeid=prior_post_node.prior_node
			 #once you have the id check search for the base node
			 base_colg=col_Group.Group.one({'_cls':u'Group','_id':{'$in':Prior_nodeid}})
			 if base_colg is None:
					#check for the Post Node id
                                 Post_nodeid=prior_post_node.post_nodeMod_colg=col_Group.Group.find({'_cls':u'Group','_id':{'$in':Post_nodeid}})
                                 Mod_colg=list(Mod_colg)
                                 if list(Mod_colg) is not None:
                                     	 #return node of the Moderated group
                                         return Mod_colg
			 else:
				 #return node of the base group
				 return base_colg

#@get_execution_time
@register.simple_tag
def Group_Editing_policy(groupid,node,user):
	col_Group = db[Group.collection_name]
	node=col_Group.Group.one({"_id":ObjectId(groupid)})

	if node.edit_policy == "EDITABLE_MODERATED":
		 status=edit_policy(groupid,node,user)
		 if status is not None:
				return "allow"
	elif node.edit_policy == "NON_EDITABLE":
		status=non_editable_policy(groupid,user.id)
		if status is not None:
				return "allow"
	elif node.edit_policy == "EDITABLE_NON_MODERATED":
		 status=edit_policy(groupid,node,user)
		 if status is not None:
				return "allow"
	elif node.edit_policy is None:
		return "allow"

#@get_execution_time
@register.simple_tag
def check_is_gstaff(groupid, user):
  """
  Checks whether given user belongs to GStaff.
  GStaff includes only those members which belongs to following criteria:
    1) User should be a super-user (Django's superuser)
    2) User should be a creator of the group (created_by field)
    3) User should be an admin-user of the group (group_admin field)

  Other memebrs (author_set field) doesn't belongs to GStaff.

  Arguments:
  groupid -- ObjectId of the currently selected group
  user -- User object taken from request object

  Returns:
  True -- If user is one of them, from the above specified list of categories.
  False -- If above criteria is not met (doesn't belongs to any of the category, mentioned above)!
  """
  print("inside check_is_gstaff")
  group_name, group_id = Group.get_group_name_id(groupid)
  print(group_name)
  cache_key = 'is_gstaff' + str(group_id) + str(user.id)

  if cache_key in cache:
  	print("inside cache:",cache_key)
  	return cache.get(cache_key)

  groupid = groupid if groupid else 'home'

  try:

    if group_id:
        group_node = Group.get_group_name_id(groupid, get_obj=True)
        result = group_node.is_gstaff(user)
        cache.set(cache_key, result, 60 * 60)
        return result

    else:
    	error_message = "No group exists with this id ("+str(groupid)+") !!!"
    	raise Exception(error_message)

  except Exception as e:
    error_message = "\n IsGStaffCheckError: " + str(e) + " \n"
    raise Http404(error_message)

#@get_execution_time
@register.simple_tag
def check_is_gapp_for_gstaff(groupid, app_dict, user):
    """
    This restricts view of MIS & MIS-PO GApp to only GStaff members
    (super-user, creator, admin-user) of the group.
    That is, other subscribed-members of the group can't even see these GApps.

    Arguments:
    groupid -- ObjectId of the currently selected group
    app_dict -- A dictionary consisting of following key-value pair
                - 'id': ObjectId of the GApp
                - 'name': name of the GApp
    user - User object taken from request object

    Returns:
    A bool value indicating:-
    True --  if user is superuser, creator or admin of the group
    False -- if user is just a subscribed-member of the group
    """

    try:
        if app_dict["name"].lower() in ["mis", "mis-po", "batch"]:
            return check_is_gstaff(groupid, user)

        else:
            return True

    except Exception as e:
        error_message = "\n GroupAdminCheckError (For MIS): " + str(e) + " \n"
        raise Http404(error_message)


#@get_execution_time
@register.simple_tag
def get_resource_collection(groupid, resource_type):
  """
  Returns collections of given resource-type belonging to currently selected group

  Arguments:
  groupid -- ObjectId (in string format) of currently selected group
  resource_type -- Type of resource (Page/File) whose collections need to find

  Returns:
  Mongodb's cursor object holding nodes having collections
  """
  try:
    file_gst = node_collection.find_one({'_cls': "GSystemType", 'name': unicode(resource_type)})
    page_gst = node_collection.find_one({'_cls': "GSystemType", 'name': "Page"})
    res_cur = node_collection.find({'_cls': {'$in': [u"GSystem", u"File"]},
                                    'member_of': {'$in': [file_gst._id, page_gst._id]},
                                    'group_set': ObjectId(groupid),
                                    'collection_set': {'$exists': True, '$not': {'$size': 0}}
                                  })
    return res_cur

  except Exception as e:
    error_message = "\n CollectionsFindError: " + str(e) + " !!!\n"
    raise Exception(error_message)

#@get_execution_time
@register.simple_tag
def get_all_file_int_count():
	'''
	getting all the file/e-library type resource
	'''
	all_files = node_collection.find({ "_cls": "File", "access_policy": "PUBLIC" })
	return all_files.count()

#@get_execution_time
@register.simple_tag
def app_translations(request, app_dict):
   app_id=app_dict['id']
   get_translation_rt = node_collection.one({'$and':[{'_cls':'RelationType'},{'name':u"translation_of"}]})
   if request.LANGUAGE_CODE != GSTUDIO_SITE_DEFAULT_LANGUAGE:
      get_rel = triple_collection.one({'$and':[{'_cls':"GRelation"},{'relation_type':get_translation_rt._id},{'subject':ObjectId(app_id)}]})
      if get_rel:
         get_trans=node_collection.one({'_id':get_rel.right_subject})
         if get_trans.language == request.LANGUAGE_CODE:
            return get_trans.name
         else:
            app_name=node_collection.one({'_id':ObjectId(app_id)})
            return app_name.name
      else:
         app_name=node_collection.one({'_id':ObjectId(app_id)})
         return app_name.name
   else:
      app_name=node_collection.one({'_id':ObjectId(app_id)})
      return app_name.name

# getting video metadata from wetube.gnowledge.org
#@get_execution_time
@register.simple_tag
def get_pandoravideo_metadata(src_id):
  try:
    api=ox.api.API("http://wetube.gnowledge.org/api")
    data=api.get({"id":src_id,"keys":""})
    mdata=data.get('data')
    return mdata
  except Exception as e:
    return 'null'

#@get_execution_time
@register.simple_tag
def get_source_id(obj_id):
  try:
    source_id_at = node_collection.find_one({'$and':[{'name':'source_id'},{'_cls':'AttributeType'}]})
    att_set = triple_collection.find_one({'_cls': 'GAttribute', 'subject': ObjectId(obj_id), 'attribute_type': source_id_at._id})
    return att_set.object_value
  except Exception as e:
    return 'null'

#@get_execution_time
def get_translation_relation(obj_id, translation_list = [], r_list = []):
   get_translation_rt = node_collection.find_one({'$and':[{'_cls':'RelationType'},{'name':u"translation_of"}]})
   r_list_append_temp=r_list.append #a temp. variable which stores the lookup for append method
   translation_list_append_temp=translation_list.append#a temp. variable which stores the lookup
   if obj_id not in r_list:
      r_list_append_temp(obj_id)
      node_sub_rt = triple_collection.find({'$and':[{'_cls':"GRelation"},{'relation_type':get_translation_rt._id},{'subject':obj_id}]})
      node_rightsub_rt = triple_collection.find({'$and':[{'_cls':"GRelation"},{'relation_type':get_translation_rt._id},{'right_subject':obj_id}]})

      if list(node_sub_rt):
         node_sub_rt.rewind()
         for each in list(node_sub_rt):
            right_subject = node_collection.find_one({'_id':each.right_subject})
            if right_subject._id not in r_list:
               r_list_append_temp(right_subject._id)
      if list(node_rightsub_rt):
         node_rightsub_rt.rewind()
         for each in list(node_rightsub_rt):
            right_subject = node_collection.one({'_id':each.subject})
            if right_subject._id not in r_list:
               r_list_append_temp(right_subject._id)
      if r_list:
         r_list.remove(obj_id)
         for each in r_list:
            dic={}
            node = node_collection.find_one({'_id':each})
            dic[node._id]=node.language
            translation_list_append_temp(dic)
            get_translation_relation(each,translation_list, r_list)
   return translation_list


# returns object value of attribute
#@get_execution_time
@register.simple_tag
def get_object_value(node):
   at_set = ['contact_point','house_street','town_city','state','pin_code','email_id','telephone','website']
   att_name_value= OrderedDict()

   for each in at_set:
      attribute_type = node_collection.find_one({'_cls':"AttributeType" , 'name':each})
      if attribute_type:
      	get_att = triple_collection.find_one({'_cls':"GAttribute", 'subject':node._id, 'attribute_type': attribute_type._id})
      	if get_att:
        	att_name_value[attribute_type.altnames] = get_att.object_value

   return att_name_value


#@get_execution_time
@register.simple_tag
# return json data of object
def get_json(node):
   node_obj = node_collection.find_one({'_id':ObjectId(str(node))})
   return json.dumps(node_obj, cls=NodeJSONEncoder, sort_keys = True)


#@get_execution_time
@register.filter("is_in")
# filter added to test if vaiable is inside of list or dict
def is_in(var, args):
    if args is None:
        return False
    arg_list = [arg.strip() for arg in args.split(',')]
    return var in arg_list


#@get_execution_time
@register.filter("del_underscore")
# filter added to remove underscore from string
def del_underscore(var):
   var = var.replace("_"," ")
   return var

#@get_execution_time
@register.simple_tag
# this function used for info-box implementation
# which convert str to dict type & returns dict which used for rendering in template
def str_to_dict(str1):
    dict_format = json.loads(str1, object_pairs_hook = OrderedDict)
    keys_to_remove = ('_id','access_policy','rating', 'fs_file_ids', 'content_org', 'content', 'comment_enabled', 'annotations', 'login_required','status','featured','module_set','property_order','url') # keys needs to hide
    keys_by_ids = ('member_of', 'group_set', 'collection_set','prior_node') # keys holds list of ids
    keys_by_userid = ('modified_by', 'contributors', 'created_by', 'author_set') # keys holds dada from User table
    keys_by_dict = ('attribute_set', 'relation_set')
    keys_by_filesize = ('file_size')
    for k in keys_to_remove:
      dict_format.pop(k, None)
    for k, v in dict_format.items():
      if type(dict_format[k]) == list :
          if len(dict_format[k]) == 0:
                  dict_format[k] = "None"
      if k in keys_by_ids:
        name_list = []
        if "None" not in dict_format[k]:
                for ids in dict_format[k]:
                        node = node_collection.find_one({'_id':ObjectId(ids)})
                        if node:
                                name_list.append(node)
                                dict_format[k] = name_list

      if k in keys_by_userid:

              if type(dict_format[k]) == list :
                      for userid in dict_format[k]:
                      		  if User.objects.filter(id = userid).exists():
	                              user = User.objects.get(id = userid)
	                              if user:
	                                dict_format[k] = user.get_username()
              else:
                      # if v != [] and v != "None":
                      if v:
                      		  if User.objects.filter(id = v).exists():
	                              user = User.objects.get(id = v)
	                              if user:
	                                dict_format[k] = user.get_username()

      if k in keys_by_dict:
              att_dic = {}
              if "None" not in dict_format[k]:
                      if type(dict_format[k]) != str and k == "attribute_set":
                              for att in dict_format[k]:
                                      for k1, v1 in att.items():
                                        if type(v1) == list:
                                                str1 = ""
                                                if type(v1[0]) in [OrderedDict, dict]:
                                                    for each in v1:
                                                        str1 += each["name"] + ", "
                                                else:
                                                    str1 = ",".join(v1)
                                                att_dic[k1] = str1
                                                dict_format[k] = att_dic
                                        else:
                                                att_dic[k1] = v1
                                                dict_format[k] = att_dic
                      if k == "relation_set":
                              for each in dict_format[k]:
                                      for k1, v1 in each.items():
                                              for rel in v1:
                                                      rel = node_collection.find_one({'_id':ObjectId(rel)})
                                                      if rel:
                                                      	att_dic[k1] = rel.name
                                      dict_format[k] = att_dic

      if k in keys_by_filesize:
              filesize_dic = {}
              for k1, v1 in dict_format[k].items():
                      filesize_dic[k1] = v1
              dict_format[k] = filesize_dic
    order_dict_format = OrderedDict()
    order_val=['altnames','language','plural','_type','member_of','created_by','created_at','tags','modified_by','author_set','group_set','collection_set','contributors','last_update','start_publication','location','legal','attribute_set','relation_set']
    for each in order_val:
            order_dict_format[each]=dict_format[each]
    return order_dict_format

#@get_execution_time
@register.simple_tag
def get_possible_translations(obj_id):
        translation_list = []
        r_list1 = []
        return get_translation_relation(obj_id._id,r_list1,translation_list)


#textb
#@get_execution_time
@register.filter("mongo_id")
def mongo_id(value):
		 # Retrieve _id value
		if type(value) == type({}):
				if value.has_key('_id'):
						value = value['_id']

		# Return value
		return unicode(str(value))

#@get_execution_time
@register.simple_tag
def get_version_of_module(module_id):
	''''
	This method will return version number of module
	'''
	ver_at = node_collection.find_one({'_cls':'AttributeType','name':'version'})
	if ver_at:
		attr = triple_collection.find_one({'_cls':'GAttribute','attribute_type':ver_at._id,'subject':ObjectId(module_id)})
		if attr:
			return attr.object_value
		else:
			return ""
	else:
		return ""

#@get_execution_time
@register.simple_tag
def get_group_name(groupid):
	# group_name, group_id = get_group_name_id(groupid)
        print("ndf tags : in get_grp_name:",groupid)
        return es_queries.get_group_name_id(groupid)[0]


@register.filter
def concat(value1, value2):
    """concatenate multiple received args
    """
    return_str = value1.__str__()
    value2 = value2.__str__()
    return return_str + value2


#@get_execution_time
@register.filter
def get_field_type(node_structure, field_name):
  """Returns data-type value associated with given field_name.
  """
  return node_structure.get(field_name)

#@get_execution_time
@register.simple_tag
def check_node_linked(node_id):
  """
  Checks whether the passed node is linked with it's corresponding author node (i.e via "has_login" relationship)

  Arguments:
  node_id -- ObjectId of the node

  Returns:
  A bool value, i.e.
  True: if linked (i.e. relationship is created for the given node)
  False: if not linked (i.e. relationship is not created)
  """

  try:
    node = node_collection.find_one({'_id': ObjectId(node_id)}, {'_id': 1})
    relation_type_node = node_collection.find_one({'_cls': "RelationType", 'name': "has_login"})
    is_linked = triple_collection.find_one({'_cls': "GRelation", 'subject': node._id, 'relation_type': relation_type_node.get_dbref()})

    if is_linked:
      return True

    else:
      return False

  except Exception as e:
    error_message = " NodeUserLinkFindError - " + str(e)
    raise Exception(error_message)

#@get_execution_time
@register.simple_tag
def get_file_node(request, file_name=""):
	file_list = []
	new_file_list = []

	a = str(file_name).split(',')

	for i in a:
		k = str(i.strip('   [](\'u\'   '))
		file_list.append(k)

	for each in file_list:
		if ObjectId.is_valid(each) is False:
			filedoc = node_collection.find({'_cls':'File','name':unicode(each)})

		else:
			filedoc = node_collection.find({'_cls':'File','_id':ObjectId(each)})

		if filedoc:
			for i in filedoc:
				new_file_list.append(i)

	return new_file_list

#@get_execution_time
@register.filter(name='jsonify')
def jsonify(value):
    """Parses python value into json-type (useful in converting
    python list/dict into javascript/json object).
    """
    print("type:",type(value))
    if isinstance(value,AttrDict):
    	value = value.to_dict()
    elif isinstance(value,AttrList):
    	value = list(value)
    return json.dumps(value, cls=NodeJSONEncoder)

#@get_execution_time
@register.simple_tag
def get_university(college_name):
    """
    Returns university name to which given college is affiliated to.
    """
    try:
        college = node_collection.find_one({
            '_cls': "GSystemType", 'name': u"College"
        })

        sel_college = node_collection.find_one({
            'member_of': college._id, 'name': unicode(college_name)
        })

        university_name = None
        if sel_college:
            university = node_collection.find_one({
                '_cls': "GSystemType", 'name': u"University"
            })
            sel_university = node_collection.find_one({
                'member_of': university._id,
                'relation_set.affiliated_college': sel_college._id
            })
            university_name = sel_university.name

        return university_name
    except Exception as e:
        error_message = "UniversityFindError: " + str(e) + " !!!"
        raise Exception(error_message)

#@get_execution_time
@register.simple_tag
def get_features_with_special_rights(group_id_or_name, user):
    """Returns list of features with special rights.

    If group is MIS_admin and user belongs to gstaff, then only give
    creation rights to list of feature(s) within MIS GApp shown as following:
      1. StudentCourseEnrollment

    For feature(s) included in list, don't provide creation rights.

    Arguments:
    group_id_or_name -- Name/ObjectId of the group
    user -- Logged-in user object (django-specific)

    Returns:
    List having names of feature(s) included in MIS GApp
    """
    # List of feature(s) for which creation rights should not be given
    features_with_special_rights = ["StudentCourseEnrollment"]

    mis_admin = node_collection.find_one({
        "_cls": "Group", "name": "MIS_admin"
    })

    if (group_id_or_name == mis_admin.name or
            group_id_or_name == str(mis_admin._id)):
        if mis_admin.is_gstaff(user):
            features_with_special_rights = []

    return features_with_special_rights

#@get_execution_time
@register.simple_tag
def get_filters_data(gst_name, group_name_or_id='home'):
	'''
	Returns the static data needed by filters. The data to be return will in following format:
	{
		"key_name": { "data_type": "<int>/<string>/<...>", "type": "attribute/field", "value": ["val1", "val2"]},
		... ,
		... ,
		"key_name": { "data_type": "<int>/<string>/<...>", "type": "attribute/field", "value": ["val1", "val2"]}
	}
	'''

	group_id, group_name = get_group_name_id(group_name_or_id)

	static_mapping = {
                    "educationalsubject": GSTUDIO_RESOURCES_EDUCATIONAL_SUBJECT,
                    "language": GSTUDIO_RESOURCES_LANGUAGES,
                    "educationaluse": GSTUDIO_RESOURCES_EDUCATIONAL_USE,
                    "interactivitytype": GSTUDIO_RESOURCES_INTERACTIVITY_TYPE,
                    # "educationalalignment": GSTUDIO_RESOURCES_EDUCATIONAL_ALIGNMENT,
                    "educationallevel": GSTUDIO_RESOURCES_EDUCATIONAL_LEVEL,
                    # "curricular": GSTUDIO_RESOURCES_CURRICULAR,
                    "audience": GSTUDIO_RESOURCES_AUDIENCE,
                    # "textcomplexity": GSTUDIO_RESOURCES_TEXT_COMPLEXITY
				}

	# following attr's values need to be get/not in settings:
	# timerequired, other_contributors, creator, age_range, readinglevel, adaptation_of, source, basedonurl

	filter_dict = {}

	# gst = node_collection.one({'_type':"GSystemType", "name": unicode(gst_name)})
	gst = node_collection.find_one({'_cls':"GSystemType", "name": unicode('File')})
	poss_attr = gst.get_possible_attributes(gst._id)
	# print gst_name, "============", gst.name

	filter_parameters = []
	# filter_parameters = GSTUDIO_FILTERS.get('File', [])
	filter_parameters = GSTUDIO_FILTERS.get(gst_name, [])[:]
	# print GSTUDIO_FILTERS
	# print filter_parameters

	exception_list = ["interactivitytype"]

	for k, v in poss_attr.iteritems():

		# if (k in exception_list) or not static_mapping.has_key(k):
		if (k in exception_list) or (k not in filter_parameters):
			continue

		# print k
		if static_mapping.has_key(k):
			fvalue = static_mapping.get(k, [])
		else:
			# print "================----"
			at_set_key = 'attribute_set.' + k
			group_obj = node_collection.find_one({"name":group_id,"_cls":"Group"})
			all_at_list = node_collection.find({at_set_key: {'$exists': True, '$nin': ['', 'None', []], },"group_set":ObjectId(group_obj._id) }).distinct(at_set_key)

			fvalue = all_at_list

		filter_dict[k] = {
	    					"data_type": v["data_type"].__name__,
	    					"altnames": v['altnames'],
	    					"type" : "attribute",
	    					"value": json.dumps(fvalue)
	    				}

		try:
			filter_parameters.pop(filter_parameters.index(k))
		except Exception as e:
			pass

		# print filter_parameters

	# additional filters:

	filter_dict["Language"] = {
								"data_type": "basestring", "type": "field",
								"value": json.dumps(static_mapping["language"])
							}


	try:
		filter_parameters.pop(filter_parameters.index('language'))
	except Exception as e:
		pass

	if filter_parameters:
		gst_structure = gst.structure
		gst_structure_keys = gst.structure.keys()

		for each_fpara in filter_parameters:
			if each_fpara in gst_structure_keys:
				fvalue = node_collection.find({'group_set': {'$in': [ObjectId(group_id)]}, 'member_of': {'$in': [gst._id]} }).distinct(each_fpara)

				if fvalue:
					filter_dict[each_fpara] = {
											'data_type': gst_structure[each_fpara],
											'type': 'field',
											'value': json.dumps(value)
										}

	# print "@@@ ", filter_dict
	return filter_dict


def sorted_ls(path):
    '''
    takes {
        path : Path to the folder location
    }
    returns {
        list of file-names sorted based on time
    }
    '''
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))


#@get_execution_time
@register.simple_tag
def get_sg_member_of(group_id):
	'''
	Returns list of names of "member_of" of sub-groups.
	- Takes group_id as compulsory and only argument.
	'''

	sg_member_of_list = []
	# get all underlying groups
	try:
		group_id = ObjectId(group_id)
	except:
		group_id, group_name = get_group_name_id(group_id)

	group_obj = node_collection.find_one({'_id': ObjectId(group_id)})
	# print group_obj.name
	# Fetch post_node of group
	if group_obj:
		if "post_node" in group_obj:
			post_node_id_list = group_obj.post_node
			if post_node_id_list:
				# getting parent's sub group's member_of in a list
				for each_sg in post_node_id_list:
					each_sg_node = node_collection.find_one({'_id': ObjectId(each_sg)})
					if each_sg_node:
						sg_member_of_list.extend(each_sg_node.member_of_names_list)
		# print "\n\n sg_member_of_list---",sg_member_of_list
	return sg_member_of_list


def get_objectid_name(nodeid):
	return (node_collection.find_one({'_id':ObjectId(nodeid)}).name)


@register.filter
def is_dict(val):
    return isinstance(val, dict)

@register.filter
def is_empty(val):
    if val == None :
    	return 1
    else :
    	return 0



#@get_execution_time
@register.simple_tag
def get_list_of_fields(oid_list, field_name='name'):
	if oid_list:
		cur = node_collection.find({'_id': {'$in': oid_list} }, {field_name: 1, '_id': 0})
		return [doc[field_name] for doc in cur]
	else:
		return []


#@get_execution_time
@register.simple_tag
def convert_list(value):
	#convert list of list to list
	return list(itertools.chain(*value))


#@get_execution_time
@register.simple_tag
def get_gstudio_help_sidebar():
	return GSTUDIO_HELP_SIDEBAR

#@get_execution_time
@register.simple_tag
def get_is_captcha_visible():
	return GSTUDIO_CAPTCHA_VISIBLE

#@get_execution_time
@register.simple_tag
def get_gstudio_twitter_via():
	return GSTUDIO_TWITTER_VIA

#@get_execution_time
@register.simple_tag
def get_gstudio_facebook_app_id():
	return GSTUDIO_FACEBOOK_APP_ID

#@get_execution_time
@register.simple_tag
def get_gstudio_social_share_resource():
	return GSTUDIO_SOCIAL_SHARE_RESOURCE


#@get_execution_time
@register.simple_tag
def get_ebook_help_text():
	return GSTUDIO_EBOOKS_HELP_TEXT

#@get_execution_time
@register.simple_tag
def get_gstudio_interaction_types():
	return GSTUDIO_INTERACTION_TYPES

#@get_execution_time
@register.simple_tag
def get_explore_url():
	return GSTUDIO_DEFAULT_EXPLORE_URL

#@get_execution_time
@register.simple_tag
def is_partner(group_obj):
	try:
		result = False
		partner_spaces = ["State Partners", "Individual Partners", "Institutional Partners"]
		if group_obj.name in partner_spaces:
			result = True
		return result
	except:
		return result


#@get_execution_time
@register.simple_tag
def get_download_filename(node, file_size_name='original'):

	extension = None
	if hasattr(node, 'if_file') and node.if_file[file_size_name].relurl:
		from django.template.defaultfilters import slugify
		relurl = node.if_file[file_size_name].relurl
		relurl_split_list = relurl.split('.')

		if len(relurl_split_list) > 1:
			extension = "." + relurl_split_list[-1]
		elif 'epub' in node.if_file.mime_type:
			extension = '.epub'
		elif not extension:
			file_hive_obj = filehive_collection.one({'_id':ObjectId(node.if_file.original.id)})
			file_blob = node.get_file(node.if_file.original.relurl)
			file_mime_type = file_hive_obj.get_file_mimetype(file_blob)
			extension = mimetypes.guess_extension(file_mime_type)
		else:
			extension = mimetypes.guess_extension(node.if_file.mime_type)
		name = node.altnames if node.altnames else node.name
		name = name.split('.')[0]
		file_name = slugify(name)
		if extension:
			file_name += extension
		return file_name
	else:
		name = node.altnames if node.altnames else node.name
		return name


#@get_execution_time
@register.simple_tag
def get_file_obj(node):
	obj = node_collection.find_one({"_id": ObjectId(node._id)})
	# print "\n\nobj",obj
	if obj.if_file.original.id:
		original_file_id = obj.if_file.original.id
		original_file_obj = filehive_collection.find_one({"_id": ObjectId(obj.if_file.original.id)})
		return original_file_obj

#@get_execution_time
@register.simple_tag
def get_help_pages_of_node(node_obj,rel_name="has_help",language="en"):
	all_help_page_node_list = []
	from gnowsys_ndf.ndf.views.translation import get_lang_node
	try:
                has_help_rt = node_collection.find_one({'_cls': 'RelationType', 'name': rel_name})
                help_rt = triple_collection.find({'subject':node_obj._id,'relation_type': has_help_rt._id, 'status': u'PUBLISHED'})
                if help_rt:
                        for each_help_rt in help_rt:
                                help_pg_node = node_collection.find_one({'_id':ObjectId(each_help_rt.right_subject)})
                                trans_node =   get_lang_node(help_pg_node._id,language)
                                help_pg_node =  trans_node or help_pg_node
                                if help_pg_node:
                                        all_help_page_node_list.append(help_pg_node)
                return all_help_page_node_list
	except:
		return all_help_page_node_list


#@get_execution_time
@register.simple_tag
def get_course_completetion_data(group_obj, user, ids_list=False):
    leaf_ids = completed_ids = incompleted_ids = total_count = completed_count = None
    result_status = course_complete_percentage = None
    return_dict = {}
    if user.is_authenticated:
        result_status = get_course_completetion_status(group_obj, user.id, True)
        # print "\n\n result_status --- ",result_status
        if result_status:
            if "completed_ids_list" in result_status:
                completed_ids_list = result_status['completed_ids_list']
            if "incompleted_ids_list" in result_status:
                incompleted_ids_list = result_status['incompleted_ids_list']
            if "list_of_leaf_node_ids" in result_status:
                list_of_leaf_node_ids = result_status['list_of_leaf_node_ids']

            return_dict = {"leaf_ids":list_of_leaf_node_ids,"completed_ids":completed_ids_list,"incompleted_ids":incompleted_ids_list}
        return return_dict

@register.simple_tag
def get_pages(page_type):
	'''
	returns the array of 'page_type' pages in the group 'help'
	ex. page_type='Info page' returns all Info pages in help group
	'''
	page_gst = node_collection.find_one({'_cls': "GSystemType", 'name': "Page"})
	help_page = node_collection.find_one({'_cls': "Group", 'name': "help"})
	page_type_gst = node_collection.find_one({'_cls': "GSystemType", 'name': page_type})
	page_nodes = node_collection.find({'member_of': page_gst._id, 'type_of': page_type_gst._id, 'group_set': help_page._id})
	return page_nodes

@register.simple_tag
def get_relation_node(node_id,rel_name):
	node = node_collection.find_one({'_id':ObjectId(node_id)})
	rt_subtitle = node_collection.find_one({'_cls':'RelationType', 'name':unicode(rel_name)})
	grel_nodes = triple_collection.find({'relation_type': rt_subtitle._id, 'subject': node._id},{'right_subject':1, 'relation_type_scope': 1, '_id': 0})
	data_list = []
	for each_grel in grel_nodes:
                data_dict = {}
                file_node = node_collection.find_one({'_id': ObjectId(each_grel['right_subject'])})
                data_dict.update({'file_path': file_node['if_file']['original']['relurl']})
                data_dict.update({'relation_type_scope': each_grel['relation_type_scope']})
                data_dict.update({'file_name': file_node.name})
                data_dict.update({'file_id': ObjectId(file_node.pk)})
                data_list.append(data_dict)
	# print data_list
	return data_list

@register.simple_tag
def get_lessons(unit_node):
	# return list of ObjectIds of all lessons
	# lesson_gst_name, lesson_gst_id = GSystemType.get_gst_name_id('lesson')
	# all_lessons_for_unit = node_collection.find({'member_of': lesson_gst_id,
	# 						'group_set': unit_node})
	lesson_nodes = node_collection.find({'_id': {'$in': unit_node.collection_set}})
	return lesson_nodes


@register.simple_tag
def get_gstudio_alt_file_formats(mime_type):
 	return GSTUDIO_ALTERNATE_FORMATS[mime_type]

@register.simple_tag
def get_gstudio_alt_size(mime_type):
 	return GSTUDIO_ALTERNATE_SIZE[mime_type]

@register.simple_tag
def get_gstudio_alt_opts():
 	return GSTUDIO_ALTERNATE_OPTS

@register.simple_tag
def get_test_page_oid():
 	return GSTUDIO_OID_HELP

@register.simple_tag
def get_gstudio_registration():
 	return GSTUDIO_REGISTRATION

@register.simple_tag
def get_unit_total_points(user_id,group_id):
	counter_obj = Counter.get_counter_obj(user_id, ObjectId(group_id))
	return counter_obj['group_points']

@register.simple_tag
def get_node_hierarchy(node_obj):
    node_structure = []
    for each in node_obj.collection_set:
        lesson_dict ={}
        lesson = Node.get_node_by_id(each)
        if lesson:
            lesson_dict['name'] = lesson.name
            lesson_dict['type'] = 'lesson'
            lesson_dict['id'] = str(lesson._id)
            lesson_dict['language'] = lesson.language[0]
            lesson_dict['activities'] = []
            if lesson.collection_set:
                for each_act in lesson.collection_set:
                    activity_dict ={}
                    activity = Node.get_node_by_id(each_act)
                    if activity:
                        activity_dict['name'] = activity.name
                        activity_dict['type'] = 'activity'
                        activity_dict['id'] = str(activity._id)
                        lesson_dict['activities'].append(activity_dict)
            node_structure.append(lesson_dict)

    return json.dumps(node_structure)

@register.simple_tag
def user_groups(is_super_user,user_id):
	user_grps_count = {}
	gst_base_unit_name, gst_base_unit_id = GSystemType.get_gst_name_id('base_unit')
	gst_group = node_collection.find_one({'_cls': "GSystemType", 'name': "Group"})
	gst_course = node_collection.find_one({'_cls': "GSystemType", 'name': "Course"})
	gst_basecoursegroup = node_collection.find_one({'_cls': "GSystemType", 'name': "BaseCourseGroup"})
	ce_gst = node_collection.find_one({'_cls': "GSystemType", 'name': "CourseEventGroup"})
	
	query = {'_cls': 'Group', 'status': u'PUBLISHED',
             'member_of': {'$in': [gst_group._id],
             '$nin': [gst_course._id, gst_basecoursegroup._id, ce_gst._id, gst_course._id, gst_base_unit_id]},
            }
	if is_super_user:
		query.update({'group_type': {'$in': [u'PUBLIC', u'PRIVATE']}})
	else:
		query.update({'name': {'$nin': GSTUDIO_DEFAULT_GROUPS_LIST},
                    'group_type': u'PUBLIC'})
	group_cur = node_collection.find(query).sort('last_update', -1)
	user_draft_nodes = node_collection.find({'_cls': "Group",'member_of':ObjectId(gst_base_unit_id),'$or': [{'group_admin': user_id}, {'author_set': user_id},{'created_by':user_id}]})
	# user_projects_nodes = node_collection.find({'_type': "Group",'$or': [{'group_admin': user_id}, {'author_set': user_id},{'created_by':user_id}]})
	user_grps_count['drafts'] = user_draft_nodes.count()
	user_grps_count['projects'] = group_cur.count()
	return user_grps_count
	return counter_obj['group_points']

@register.simple_tag
def if_edit_course_structure():
	return GSTUDIO_EDIT_LMS_COURSE_STRUCTURE

@register.simple_tag
def get_default_discussion_lbl():
	return DEFAULT_DISCUSSION_LABEL

@register.simple_tag
def get_gstudio_workspace_instance():
	return GSTUDIO_WORKSPACE_INSTANCE

@register.simple_tag
def get_topic_nodes(node_id):
	RT_teaches = node_collection.find_one({'_cls':'RelationType', 'name': 'teaches'})
	teaches_grelations = triple_collection.find_one({'_cls': 'GRelation', 'right_subject': ObjectId(node_id), 'relation_type': RT_teaches._id })
	teaches_grelations_id_list = []
	for each in teaches_grelations:
		teaches_grelations_id_list.append(each.subject)
	teaches_nodes = node_collection.find({"_id":{'$in' : teaches_grelations_id_list } })
	return teaches_nodes

@register.simple_tag
def get_selected_topics(node_id):
	rel_val = get_relation_value(ObjectId(node_id),'teaches')
	teaches_grelations_id_list = []
	for each in rel_val['grel_node']:
		teaches_grelations_id_list.append(str(each._id))
		# teaches_grelations_id_list = map(ObjectId,teaches_grelations_id_list)
	return teaches_grelations_id_list

@register.simple_tag
def rewind_cursor(cursor_obj):
	cursor_obj.rewind()
	return cursor_obj

@register.simple_tag
def get_node_by_member_of_name(group_id, member_of_name):
	member_of_gst_name, member_of_gst_id = GSystemType.get_gst_name_id(member_of_name)
	return list(node_collection.find({'group_set': group_id, 'member_of': member_of_gst_id}))

#@get_execution_time
@register.simple_tag
def cast_to_node(node_or_node_list):
	print("cast_to_node")
	print("\nInput type: ", type(node_or_node_list))
	node_or_node_list = list(iter(node_or_node_list))
	print("\nOutput type: ", type(node_or_node_list))
	if isinstance(node_or_node_list, list):
		if not isinstance(node_or_node_list[0],dict):
			node_or_node_list = [each.to_dict() for each in node_or_node_list]
			return node_or_node_list
		else:
			return map(Node,node_or_node_list)
		# print "node",type(node_or_node_list[0]),node_or_node_list[0]
		# nd = map(Node,node_or_node_list)
		# print "Ddone with casting:",nd[0]
	else:
		return Node(node_or_node_list)

@register.simple_tag
def get_trans_node(node_id,lang):
    rel_value = get_relation_value(ObjectId(node_id),"translation_of")
    for each in rel_value['grel_node']:
        if each.language[0] ==  get_language_tuple(lang)[0]:
            trans_node = each
            print("\n\ntrans_node", trans_node)
            return trans_node

@register.simple_tag
def get_module_enrollment_status(request, module_obj):
    def _user_enrolled(userid,unit_ids_list):
        user_data_dict = {userid: None}
        enrolled_flag = True
        for unit_id in unit_ids_list:
            unit_obj = node_collection.find_one({'_id': ObjectId(unit_id), '_cls': 'Group'})
            if unit_obj:
	            if userid not in unit_obj.author_set:
	                enrolled_flag = False
        user_data_dict[userid] = enrolled_flag
        return user_data_dict
    data_dict = {}
    buddies_ids = request.session.get('buddies_userid_list', [])
    # print "\nbuddies_ids: ", buddies_ids

    buddies_ids.append(request.user.pk)
    if buddies_ids:
        for  userid in buddies_ids:
            data_dict.update(_user_enrolled(userid, module_obj.collection_set))
            # data_dict.update({userid : all(userid in groupobj.author_set for ind, groupobj in module_obj.collection_dict.items())})
            data_dict.update({'full_enrolled': all(data_dict.values())})
        print("\n data: ", data_dict)
        return data_dict
    return _user_enrolled(request.user.pk, module_obj.collection_set)
    # return {request.user.pk : user_enrolled, 'full_enrolled': user_enrolled}

#@get_execution_time
@register.filter
def get_unicode_lang(lang_code):
    try:
        return get_language_tuple(lang_code)[1]
    except Exception as e:
        return lang_code
        pass

#@get_execution_time
@register.filter
def get_header_lang(lang):
    for each_lang in HEADER_LANGUAGES:
        if lang in each_lang:
            return each_lang[1]
    return lang


#@get_execution_time
@register.simple_tag
def get_profile_full_name(user_obj):
	if isinstance(user_obj, basestring):
		if user_obj.isdigit():
			user_obj = int(user_obj)
		else:
			user_obj = User.objects.get(username=user_obj)
	if isinstance(user_obj, int):
		user_obj = User.objects.get(pk=user_obj)
	auth_obj = Author.get_author_by_userid(user_obj.pk)
	list_of_attr = ['first_name', 'last_name']
	auth_attr = auth_obj.get_attributes_from_names_list(list_of_attr)
	if auth_attr.values():
		full_name = ' '.join("%s" % val for (key,val) in auth_attr.iteritems())
		full_name += " (Username: " + user_obj.username + ", ID: " + str(user_obj.pk) + ")"
	else:
		full_name = "Username: " + user_obj.username  + ", ID: " + str(user_obj.pk)
	return full_name

#@get_execution_time
@register.simple_tag
def get_implicit_enrollment_flag():
	return GSTUDIO_IMPLICIT_ENROLL

#@get_execution_time
@register.simple_tag
def get_name_by_node_id(node_id):
    if isinstance(node_id, list) and len(node_id):
        node_id = node_id[-1]
    node = Node.get_node_by_id(node_id)
    if node:
        return node.name
    else:
        return None

#@get_execution_time
@register.simple_tag
def get_institute_name():
	return GSTUDIO_INSTITUTE_NAME
