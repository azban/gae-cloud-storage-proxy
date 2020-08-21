import logging
import os
from flask import Flask, abort
from google.cloud import storage

app = Flask(__name__)

# Configure this environment variable via app.yaml
CLOUD_STORAGE_BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET')
CLOUD_STORAGE_PREFIX = os.environ.get('CLOUD_STORAGE_PREFIX', '')

if not CLOUD_STORAGE_BUCKET:
    raise RuntimeError('CLOUD_STORAGE_BUCKET environment variable must be specified')


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>')
def index(path):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(CLOUD_STORAGE_BUCKET)
    blob = bucket.get_blob(os.path.join(CLOUD_STORAGE_PREFIX, path))
    if blob is None:
        abort(404)

    content = blob.download_as_string()
    if blob.content_encoding:
        return content.decode(blob.content_encoding)
    else:
        return content


@app.errorhandler(404)
def handle_404(_):
    return '404: This page does not exist', 404


@app.errorhandler(Exception)
def server_error(e):
    logging.exception(e)
    return """An internal error occurred: <pre>{}</pre>
See logs for full stacktrace.""".format(e)


if __name__ == '__main__':
    app.run(debug=True)
