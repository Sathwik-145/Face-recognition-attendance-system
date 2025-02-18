import os
import cv2
import face_recognition
import numpy as np
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox
import itertools

# Initialize the main window
root = tk.Tk()
root.title("Attendance System")
root.geometry("800x800")
root.configure(bg="#cce7ff")  # Light blue background

# Finding images in the folder
path = "face_database"
imaddrs = os.listdir(path)
images = []
namesList = []
valid_extensions = ('.jpg', '.jpeg', '.png')

for add in imaddrs:
    if add.lower().endswith(valid_extensions):  # Ensure it's an image file
        currentImage = cv2.imread(f'{path}/{add}')
        if currentImage is not None:  # Check if the image was loaded successfully
            images.append(currentImage)
            namesList.append(os.path.splitext(add)[0])

print("Names in the database:", namesList)

# Function to post attendance
def postAttendance(name):
    tDate = date.today()
    try:
        os.makedirs("attendance_records", exist_ok=True)
        with open(f'attendance_records/{tDate}.csv', "x") as f:
            f.writelines('Name,InTime,OutTime\n')
    except FileExistsError:
        pass

    with open(f"attendance_records/{tDate}.csv", "r+") as f:
        currentFile = f'attendance_records/{tDate}.csv'
        namesList = []
        inTimeList = []
        outTimeList = []
        fileData = f.readlines()
        
        for line in fileData[1:]:
            FileData = line.strip().split(',')
            namesList.append(FileData[0])
            inTimeList.append(FileData[1])
            outTimeList.append(FileData[2])

        if name not in namesList:
            now = datetime.now()
            dateTimeString = now.strftime('%H:%M:%S')
            f.writelines(f'{name},{dateTimeString},notAvailable\n')
            return 'In Time Noted'
        else:
            index = namesList.index(name)
            now = datetime.now()
            currentTime = now.strftime('%H:%M:%S')
            currentTimeC = datetime.strptime(currentTime, '%H:%M:%S')
            inTime = datetime.strptime(inTimeList[index], '%H:%M:%S')

            if outTimeList[index] == "notAvailable":
                timeDiff = (currentTimeC - inTime).total_seconds()
                if timeDiff >= 60:  # Ensure sufficient time difference before noting Out-time
                    changeOutTime = currentTime
                    fileData[index + 1] = f'{name},{inTimeList[index]},{changeOutTime}\n'
                    with open(currentFile, 'w') as file:
                        file.writelines(fileData)
                    return 'Out Time Noted'
                else:
                    return f'In time noted, {int(timeDiff)} seconds ago!'
            else:
                return "Attendance already posted!"

# Encoding images
def encode(images):
    encodedList = []
    for img in images:
        converted = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encoded = face_recognition.face_encodings(converted)
        if encoded:  # Only add encoding if the face was detected
            encodedList.append(encoded[0])
    return encodedList

listOfKnownEncodings = encode(images)
print("Encoding completed\n", len(listOfKnownEncodings), "faces in the list")

# Function to start attendance process
def start_attendance():
    cap = cv2.VideoCapture(0)
    recognized_attendees = set()

    while True:
        status, frame = cap.read()
        if not status:
            messagebox.showerror("Error", "Failed to access the camera.")
            break

        smallImg = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        currentFaceLoc = face_recognition.face_locations(smallImg)
        currentEncode = face_recognition.face_encodings(smallImg, currentFaceLoc)

        for faceEncode, faceLoc in zip(currentEncode, currentFaceLoc):
            matches = face_recognition.compare_faces(listOfKnownEncodings, faceEncode)
            faceDis = face_recognition.face_distance(listOfKnownEncodings, faceEncode)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = namesList[matchIndex]
                if name not in recognized_attendees:
                    recognized_attendees.add(name)
                    feedback = postAttendance(name)
                    attendees_tree.insert("", "end", values=(len(recognized_attendees), name))
                    total_label.config(text=f"Total Present: {len(recognized_attendees)}")

                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(frame, feedback, (10, 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)

        cv2.imshow("Camera Output - Press 'Q' to Close", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Button color cycle generator
button_colors = itertools.cycle(["#ffcccc", "#ccffcc", "#ccccff", "#ffffcc", "#ffccff", "#ccffff"])

def update_button_colors():
    new_color = next(button_colors)
    attendance_button.config(bg=new_color)
    root.after(2000, update_button_colors)

attendance_button = tk.Button(root, text="Start Attendance", command=start_attendance, bg="#ffcccc", fg="indigo", font=("Helvetica", 24, "bold"), width=25, bd=2,  highlightthickness=2,  highlightbackground="green", highlightcolor="red"  )
attendance_button.pack(pady=20)

columns = ("S.No", "Name")
attendees_tree = ttk.Treeview(root, columns=columns, show="headings", height=20)
attendees_tree.heading("S.No", text="S.No", anchor="center")
attendees_tree.heading("Name", text="Name", anchor="w")
attendees_tree.column("S.No", anchor="center", width=80)
attendees_tree.column("Name", anchor="w", width=600)
attendees_tree.pack(pady=10)

# Style the Treeview
style = ttk.Style()
style.configure("Treeview", 
    background="white",  
    fieldbackground="white",  
    foreground="black",  
    font=("Helvetica", 16), 
    rowheight=30, 
    borderwidth=1,  
    relief="solid",  
    highlightthickness=0,  
    lightcolor="black",  
    darkcolor="black",   
)

style.map("Treeview", 
    background=[("selected", "lightblue")],  
    foreground=[("selected", "black")]  
)

style.configure("Treeview.Heading", 
    font=("Helvetica", 16, "bold"), 
    foreground="black", 
    background="white",  
    relief="solid",  
    borderwidth=1
)

style.configure("Treeview", 
    lightcolor="black",  
    darkcolor="black",   
)

total_label = tk.Label(root, text="Total Present: 0", bg="#cce7ff", fg="blue", font=("Helvetica", 21, "bold"))
total_label.pack(pady=20)

close_button = tk.Button(root, text="Close", command=root.destroy, bg="#ffcccc", fg="green", font=("Helvetica", 20, "bold"), width=25)
close_button.pack(pady=20, side="bottom")

update_button_colors()

root.mainloop()
