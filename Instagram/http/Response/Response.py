



class Response(AutoResponseFunctionSetter):

    STATUS_OK = 'ok'
    STATUS_FAIL = 'fail'

    status=None
    message=None
    fullResponse=None

    def __init__(self):
        pass

    def setStatus(self,status):
    
        self.status = status
    

    def  getStatus(self):
    
        return self.status
    

    def setMessage(self,message):
    
        self.message = message

    def getMessage(self):
    
        return self.message
    

    def setFullResponse(self,response):
    
        self.fullResponse = response
    

    def getFullResponse(self):
    
        return self.fullResponse
    

    def isOk(self):
    
        return self.getStatus() == self.STATUS_OK
    

