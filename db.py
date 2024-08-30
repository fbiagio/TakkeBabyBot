import sqlite3
import logging
import prettytable as pt
logger = logging.getLogger(__name__)

DBFILE="sqlite.db"

def init():
    logger.info("init DB")
    conn = None
    try:
        conn = sqlite3.connect(DBFILE)
        print(sqlite3.sqlite_version)
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
    
    dbinit=[
        """
        CREATE TABLE IF NOT EXISTS "report" (
        "id"	INTEGER NOT NULL UNIQUE,
        "task"	TEXT,
        "datetime"	TEXT,
        "date"	TEXT,
        "start"	TEXT,
        "stop"	TEXT,
        "delta"	TEXT,
        "note"	TEXT,
        PRIMARY KEY("id" AUTOINCREMENT)
        )
        """
    ]
    try:
        with sqlite3.connect(DBFILE) as conn:
            cursor = conn.cursor()
            for statement in dbinit:
                print(f'{statement}')
                cursor.execute(statement)
            print("commit")
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"{e}")
    finally:
        if conn:
            conn.close()    

def last_breast() -> str:
    logger.info("dbquery - search last breast used")
    result = "??????"
    try:
        query=[ 
            """
            select note
            from report 
            where task == "milk" 
            order by datetime DESC LIMIT 1;
            """
        ]
        with sqlite3.connect(DBFILE) as conn:
            cur = conn.cursor()
        
            for row in cur.execute(query[0]):
                result=row
    except Exception as e:
        logger.error("impossibile leggere dal db")
    finally:
        if conn:
            conn.close()
        return result


def final_report() -> str:
    final_report="Report Giornaliero\n\n\n"
    try:
        query=[
            """
            select *
            from report 
            where task == "milk"
            and date == date('now', '-0 day') 
            order by datetime;
            """,
            """
            select task, count(task) 
            from report
            where date == date('now', '-0 day')
            and task == "poo"
            GROUP by task;
            """,
            """
            select task, count(task) 
            from report
            where date == date('now', '-0 day')
            and task == "pee"
            GROUP by task;
            """,
            """
            select task, count(task) 
            from report
            where date == date('now', '-0 day')
            and task == "milk"
            GROUP by task;
            """


        ]
        with sqlite3.connect(DBFILE) as conn:
            cur = conn.cursor()

        
            for row in cur.execute  (query[0]):
                
                final_report = f"{final_report}\n {":".join(row[4].split(":")[:-1])} -> {":".join(row[4].split(":")[:-1])} \t [{int(int(str(row[6]).split(".")[0])/60)} min ] ( {row[7]} )"
            
            final_report=f"{final_report}\n\n [[[ Numeri ]]]\n"
            for row in cur.execute  (query[1]):
                final_report = f"{final_report}\n {row[1]}\t \N{Pile of Poo} "
                #https://unicode.org/emoji/charts/full-emoji-list.html
            
            for row in cur.execute  (query[2]):
                final_report = f"{final_report}\n {row[1]}\t \N{Splashing Sweat Symbol}"
            
            for row in cur.execute  (query[3]):
                final_report = f"{final_report}\n {row[1]}\t \N{Baby Bottle}"
            
            
        logger.info(f"{final_report}")
    except Exception as e:
        logger.error(f"{e}")
        final_report="unable to get data"
    finally:
        if conn:
            conn.close()
        return final_report

def final_report_table() -> str:
    final_report=None
    
    table = pt.PrettyTable(['Inizio', 'Fine', 'Durata', 'note'])

    try:
        query=[
            """
            select *
            from report 
            where task == "milk"
            and date == date('now', '-0 day') 
            order by datetime;
            """
        ]
        with sqlite3.connect(DBFILE) as conn:
            cur = conn.cursor()

        
            for row in cur.execute  (query[0]):
                #final_report = f"{final_report}\n {row[4]} {row[5]} {row[6]} {row[7]}"
                table.add_row([row[4], row[5], f'{int(int(str(row[6]).split(".")[0])/60)} m', row[7]])
        
        logger.info(f"{table}")
        final_report = f"{table}"
    except Exception as e:
        logger.error(f"{e}")
    finally:
        if conn:
            conn.close()
        return final_report

def update_report(entry) -> bool:
    op = None
    try:
        with sqlite3.connect(DBFILE) as conn:
            cur = conn.cursor()
        
            data = [
                (
                entry["task"],
                entry["datetime"],
                entry["date"],
                entry["start"],
                entry["stop"],
                entry["delta"],
                entry["note"]
                )
            ]
            cur.executemany("INSERT INTO report (task, datetime, date, start, stop, delta, note) VALUES(?, ?, ?, ?, ?, ?, ?)", data)
            conn.commit()  # Remember to commit the transaction after executing INSERT.
            conn.close()
        op=True
    except Exception as e:
        logger.error("impossibile scriver sul db le informazioni")
        op=False
    finally:
        if conn:
            conn.close()
        return op
if __name__ == "__main__":
    init()