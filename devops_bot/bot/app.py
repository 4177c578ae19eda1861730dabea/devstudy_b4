import os
import logging
import re
import paramiko
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import psycopg2
from psycopg2 import Error


# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# Получаем логи из функций библиотек
logger = logging.getLogger(__name__)

# Подгружаем .env
#load_dotenv()

# Выбираем нужную переменную из .env
TOKEN = os.getenv('YOUR_BOT_TOKEN')
host = os.getenv('HOST')
port = os.getenv('PORT')
username = os.getenv('USER')
password = os.getenv('PASSWORD')
pg_user = os.getenv('PG_USER')
pg_password = os.getenv('PG_PASSWORD')
pg_host = os.getenv('PG_HOST')
pg_port = os.getenv('PG_PORT')
pg_dbname = os.getenv('PG_DBNAME')

globalPhoneNumbers = []
globalEmail = []
def pgSelect(command):

    try:
        connection = psycopg2.connect(user=pg_user,
                                        password=pg_password,
                                        host=pg_host,
                                        port=pg_port,
                                        database=pg_dbname)
        cursor = connection.cursor()
        cursor.execute(command)
        data = cursor.fetchall()

        logging.info("Команда успешно выполнена")

    except (Exception, Error) as error:
        logging.error("Ошибка при работе с POstgreSQL", error)

    finally:
        if connection is not None:
            cursor.close()
            connection.close()
        logging.info("Соединение с PostgreSQL закрыто")

    return data;

def pgInsert(command):

    try:
        connection = psycopg2.connect(user=pg_user,
                                        password=pg_password,
                                        host=pg_host,
                                        port=pg_port,
                                        database=pg_dbname)
        cursor = connection.cursor()
        cursor.execute(command)
        connection.commit()
        
        logging.info("Команда успешно выполнена")
        data = " успешно записано"

    except (Exception, Error) as error:
        logging.error("Ошибка при работе с POstgreSQL", error)
        data = " ошибка при записи"
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
        logging.info("Соединение с PostgreSQL закрыто")

    return data;


# Функция /start которое выводит приветствие
def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

# Функция /help в которую можно добавить инструкцию по работе c ботом
def helpCommand(update: Update, context):
    update.message.reply_text('Что умеет бот:\n/start - Приветствие бота\n/help - Вывести информацию о возможностей бота\n/find_phone_number - Поиск номера телефона в тексте\n/find_email - Поиск email в тексте\n/verify_password - Проверка пароля на сложность\n/get_release\n/get_uname\n/get_uptime\n/get_df\n/get_free\n/get_mpstat\n/get_w\n/get_auths\n/get_critical\n/get_ps\n/get_ss\n/get_apt_list\n/get_services\n/get_repllog\n/get_emails\n/get_phone_numbers')

# Функция вывод тестка для запроса номеров телефона
def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')

    return 'find_phone_number'

