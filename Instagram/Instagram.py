__author__ = 'root'
from SignatureUtils import SignatureUtils,md5
import os
from http.HttpInterface import HttpInterface
import json
import requests
import Constants
import datetime

class Instagram:

    username=None#            # Instagram username
    password=None#            # Instagram password
    debug=None#               # Debug

    uuid=None#                # UUID
    device_id=None#           # Device ID
    username_id=None#         # Username ID
    token=None#               # _csrftoken
    isLoggedIn = False#  # Session status
    rank_token=None#          # Rank token
    IGDataPath=None#          # Data storage path
    http=None#
    settings=None#
    proxy = None#        # Proxy
    proxy_auth = None#   # Proxy Auth

    #
    # Default class constructor.
    #
    # @param string username
    #   Your Instagram username.
    # @param string password
    #   Your Instagram password.
    # @param debug
    #   Debug on or off, False by default.
    # @param IGDataPath
    #  Default folder to store data, you can change it.
    #

    def __init__(self,username, password, debug = False, IGDataPath = None):

        self.debug = debug#
        self.device_id = SignatureUtils.generateDeviceId(md5(username+password))

        if IGDataPath:
            self.IGDataPath = IGDataPath#
        else :
            self.IGDataPath = __file__+os.path.sep+'data'.os.path.sep+username+os.path.sep#
            if not os.path.exists(self.IGDataPath) :
                os.mkdir(self.IGDataPath)



        self.checkSettings(username)#

        self.http = HttpInterface(self)#

        self.setUser(username, password)#


        #
        # Set the user. Manage multiple accounts.
        #
        # @param string username
        #   Your Instagram username.
        # @param string password
        #   Your Instagram password.
        #
    def setUser(self,username, password):

        self.username = username#
        self.password = password#

        self.checkSettings(username)#

        self.uuid = SignatureUtils.generateUUID(True)#

        if ((os.path.exists(self.IGDataPath+self.username+"-cookies.dat")) and (self.settings.get('username_id') != None)
        and (self.settings.get('token') != None)):
            self.isLoggedIn = True#
            self.username_id = self.settings.get('username_id')#
            self.rank_token = self.username_id+'_'+self.uuid#
            self.token = self.settings.get('token')#
        else :
            self.isLoggedIn = False#



    def checkSettings(self,username):

        self.IGDataPath = __file__+os.path.sep+'data'+os.path.sep+username+os.path.sep#
        if not os.path.exists(self.IGDataPath):
            os.mkdir(self.IGDataPath)


        self.settings = Settings(self.IGDataPath+'settings-'+username+'.dat')#

        if (self.settings.get('version') == None):
            self.settings.set('version', Constants.VERSION)#


        if ((self.settings.get('user_agent') == None) or (int(self.settings.get('version')) < int(Constants.VERSION))):
            userAgent = UserAgent(self)#
            ua = userAgent.buildUserAgent()#
            self.settings.set('version', Constants.VERSION)#
            self.settings.set('user_agent', ua)#



    #
    # Set the proxy.
    #
    # @param string proxy
    #                         Full proxy string. Ex: user:pass@192.168.0.0:8080
    #                         Use proxy = "" to clear proxy
    # @param int    port
    #                         Port of proxy
    # @param string username
    #                         Username for proxy
    # @param string password
    #                         Password for proxy
    #
    # @throws InstagramException
    #/
    def setProxy(self,proxy, port = None, username = None, password = None):

        if (proxy == ''):
            self.proxy = ''#

            return#

        if username and password:
            user = username+':'+password+'@'
        else:
            user=''
        self.proxy = {'http': 'http://'+user+proxy+':'+str(port),
                      'https': 'http://'+user+proxy+':'+str(port)
                      }



