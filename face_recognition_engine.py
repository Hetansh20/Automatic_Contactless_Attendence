import cv2
import numpy as np
import os
from pathlib import Path
from database import Database
import time
from datetime import datetime
import json

class FaceRecognitionEngine:
    """Face recognition engine using LBPH method - same as original project"""
    
    def __init__(self):
        self.db = Database()
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.training_data_path = "TrainingImage"
        self.model_path = "TrainingImageLabel" + os.sep + "Trainner.yml"
        self.label_mapping_path = "TrainingImageLabel" + os.sep + "label_mapping.json"
        self.confidence_threshold = 40  # LBPH: lower is better (0-40 is good match)
        self.label_mapping = {}  # Maps label index to student database ID
        
        # Create directories if they don't exist
        os.makedirs(self.training_data_path, exist_ok=True)
        os.makedirs("TrainingImageLabel", exist_ok=True)
        
        # Load trained model if exists
        if os.path.exists(self.model_path):
            try:
                self.recognizer.read(self.model_path)
                print("[v0] Model loaded successfully")
            except Exception as e:
                print(f"[v0] Error loading model: {e}")
        
        # Load label mapping if exists
        if os.path.exists(self.label_mapping_path):
            try:
                with open(self.label_mapping_path, 'r') as f:
                    self.label_mapping = json.load(f)
                print(f"[v0] Label mapping loaded: {self.label_mapping}")
            except Exception as e:
                print(f"[v0] Error loading label mapping: {e}")
    
    def get_images_and_labels(self, path):
        """Get images and labels from training directory"""
        faces = []
        Ids = []
        label_to_student = {}  # Maps label index to student database ID
        current_label = 0
        
        if not os.path.exists(path):
            print(f"[v0] Training path does not exist: {path}")
            return faces, Ids, label_to_student
        
        for student_dir in sorted(os.listdir(path)):
            student_path = os.path.join(path, student_dir)
            if not os.path.isdir(student_path):
                continue
            
            try:
                # Extract student ID from directory name: Name.StudentID
                parts = student_dir.rsplit('.', 1)  # Split from right to handle names with dots
                if len(parts) != 2:
                    print(f"[v0] Invalid directory format: {student_dir}, expected Name.StudentID")
                    continue
                
                try:
                    student_id = int(parts[1])
                except ValueError:
                    print(f"[v0] Invalid student ID in directory: {student_dir}")
                    continue
                
                # Get student from database to verify they exist
                student = self.db.get_student_by_id(student_id)
                if not student:
                    print(f"[v0] Student ID {student_id} not found in database, skipping")
                    continue
                
                label_to_student[current_label] = student_id
                
                # Read all images in this student's directory
                image_count = 0
                for image_file in sorted(os.listdir(student_path)):
                    if not image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        continue
                    
                    image_path = os.path.join(student_path, image_file)
                    try:
                        pilImage = cv2.imread(image_path)
                        if pilImage is None:
                            print(f"[v0] Could not read image: {image_path}")
                            continue
                        
                        gray = cv2.cvtColor(pilImage, cv2.COLOR_BGR2GRAY)
                        faces.append(gray)
                        Ids.append(current_label)
                        image_count += 1
                    except Exception as e:
                        print(f"[v0] Error processing {image_path}: {str(e)}")
                        continue
                
                print(f"[v0] Loaded {image_count} images for student {student_id} ({student[2]})")
                current_label += 1
            
            except Exception as e:
                print(f"[v0] Error processing directory {student_dir}: {str(e)}")
                continue
        
        print(f"[v0] Total faces loaded: {len(faces)}, Label mapping: {label_to_student}")
        return faces, Ids, label_to_student
    
    def capture_student_faces(self, student_id, student_name, num_images=30):
        """Capture multiple face images for a student"""
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            
            if not cap.isOpened():
                return False, "Cannot access webcam"
            
            cap.set(3, 640)  # set video width
            cap.set(4, 480)  # set video height
            
            count = 0
            
            student_dir = os.path.join(self.training_data_path, f"{student_name}.{student_id}")
            os.makedirs(student_dir, exist_ok=True)
            
            print(f"[v0] Capturing {num_images} images for {student_name} (ID: {student_id})...")
            
            while count < num_images:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)
                
                for (x, y, w, h) in faces:
                    count += 1
                    
                    # Save the captured face with naming convention: Name.StudentID.ImageNumber.jpg
                    face_roi = frame[y:y+h, x:x+w]
                    image_path = os.path.join(student_dir, f"{student_name}.{student_id}.{count}.jpg")
                    cv2.imwrite(image_path, face_roi)
                    
                    # Draw rectangle on frame
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cv2.putText(frame, f"Captured: {count}/{num_images}", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow('Capturing Faces', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            if count >= num_images:
                return True, f"Successfully captured {count} images for {student_name}"
            else:
                return False, f"Only captured {count} images out of {num_images}"
        
        except Exception as e:
            return False, f"Error capturing faces: {str(e)}"
    
    def train_model(self):
        """Train the LBPH face recognition model"""
        try:
            faces, Ids, label_to_student = self.get_images_and_labels(self.training_data_path)
            
            if len(faces) == 0:
                return False, "No training images found. Please capture student faces first."
            
            print(f"[v0] Training model with {len(faces)} images...")
            
            self.label_mapping = {str(k): v for k, v in label_to_student.items()}
            with open(self.label_mapping_path, "w") as f:
                json.dump(self.label_mapping, f, indent=2)
            
            print(f"[v0] Label mapping saved: {self.label_mapping}")
            
            self.recognizer.train(faces, np.array(Ids))
            self.recognizer.save(self.model_path)
            
            print(f"[v0] Model trained successfully and saved to {self.model_path}")
            return True, f"Model trained successfully with {len(faces)} images from {len(label_to_student)} students"
        
        except Exception as e:
            print(f"[v0] Error training model: {str(e)}")
            return False, f"Error training model: {str(e)}"
    
    def recognize_faces_realtime(self, timetable_id, session_callback=None):
        """Recognize faces in real-time and mark attendance"""
        try:
            if not os.path.exists(self.model_path):
                return False, "Model not trained. Please train the model first."
            
            if not self.label_mapping:
                print("[v0] Loading label mapping...")
                if os.path.exists(self.label_mapping_path):
                    with open(self.label_mapping_path, 'r') as f:
                        self.label_mapping = json.load(f)
                else:
                    return False, "Label mapping not found. Please train the model first."
            
            print(f"[v0] Label mapping available: {self.label_mapping}")
            
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            
            if not cap.isOpened():
                return False, "Cannot access webcam"
            
            cap.set(3, 640)  # set video width
            cap.set(4, 480)  # set video height
            
            # Define min window size to be recognized as a face
            minW = 0.1 * cap.get(3)
            minH = 0.1 * cap.get(4)
            
            recognized_students = {}
            frame_count = 0
            
            print("[v0] Starting face recognition...")
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                frame_count += 1
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, 1.2, 5, 
                    minSize=(int(minW), int(minH)), 
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (10, 159, 255), 2)
                    
                    label, conf = self.recognizer.predict(gray[y:y+h, x:x+w])
                    confstr = "  {0}%".format(round(100 - conf))
                    
                    print(f"[v0] Frame {frame_count}: Detected label={label}, conf={conf}, threshold={self.confidence_threshold}")
                    
                    if str(label) in self.label_mapping:
                        student_id = int(self.label_mapping[str(label)])
                        
                        if conf < self.confidence_threshold:
                            student = self.db.get_student_by_id(student_id)
                            if student:
                                student_name = student[2]
                                
                                # Mark attendance only once per session
                                if student_id not in recognized_students:
                                    ts = time.time()
                                    timeStamp = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                    self.db.mark_attendance(student_id, timetable_id, conf)
                                    recognized_students[student_id] = (student_name, timeStamp)
                                    
                                    print(f"[v0] Marked attendance for {student_name} (ID: {student_id})")
                                    
                                    if session_callback:
                                        session_callback(f"Recognized: {student_name}", 100 - conf)
                                
                                tt = f"{student_id}-{student_name} [Pass]"
                                cv2.putText(frame, str(tt), (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                                cv2.putText(frame, str(confstr), (x+5, y+h-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
                            else:
                                print(f"[v0] Student ID {student_id} not found in database")
                                tt = "Unknown"
                                cv2.putText(frame, str(tt), (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                                cv2.putText(frame, str(confstr), (x+5, y+h-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
                        else:
                            print(f"[v0] Confidence {conf} exceeds threshold {self.confidence_threshold}")
                            tt = "Unknown"
                            cv2.putText(frame, str(tt), (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                            if conf < 50:
                                cv2.putText(frame, str(confstr), (x+5, y+h-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1)
                            else:
                                cv2.putText(frame, str(confstr), (x+5, y+h-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
                    else:
                        print(f"[v0] Label {label} not in mapping. Available labels: {list(self.label_mapping.keys())}")
                        tt = "Unknown"
                        cv2.putText(frame, str(tt), (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        cv2.putText(frame, str(confstr), (x+5, y+h-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
                
                cv2.imshow('Attendance', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            return True, f"Recognition complete. Marked {len(recognized_students)} students"
        
        except Exception as e:
            print(f"[v0] Error during recognition: {str(e)}")
            return False, f"Error during recognition: {str(e)}"
    
    def check_camera(self):
        """Check if camera is working"""
        try:
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            
            if not cap.isOpened():
                return False, "Camera not accessible"
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                return True, "Camera is working properly"
            else:
                return False, "Camera is not responding"
        
        except Exception as e:
            return False, f"Error checking camera: {str(e)}"

# Initialize face recognition engine
face_recognition_engine = FaceRecognitionEngine()
