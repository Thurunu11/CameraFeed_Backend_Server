import mysql.connector
import numpy as np
from mysql.connector import errorcode
import os
from dotenv import load_dotenv
import datetime
import matplotlib.pyplot as plt
import matplotlib;

matplotlib.use("TkAgg")

# loading the data from the .env file
load_dotenv()
# Current date and time
timenow = datetime.datetime.now()  # ---->Current date and time
plt.Figure(figsize=(24, 32))  # ---->Setting the figure size
plt.ion()  # ---->interactive mode on

row_array = []
date_array = []
thermal_data = []
timestamp_data = []
dataCount = 0
dataCountProcessed = 0


# **********Code snippet for the database connection **********

def initiate_database_connection():
    print('initiating database connection')
    # loading the data from the .env file
    load_dotenv()
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    USER = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')
    DATABASE = os.getenv('DATABASE')
    fetch_data_from_database(HOST, PORT, USER, PASSWORD, DATABASE)


def fetch_data_from_database(HOST, PORT, USER, PASSWORD, DATABASE):
    global thermal_data, timestamp_data, row_array, date_array, dataCount

    try:
        mydb = mysql.connector.connect(host=HOST, port=PORT, user=USER, password=PASSWORD, database=DATABASE)
        mydb.autocommit = True
        thermal2date = mydb.cursor(buffered=True)
        dataCount = mydb.cursor(buffered=True)
        print('database connection successful')
        # Execute a query
        thermal2date.execute(
            "SELECT thermaldata,Date1 FROM thermalimage")  # ---->Fetching the thermal data and timestamp from the database
        dataCount.execute(
            "SELECT COUNT(thermaldata) FROM thermalimage")  # ---->Fetching the thermal data and timestamp from the database

        row_array = []  # -->
        date_array = []  # -->
        thermal_data = []  # ----> For the temperarory storage of the data from the database
        timestamp_data = []  # -->

        for row in thermal2date.fetchall():
            thermal_data.append(row[0])  # --->fetching thermal data from the database
            timestamp_data.append(row[1])  # --->fetching timestamp data from the database

        dataCount = dataCount.fetchall()

        print('data fetched from database')
        mydb.close()
        print('database connection closed')  # --->closing the database connection

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Please check your username or password!")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)


def process_images():
    global thermal_data, timestamp_data, row_array, date_array, dataCount, dataCountProcessed

    dataCountProcessed = dataCount[0][0]  #-----> Converting the python list object to integer
    thermal_np = np.array(thermal_data)
    thermal_np = [str(thermal_np[i]) for i in range(len(thermal_np))]
    thermal_np = [thermal_np[i].split(',') for i in range(len(thermal_np))]

    for i in range(len(thermal_np)):
        thermal_np[i][0] = thermal_np[i][0].replace("['", '')
        thermal_np[i][-1] = thermal_np[i][-1].replace("']", '')
        try:
            thermal_np[i] = [float(thermal_np[i][j]) for j in range(len(thermal_np[i]))]
        except:
            pass

    for j in range(2, len(thermal_np)):  # ---->As the first 2 values are corrupted from the sensor
        row_array = np.array(thermal_np[j])
        # result_array1.append(row_array)
        y = np.array(thermal_np[j])
        final_therm = y.reshape(24, 32)  # ---->Reshaping the temperature array to 24x32 final thermal array
        print(final_therm)

        plt.clf()  # clear plot before each iteration
        plt.ylim(ymin=0, ymax=23)
        plt.imshow(final_therm, cmap='jet', interpolation='quadric')
        plt.colorbar()
        plt.title(f"Timestamp: {timestamp_data[j]}")
        plt.pause(0.01)  # add pause to allow time for plot to update

    plt.draw()
    # plt.show()


if __name__ == '__main__':
    initiate_database_connection()
    process_images()