#
# Login to Instagram.
#
# @param bool force
#   Force login to Instagram, self will create a new session
#
# @return array
#    Login data
#/
    def login(self,force = False):

        if not self.isLoggedIn or force:
            fetch = self.http.request('si/fetch_headers/?challenge_type=signup&guid='+SignatureUtils.generateUUID(False), None, True)#

            if  not fetch[0] or fetch[1]['status'] == 'fail':
                Exception("Couldn't get challenge, check your connection")#

                return

            import re
            token = re.search('#Set-Cookie: csrftoken=({^#]+)#', fetch[0],re.IGNORECASE)#
            if not token:
                print 'no token'
            data = {
                'phone_id': SignatureUtils.generateUUID(True),
                '_csrftoken': token.group(0),
                'username': self.username,
                'guid': self.uuid,
                'device_id': self.device_id,
                'password': self.password,
                'login_attempt_count': '0',
            }

            login = self.http.request('accounts/login/', SignatureUtils.generateSignature(json.dumps(data)), True)#
            response = LoginResponse(login[1])#

            if not response.isOk() :
                Exception(response.getMessage())#

                return response#


            self.isLoggedIn = True#
            self.username_id = response.getUsernameId()#
            self.settings.set('username_id', self.username_id)#
            self.rank_token = self.username_id+'_'+self.uuid#
            match = re.search('#Set-Cookie: csrftoken=({^#]+)#', login[0], re.IGNORECASE)#
            self.token = match.group(0)#
            self.settings.set('token', self.token)#

            self.syncFeatures()#
            self.autoCompleteUserList()#
            self.timelineFeed()#
            self.getv2Inbox()#
            self.getRecentActivity()#

            return response#


        check = self.timelineFeed()#
        if check['message'] and check['message'] == 'login_required':
            self.login(True)#

        self.getv2Inbox()#
        self.getRecentActivity()#


    def syncFeatures(self):

        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            'id': self.username_id,
            '_csrftoken': self.token,
            'experiments': Constants.EXPERIMENTS,
        })  #

        return self.http.request('qe/sync/', SignatureUtils.generateSignature(data))[1]#


    def autoCompleteUserList(self):

        return self.http.request('friendships/autocomplete_user_list/')[1]#


    def timelineFeed(self):

        return self.http.request('feed/timeline/')[1]#


    def megaphoneLog(self):
        return self.http.request('megaphone/log/')[1]#


    #
    # Pending Inbox.
    #
    # @return array
    #               Pending Inbox Data
    #/
    def getPendingInbox(self):

        pendingInbox = self.request('direct_v2/pending_inbox/?')[1]

        if (pendingInbox['status'] != 'ok') :
            Exception(pendingInbox['message'])#
            return
        return pendingInbox#


#
# Explore Tab.
#
# @return array
#               Explore data
#/
    def explore(self):

        return self.request('discover/explore/?')[1]#


    def expose(self):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            'id': self.username_id,
            '_csrftoken': self.token,
            'experiment': 'ig_android_profile_contextual_feed',
        })  #

        return self.http.request('qe/expose/', SignatureUtils.generateSignature(data))[1]  #


#
# Logout of Instagram.
#
# @return bool
#    Returns true if logged out correctly
#/
    def logout(self):

        logout = self.http.request('accounts/logout/')#

        if (logout == 'ok'):
            return True#
        else :
            return False#



#
# Upload photo to Instagram.
#
# @param string photo
#                        Path to your photo
# @param string caption
#                        Caption to be included in your photo.
#
# @return array
#               Upload data
#/
    def uploadPhoto(self,photo, caption = None, upload_id = None):

        return self.http.uploadPhoto(photo, caption, upload_id)#


    #
    # Upload video to Instagram.
    #
    # @param string video
    #                        Path to your video
    # @param string caption
    #                        Caption to be included in your video.
    #
    # @return array
    #               Upload data
    #/
    def uploadVideo(self,video, caption = None):

        return self.http.uploadVideo(video, caption)#


    def direct_share(self,media_id, recipients, text = None):

           return self.http.direct_share(media_id, recipients, text)#


    #
    # Direct Thread Data.
    #
    # @param string threadId
    #                         Thread Id
    #
    # @return array
    #               Direct Thread Data
    #/
    def directThread(self,threadId):

        directThread = self.request("direct_v2/threads/"+threadId+"/?")[1]#

        if (directThread['status'] != 'ok'):
            Exception(directThread['message'])#

            return#


        return directThread#


