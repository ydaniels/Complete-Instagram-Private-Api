

class InstagramRegistration:

    debug=None
    IGDataPath=None
    username=None
    uuid=None
    waterfall_id=None
    token=None
    userAgent=None
    settings=None
    proxy =None   
    proxyHost = None# Proxy Host and Port
    proxyAuth = None; # Proxy User and Pass

    def __construct($debug = false, $IGDataPath = None)
    {
        $this->debug = $debug;
        $this->uuid = SignatureUtils::generateUUID(true);
        $this->waterfall_id = SignatureUtils::generateUUID(true);

        if (!is_None($IGDataPath)) {
            $this->IGDataPath = $IGDataPath;
        } else {
            $this->IGDataPath = __DIR__.DIRECTORY_SEPARATOR.'data'.DIRECTORY_SEPARATOR;
        }

        $this->userAgent = 'Instagram '.Constants::VERSION.' Android (18/4.3; 320dpi; 720x1280; Xiaomi; HM 1SW; armani; qcom; en_US)';
    }

    /**
     * Set the proxy.
     *
     * @param string $proxy    Full proxy string. Ex: user:pass@192.168.0.0:8080 Use $proxy = "" to clear proxy
     * @param int    $port     Port of proxy
     * @param string $username Username for proxy
     * @param string $password Password for proxy
     *
     * @throws InstagramException
     */
    def setProxy($proxy, $port = None, $username = None, $password = None)
    {
        $this->proxy = $proxy;

        if ($proxy == '') {
            return;
        }

        $proxy = parse_url($proxy);

        if (!is_None($port) && is_int($port)) {
            $proxy['port'] = $port;
        }

        if (!is_None($username) && !is_None($password)) {
            $proxy['user'] = $username;
            $proxy['pass'] = $password;
        }

        if (!empty($proxy['host']) && isset($proxy['port']) && is_int($proxy['port'])) {
            $this->proxyHost = $proxy['host'].':'.$proxy['port'];
        } else {
            throw new InstagramException('Proxy host error. Please check ip address and port of proxy.');
        }

        if (isset($proxy['user']) && isset($proxy['pass'])) {
            $this->proxyAuth = $proxy['user'].':'.$proxy['pass'];
        }
    }

    /**
     * Checks if the username is already taken (exists).
     *
     * @param string $username
     *
     * @return CheckUsernameResponse
     */
    def checkUsername($username)
    {
        $data = json_encode([
            '_uuid'      => $this->uuid,
            'username'   => $username,
            '_csrftoken' => 'missing',
        ]);

        $this->username = $username;
        $this->settings = new Settings($this->IGDataPath.$username.DIRECTORY_SEPARATOR.'settings-'.$username.'.dat');

        return new CheckUsernameResponse($this->request('users/check_username/', SignatureUtils::generateSignature($data))[1]);
    }

    /**
     * Checks if the email is already used (exists).
     *
     * @param string $email
     *
     * @return CheckEmailResponse
     */
    def checkEmail($email)
    {
        $data = json_encode([
            'qe_id'        => SignatureUtils::generateUUID(true),
            'waterfall_id' => SignatureUtils::generateUUID(true),
            'email'        => $email,
            '_csrftoken'   => 'missing',
        ]);

        return new CheckEmailResponse($this->request('users/check_email/', SignatureUtils::generateSignature($data))[1]);
    }

    def usernameSuggestions($email, $name)
    {
        $data = json_encode([
            'name'         => SignatureUtils::generateUUID(true),
            'waterfall_id' => SignatureUtils::generateUUID(true),
            'email'        => $email,
            '_csrftoken'   => 'missing',
        ]);

        return new UsernameSuggestionsResponse($this->request('accounts/username_suggestions/', SignatureUtils::generateSignature($data))[1]);
    }

    /**
     * Register account.
     *
     * @param string $username
     * @param string $password
     * @param string $email
     *
     * @return array AccountCreationResponse
     */
    def createAccount($username, $password, $email, $name = '')
    {
        $token = $this->getCsfrtoken();
        $data = json_encode([
            'allow_contacts_sync' => 'true',
            'phone_id'            => $this->uuid,
            '_csrftoken'          => $token,
            'username'            => $username,
            'first_name'          => $name,
            'guid'                => $this->uuid,
            'device_id'           => SignatureUtils::generateDeviceId(md5($username.$password)),
            'email'               => $email,
            'force_sign_up_code'  => '',
            'waterfall_id'        => $this->waterfall_id,
            'qs_stamp'            => '',
            'password'            => $password,
        ]);

        $result = $this->request('accounts/create/', SignatureUtils::generateSignature($data));
        $header = $result[0];
        $response = new AccountCreationResponse($result[1]);
        if ($response->isAccountCreated()) {
            $this->username_id = $response->getUsernameId();
            $this->settings->set('username_id', $this->username_id);
            preg_match('#Set-Cookie: csrftoken=([^;]+)#', $header, $match);
            $token = $match[1];
            $this->settings->set('token', $token);
        }

        return $response;
    }

    def getCsfrtoken()
    {
        $fetch = $this->request('si/fetch_headers/', None, true);
        $header = $fetch[0];
        $response = new ChallengeResponse($fetch[1]);

        if (!isset($header) || (!$response->isOk())) {
            throw new InstagramException("Couldn't get challenge, check your connection");
        }

        if (!preg_match('#Set-Cookie: csrftoken=([^;]+)#', $fetch[0], $token)) {
            throw new InstagramException('Missing csfrtoken');
        }

        return substr($token[0], 22);
    }

    def request($endpoint, $post = None)
    {
        $ch = curl_init();

        curl_setopt($ch, CURLOPT_URL, Constants::API_URL.$endpoint);
        curl_setopt($ch, CURLOPT_USERAGENT, $this->userAgent);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($ch, CURLOPT_HEADER, true);
        curl_setopt($ch, CURLOPT_VERBOSE, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
        curl_setopt($ch, CURLOPT_COOKIEFILE, $this->IGDataPath.$this->username.DIRECTORY_SEPARATOR."$this->username-cookies.dat");
        curl_setopt($ch, CURLOPT_COOKIEJAR, $this->IGDataPath.$this->username.DIRECTORY_SEPARATOR."$this->username-cookies.dat");

        if ($post) {
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $post);
        }

        if ($this->proxy) {
            curl_setopt($ch, CURLOPT_PROXY, $this->proxyHost);
            if ($this->proxyAuth) {
                curl_setopt($ch, CURLOPT_PROXYUSERPWD, $this->proxyAuth);
            }
        }

        $resp = curl_exec($ch);
        $header_len = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
        $header = substr($resp, 0, $header_len);
        $body = substr($resp, $header_len);

        curl_close($ch);

        if ($this->debug) {
            echo "REQUEST: $endpoint\n";
            if (!is_None($post)) {
                if (!is_array($post)) {
                    echo "DATA: $post\n";
                }
            }
            echo "RESPONSE: $body\n\n";
        }

        return [$header, json_decode($body, true)];
    }
}
