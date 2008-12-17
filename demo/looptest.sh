#!/bin/sh

while [[ $? == "0" ]]; do
python manage.py test
done