#
# Direct Thread Action.
#
# @param string threadId
#                             Thread Id
# @param string threadAction
#                             Thread Action 'approve' OR 'decline' OR 'block'
#
# @return array
#               Direct Thread Action Data
#/
    def directThreadAction(self,threadId, threadAction):

        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
        })  #

        return self.request("direct_v2/threads/"+threadId+"/"+threadAction+"/", self.generateSignature(data))[1]#


    def configureVideo(self,upload_id, video, caption = ''):

        self.uploadPhoto(video, caption, upload_id)#

        size = getimagesize(video)[0]#

        post = json.dumps({
            'upload_id': upload_id,
            'source_type': '3',
            'poster_frame_index': 0,
            'length': 0.00,
            'audio_muted': False,
            'filter_type': '0',
            'video_result': 'deprecated',
            'clips': {
                'length': Utils.getSeconds(video),
                        'source_type': '3',
                        'camera_position': 'back',
                    },
                'extra': {
            '               source_width': 960,
                            'source_height': 1280,
                            },
                'device': {
            '           manufacturer': self.settings.get('manufacturer'),
                        'model': self.settings.get('model'),
                        'android_version': Constants.ANDROID_VERSION,
                        'android_release': Constants.ANDROID_RELEASE,
                            },
                '_csrftoken': self.token,
                      '_uuid': self.uuid,
                      '_uid': self.username_id,
                        'caption': caption,
                    })  #

        post =  post.replace('"length":0', '"length":0.00',)#

        return  ConfigureVideoResponse(self.http.request('media/configure/?video=1', SignatureUtils.generateSignature(post))[1])#


    def configure(self,upload_id, photo, caption = ''):

        size = getimagesize(photo)[0]#

        post = json.dumps({
            'upload_id': upload_id,
            'camera_model': self.settings.get('model').replace(' ', '', ),
            'source_type': 3,
            'date_time_original': datetime.date('Y:m:d H:i:s'),
            'camera_make': self.settings.get('manufacturer'),
            'edits': {
                'crop_original_size': [size, size],
                                    'crop_zoom': 1.3333334,
                                        'crop_center': [0.0, -0.0],
                    },
            'extra': {
            'source_width': size,
                            'source_height': size,
                        },
                'device': {
                            'manufacturer': self.settings.get('manufacturer'),
                            'model': self.settings.get('model'),
                            'android_version': Constants.ANDROID_VERSION,
                            'android_release': Constants.ANDROID_RELEASE,
                        },
                '_csrftoken': self.token,
                '_uuid': self.uuid,
                '_uid': self.username_id,
                'caption': caption,
                })  #

        post = post.replace('"crop_center":[0,0]', '"crop_center":[0.0,-0.0]')  #

        return ConfigureResponse(self.http.request('media/configure/', SignatureUtils.generateSignature(post))[1])#


#
# Edit media.
#
# @param string mediaId
#   Media id
# @param string captionText
#   Caption text
#
# @return array
#   edit media data
#/
    def editMedia(self,mediaId, captionText = ''):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
            'caption_text': captionText,
        })

        return self.http.request("media/"+mediaId+"/edit_media/", SignatureUtils.generateSignature(data))[1]#


#
# Remove yourself from a tagged media.
#
# @param string mediaId
#   Media id
#
# @return array
#   edit media data
#/
    def removeSelftag(self,mediaId):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
        })  #

        return self.http.request("usertags/"+mediaId+"/remove/", SignatureUtils.generateSignature(data))[1]#


#
# Media info.
#
# @param string mediaId
#   Media id
#
# @return array
#   delete request data
#/
    def mediaInfo(self,mediaId):

        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
            'media_id': mediaId,
        })  #

        return  MediaInfoResponse(self.http.request("media/"+mediaId+"/info/", SignatureUtils.generateSignature(data))[1])#


#
# Delete photo or video.
#
# @param string mediaId
#   Media id
#
# @return array
#   delete request data
#/
    def deleteMedia(self,mediaId):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
            'media_id': mediaId,
        })  #
        return self.http.request("media/"+mediaId+"/delete/", SignatureUtils.generateSignature(data))[1]#


#
# Comment media.
#
# @param string mediaId
#   Media id
# @param string commentText
#   Comment Text
#
# @return array
#   comment media data
#/
    def comment(self,mediaId, commentText):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
            'comment_text': commentText,
        })  #
        return self.http.request("media/"+mediaId+"/comment/", SignatureUtils.generateSignature(data))[1]#


