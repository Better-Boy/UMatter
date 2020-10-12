#!/bin/bash

exec gunicorn --config gunicorn-config.py wsgi:app