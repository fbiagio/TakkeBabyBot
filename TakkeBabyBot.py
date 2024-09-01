#!/usr/bin/env python

import logging
import datetime
import db
import json
from typing import Dict
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
from config import TakkeBabybot as TOKEN
from config import babyname as babyname
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_MILK, TYPING_MILKING_START, TYPING_MILKING_STOP , REPORT_ASK = range(6)
REPORT_STRUCT= {
        "task" : "",
        "datetime" : "",
        "date" : "",
        "start" : "",
        "stop"  : "",
        "note"  : "",
        "delta" : ""
        }

datetimeformat="%Y-%m-%d %H:%M:%S"
dateformat="%Y-%m-%d"
timeformat="%H:%M:%S"

def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask user for input."""
    logger.info(f'start conversation')
    await update.message.reply_text(
        "Ciao SuperMamma! cosa possiamo registrare oggi?",
        reply_markup=ReplyKeyboardMarkup([ ["pee", "poo"], ["milk", "dayreport"],["Cancel"],], one_time_keyboard=True),
    )
    return CHOOSING

async def milk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f'milk - ask few information')
    text = update.message.text
    context.user_data["record"] = REPORT_STRUCT
    context.user_data["record"]["task"]="milk"        
    logger.info(f'text - [ {text} ]')
    last_breast=db.last_breast()
    logger.info(f'milk - last breast {last_breast}')

    await update.message.reply_text(
        f"[{text.lower()}] è ora di sfamare {babyname}..."
        f"quale seno vuoi proporre ?"
        f"nell'ultima poppata hai dato quello {last_breast}",
        reply_markup=ReplyKeyboardMarkup([ ["SX", "DX"], ["Cancel"] ], one_time_keyboard=True),
        )
    return TYPING_MILKING_START
'''
async def ask_breast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data["record"]["note"]=text
    logger.info(f'text - [ {text} ]')
    await update.message.reply_text(
        f"hai scelto la tetta [ {text.upper()} ], adesso puoi iniziare a sfamare {babyname}",
        reply_markup=ReplyKeyboardMarkup([ ["Start"], ["Cancel"] ], one_time_keyboard=True),
        )
    return TYPING_MILKING_START
'''
async def start_milking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    #context.user_data["choice"] = text
    context.user_data["record"]["date"]=datetime.datetime.now().strftime(dateformat)
    context.user_data["record"]["datetime"]=datetime.datetime.now().strftime(datetimeformat)            
    context.user_data["record"]["start"]=datetime.datetime.now().strftime(timeformat)
    logger.info(f'text - [ {text} ]')
    await update.message.reply_text(
        f"dimmi quando {babyname} è sazio ... ",
        reply_markup=ReplyKeyboardMarkup([ ["Stop"], ["Cancel"] ], one_time_keyboard=True),
        )
    return TYPING_MILKING_STOP

async def stop_milking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    user_data = context.user_data
    
    #context.user_data["choice"] = text
    context.user_data["record"]["stop"] = datetime.datetime.now().strftime(timeformat)
    logger.info(f'{context.user_data["record"]["datetime"]}')
    a = datetime.datetime.now()
    b = datetime.datetime.strptime(context.user_data["record"]["datetime"], datetimeformat)
    logger.info(f"{type(a)} {type(b)}")
    diff= a - b
    context.user_data["record"]["delta"] = diff.total_seconds()
    logger.info(f'text - [ {text} ]')
    #markup = ReplyKeyboardMarkup([ ["Stop"], ["Cancel"] ], one_time_keyboard=True)
    await update.message.reply_text(
        f"finalmente puoi riposarti un po'",
        )
    
    db.update_report(user_data["record"])
    user_data.clear()
    logger.info("stop conversation, cancel interaction")        
    return ConversationHandler.END
    #return REPORT

async def pee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f'pee function')
    text = update.message.text 
    user_data = context.user_data
       
    context.user_data["record"] = REPORT_STRUCT
    context.user_data["record"]["task"]="pee"
    context.user_data["record"]["date"]=datetime.datetime.now().strftime(dateformat)        
    context.user_data["record"]["start"]=datetime.datetime.now().strftime(datetimeformat)
    await update.message.reply_text(
        f"Hai un pannolino da cambiare a {babyname} !!! Sbrigati!!"
    )
    db.update_report(user_data["record"])
    user_data.clear()
    logger.info("stop conversation, cancel interaction")        
    return ConversationHandler.END
    #return REPORT

async def poo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f'poo function')
    text = update.message.text
    user_data = context.user_data

    context.user_data["record"] = REPORT_STRUCT
    context.user_data["record"]["task"]="poo"
    context.user_data["record"]["date"]=datetime.datetime.now().strftime(dateformat)        
    context.user_data["record"]["start"]=datetime.datetime.now().strftime(datetimeformat)        

    await update.message.reply_text(
        f"Devi cambiare un pannollino [{text.lower()}]!!! Sbrigati!! c'è un odore terribile nell'aria",
       )
    
    db.update_report(user_data["record"])
    user_data.clear()
    logger.info("stop conversation, cancel interaction")        
    return ConversationHandler.END        
    #return REPORT

async def askdayreport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f'dayreport - ask for day')
    text = update.message.text
    #final_repot=db.final_report(0)
    
    #await update.message.reply_text(f'{final_repot}', parse_mode=ParseMode)
    await update.message.reply_text( f"quanti giorni fa?",
                                        reply_markup=ReplyKeyboardMarkup([ ["0","1","2", "3"], ["Cancel"] ], one_time_keyboard=True),
                                    )    
    return REPORT_ASK

async def dayreport(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f'dayreport - list all task of day')
    text = update.message.text
    #final_repot_table=db.final_report_table(text.)
    final_repot=db.final_report(text)
    
    #await update.message.reply_text(f'{final_repot}', parse_mode=ParseMode)
    await update.message.reply_text( f"{final_repot}")    
    return ConversationHandler.END



async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    logger.info(f"{json.dumps(user_data, indent=3)}")    
    await update.message.reply_text(
        f"Dati che verranno inseriti nel report: {facts_to_str(user_data)}Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )
    db.update_report(user_data["record"])
    user_data.clear()
    logger.info("stop conversation, cancel interaction")        
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("stop conversation, cancel interaction")
    return ConversationHandler.END




def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.        
    application = Application.builder().token(TOKEN).build()
    # Add conversation handler with the states CHOOSING, TYPING_MILK and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex("^pee$"), pee
                ),
                MessageHandler(
                    filters.Regex("^poo$"), poo
                ),
                MessageHandler(
                    filters.Regex("^milk$"), milk
                ),
                MessageHandler(
                    filters.Regex("^dayreport$"), askdayreport
                )
            ],
            TYPING_MILKING_START: [
                MessageHandler(
                    filters.Regex("^^(DX|SX)$$"), start_milking
                )
            ],
            TYPING_MILKING_STOP: [
                MessageHandler(
                    filters.Regex("^Stop$"), stop_milking
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), start,
                )
            ],
            REPORT_ASK: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^/d+$")), dayreport,
                )
            ]
        },
        fallbacks=[
            MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Cancel$")), cancel,
                ),
            MessageHandler(
                filters.Regex("^Cancel$"), cancel
                )
            ]
    )
    application.add_handler(conv_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()