#
# Delete Comment.
#
# @param string mediaId
#   Media ID
# @param string commentId
#   Comment ID
#
# @return array
#   Delete comment data
#/
    def deleteComment(self,mediaId, captionText, commentId):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
            'caption_text': captionText,
        })  #

        return self.http.request("media/"+mediaId+"/comment/"+commentId+"/delete/", SignatureUtils.generateSignature(data))[1]#


#
# Delete Comment Bulk.
#
# @param string mediaId
#   Media id
# @param string commentIds
#   List of comments to delete
#
# @return array
#   Delete Comment Bulk Data
#/
    def deleteCommentsBulk(self,mediaId, commentIds):

        if type(commentIds)!='list':
            commentIds = [commentIds]#


        string = []#
        for com in  commentIds:
            string.append(str (com))#


        comment_ids_to_delete = ','.join(string)#

        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
            'comment_ids_to_delete': comment_ids_to_delete,
        })  #

        return self.http.request("media/"+mediaId+"/comment/bulk_delete/", SignatureUtils.generateSignature(data))[1]#


#
# Sets account to .
#
# @param string photo
#   Path to photo
#/
    def changeProfilePicture(self,photo):
        self.http.changeProfilePicture(photo)#


#
# Remove profile picture.
#
# @return array
#   status request data
#/
    def removeProfilePicture(self):

        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
        })  #

        return self.http.request('accounts/remove_profile_picture/', SignatureUtils.generateSignature(data))[1]#


#
# Sets account to private.
#
# @return array
#   status request data
#/
    def setPrivateAccount(self):

        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
        })  #

        return self.http.request('accounts/set_private/', SignatureUtils.generateSignature(data))[1]#


#
# Sets account to .
#
# @return array
#   status request data
#/
    def setAccount(self):

        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
        })  #

        return self.http.request('accounts/set_/', SignatureUtils.generateSignature(data))[1]#


#
# Get personal profile data.
#
# @return array
#   profile data
#/
    def getProfileData(self):

        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
        })  #

        return self.http.request('accounts/current_user/?edit=true', SignatureUtils.generateSignature(data))[1]#


#
# Edit profile.
#
# @param string url
#   Url - website. "" for nothing
# @param string phone
#   Phone number. "" for nothing
# @param string first_name
#   Name. "" for nothing
# @param string email
#   Email. Required.
# @param int gender
#   Gender. male = 1 , female = 0
#
# @return array
#   edit profile data
#/
    def editProfile(self,url, phone, first_name, biography, email, gender):

        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
            'external_url': url,
            'phone_number': phone,
            'username': self.username,
            'full_name': first_name,
            'biography': biography,
            'email': email,
            'gender': gender,
        })  #

        return self.http.request('accounts/edit_profile/', SignatureUtils.generateSignature(data))[1]#


#
# Change Password.
#
# @param string oldPassword
#   Old Password
# @param string newPassword
#   New Password
#
# @return array
#   Change Password Data
#/
    def changePassword(self,oldPassword, newPassword):

        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
            '_csrftoken': self.token,
            'old_password': oldPassword,
            'new_password1': newPassword,
            'new_password2': newPassword,
        })  #

        return self.http.request('accounts/change_password/', SignatureUtils.generateSignature(data))[1]#


#
# Get username info.
#
# @param string usernameId
#   Username id
#
# @return array
#   Username data
#/
    def getUsernameInfo(self,usernameId):
        return self.http.request("users/"+usernameId+"/info/")[1]#


#
# Get self username info.
#
# @return array
#   Username data
#/
    def getSelfUsernameInfo(self):

        return self.getUsernameInfo(self.username_id)#


#
# Get recent activity.
#
# @return array
#   Recent activity data
#/
    def getRecentActivity(self):

        activity = self.http.request('news/inbox/?')[1]#

        if (activity['status'] != 'ok'):
            Exception(activity['message'])#

            return#


        return activity#


#
# Get recent activity from accounts followed.
#
# @return array
#   Recent activity data of follows
#/
    def getFollowingRecentActivity(self):

        activity = self.http.request('news/?')[1]#

        if (activity['status'] != 'ok') :
            Exception(activity['message'])#

            return#


        return activity#


#
# I dont know self yet.
#
# @return array
#   v2 inbox data
#/
    def getv2Inbox(self):

        inbox = self.http.request('direct_v2/inbox/?')[1]#

        if (inbox['status'] != 'ok'):
            Exception(inbox['message'])#

            return#


        return inbox#


