



class Item:

    PHOTO =1
    VIDEO=2

    taken_at=None
    pk=None
    id=None
    device_timestamp=None
    media_type=None
    code=None
    client_cache_key=None
    filter_type=None
    ###
     # @var Image_Versions2
     ##
    image_versions2=None
    original_width=None
    original_height=None
    view_count = 0
    organic_tracking_token=None
    has_more_comments=None
    max_num_visible_preview_comments=None
    preview_comments=None
    reel_mentions=None
    story_cta=None
    caption_position=None
    expiring_at=None
    is_reel_media=None
    next_max_id =None

    ###
     # @var Comment[]
     ##
    comments=None
    comment_count = 0
     # @var Caption|null
     ##
    caption = null=None
    caption_is_edited=None
    photo_of_you=None
    ###
     # @var VideoVersions[]|null
     ##
    video_versions=None
    has_audio = False
    video_duration = ''
    ###
     # @var User
     ##
    user=None
    ###
     # @var User[]
     ##
    likers = ''
    like_count = 0
    preview = ''
    has_liked = False
    explore_context = ''
    explore_source_token = ''
    ###
     # @var Explore|string
     ##
    explore = ''
    impression_token = ''
    ###
     # @var Usertag|null
     ##
    usertags = None
    media_or_ad=None
    ###
     # @var Media
     ##
    media=None
    stories=None
    top_likers=None

    def  setMediaOrAd(self,params):
    
        for k,v in params.iteritems():
            self.k = v


    def  getItemUrl(self):
    
        return 'https:##www.instagram.com#p#'+self.getCode()+'#'




class Image_Versions2:

    ###
     # @var HdProfilePicUrlInfo[]
     ##
    candidates=None

