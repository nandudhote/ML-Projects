import cv2
from pyzbar.pyzbar import decode
import pandas as pd
from time import sleep

def readExcel(excelFileName):
    try:
        excel = pd.read_excel(excelFileName)
        # print(excel)
        return excel
    except Exception as e:
        print("Error:", e)

def findFilledRowNumber(exceldata):
    return exceldata['ScannedDeviceId'].count()

def updateStatusinExcel(excelFileName, excelDF, rowIndex, ColumnNane, deviceId):
    excelDF.at[rowIndex, ColumnNane] = deviceId
    excelDF.to_excel(excelFileName, index=False, engine='openpyxl')

def scanQRAndStoreDevIdInExcel(rowNo, camIdx):
    # Open the USB camera
    cap = cv2.VideoCapture(camIdx)
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            # Extract the data from the QR code
            deviceId = obj.data.decode('utf-8')
            print("Device is: ", deviceId)

            # Store the QR code data in an Excel file
            if deviceId != "":
                ColumnNane = "ScannedDeviceId"
                rowNo += 1
                updateStatusinExcel(exelFileName, excelData, rowNo, ColumnNane, deviceId)
                deviceId = ""
                print ("Please wait, I'm Loggind Data in Excel..../")
                sleep(5)
                print ("Ready to Scan New Device...")

        # Display the frame
        cv2.imshow("CameraFrame", frame)

        # Check for 'q' key to exit the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

cameraIdx = 0
exelFileName = "DispatchedDeviceList.xlsx"
excelData = readExcel(exelFileName)
rowNum = findFilledRowNumber(excelData)
print("rowNum:", rowNum)
scanQRAndStoreDevIdInExcel(rowNum, cameraIdx)
