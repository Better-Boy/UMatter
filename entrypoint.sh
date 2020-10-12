#!/bin/bash

exec gunicorn --config gunicorn-config wsgi:app