# Функция поиска номера телефона в тексте
def findPhoneNumbers(update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(8|\+7)(-| )?(\()?(\d{3})(\))?(-| )?(\d{3})(-| )?(\d{2})(-| )?(\d{2})') # Фрмат номера с пробелами или дефис и без них, а так же со скобками и без, и начало с 8 или +7

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов
    
    
    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END # Завершаем работу обработчика диалога
    global globalPhoneNumbers
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    globalPhoneNumbers = []
    

    logging.info('В масиве номров первый номер ' + ''.join(phoneNumberList[0])) # Логирование для проверки записаного формата номера
    for i in range(len(phoneNumberList)):

        phoneNumbers += f'{i+1}. {"".join(phoneNumberList[i])}\n' # Записываем очередной номер
        globalPhoneNumbers.append("".join(phoneNumberList[i]))

    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    
    update.message.reply_text("Записать номера телефонов в базу?(да/нет)")
            
    return 'write_phone_numbers_db'


def writePhoneNumbersDb(update: Update, context):
    user_input = update.message.text
     
    if user_input.lower() == 'да':
        for item in globalPhoneNumbers:
            result = pgInsert(f"INSERT INTO numberPhone(numberphone) VALUES('{item}')")
            update.message.reply_text(item + result)
    else:
        update.message.reply_text("Запись в базу данных не требуется")
    return ConversationHandler.END

# Функция вывод тестка для запроса email
def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска email: ')

    return 'find_email'

# Функция поиска email в тексте
def findEmail(update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) email

    emailRegex = re.compile(r"([A-Za-z0-9!#$%&'*+\-\/=?^_`{|}~]+)(\.{0,1}[A-Za-z0-9!#$%&'*+\-\/=?^_`{|}~]+)+(@)([0-9a-zA-Z][0-9a-zA-Z\-]*[0-9a-zA-Z]\.)+([0-9a-zA-Z]*[a-zA-Z]+[0-9a-zA-Z]*)") # Формат email

    emailList = emailRegex.findall(user_input) # Ищем email
    
    
    if not emailList: # Обрабатываем случай, когда нет email
        update.message.reply_text('Email не найдены')
        return ConversationHandler.END # Завершаем работу обработчика диалога

    email = '' # Создаем строку, в которую будем записывать номера телефонов
    global globalEmail
    globalEmail = []
	
    logging.info('В масиве email первый email ' + ''.join(emailList[0])) # Логирование для проверки записаного формата email
    for i in range(len(emailList)):
        email += f'{i+1}. {"".join(emailList[i])}\n' # Записываем очередной email
        globalEmail.append("".join(emailList[i]))
		
    update.message.reply_text(email) # Отправляем сообщение пользователю
    update.message.reply_text("Записать email в базу?(да/нет)")
	
    return 'write_email_db'

def writeEmailDb(update: Update, context):
    user_input = update.message.text

    if user_input.lower() == 'да':
        for item in globalEmail:
            result = pgInsert(f"INSERT INTO email(emailname) VALUES('{item}')")
            update.message.reply_text(item + result)
    else:
        update.message.reply_text("Запись в базу данных не требуется")
    return ConversationHandler.END

# Функция вывод тестка для запроса пароля
def checkVerifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки его сложности: ')

    return 'verify_password'

# Функция проверки сложности пароля
def checkVerifyPassword(update: Update, context):
    user_input = update.message.text  # Получаем пароль

    passwordRegex = re.compile(
        r'^(?=.*[A-Z])(?=.*[!@#$%^&*()])(?=.*[0-9])(?=.*[a-z]).{8,}$')  # Регулярное выражение сложного пароля

    password = passwordRegex.search(user_input)  # Проверяем пароль на соответствие

    if password:
        logging.info(
            'Ввели сложный пароль ' + password.group())  # Логирование для что попало в пароль после проверки регуляркой
        update.message.reply_text('Пароль сложный')  # Отправляем сообщение пользователю если пароль сложный
    else:
        logging.info(
            'Ввели простой пароль ' + user_input)  # Логирование для что попало в пароль после проверки регуляркой
        update.message.reply_text('Пароль простой')  # Отправляем сообщение пользователю если пароль простой


    return ConversationHandler.END  # Завершаем работу обработчика диалога

# Функция мониторинга Linux
def getRelease(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('cat /etc/issue')
    data = stdout.read()
    logging.info(
        'Результат выполнения команды:\n' + str(data))
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getUname(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uname -a')
    data = stdout.read()
    logging.info(
        'Результат выполнения команды:\n' + str(data))
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getUptime(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uptime')
    data = stdout.read()
    logging.info(
        'Результат выполнения команды:\n' + str(data))
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getDf(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('df -h')
    data = stdout.read()
    logging.info(
        'Результат выполнения команды:\n' + str(data))
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getFree(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('free -h')
    data = stdout.read()
    logging.info(
        'Результат выполнения команды:\n' + str(data))
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getMpstat(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('mpstat')
    data = stdout.read()
    logging.info(
        'Результат выполнения команды:\n' + str(data))
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getW(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('who -u')
    data = stdout.read()
    logging.info(
        'Результат выполнения команды:\n' + str(data))
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getAuths(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('last -n 20')
    data = stdout.read()
    logging.info(
        'Результат выполнения команды:\n' + str(data))
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    index = 0
    data_out = ''
    for line in data.split("\n")[:-2]:
        if len(line):
            if "reboot" not in line:
                index += 1
                if index > 10:
                    break
                data_out += (f"{index}. {line} \n")

    update.message.reply_text(data_out)

def getCritical(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('journalctl -p2 -n5')
    data = stdout.read()
    logging.info(
        'Результат выполнения команды:\n' + str(data))
    client.close()

    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getPs(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ps au')
    data = stdout.read()
    logging.info(
        'Результат выполнения команды:\n' + str(data))
    client.close()

    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getSs(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ss -tulnap')
    data = stdout.read()
    logging.info(
        'Результат выполнения команды:\n' + str(data))
    client.close()

    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

# Функция вывода текста для работы с пакетами
def getAptListCommand(update: Update, context):

    messages = 'Для получения информации о пакете ввидите это название или `list` для получения списка всех пакетов'
    update.message.reply_text(messages)

    return 'get_apt_list'

def getAptList(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    package = update.message.text
    if package == 'list':
        command = 'apt list --installed '
    else:
        command = 'apt show ' + package

    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read()
    logging.info(
        'Результат выполнения команды:\n' + str(data))
    client.close()
    if not len(data):
        update.message.reply_text('Введено неверное имя пакета')
        return ConversationHandler.END
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]

    if len(data) > 4096:
        for index in range(0, len(data), 4096):
            update.message.reply_text(data[index:index + 4096])
    else:
        update.message.reply_text(data)
def getServices(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('systemctl list-units --type=service --state=running')
    data = stdout.read()
    logging.info(
        'Результат выполнения команды:\n' + str(data))
    client.close()

    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getReplLog(update: Update, context):

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('journalctl -eu postgres.service | grep replication | tail -n5' )
    data = stdout.read()
    logging.info(
        'Результат выполнения команды:\n' + str(data))
    client.close()

    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    update.message.reply_text(data)

def getEmails(update: Update, context):

    data = pgSelect("SELECT * FROM email")

    data_tmp = ''
    for item in data:
        data_tmp += str(item[0]) + '. ' + item[1] + '\n'
        
    update.message.reply_text(data_tmp)

def getPhoneNumbers(update: Update, context):

    data = pgSelect("SELECT * FROM numberPhone")

    data_tmp = ''
    for item in data:
        data_tmp += str(item[0]) + '. ' + item[1] + '\n'

    update.message.reply_text(data_tmp)



def main():
    # Создайте программу обновлений и передайте ей токен вашего бота
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога поиска номера телефона
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'write_phone_numbers_db': [MessageHandler(Filters.text & ~Filters.command, writePhoneNumbersDb)]
        },
        fallbacks=[]
    )

    # Обработчик диалога поиска email
    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, findEmail)],
            'write_email_db': [MessageHandler(Filters.text & ~Filters.command, writeEmailDb)]
        },
        fallbacks=[]
    )

    # Обработчик диалога проверки пароля
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', checkVerifyPasswordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, checkVerifyPassword)],
        },
        fallbacks=[]
    )

    # Обработчик диалога запроса списка пакетов
    convHandlerAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', getAptListCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, getAptList)],
        },
        fallbacks=[]
    )

    # Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmail)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(CommandHandler("get_release", getRelease))
    dp.add_handler(CommandHandler("get_uname", getUname))
    dp.add_handler(CommandHandler("get_uptime", getUptime))
    dp.add_handler(CommandHandler("get_df", getDf))
    dp.add_handler(CommandHandler("get_free", getFree))
    dp.add_handler(CommandHandler("get_mpstat", getMpstat))
    dp.add_handler(CommandHandler("get_w", getW))
    dp.add_handler(CommandHandler("get_auths", getAuths))
    dp.add_handler(CommandHandler("get_critical", getCritical))
    dp.add_handler(CommandHandler("get_ps", getPs))
    dp.add_handler(CommandHandler("get_ss", getSs))
    dp.add_handler(convHandlerAptList)
    dp.add_handler(CommandHandler("get_services", getServices))
    dp.add_handler(CommandHandler("get_repllog", getReplLog))
    dp.add_handler(CommandHandler("get_emails", getEmails))
    dp.add_handler(CommandHandler("get_phone_numbers", getPhoneNumbers))


    # Запускаем бота
    updater.start_polling()

    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()

