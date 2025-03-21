const express = require('express');
const path = require('path');
const fs = require('fs');
const multer  = require('multer');
const app = express();
const PORT = process.env.PORT || 3000;

// Configure Multer storage for file uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'static/images/'); // Ensure this folder exists
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + '-' + file.originalname);
  }
});
const upload = multer({ storage: storage });

// Middleware to parse form data and JSON
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
// Serve static files
app.use('/static', express.static(path.join(__dirname, 'static')));

// JSON file paths
const usersFile = path.join(__dirname, 'data', 'users.json');
const candidatesFile = path.join(__dirname, 'data', 'candidates.json');

// Utility functions for JSON file operations
const readJSON = (filePath) => {
  try {
    return JSON.parse(fs.readFileSync(filePath));
  } catch (err) {
    return [];
  }
};

const writeJSON = (filePath, data) => {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
};

// --- Routes --- //

// Welcome page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'welcome.html'));
});

// Voter login pages
app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'login.html'));
});

// Voter registration page (GET)
app.get('/register', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'register.html'));
});

app.get('/api/candidates', (req, res) => {
  const candidates = readJSON(path.join(__dirname, 'data', 'candidates.json'));
  res.json(candidates);
});

// Voter registration (POST)
app.post('/register', (req, res) => {
  const { firstName, lastName, mobile, email, username, password, aadhaar } = req.body;
  let users = readJSON(usersFile);
  if (users.find(u => u.username === username || u.email === email)) {
    return res.send("User already exists. Please choose a different username or email.");
  }
  const newUser = { 
    firstName, 
    lastName, 
    mobile, 
    email, 
    username, 
    password,  // In production, hash the password!
    aadhaar,
    hasVoted: false
  };
  users.push(newUser);
  writeJSON(usersFile, users);
  res.redirect('/login');
});

// Voter login (POST)
app.post('/login', (req, res) => {
  const { usernameEmail, password } = req.body;
  let users = readJSON(usersFile);
  const user = users.find(u =>
    (u.username === usernameEmail || u.email === usernameEmail) && u.password === password
  );
  if (user) {
    // Redirect to voter dashboard with username in query string
    res.redirect(`/voter_dashboard?username=${encodeURIComponent(user.username)}`);
  } else {
    res.send("Invalid credentials. Please try again.");
  }
});

// API endpoint to get voter data by username (used by dashboard)
app.get('/api/voter', (req, res) => {
  const username = req.query.username;
  if (!username) return res.status(400).json({ error: "Missing username" });
  let users = readJSON(usersFile);
  const user = users.find(u => u.username === username);
  if (user) {
    res.json(user);
  } else {
    res.status(404).json({ error: "User not found" });
  }
});

// Voter dashboard page
app.get('/voter_dashboard', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'voter_dashboard.html'));
});

// Vote page
app.get('/vote', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'vote.html'));
});


// Define the path for votes.json
const votesFile = path.join(__dirname, 'data', 'votes.json');

app.post('/vote', (req, res) => {
  const { username, candidateId } = req.body;
  
  // Load users, votes, and candidates from their JSON files
  let users = readJSON(usersFile);
  let votes = readJSON(votesFile);
  let candidates = readJSON(candidatesFile);
  
  // Find the voter
  let user = users.find(u => u.username === username);
  if (!user) {
    return res.status(400).json({ message: "User not found!" });
  }
  
  // Check if the user has already voted
  if (user.hasVoted) {
    return res.status(400).json({ message: "You have already voted!" });
  }
  
  // Record the vote in votes.json
  const voteRecord = {
    username,
    candidateId,
    timestamp: new Date().toISOString()
  };
  votes.push(voteRecord);
  writeJSON(votesFile, votes);
  
  // Update user's status to indicate they have voted
  user.hasVoted = true;
  writeJSON(usersFile, users);
  
  // Optionally, update candidate vote count
  let candidate = candidates.find(c => c.id == candidateId);
  if (candidate) {
    candidate.votes = candidate.votes ? candidate.votes + 1 : 1;
    writeJSON(candidatesFile, candidates);
  }
  
  res.json({ message: "Vote recorded successfully!" });
});

app.get('/instructions', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'instructions.html'));
});

// Candidate registration page (GET)
app.get('/candidate_register', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'candidate_register.html'));
});

// Candidate registration (POST) with file upload for symbol image
app.post('/candidate_register', upload.single('symbolFile'), (req, res) => {
  const { name, party, classification, experience } = req.body;
  const symbol = req.file.filename; // Uploaded file name
  let candidates = readJSON(candidatesFile);
  const newCandidate = {
    id: candidates.length + 1,
    name,
    party,
    classification,
    experience,
    symbol
  };
  candidates.push(newCandidate);
  writeJSON(candidatesFile, candidates);
  res.redirect('/nominee');
});

// Nominee page: Display all candidates with extra details
app.get('/nominee', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'nominee.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