#
# Get user tags.
#
# @param string usernameId
#
# @return array
#   user tags data
#/
    def getUserTags(self,usernameId):

        tags = self.http.request("usertags/"+usernameId+"/feed/?rank_token="+self.rank_token+"&ranked_content=true&")[1]#

        if (tags['status'] != 'ok') :
            Exception(tags['message'])#

            return#


        return tags#


#
# Get self user tags.
#
# @return array
#   self user tags data
#/
    def getSelfUserTags(self):

        return self.getUserTags(self.username_id)#


#
# Get tagged media.
#
# @param string tag
#
# @return array
#/
    def tagFeed(self,tag):

        userFeed = self.http.request("feed/tag/"+tag+"/?rank_token="+self.rank_token+"&ranked_content=true&")[1]#

        if (userFeed['status'] != 'ok') :
            Exception(userFeed['message'])#

            return#


        return userFeed#


#
# Get media likers.
#
# @param string mediaId
#
# @return array
#/
    def getMediaLikers(self,mediaId):

        likers = self.http.request("media/"+mediaId+"/likers/?")[1]#
        if (likers['status'] != 'ok') :
            Exception(likers['message']+"\n")#

            return#


        return likers#


#
# Get user locations media.
#
# @param string usernameId
#   Username id
#
# @return array
#   Geo Media data
#/
    def getGeoMedia(self,usernameId):

        locations = self.http.request("maps/user/"+usernameId)[1]#

        if (locations['status'] != 'ok') :
            Exception(locations['message'])#

            return#


        return locations#


#
# Get self user locations media.
#
# @return array
#   Geo Media data
#/
    def getSelfGeoMedia(self):

        return self.getGeoMedia(self.username_id)#


#
# facebook user search.
#
# @param string query
#
# @return array
#   query data
#/
    def fbUserSearch(self,query):

        #query = rawurlencode(query)#
        query = self.http.request("fbsearch/topsearch/?context=blended&query="+query+"&rank_token="+self.rank_token)[1]#

        if (query['status'] != 'ok'):
            Exception(query['message'])#

            return


        return query#


#
# Search users.
#
# @param string query
#
# @return array
#   query data
#/
    def searchUsers(self,query):

        query = self.http.request('users/search/?ig_sig_key_version='+Constants.SIG_KEY_VERSION+
        "&is_typeahead=true&query="+query+"&rank_token="+self.rank_token)[1]#

        if (query['status'] != 'ok'):
            Exception(query['message']+"\n")#

            return


        return query#


#
# Search exact username.
#
# @param string usernameName username as STRING not an id
#
# @return array
#   query data
#/
    def searchUsername(self,usernameName):

        query = self.http.request("users/"+usernameName+"/usernameinfo/")[1]#

        if (query['status'] != 'ok') :
            Exception(query['message'])#
            return


        return query#


#
# Search users using addres book.
#
# @param array contacts
#
# @return array
#   query data
#/
    def syncFromAdressBook(self,contacts):

        data = 'contacts='+json.dumps(contacts, True)#

        return self.http.request('address_book/link/?include=extra_display_name,thumbnails', data)[1]#


#
# Search tags.
#
# @param string query
#
# @return array
#   query data
#/
    def searchTags(self,query):
        query = self.http.request("tags/search/?is_typeahead=true&q="+query+"&rank_token="+self.rank_token)[1]#
        if (query['status'] != 'ok'):
            Exception(query['message'])#

            return#


        return query#


#
# Get timeline data.
#
# @return array
#   timeline data
#/
    def getTimeline(self,maxid = None):
        mx = '&max_id=' + maxid if maxid else ''
        timeline = self.http.request("feed/timeline/?rank_token="+self.rank_token+"&ranked_content=true"+mx)[1]#
        if (timeline['status'] != 'ok'):
            Exception(timeline['message']+"\n")#
            return#
        return timeline#


#
# Get user feed.
#
# @param string usernameId
#    Username id
# @param None maxid
#    Max Id
# @param None minTimestamp
#    Min timestamp
#
# @throws InstagramException
#
# @return array User feed data
#    User feed data
#/
    def getUserFeed(self,usernameId, maxid = None, minTimestamp = None):
        mx= '&max_id='+maxid if maxid else ''
        mt =  '&min_timestamp='+minTimestamp if minTimestamp else ''
        userFeed = self.http.request("feed/user/usernameId/?rank_token="+self.rank_token+mx+mt+'&ranked_content=true')[1]#

        if (userFeed['status'] != 'ok'):
            Exception(userFeed['message'])
            return#
        return userFeed#


