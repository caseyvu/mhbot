# mhbot

## Install postfix

For ubuntu:
```
sudo apt-get update
sudo apt-get install postfix
```

Enter domain name (i.e.: caseyvu.com)

## Run it

Create the actual conf file:
```
cp conf.default conf
```
Fill in the details in conf, the email_from should be some_one@you_domain_name

Run:
```
python3 main.py -c conf
```

## Docker
Attempted to dockerize it, however, there is still some issues with sending email from inside the docker. Thus it is not used
