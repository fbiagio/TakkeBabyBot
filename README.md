# TakkeBabyBot
Bot Telegram that allow to create report for food, pee and poo

## Init DB 

to initialize the db instance run once the below command

```bash
python db.py
```

## run the bot 

Create a venv and install requirements (if you run on a raspberry use requirements_arm.txt)

```bash
python -m venv venv 
pip install requirements.txt
```

finally run your bot
```bash
python TakkeBabyBot.py
```

## Update 


```bash
git update-index --assume-unchanged config.py
git pull
```
# to do list:
 - add report for vitaminic
 - send a messagge at the end of the day with the report to subscriber



