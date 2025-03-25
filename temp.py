import pymysql
import numpy as np
import time
import threading

# 数据库连接信息
host = 'localhost'
port = 3306
db = "test"
user = 'root'
password = '1234'

def get_connection():
    return pymysql.connect(host=host, port=port, db=db, user=user, password=password)

def clear_database():
    """清空数据库中的指定表"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("TRUNCATE TABLE temps")
        cursor.execute("TRUNCATE TABLE powers")
        conn.commit()
        print("Database tables cleared.")
    except Exception as e:
        print(f"Error clearing database: {e}")
    finally:
        cursor.close()
        conn.close()

class Data_Generator:
    def __init__(self):
        self.x = 0
        self.conn = get_connection()
        self.column_temp = self.get_column_name("temps")
        self.column_power = self.get_column_name("powers")
        self.cards_num = len(self.column_temp) - 1

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def get_column_name(self, table_name):
        cursor = self.conn.cursor()
        sql = f"DESCRIBE {table_name}"
        cursor.execute(sql)
        results = cursor.fetchall()
        column_name = [result[0] for result in results]
        cursor.close()
        return column_name

    def generate_data(self):
        while True:
            self.generate_temp()
            self.generate_power()
            time.sleep(1)

    def generate_temp(self):
        temp1 = round(50 * self.sigmoid(self.x / 200) + np.random.normal(1, 1), 2)
        temp2 = round(55 * self.sigmoid(self.x / 210) + np.random.normal(1, 2), 2)
        temp3 = round(60 * self.sigmoid(self.x / 230) + np.random.normal(2, 1), 2)
        cursor = self.conn.cursor()
        sql = "INSERT INTO temps(" + ",".join(self.column_temp[1:4]) + ") VALUES(%s, %s, %s)"
        cursor.execute(sql, (temp1, temp2, temp3))
        self.conn.commit()
        cursor.close()
        self.x += 1

    def generate_power(self):
        power1 = round(2 * self.sigmoid(self.x / 200) + np.random.normal(0.2, 0.5), 2)
        power2 = round(3 * self.sigmoid(self.x / 210) + np.random.normal(0.1, 0.5), 2)
        power3 = round(6 * self.sigmoid(self.x / 230) + np.random.normal(0.2, 0.5), 2)
        cursor = self.conn.cursor()
        sql = "INSERT INTO powers(" + ",".join(self.column_power[1:4]) + ") VALUES(%s, %s, %s)"
        cursor.execute(sql, (power1, power2, power3))
        self.conn.commit()
        cursor.close()

    def __del__(self):
        self.conn.close()

def read_data():
    """在每次显示请求时从数据库读取最新的数据"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT * FROM temps ORDER BY id DESC LIMIT 5")
        temp_data = cursor.fetchall()
        cursor.execute("SELECT * FROM powers ORDER BY id DESC LIMIT 5")
        power_data = cursor.fetchall()

        print("Latest temperature data:")
        for record in temp_data:
            print(record)

        print("\nLatest power data:")
        for record in power_data:
            print(record)
    finally:
        cursor.close()
        conn.close()

def main():
    # 清空数据库表
    clear_database()

    # 启动数据生成线程
    data_generator = Data_Generator()
    data_thread = threading.Thread(target=data_generator.generate_data)
    data_thread.daemon = True
    data_thread.start()

    try:
        while True:
            command = input("Enter 'show' to display latest data or 'exit' to quit: ").strip()
            if command.lower() == 'show':
                read_data()  # 直接读取最新的数据
            elif command.lower() == 'exit':
                break
            else:
                print("Invalid command. Use 'show' or 'exit'.")
    finally:
        print("Exiting program...")

if __name__ == "__main__":
    main()