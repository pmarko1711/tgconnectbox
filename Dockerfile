# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim-buster

LABEL Name=tgconnectbox Version=0.0.1

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Install pip requirements
# TODO: pip install connect-box directly (and remove git install and removal), once the pypi image contains ipv6 functionality
ADD requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends git && apt-get purge -y --auto-remove && rm -rf /var/lib/apt/lists/* && python -m pip install -r requirements.txt && python -m pip install git+https://github.com/home-assistant-ecosystem/python-connect-box.git && apt-get purge -y git
#RUN pip install -r requirements.txt

WORKDIR /app
ADD app.py /app
ADD connectbox.py /app

# config directory
VOLUME /config

# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
#RUN useradd appuser && chown -R appuser /app && chown -R appuser /config
RUN useradd appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "app.py"]
