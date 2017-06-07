# vim:set ft=dockerfile:
FROM       debian:jessie

RUN        apt-get update && apt-get install -y --no-install-recommends \
	   python \
           python-setuptools
           make \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

RUN        easy_install pip
RUN        pip install \
           sphinx \
           sphinx_rtd_theme

VOLUME     /opt/AMS-library/docs

WORKDIR    /opt/AMS-library/docs

ENTRYPOINT ["make"]

CMD        ["help"]
