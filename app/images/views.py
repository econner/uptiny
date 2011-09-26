from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

# Imaging libraries
from boto.s3.connection import S3Connection # boto has bindings to connect to s3
import cStringIO
import urllib2
import Image
import base64
import random
import string

class S3ImageUpload(object):
    BUCKET_NAME = "media.uptiny.com"
    
    def upload_image(self, base64im):
        
        # Now we connect to our s3 bucket and upload from memory
        conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        # Connect to bucket and create key
        bucket = conn.get_bucket(self.BUCKET_NAME)
        
        decoded_img = base64.decodestring(base64im)
        
        # Load the URL data into an image
        try:
            img = cStringIO.StringIO(decoded_img)
        except (urllib2.HTTPError, urllib2.URLError):
            print "Could not read image into string"
            return

        try:
            im = Image.open(img)
        except IOError:
            print "Could not open image file"
            return
            
        print im

        # ensure its in the proper mode to save to jpg
        if im.mode != "RGB":
            im = im.convert("RGB")
        
        filename = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(8)) + '.png'
         # NOTE, we're saving the image into a cStringIO object to avoid writing to disk
        out_im = cStringIO.StringIO()
        # You MUST specify the file type because there is no file name to discern it from
        im.save(out_im, 'PNG')

        key = bucket.new_key(filename)
        key.set_metadata("Content-Type", 'image/png')

        # Note we're setting contents from the in-memory string provided by cStringIO
        key.set_contents_from_string(out_im.getvalue())
        
        return filename

def index(request):
    if "file" in request.POST:
        start_pos = request.POST['file'].find(',') + 1 # skip the comma
        im_str = request.POST['file'][start_pos:]
        s3uploader = S3ImageUpload()
        filename = s3uploader.upload_image(im_str)
        print filename
        return HttpResponse(filename)
    
    return render_to_response(
        "index.html",
        { 
        },
        context_instance = RequestContext(request)
    )