import mysql.connector
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv

def initialize_db():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY,
        last_alert_time TIMESTAMP,
        alert_count INTEGER
    )
    ''')
    conn.commit()
    conn.close()

def get_alert_info():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT last_alert_time, alert_count FROM alerts WHERE id = 1')
    result = cursor.fetchone()
    conn.close()
    if result:
        return datetime.fromisoformat(result[0]), result[1]
    return None, 0

def update_alert_info(last_alert_time, alert_count):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO alerts (id, last_alert_time, alert_count)
    VALUES (1, ?, ?)
    ''', (last_alert_time.isoformat(), alert_count))
    conn.commit()
    conn.close()

def check_slave_status():
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SHOW SLAVE STATUS")
        result = cursor.fetchone()

        if result:
            io_running = result['Slave_IO_Running']
            sql_running = result['Slave_SQL_Running']

            if io_running == 'No' or sql_running == 'No':
                handle_alert(io_running, sql_running)
            else:
                # Reset alert count if everything is OK
                update_alert_info(datetime.now(), 0)
        else:
            print("No slave status information available.")

        cursor.close()
        connection.close()

    except mysql.connector.Error as error:
        print(f"Error connecting to MySQL: {error}")

def handle_alert(io_running, sql_running):
    last_alert_time, alert_count = get_alert_info()
    current_time = datetime.now()

    if last_alert_time:
        time_since_last_alert = (current_time - last_alert_time).total_seconds() / 60  # in minutes
        backoff_interval = min(initial_interval * (2 ** alert_count), max_interval)

        if time_since_last_alert < backoff_interval:
            print(f"Skipping alert. Next alert in {backoff_interval - time_since_last_alert:.2f} minutes.")
            return

    send_alert(io_running, sql_running)
    update_alert_info(current_time, alert_count + 1)

def send_alert(io_running, sql_running):
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject='MySQL Slave Status Alert',
        html_content=f'<p>Alert: MySQL slave status issue detected.</p>'
                     f'<p>Slave_IO_Running: {io_running}</p>'
                     f'<p>Slave_SQL_Running: {sql_running}</p>'
    )

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        print(f"Email alert sent. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    load_dotenv()

    # MySQL connection details
    mysql_config = {
        'host': os.getenv('MYSQL_SLAVE_HOST'),
        'port': os.getenv('MYSQL_SLAVE_PORT'),
        'user': os.getenv('MYSQL_SLAVE_USER'),
        'password': os.getenv('MYSQL_SLAVE_PASSWORD')
    }

    # SendGrid configuration
    sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('FROM_EMAIL')
    to_email = os.getenv('TO_EMAIL')

    # SQLite database file
    db_file = '../alert_history.db'

    # Backoff settings
    initial_interval = 5  # minutes
    max_interval = 240  # 4 hours

    initialize_db()
    check_slave_status()
