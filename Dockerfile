FROM kbase/kbase:sdkbase2.latest
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# RUN apt-get update

# Update security deps
RUN pip install -U pip
RUN pip install --upgrade \
    cffi pyopenssl ndg-httpsclient pyasn1 requests 'requests[security]'

# Install pip deps
COPY requirements.txt /kb/module/requirements.txt
WORKDIR /kb/module
RUN pip install -r requirements.txt

# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module
RUN make all
ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