#
# Get hashtag feed.
#
# @param string hashtagString
#    Hashtag string, not including the #
#
# @return array
#   Hashtag feed data
#/
    def getHashtagFeed(self,hashtagString, maxid = None):

        if not maxid:
            endpoint = "feed/tag/"+hashtagString+"/?rank_token="+self.rank_token+"&ranked_content=true&"#
        else:
            endpoint = "feed/tag/"+hashtagString+"/?max_id="+maxid+"&rank_token="+self.rank_token+"&ranked_content=true&"


        hashtagFeed = self.http.request(endpoint)[1]#

        if (hashtagFeed['status'] != 'ok'):
            Exception(hashtagFeed['message'])#

            return


        return hashtagFeed#


#
# Get locations.
#
# @param string query
#    search query
#
# @return array
#   Location location data
#/
    def searchLocation(self,query):


        endpoint = "fbsearch/places/?rank_token="+self.rank_token+"&query="+query#

        locationFeed = self.http.request(endpoint)[1]#

        if (locationFeed['status'] != 'ok'):
            Exception(locationFeed['message']+"\n")#

            return


        return locationFeed#


#
# Get location feed.
#
# @param string locationId
#    location id
#
# @return array
#   Location feed data
#/

    def getLocationFeed(self,locationId, maxid = None):

        if not maxid :
            endpoint = "feed/location/"+locationId+"/?rank_token="+self.rank_token+"&ranked_content=true&"#
        else:
            endpoint = "feed/location/"+locationId+"/?max_id="+maxid+"&rank_token="+self.rank_token+"&ranked_content=true&"#


        locationFeed = self.http.request(endpoint)[1]#

        if (locationFeed['status'] != 'ok'):
            Exception(locationFeed['message']+"\n")#
            return#


        return locationFeed#


#
# Get self user feed.
#
# @return array
#   User feed data
#/
    def getSelfUserFeed(self):

        return self.getUserFeed(self.username_id)#


#
# Get popular feed.
#
# @return array
#   popular feed data
#/
    def getPopularFeed(self):

        popularFeed = self.http.request("feed/popular/?people_teaser_supported=1&rank_token="+self.rank_token+"&ranked_content=true&")[1]#

        if (popularFeed['status'] != 'ok'):
            Exception(popularFeed['message'])#
            return#


        return popularFeed#


#
# Get user followings.
#
# @param string usernameId
#   Username id
#
# @return array
#   followers data
#/
    def getUserFollowings(self,usernameId, maxid = None):

        return self.http.request("friendships/"+usernameId+"/following/?max_id=maxid&ig_sig_key_version="+Constants.SIG_KEY_VERSION+"&rank_token="+self.rank_token)[1]#


    #
    # Get user followers.
    #
    # @param string usernameId
    #   Username id
    #
    # @return array
    #   followers data
    #/
    def getUserFollowers(self,usernameId, maxid = None):

        return self.http.request("friendships/"+usernameId+"/followers/?max_id=maxid&ig_sig_key_version="+Constants.SIG_KEY_VERSION+"&rank_token="+self.rank_token)[1]#


#
# Get self user followers.
#
# @return array
#   followers data
#/
    def getSelfUserFollowers(self):

        return self.getUserFollowers(self.username_id)#


#
# Get self users we are following.
#
# @return array
#   users we are following data
#/
    def getSelfUsersFollowing(self):

        return self.http.request('friendships/following/?ig_sig_key_version='+Constants.SIG_KEY_VERSION+"&rank_token="+self.rank_token)[1]#


#
# Like photo or video.
#
# @param string mediaId
#   Media id
#
# @return array
#   status request
#/
    def like(self,mediaId):

        data = json.dumps({
            '_uuid'      : self.uuid,
            '_uid'       : self.username_id,
            '_csrftoken' : self.token,
            'media_id'   : mediaId,
        })#

        return self.http.request("media/"+mediaId+"/like/", SignatureUtils.generateSignature(data))[1]#


