let token = localStorage.getItem('token');

function createStars() {
    const container = document.querySelector('.stars-container');
    for (let i = 0; i < 100; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        star.style.width = Math.random() * 3 + 'px';
        star.style.height = star.style.width;
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.animationDelay = Math.random() * 2 + 's';
        container.appendChild(star);
    }
}

function toggleForm(formType) {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    
    if (formType === 'signup') {
        loginForm.classList.add('hidden');
        signupForm.classList.remove('hidden');
    } else {
        signupForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
    }
}

function toggleUserDropdown() {
    const dropdown = document.getElementById('userDropdown');
    dropdown.classList.toggle('show');
}

async function handleSignup(event) {
    event.preventDefault();
    const username = document.getElementById('signupUsername').value.trim();
    const password = document.getElementById('signupPassword').value;

    if (!username || !password) {
        alert('Please enter both username and password');
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        
        if (response.ok) {
            alert('Registration successful! Please login.');
            toggleForm('login');
            document.getElementById('loginUsername').value = username;
        } else {
            throw new Error(data.message || 'Registration failed');
        }
    } catch (error) {
        console.error('Registration error:', error);
        alert(error.message || 'Registration failed. Please try again.');
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!username || !password) {
        alert('Please enter both username and password');
        return;
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        
        if (response.ok) {
            token = data.token;
            localStorage.setItem('token', token);
            localStorage.setItem('username', data.username);
            localStorage.setItem('calculations', data.calculations);
            localStorage.setItem('lastLogin', data.last_login);
            
            updateUserProfile(data);
            
            document.getElementById('authContainer').classList.add('hidden');
            document.getElementById('mainContainer').classList.remove('hidden');
            document.getElementById('userProfile').classList.remove('hidden');
        } else {
            throw new Error(data.message || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        alert(error.message || 'Login failed. Please try again.');
    }
}

function updateUserProfile(userData) {
    document.getElementById('userInitial').textContent = userData.username[0].toUpperCase();
    document.getElementById('profileUsername').textContent = userData.username;
    document.getElementById('lastLogin').textContent = `Last login: ${new Date(userData.last_login).toLocaleString()}`;
    document.getElementById('totalCalculations').textContent = `Calculations: ${userData.calculations}`;
}

function logout() {
    token = null;
    localStorage.clear();
    document.getElementById('mainContainer').classList.add('hidden');
    document.getElementById('authContainer').classList.remove('hidden');
    document.getElementById('userProfile').classList.add('hidden');
    document.getElementById('userDropdown').classList.remove('show');
}

async function calculateMoonPhase() {
    const dateInput = document.getElementById('dateInput');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    const error = document.getElementById('error');

    loading.classList.remove('hidden');
    result.classList.add('hidden');
    error.classList.add('hidden');

    try {
        const response = await fetch('http://127.0.0.1:5000/get-moon-phase', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ date: dateInput.value })
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('moonImage').src = `data:image/png;base64,${data.moon_image}`;
            document.getElementById('phaseName').textContent = data.phase_name;
            document.getElementById('illumination').textContent = 
                `Illumination: ${data.illumination.toFixed(2)}%`;
            
            document.getElementById('totalCalculations').textContent = 
                `Calculations: ${data.calculations}`;
            
            result.classList.remove('hidden');
        } else {
            throw new Error(data.message || 'Failed to calculate moon phase');
        }
    } catch (error) {
        console.error('Calculation error:', error);
        document.getElementById('error').textContent = error.message;
        document.getElementById('error').classList.remove('hidden');
        
        if (error.message.includes('Token')) {
            logout();
        }
    } finally {
        loading.classList.add('hidden');
    }
}

document.addEventListener('click', (event) => {
    const dropdown = document.getElementById('userDropdown');
    const avatar = document.getElementById('userProfile');
    if (!avatar.contains(event.target) && dropdown.classList.contains('show')) {
        dropdown.classList.remove('show');
    }
});

document.addEventListener('DOMContentLoaded', () => {
    createStars();
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('dateInput').value = today;
    
    const savedToken = localStorage.getItem('token');
    const savedUsername = localStorage.getItem('username');
    
    if (savedToken && savedUsername) {
        token = savedToken;
        updateUserProfile({
            username: savedUsername,
            calculations: localStorage.getItem('calculations') || 0,
            last_login: localStorage.getItem('lastLogin')
        });
        document.getElementById('authContainer').classList.add('hidden');
        document.getElementById('mainContainer').classList.remove('hidden');
        document.getElementById('userProfile').classList.remove('hidden');
    }
});