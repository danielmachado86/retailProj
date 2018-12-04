import hashlib

from flask import Flask, g, jsonify, render_template, request, current_app, abort, after_this_request
from dbmodel.user_account.usermodel import User
from flask_httpauth import HTTPBasicAuth

import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

from datetime import timedelta, datetime
from functools import update_wrapper
from werkzeug import exceptions
import io
import gzip
import functools

from werkzeug.wrappers import ETagResponseMixin, Response

app = Flask(__name__)

