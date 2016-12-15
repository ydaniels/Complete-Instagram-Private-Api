import Image
class AdaptImage:

    sizes=None;
    images=None;
    width=None;
    height=None;
    newWidth=None;
    newHeight=None;
    x=None;
    y=None;

    def checkAndProcess(self,photo = None):
    
        try 

            if (photo == None) 
                raise Exception('Error: You did not specify image.');
                return ;
            
            self.images =Image.fromstring(photo);
            self.width = imagesx(self.images);
            self.height = imagesy(self.images);
            //IMAGE PROCESS
            if (self.width <= 320 && self.height <= 320) 
                self.newHeight = round((320 / self.width) * self.height);
                self.newWidth = round((self.newHeight / self.height) * self.width);
                im = imagecreatetruecolor(320, 320);
                wb = imagecolorallocate(im, 255, 255, 255);
                imagefill(im, 0, 0, wb);
                self.x = (320 - self.newHeight) / 2;
                self.y = (320 - self.newWidth) / 2;
                imagecopyresized(im, self.images, self.x, self.y, 0, 0, self.newWidth, self.newHeight, self.width, self.height);
             elseif (self.width >= self.height && self.width >= 1080) 
                self.newHeight = round((1080 / self.width) * self.height);
                self.newWidth = round((self.newHeight / self.height) * self.width);
                if (self.height < 575) 
                    self.newHeight = 575;
                 elseif (self.height > 1080) 
                    self.newHeight = 1080;
                
                im = imagecreatetruecolor(1080, 1080);
                wb = imagecolorallocate(im, 255, 255, 255);
                imagefill(im, 0, 0, wb);
                if (1080 > self.newHeight) 
                    self.y = (1080 - self.newHeight) / 2;
                 else 
                    self.y = (self.newHeight - 1080) / 2;
                
                if (1080 > self.newWidth) 
                    self.x = (1080 - self.newWidth) / 2;
                 else 
                    self.x = (self.newWidth - 1080) / 2;
                
                imagecopyresized(im, self.images, self.x, self.y, 0, 0, self.newWidth, self.newHeight, self.width, self.height);
             elseif (self.width >= self.height && self.width < 1080) 
                self.newHeight = round((640 / self.width) * self.height);
                self.newWidth = round((self.newHeight / self.height) * self.width);
                im = imagecreatetruecolor(640, self.newHeight);
                wb = imagecolorallocate(im, 255, 255, 255);
                imagefill(im, 0, 0, wb);
                if (640 > self.newWidth) 
                    self.x = (640 - self.newWidth) / 2;
                 else 
                    self.x = (self.newWidth - 640) / 2;
                
                imagecopyresized(im, self.images, self.x, self.y, 0, 0, self.newWidth, self.newHeight, self.width, self.height);
             elseif (self.height >= self.width && self.height > 1100) 
                self.newHeight = round((1080 / self.width) * self.height);
                self.newWidth = round((1349 / self.height) * self.width);
                im = imagecreatetruecolor(1080, 1349);
                wb = imagecolorallocate(im, 255, 255, 255);
                imagefill(im, 0, 0, wb);
                if (1379 > self.newHeight) 
                    self.y = (1379 - self.newHeight) / 2;
                 else 
                    self.y = (self.newHeight - 1379) / 2;
                
                if (1080 > self.newWidth) 
                    self.x = (1080 - self.newWidth) / 2;
                 else 
                    self.x = (self.newWidth - 1080) / 2;
                
                imagecopyresized(im, self.images, self.x, 0, 0, 0, self.newWidth, 1349, self.width, self.height);
             elseif (self.height > self.width && self.height <= 1100) 
                self.newHeight = round((640 / self.width) * self.height);
                self.newWidth = round((799 / self.height) * self.width);
                im = imagecreatetruecolor(640, 799);
                wb = imagecolorallocate(im, 255, 255, 255);
                imagefill(im, 0, 0, wb);
                if (799 > self.newHeight) 
                    self.y = (799 - self.newHeight) / 2;
                 else 
                    self.y = (self.newHeight - 799) / 2;
                
                if (640 > self.newWidth) 
                    self.x = (640 - self.newWidth) / 2;
                 else 
                    self.x = (self.newWidth - 640) / 2;
                

                imagecopyresized(im, self.images, self.x, 0, 0, 0, self.newWidth, 799, self.width, self.height);
            
            ob_start();
            imagejpeg(im);
            data = ob_get_contents();
            ob_end_clean();

            return data;
         catch (Exception e) 
            return e->getMessage();
        
    

