# ImmobilienScout instant notifier

## Purpose

This application sends push notifications for new announcements on Immobilienscount based on a search query.

## External services

The application makes use of free services or free usage plans of a variety of online services. The services used are:
- [Heroku](https://heroku.com) - Serverless hosting platform with free plan available
- [mongoDB Atlas](https://www.mongodb.com/cloud) - Free mongoDB hosting. We use this to store the already seen announcements.
- [Telegram](https://www.telegram.org/) - Cross-platform messaging application. Used to receive push notifications.

Suggested, but not required:
- [Pipedream](https://pipedream.com) - Used to trigger the application based on a defined schedule

## Set up

After registering in Heroku and Telegram, one can start setting up the application and deploy it.

### Install Heroku CLI

First install on your local machine and login to [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli). Afterwards, select an application name and make it available as an environment variable:

```
export APP_NAME=<YOUR_HEROKU_APP_NAME>
```

### Set up database

Create a free accout at [Mongo Cloud](https://www.mongodb.com/cloud) and set up a user for accessing the database. Provide the database credentians and names as environment variables:

```
export DB_USERNAME=<YOUR_DB_USERNAME>
export DB_PASSWORD=<YOUR_DB_PASSEWORD>
export DB_NAME=<YOUR_DB_NAME>
export BH_COLLECTION_NAME=<YOUR_BH_COLLECTION_NAME>
export IMMO_COLLECTION_NAME=<YOUR_IMMO_COLLECTION_NAME>
```

### Store API secrets for deployment in Heroku

In order not to share the secrets, Heroku's secret injection feature can be utilized. It provies a secret storage, which are used during deployment to populate environment variables.


### Telegram bot
Use BotFather to create a bot in telegram. Short explanation is [here](https://core.telegram.org/bots#6-botfather).
Basically find BotFather in Telegram and send the message `/newbot` and follow the instructions.
After you have created the bot you should have gotten a token that allows you to control the bot, something like `110201543:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`.

```
$ export BOT_TOKEN=<TELEGRAM_BOT_TOKEN>
```

From Telegram it is also needed a chat id, i.e. the id of your chat with the bot. 
After writing a couple of dummy messages to the bot, run this command to get the id:
```
$ curl https://api.telegram.org/bot<YourBOTToken>/getUpdates
```

The `chat` object in the message looks something along the lines:
```
{
    "update_id": 8393,
    "message": {
        "message_id": 3,
        "from": {"id": 7474, "first_name": "AAA"},
        "chat": {"id": "<TELEGRAM_BOT_CHAT_ID>", "title": ""},
        "date": 25497,
        "new_chat_participant": {
            "id": 71, "first_name": "NAME", "username": "YOUR_BOT_NAME"
        }
    }
}
```

After finding the chat id, export it:
```
$ export CHAT_ID=<TELEGRAM_BOT_CHAT_ID>
```
If the response does not look like that, write a couple of more messages to the bot.

### Last steps

Finally, one can set up the configuration variables:
```
heroku config:set -a $APP_NAME DB_NAME=$DB_NAME
heroku config:set -a $APP_NAME DB_USERNAME=$DB_USERNAME
heroku config:set -a $APP_NAME DB_PASSWORD=$DB_PASSWORD
heroku config:set -a $APP_NAME BH_COLLECTION_NAME=$BH_COLLECTION_NAME
heroku config:set -a $APP_NAME IMMO_COLLECTION_NAME=$IMMO_COLLECTION_NAME
heroku config:set -a $APP_NAME BOT_TOKEN=$BOT_TOKEN
heroku config:set -a $APP_NAME CHAT_ID=$CHAT_ID
heroku config:set -a $APP_NAME SECRET=<SECRET>
```

## Customize and deploy

### Customize ImmobilienScout search link

The variable `IMMO_SEARCH_URL` is just an ImmobilienScout24 URL. 

This URL is used for scraping. For a properly functioning application you should make sure that the URL is having the following properties:
- Apartments are in list view (not map view)
- Sorted by date, so that newest are first. This is especially important as you only request the first page and looking for new stuff on that page.

After getting the URL from the browser, run: 
```
export IMMO_SEARCH_URL=<YOUR_IMMO_URL>
heroku config:set -a $APP_NAME IMMO_SEARCH_URL=<IMMOSEARCH_URL>
```

Feel free to go crazy with search criteria, one just needs to update the variable.

### Deploy

Application deployment gets invoked on every git push, via GitHub Integration.

### Execute

The application offers a single GET endpoint `/findplaces`. It returns the unseen apartments as a json, and it sends a notification for each of them via Telegram. On the same endpoint, one can set up the regular execution.