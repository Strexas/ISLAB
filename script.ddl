--@(#) script.ddl

CREATE TABLE OrderStatus
(
	id_OrderStatus int NOT NULL,
	"name" varchar (9) NOT NULL,
	PRIMARY KEY(id_OrderStatus)
);
INSERT INTO OrderStatus(id_OrderStatus, "name") VALUES(1, 'Sent');
INSERT INTO OrderStatus(id_OrderStatus, "name") VALUES(2, 'Shipped');
INSERT INTO OrderStatus(id_OrderStatus, "name") VALUES(3, 'Completed');
INSERT INTO OrderStatus(id_OrderStatus, "name") VALUES(4, 'Failed');

CREATE TABLE PaymentStatus
(
	id_PaymentStatus int NOT NULL,
	"name" varchar (10) NOT NULL,
	PRIMARY KEY(id_PaymentStatus)
);
INSERT INTO PaymentStatus(id_PaymentStatus, "name") VALUES(1, 'Pending');
INSERT INTO PaymentStatus(id_PaymentStatus, "name") VALUES(2, 'Authorized');
INSERT INTO PaymentStatus(id_PaymentStatus, "name") VALUES(3, 'Success');
INSERT INTO PaymentStatus(id_PaymentStatus, "name") VALUES(4, 'Failed');

CREATE TABLE ReservationStatus
(
	id_ReservationStatus int NOT NULL,
	"name" varchar (9) NOT NULL,
	PRIMARY KEY(id_ReservationStatus)
);
INSERT INTO ReservationStatus(id_ReservationStatus, "name") VALUES(1, 'Pending');
INSERT INTO ReservationStatus(id_ReservationStatus, "name") VALUES(2, 'Active');
INSERT INTO ReservationStatus(id_ReservationStatus, "name") VALUES(3, 'Completed');
INSERT INTO ReservationStatus(id_ReservationStatus, "name") VALUES(4, 'Canceled');

CREATE TABLE UserRoles
(
	id_UserRoles int NOT NULL,
	"name" varchar (15) NOT NULL,
	PRIMARY KEY(id_UserRoles)
);

INSERT INTO UserRoles(id_UserRoles, "name") VALUES(1, 'Customer');
INSERT INTO UserRoles(id_UserRoles, "name") VALUES(2, 'Office Employee');
INSERT INTO UserRoles(id_UserRoles, "name") VALUES(3, 'Accountant');

CREATE TABLE VehicleStatus
(
	id_VehicleStatus int NOT NULL,
	"name" varchar (11) NOT NULL,
	PRIMARY KEY(id_VehicleStatus)
);
INSERT INTO VehicleStatus(id_VehicleStatus, "name") VALUES(1, 'Available');
INSERT INTO VehicleStatus(id_VehicleStatus, "name") VALUES(2, 'Rented');
INSERT INTO VehicleStatus(id_VehicleStatus, "name") VALUES(3, 'Maintenance');
INSERT INTO VehicleStatus(id_VehicleStatus, "name") VALUES(4, 'Inactive');

CREATE TABLE "User"
(
	"Name" varchar (255) NOT NULL,
	"Password" varchar (255) NOT NULL,
	"Surname" varchar NOT NULL,
	Email varchar (255) NOT NULL,
	Birthdate date NOT NULL,
	AccountStatus bool NOT NULL,
	DriverLicenceNumber varchar (255) NOT NULL,
	LicenceExpirationDate date NOT NULL,
	WalletBalance float NOT NULL,
	"Role" int NOT NULL,
	id_User int NOT NULL,
	PRIMARY KEY(id_User),
	FOREIGN KEY("Role") REFERENCES UserRoles (id_UserRoles)
);

CREATE TABLE Vehicle
(
	VehicleLicencePlate varchar (255) NOT NULL,
	Manufactorer varchar (255) NOT NULL,
	Model varchar (255) NOT NULL,
	"Year" date NOT NULL,
	DailyRate float NOT NULL,
	Transmission varchar (255) NOT NULL,
	Seat int NOT NULL,
	FuelType varchar (255) NOT NULL,
	Status int NOT NULL,
	id_Vehicle int NOT NULL,
	PRIMARY KEY(id_Vehicle),
	FOREIGN KEY(Status) REFERENCES VehicleStatus (id_VehicleStatus)
);

CREATE TABLE CreditCard
(
	CardholderName varchar (255) NOT NULL,
	CardNumber varchar (255) NOT NULL,
	ExpireDate date NOT NULL,
	BillingAddress varchar (255) NOT NULL,
	Added date NOT NULL,
	id_CreditCard int NOT NULL,
	fk_Userid_User int NOT NULL,
	PRIMARY KEY(id_CreditCard),
	CONSTRAINT Have FOREIGN KEY(fk_Userid_User) REFERENCES "User" (id_User)
);

CREATE TABLE Maintenance
(
	MaintenanceDescription varchar (255) NOT NULL,
	StartDate date NOT NULL,
	EndDate date NOT NULL,
	ReportedProblem date NOT NULL,
	id_Maintenance int NOT NULL,
	fk_Vehicleid_Vehicle int NOT NULL,
	PRIMARY KEY(id_Maintenance),
	CONSTRAINT Undergoes FOREIGN KEY(fk_Vehicleid_Vehicle) REFERENCES Vehicle (id_Vehicle)
);

CREATE TABLE RentPrice
(
	"Price" float NOT NULL,
	"Date" date NOT NULL,
	id_RentPrice int NOT NULL,
	fk_Vehicleid_Vehicle int NOT NULL,
	PRIMARY KEY(id_RentPrice),
	CONSTRAINT Has FOREIGN KEY(fk_Vehicleid_Vehicle) REFERENCES Vehicle (id_Vehicle)
);

CREATE TABLE Reservation
(
	TotalAmount float NOT NULL,
	PickupDate date NOT NULL,
	DropoffDate date NOT NULL,
	Status int NOT NULL,
	id_Reservation int NOT NULL,
	fk_Userid_User int NOT NULL,
	fk_Vehicleid_Vehicle int NOT NULL,
	PRIMARY KEY(id_Reservation),
	FOREIGN KEY(Status) REFERENCES ReservationStatus (id_ReservationStatus),
	CONSTRAINT Submits FOREIGN KEY(fk_Userid_User) REFERENCES "User" (id_User),
	CONSTRAINT PartOf FOREIGN KEY(fk_Vehicleid_Vehicle) REFERENCES Vehicle (id_Vehicle)
);

CREATE TABLE ReviewCache
(
	AverageRating float NOT NULL,
	ReviewCount int NOT NULL,
	LastUpdated date NOT NULL,
	"Source" varchar (255) NOT NULL,
	id_ReviewCache int NOT NULL,
	fk_Vehicleid_Vehicle int NOT NULL,
	PRIMARY KEY(id_ReviewCache),
	UNIQUE(fk_Vehicleid_Vehicle),
	CONSTRAINT Has FOREIGN KEY(fk_Vehicleid_Vehicle) REFERENCES Vehicle (id_Vehicle)
);

CREATE TABLE InsurancePolicy
(
	Provider varchar (255) NOT NULL,
	PaymentAmount float NOT NULL,
	StartDate date NOT NULL,
	EndDate date NOT NULL,
	PolicyNumber varchar (255) NOT NULL,
	id_InsurancePolicy int NOT NULL,
	fk_Reservationid_Reservation int NOT NULL,
	PRIMARY KEY(id_InsurancePolicy),
	UNIQUE(fk_Reservationid_Reservation),
	CONSTRAINT Has FOREIGN KEY(fk_Reservationid_Reservation) REFERENCES Reservation (id_Reservation)
);

CREATE TABLE "Order"
(
	"Date" date NOT NULL,
	Status int NOT NULL,
	id_Order int NOT NULL,
	fk_Maintenanceid_Maintenance int NOT NULL,
	PRIMARY KEY(id_Order),
	FOREIGN KEY(Status) REFERENCES OrderStatus (id_OrderStatus),
	CONSTRAINT Requests FOREIGN KEY(fk_Maintenanceid_Maintenance) REFERENCES Maintenance (id_Maintenance)
);

CREATE TABLE Payment
(
	"Date" date NOT NULL,
	Amount float NOT NULL,
	Description varchar (255) NOT NULL,
	ReservationID varchar (255) NOT NULL,
	PaymentMethod varchar (255) NOT NULL,
	Status int NOT NULL,
	id_Payment int NOT NULL,
	fk_Reservationid_Reservation int NOT NULL,
	fk_Userid_User int NOT NULL,
	PRIMARY KEY(id_Payment),
	FOREIGN KEY(Status) REFERENCES PaymentStatus (id_PaymentStatus),
	FOREIGN KEY(fk_Reservationid_Reservation) REFERENCES Reservation (id_Reservation),
	CONSTRAINT Makes FOREIGN KEY(fk_Userid_User) REFERENCES "User" (id_User)
);

CREATE TABLE Component
(
	"Name" varchar (255) NOT NULL,
	Price float NOT NULL,
	Quantity int NOT NULL,
	id_Component int NOT NULL,
	fk_Orderid_Order int NOT NULL,
	PRIMARY KEY(id_Component),
	CONSTRAINT "Contains" FOREIGN KEY(fk_Orderid_Order) REFERENCES "Order" (id_Order)
);

