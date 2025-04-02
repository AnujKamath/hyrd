### **Hyrd - Applicant Tracking System**  

## **🚀 Getting Started**  

### **1. Clone the Repository**  
```sh
git clone https://github.com/AnujKamath/Hyrd.git
cd Hyrd
```

### **2. Install Dependencies**  
```sh
npm install
cd client && npm install
cd ../server && npm install
```

### **3. Setup Environment Variables**  
Create a `.env` file in the `/server` directory and add:  
```env
PORT=5000
MONGO_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret
```

### **4. Run the Project**  

#### **Start Backend (Server)**
```sh
cd server
npm start
```

#### **Start Frontend (Client)**
```sh
cd client
npm start
```

### **5. Project Structure**
```
/Hyrd
├── /client  (React frontend)
├── /server  (Express backend)
├── package.json  (Monorepo setup)
├── README.md
```

### **6. Contributing**  
- **Branching**: `main` for production, `dev` for active development  
- **Commits**: Follow meaningful commit messages  
- **PRs**: Make PRs to `dev`, get approval before merging  
