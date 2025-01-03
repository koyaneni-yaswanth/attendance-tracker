require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");
const bodyParser = require("body-parser");

const app = express();
app.use(bodyParser.json());

// Connect to MongoDB
mongoose.connect("mongodb://127.0.0.1:27017/attendance", {
    useNewUrlParser: true,
    useUnifiedTopology: true,
})
    .then(() => console.log("Connected to MongoDB"))
    .catch(err => console.error("Database connection error:", err));

// Define the Attendance model
const Attendance = require("./models/attendance");

// Create the API route
app.post("/api/attendance", async (req, res) => {
    try {
        const attendance = new Attendance(req.body);
        await attendance.save();
        res.status(201).json({ message: "Attendance saved successfully!" });
    } catch (err) {
        res.status(400).json({ error: err.message });
    }
});

// Start the server
const PORT = 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
