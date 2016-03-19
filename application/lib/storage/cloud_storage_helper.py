from time import time
import cloudstorage
from google.appengine.api import blobstore
from google.appengine.api import images


def _save_file(image_binary, filepath):
    ext = filepath.split(".")[-1]

    '''
    writable_file_name = files.gs.create(
        filepath,
        acl="public-read",
        mime_type='image/' +
        ext)
    '''
    gcs_file = cloudstorage.open(filepath,
                                 'w',
                                 content_type='image/' + ext,
                                 options={'x-goog-acl': 'public-read'})
    gcs_file.write(image_binary)
    gcs_file.close()
    print "gcs save done"


def upload_image(image_binary, content_type):
    """

    :param image_binary:
    :param content_type:
    :return: (profile_url, profile_serving_url)
    """
    filename = str(time()).replace('.', '') + "." \
               + content_type.split('/')[1]
    directory = '/bd-profile-image/temp/'
    filepath = directory + filename
    _save_file(image_binary, filepath)

    # generate profile serving url
    bkey = blobstore.create_gs_key('/gs' + filepath)
    profile_serving_url = images.get_serving_url(bkey)

    # pulic profile url
    profile_url = 'http://storage.googleapis.com' + filepath
    return profile_url, profile_serving_url
