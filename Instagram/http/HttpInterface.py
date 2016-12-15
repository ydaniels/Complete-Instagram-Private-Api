__author__ = 'root'
import requests

import time
import urllib
import pickle
import Instagram.Constants.Constants as Constants
import tempfile
import os
import uuid
import locale

locale.setlocale(locale.LC_NUMERIC, '')

def number_format(num, places=0):
    return locale.format("%.*f", (places, num), True)



def save_cookies(requests_cookiejar, filename):
    with open(filename, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

def load_cookies(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

class HttpInterface():
    parent = None
    userAgent = None
    proxy = None
    proxyPort = None
    proxyUser = None
    proxyPass = None
    verifyPeer = False;
    verifyHost = False;


    def  __init__(self,parent):
     
        self.parent = parent;
        self.userAgent = self.parent.settings.get('user_agent')
    
    def request(self,endpoint, post = None, login = False, flood_wait = False, assoc = True):

        if not self.parent.isLoggedIn and not login:
            Exception("Not logged in\n")
            return

        headers = {
        'Connection': 'close',
        'Accept': '*/*',
        'X-IG-Capabilities ': Constants.X_IG_Capabilities,
             'X-IG-Connection-Type': 'WIFI',
        'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',

        'Accept-Language':' en-US',

        }
        ch =requests.Session()
        ret =requests.Request()
        req = ch.prepare_request(ret)
        req.url= Constants.API_URL+endpoint
        headers['User-agent']=self.userAgent
        req.headers=headers
        if self.parent.settingsAdopter['type'] == 'file':
            cook = load_cookies(self.parent.settings.cookiesPath)
            req.cookies =  cook
        else :
            cookieJar = self.parent.settings.get('cookies');
            cookieJarFile =  os.tempnam(( tempfile.gettempdir(), uuid.uuid1()))
            save_cookies(cookieJar,cookieJarFile)
            req.cookies = cookieJar


        if (post):
            req.method='POST'
            req.data= post

        if (self.parent.proxy) :
            resp = ch.send(req,

            verify=self.verifyHost,
            proxies=self.parent.proxy,
            cert=False,

                          )
        else:
            resp = ch.send(req,
            verify=self.verifyHost,
            cert=False)


        if (self.parent.debug):
            print "REQUEST: endpoint"
            if post:

                   print 'DATA: '+urllib.urldecode(post)


            print "RESPONSE: body\n\n";

        return [resp.response.headers, resp.json()];

    def uploadPhoto(photo, caption = None, upload_id = None):

        endpoint = Constants.API_URL+'upload/photo/';
        boundary = self.parent.uuid;
        if upload_id:
            fileToUpload = Utils.createVideoIcon(photo);
        else:
            upload_id = number_format(time.time() * 1000, 0)
            with open(photo,'rb') as f:
               fileToUpload =f.read()

        bodies = {
            {
                'type' : 'form-data',
                'name' : 'upload_id',
                'data' : upload_id,
            },
            {
                'type' : 'form-data',
                'name' : '_uuid',
                'data' : self.parent.uuid,
            },
                {
                'type' : 'form-data',
                'name' : '_csrftoken',
                'data' : self.parent.token,
            },
            {
                'type' : 'form-data',
                'name' : 'image_compression',
              'data'   : '{"lib_name":"jt","lib_version":"1.3.0","quality":"70"}',
                },
        {
                'type'     : 'form-data',
                'name'     : 'photo',
                'data'     : fileToUpload,
                'filename' : 'pending_media_'+str(number_format(time.time() * 1000, 0))+'.jpg',
                'headers'  : {
          'Content-Transfer-Encoding: binary',
                    'Content-type: application/octet-stream',
                    },
        },
        }
        data = self.buildBody(bodies, boundary);
        headers = {
                'Connection':' close',
                'Accept':' */*',
                'Content-type': 'multipart/form-data; boundary='+boundary,
        'Content-Length': len(data),
        'Cookie2':' Version=1',
        'Accept-Language':' en-US',
        'Accept-Encoding':' gzip',
        };

        cook = load_cookies(self.parent.IGDataPath+self.parent.username+'-cookies.dat')
        #curl_setopt(ch, CURLOPT_COOKIEFILE, self.parent.IGDataPath+self.parent.username+'-cookies.dat');
        #curl_setopt(ch, CURLOPT_COOKIEJAR, self.parent.IGDataPath+self.parent.username+'-cookies.dat');
        req.cookies =  cook
        if (post):
            req.method='POST'
            req.data=data

        if (self.parent.proxy) :
            resp = s.send(req,

            verify=False,
            proxies=self.parent.proxy,
            cert=False,

                          )
        else:
            resp = s.send(req,
            verify=False,
            cert=False)

        upload = UploadPhotoResponse(resp.json(), True)

        if not upload.isOk():
            Exception(upload.getMessage())
            return

        if (self.parent.debug) :
            print 'RESPONSE: '+resp.json();

        configure = self.parent.configure(upload.getUploadId(), photo, caption);
        self.parent.expose();
        return configure;

    def uploadVideo(self,video, caption = None):

        with open(video,'rb') as b:
            videoData=b.read()
        endpoint = Constants.API_URL+'upload/video/'
        boundary = self.parent.uuid;
        upload_id = int(time.time()*1000)
        bodies = {
            {
              'type' : 'form-data',
              'name' : 'upload_id',
              'data' : upload_id,
            },
            {
              'type' : 'form-data',
              'name' : '_csrftoken',
              'data' : self.parent.token,
            },
            {
              'type'   : 'form-data',
              'name'   : 'media_type',
              'data'   : '2',
            },
            {
              'type' : 'form-data',
              'name' : '_uuid',
              'data' : self.parent.uuid,
            },
        };
        data = self.buildBody(bodies, boundary);
        headers = {
          'Connection': 'keep-alive',
          'Accept': '*/*',
          'Host': 'i.instagram.com',
          'Content-type': 'multipart/form-data; boundary='+boundary,
          'Accept-Language':' en-en',
        };
        cook = load_cookies(self.parent.IGDataPath+self.parent.username+'-cookies.dat')
        #curl_setopt(ch, CURLOPT_COOKIEFILE, self.parent.IGDataPath+self.parent.username+'-cookies.dat');
        #curl_setopt(ch, CURLOPT_COOKIEJAR, self.parent.IGDataPath+self.parent.username+'-cookies.dat');
        req.cookies =  cook
        if (post):
            req.method='POST'
            req.data=data

        if (self.parent.proxy) :
            resp = s.send(req,

            verify=False,
            proxies=self.parent.proxy,
            cert=False,

                          )
        else:
            resp = s.send(req,
            verify=False,
            cert=False)



        body = UploadJobVideoResponse(resp.json(), True)
        uploadUrl = body.getVideoUploadUrl();
        job = body.getVideoUploadJob();
        request_size = floor(len(videoData) / 4);
        lastRequestExtra = (len(videoData) - (request_size * 4));
        arra=[]
        cook = load_cookies(self.parent.IGDataPath+self.parent.username+'-cookies.dat')
        #curl_setopt(ch, CURLOPT_COOKIEFILE, self.parent.IGDataPath+self.parent.username+'-cookies.dat');
        #curl_setopt(ch, CURLOPT_COOKIEJAR, self.parent.IGDataPath+self.parent.username+'-cookies.dat');
        req.cookies =  cook
        for a in range(4) :
            start = (a * request_size);
            b=  lastRequestExtra if a == 3 else 0
            end = (a + 1) * request_size + b
            headers = {
              'Connection': 'keep-alive',
              'Accept':' */*',
              'Host': 'upload.instagram.com',
              'Cookie2': 'Version=1',
              'Accept-Encoding':' gzip, deflate',
              'Content-Type': 'application/octet-stream',
              'Session-ID':str(upload_id),
              'Accept-Language':' en-en',
              'Content-Disposition': 'attachment; filename="video.mov"',
              'Content-Length': str(int(end) - int(start)),
              'Content-Range': 'bytes '+str(start)+'-'+str((end - 1))+'/'+str(len(videoData)),
              'job': str(job),
            }


            req.method='POST'
            req.data=videoData[start:end]

            if (self.parent.proxy) :
                resp = s.send(req,

                verify=False,
                proxies=self.parent.proxy,
                cert=False,

                              )
            else:
                resp = s.send(req,
                verify=False,
                cert=False)
                result = curl_exec(ch);

                arra.append( resp.content)

        req.method='POST'


        if (self.parent.proxy) :
            resp = s.send(req,

            verify=False,
            proxies=self.parent.proxy,
            cert=False)
        else:
            resp = s.send(req,
            verify=False,
            cert=False)

        upload = UploadVideoResponse(resp.json(), true)

        if self.parent.debug:
            print 'RESPONSE: '+resp.json();

        configure = self.parent.configureVideo(upload_id, video, caption)
        self.parent.expose()
        return configure

    def changeProfilePicture(self,photo):

        if not photo:
            print  "Photo not valid\n\n";
            return;

        uData = json.loads({
        '_csrftoken' : self.parent.token,
        '_uuid'      : self.parent.uuid,
        '_uid'       : self.parent.username_id,
             });
        endpoint = Constants.API_URL+'accounts/change_profile_picture/';
        boundary = self.parent.uuid;
        with open(photo,'rb') as e:
              ph=  e.read()
        bodies = {
            {
          'type' : 'form-data',
          'name' : 'ig_sig_key_version',
          'data' : Constants.SIG_KEY_VERSION,
        },
            {
          'type' : 'form-data',
          'name' : 'signed_body',

          'data' :hmac.new( Constants.IG_SIG_KEY,uData,hashlib.sha256).digest()+uData,
            },
            {
          'type'     : 'form-data',
          'name'     : 'profile_pic',
          'data'     :ph ,
          'filename' : 'profile_pic',
          'headers'  : [
            'Content-type: application/octet-stream',
            'Content-Transfer-Encoding: binary',
            ],
            },
        };
        data = self.buildBody(bodies, boundary);
        headers = {
          'Proxy-Connection': 'keep-alive',
          'Connection': 'keep-alive',
          'Accept': '*/*',
          'Content-type': 'multipart/form-data; boundary='+boundary,
          'Accept-Language': 'en-en',
          'Accept-Encoding': 'gzip, deflate',
        };
        ch =requests.Session()
        ret =requests.Request()
        req = ch.prepare_request(ret)
        req.url= endpoint
        headers['User-agent']=self.userAgent
        req.headers=headers
        cook = load_cookies(self.parent.IGDataPath+self.parent.username+'-cookies.dat')
        #curl_setopt(ch, CURLOPT_COOKIEFILE, self.parent.IGDataPath+self.parent.username+'-cookies.dat');
        #curl_setopt(ch, CURLOPT_COOKIEJAR, self.parent.IGDataPath+self.parent.username+'-cookies.dat');
        req.cookies =  cook

        req.method='POST'
        req.data=post

        if (self.parent.proxy) :
            resp = s.send(req,

            verify=False,
            proxies=self.parent.proxy,
            cert=False,

                          )
        else:
            resp = s.send(req,
            verify=False,
            cert=False)


        if (self.parent.debug):
            print "REQUEST: endpoint"
            if post:

                   print 'DATA: '+urllib.urldecode(post)


            print "RESPONSE: body\n\n";


    def direct_share(self,media_id, recipients, text = None):

        if (type(recipients)!='list'):
            recipients = [recipients]

        string = [];
        for rec in recipients:
            string.appnd( "'"+rec+"'")

        recipient_users =','.join( string);
        endpoint = Constants.API_URL+'direct_v2/threads/broadcast/media_share/?media_type=photo';
        boundary = self.parent.uuid;
        bodies = {
            {
                'type' : 'form-data',
                'name' : 'media_id',
                'data' : media_id,
            },
            {
                'type' : 'form-data',
                'name' : 'recipient_users',
                'data' : "[["+recipient_users+"]]",
            },
            {
                'type' : 'form-data',
                'name' : 'client_context',
                'data' : self.parent.uuid,
            },
            {
                'type' : 'form-data',
                'name' : 'thread_ids',
                'data' : '["0"]',
            },
            {
                'type' : 'form-data',
                'name' : 'text',
                'data' :  '' if not text else text,
        },
        };
        data = self.buildBody(bodies, boundary);
        headers = {
                'Proxy-Connection': 'keep-alive',
                'Connection': 'keep-alive',
                'Accept': '*/*',
                'Content-type': 'multipart/form-data; boundary='+boundary,
                'Accept-Language':' en-en',
        };

    def  direct_message(self,recipients, text):

        if not isinstance(recipients,list) :
            recipients = [].append(recipients)

        string = [];
        for recipient in recipients:
            string.append( "\""+recipient+"\"")

        $recipient_users = implode(',', $string);
        $endpoint = 'direct_v2/threads/broadcast/text/';
        $boundary = $this->parent->uuid;
        $bodies = [
            [
                'type' => 'form-data',
                'name' => 'recipient_users',
                'data' => "[[$recipient_users]]",
            ],
            [
                'type' => 'form-data',
                'name' => 'client_context',
                'data' => $this->parent->uuid,
            ],
            [
                'type' => 'form-data',
                'name' => 'thread_ids',
                'data' => '["0"]',
            ],
            [
                'type' => 'form-data',
                'name' => 'text',
                'data' => is_null($text) ? '' : $text,
            ],
        ];
        $data = $this->buildBody($bodies, $boundary);
        $headers = [
            'Proxy-Connection: keep-alive',
            'Connection: keep-alive',
            'Accept: */*',
            'Content-Type: multipart/form-data; boundary='.$boundary,
            'Accept-Language: en-en',
        ];
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, Constants::API_URL.$endpoint);
        curl_setopt($ch, CURLOPT_USERAGENT, $this->userAgent);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($ch, CURLOPT_HEADER, true);
        curl_setopt($ch, CURLOPT_VERBOSE, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, $this->verifyPeer);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, $this->verifyHost);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        if ($this->parent->settingsAdopter['type'] == 'file') {
            curl_setopt($ch, CURLOPT_COOKIEFILE, $this->parent->settings->cookiesPath);
            curl_setopt($ch, CURLOPT_COOKIEJAR, $this->parent->settings->cookiesPath);
        } else {
            $cookieJar = $this->parent->settings->get('cookies');
            $cookieJarFile = tempnam(sys_get_temp_dir(), uniqid('_instagram_cookie'));
            file_put_contents($cookieJarFile, $cookieJar);
            curl_setopt($ch, CURLOPT_COOKIEJAR, $cookieJarFile);
            curl_setopt($ch, CURLOPT_COOKIEFILE, $cookieJarFile);
        }
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        if ($this->proxy) {
            curl_setopt($ch, CURLOPT_PROXY, $this->proxy['host'].':'.$this->proxy['port']);
            if ($this->proxy['username']) {
                curl_setopt($ch, CURLOPT_PROXYUSERPWD, $this->proxy['username'].':'.$this->proxy['password']);
            }
        }
        $resp = curl_exec($ch);
        $header_len = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
        $header = substr($resp, 0, $header_len);
        $upload = json_decode(substr($resp, $header_len), true);
        if ($this->parent->debug) {
            Debug::printRequest('POST', $endpoint);
            $uploadBytes = Utils::formatBytes(curl_getinfo($ch, CURLINFO_SIZE_UPLOAD));
            Debug::printUpload($uploadBytes);
            $bytes = Utils::formatBytes(curl_getinfo($ch, CURLINFO_SIZE_DOWNLOAD));
            $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            Debug::printHttpCode($httpCode, $bytes);
            Debug::printResponse(substr($resp, $header_len));
        }
        curl_close($ch);
        if ($this->parent->settingsAdopter['type'] == 'mysql') {
            $newCookies = file_get_contents($cookieJarFile);
            $this->parent->settings->set('cookies', $newCookies);
        }
    }

    def buildBody(self,bodies, boundary):

        body = '';
        for  b in bodies:
            body += '--'+boundary+"\r\n";
            body += 'Content-Disposition: '+b['type']+'; name="'+b['name']+'"';
            if b['filename']:
                filename, extn = os.path.splitext(b['filename'])
                body += '; filename="'+'pending_media_'+number_format(time.time() * 1000, 0)+'.'+extn+'"';

            if b['headers']:
                for header in b['headers'] :
                    body += "\r\n"+header;


            body += "\r\n\r\n"+b['data']+"\r\n";

        body += '--'+boundary+'--';
        return body;

    def verifyPeer(self,enable):

        self.verifyPeer = enable

    def verifyHost(self,enable):

        self.verifyHost = enable

