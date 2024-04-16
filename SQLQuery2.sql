USE HMS;
CREATE TABLE Roles (
    RoleId INT PRIMARY KEY IDENTITY,
    RoleName NVARCHAR(50)
);

CREATE TABLE Users (
    UserId INT PRIMARY KEY IDENTITY,
    Name NVARCHAR(255),
    Email NVARCHAR(255) UNIQUE,
    Password NVARCHAR(255),
    IsActive BIT DEFAULT 1
);

CREATE TABLE UserRoles (
    UserId INT,
    RoleId INT,
    PRIMARY KEY (UserId, RoleId),
    FOREIGN KEY (UserId) REFERENCES Users(UserId),
    FOREIGN KEY (RoleId) REFERENCES Roles(RoleId)
);

CREATE TABLE Devices (
    DeviceId INT PRIMARY KEY IDENTITY,
    DeviceName NVARCHAR(255)
);

CREATE TABLE PatientDevices (
    PatientDeviceId INT PRIMARY KEY IDENTITY,
    PatientId INT,
    DeviceId INT,
    AssignedDate DATETIME,
    FOREIGN KEY (PatientId) REFERENCES Users(UserId),
    FOREIGN KEY (DeviceId) REFERENCES Devices(DeviceId)
);

CREATE TABLE Messages (
    MessageId INT PRIMARY KEY IDENTITY,
    SenderId INT,
    RecipientId INT,
    Content TEXT,
    Timestamp DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (SenderId) REFERENCES Users(UserId),
    FOREIGN KEY (RecipientId) REFERENCES Users(UserId)
);

CREATE TABLE Media (
    MediaId INT PRIMARY KEY IDENTITY,
    UserId INT,
    FilePath NVARCHAR(255),
    Timestamp DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (UserId) REFERENCES Users(UserId)
);

CREATE TABLE Appointments (
    AppointmentId INT PRIMARY KEY IDENTITY,
    PatientId INT,
    DoctorId INT,
    Date DATE,
    Time TIME,
    Status NVARCHAR(50) DEFAULT 'Scheduled',
    FOREIGN KEY (PatientId) REFERENCES Users(UserId),
    FOREIGN KEY (DoctorId) REFERENCES Users(UserId)
);

CREATE TABLE Alerts (
    AlertId INT PRIMARY KEY IDENTITY,
    PatientId INT,
    MeasurementType NVARCHAR(50),
    ThresholdValue NVARCHAR(50),
    AlertMessage TEXT,
    FOREIGN KEY (PatientId) REFERENCES Users(UserId)
);

CREATE TABLE Measurements (
    MeasurementId INT PRIMARY KEY IDENTITY,
    UserId INT,
    Type NVARCHAR(50),
    Value NVARCHAR(50),
    Timestamp DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (UserId) REFERENCES Users(UserId)
);

SELECT*FROM Users

INSERT INTO Roles (RoleName) VALUES ('Patient'), ('Nurse'), ('Doctor'), ('Admin'), ('Family Member');
-- Insert a sample user
INSERT INTO Users (Name, Email, Password, IsActive) VALUES ('admin', 'admin@gmail.com', 'admin', 1);

-- Assign a role to the user (Assuming RoleId 1 is 'Patient')
INSERT INTO UserRoles (UserId, RoleId) VALUES (5, 4);

INSERT INTO Devices (DeviceName) VALUES 
('Heart Rate Monitor'),
('Thermometer'),
('Glucometer'),
('Oxygen Saturation Monitor'),
('ECG Machine'),
('EEG Machine'),
('Ventilator'),
('MRI Scanner'),
('CT Scanner');

INSERT INTO PatientDevices (PatientId, DeviceId, AssignedDate) VALUES 
(2, 1, '2024-04-15'),
(2, 2, '2024-04-14'),
(2, 3, '2024-04-13'),
(4, 6, '2024-04-12'),
(4, 8, '2024-04-11');

INSERT INTO Messages (SenderId, RecipientId, Content) VALUES 
(2, 1, 'Hi, how are you?'),
(2, 1, 'Reminder for your appointment tomorrow.'),
(2, 1, 'Please update your medical history.'),
(2, 1, 'Your prescription is ready for pickup.'),
(2, 1, 'We need to schedule a follow-up visit.'),
(1, 2, 'Feeling much better, thanks!'),
(1, 2, 'Got it, thank you.'),
(1, 2, 'Will do, thanks for the reminder.'),
(1, 2, 'I''ll come by in the afternoon.'),
(1, 2, 'Please let me know the available times.');

INSERT INTO Appointments (PatientId, DoctorId, Date, Time) VALUES 
(2, 3, '2024-05-01', '10:00'),
(2, 3, '2024-05-02', '11:00'),
(4, 3, '2024-05-03', '09:00'),
(4, 3, '2024-05-04', '14:00'),
(4, 3, '2024-05-05', '15:30');

INSERT INTO Alerts (PatientId, MeasurementType, ThresholdValue, AlertMessage) VALUES 
(2, 'Heart Rate', '100', 'High heart rate detected.'),
(2, 'Blood Pressure', '140/90', 'High blood pressure detected.'),
(2, 'Temperature', '38', 'High temperature detected.'),
(4, 'Blood Sugar', '180', 'High blood sugar detected.'),
(4, 'Oxygen Saturation', '92', 'Low oxygen saturation detected.');

INSERT INTO Measurements (UserId, Type, Value) VALUES 
(2, 'Heart Rate', '75'),
(2, 'Blood Pressure', '120/80'),
(2, 'Temperature', '36.6'),
(2, 'Blood Sugar', '90'),
(2, 'Oxygen Saturation', '98'),
(4, 'Heart Rate', '80'),
(4, 'Blood Pressure', '125/85'),
(4, 'Temperature', '36.7'),
(4, 'Blood Sugar', '95'),
(4, 'Oxygen Saturation', '99');

SELECT*FROM Media