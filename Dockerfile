FROM retailproj-requirements

ENV UWSGI_INI /retailProj/uwsgi.ini
ENV PYTHONPATH "${PYTHONPATH}:/retailProj"

COPY . /retailProj


WORKDIR /retailProj