#
# Unlike photo or video.
#
# @param string mediaId
#   Media id
#
# @return array
#   status request
#/
    def unlike(self,mediaId):

        data = json.dumps({
            '_uuid'      : self.uuid,
            '_uid'       : self.username_id,
            '_csrftoken' : self.token,
            'media_id'   : mediaId,
        })#

        return self.http.request("media/"+mediaId+"/unlike/", SignatureUtils.generateSignature(data))[1]#


#
# Get media comments.
#
# @param string mediaId
#   Media id
#
# @return array
#   Media comments data
#/
    def getMediaComments(self,mediaId):

        return self.http.request("media/"+mediaId+"/comments/?")[1]#


#
# Set name and phone (Optional).
#
# @param string name
# @param string phone
#
# @return array
#   Set status data
#/
    def setNameAndPhone(self,name = '', phone = ''):

        data = json.dumps({
            '_uuid'         : self.uuid,
            '_uid'          : self.username_id,
            'first_name'    : name,
            'phone_number'  : phone,
            '_csrftoken'    : self.token})

        return self.http.request('accounts/set_phone_and_name/', SignatureUtils.generateSignature(data))[1]#


#
# Get direct share.
#
# @return array
#   Direct share data
#/
    def getDirectShare(self):

        return self.http.request('direct_share/inbox/?')[1]#


#
# Backups all your uploaded photos :).
#/
    def backup(self):

        myUploads = self.getSelfUserFeed()#
        for item in myUploads['items']:
            if not os.path.isdir(self.IGDataPath+'backup/'+self.username+"-"+datetime.date('Y-m-d')):
                os.mkdir(self.IGDataPath+'backup/'+self.username+"-"+datetime.date('Y-m-d'))
            r=requests.get(item['image_versions2']['candidates'][0]['url'])
            with open(self.IGDataPath+'backup/'+self.username+"-"+datetime.date('Y-m-d')+'/'+item['id']+'.jpg','w' ) as e:
                e.write(r.content)



#
# Follow.
#
# @param string userId
#
# @return array
#   Friendship status data
#/
    def follow(self,userId):

        data = json.dumps({
            '_uuid'      : self.uuid,
            '_uid'       : self.username_id,
            'user_id'    : userId,
            '_csrftoken' : self.token,
            })

        return self.http.request("friendships/create/"+userId+"/", SignatureUtils.generateSignature(data))[1]#


#
# Unfollow.
#
# @param string userId
#
# @return array
#   Friendship status data
#
    def unfollow(self,userId):

        data = json.dumps({
            '_uuid'      : self.uuid,
            '_uid'       : self.username_id,
            'user_id'    : userId,
            '_csrftoken' : self.token,
        })#

        return self.http.request("friendships/destroy/"+userId+"/", SignatureUtils.generateSignature(data))[1]#


    #
    # Block.
    #
    # @param string userId
    #
    # @return array
    #   Friendship status data
    #
    def block(self,userId):

        data = json.dumps({
            '_uuid'      : self.uuid,
            '_uid'       : self.username_id,
            'user_id'    : userId,
            '_csrftoken' : self.token,
        })

        return self.http.request("friendships/block/"+userId+"/", SignatureUtils.generateSignature(data))[1]#


    #
    # Unblock.
    #
    # @param string userId
    #
    # @return array
    #   Friendship status data
    #/
    def unblock(self,userId):

        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.username_id,
              
            'user_id': userId,
            '_csrftoken': self.token,
        })  #

        return self.http.request("friendships/unblock/"+userId+"/", SignatureUtils.generateSignature(data))[1]#


    #
    # Show User Friendship.
    #
    # @param string userId
    #
    # @return array
    #   Friendship relationship data
    #/
    def userFriendship(self,userId):

        data = json.dumps({
            '_uuid'      : self.uuid,
            '_uid'       : self.username_id,
            'user_id'    : userId,
            '_csrftoken' : self.token,
        })#

        return self.http.request("friendships/show/"+userId+"/", SignatureUtils.generateSignature(data))[1]#


    #
    # Get liked media.
    #
    # @return array
    # Liked media data

    def getLikedMedia(self,maxid = None):
        m= 'max_id='+maxid+'&'  if maxid else ''
        endpoint = 'feed/liked/?'+m
        return self.http.request(endpoint)[1]


