import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import data_pb2
import by_pb2
import requests
import jwt
from flask import Flask, request, jsonify, render_template_string
import time
import random

app = Flask(__name__)

# المفاتيح للتشفير
key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

# قالب HTML مع CSS و JavaScript مدمج
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>L7AJ - Game Tools</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Exo+2:wght@300;400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Exo 2', sans-serif;
        }
        
        body {
            background: linear-gradient(-45deg, #0a0a2a, #000033, #0d0d21, #00004d);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            color: #fff;
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }
        
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .matrix-rain {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -2;
            opacity: 0.2;
        }
        
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
        }
        
        .particle {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            animation: float 15s infinite linear;
        }
        
        @keyframes float {
            0% { transform: translateY(0) translateX(0); opacity: 1; }
            100% { transform: translateY(-100vh) translateX(100vw); opacity: 0; }
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
            z-index: 1;
        }
        
        header {
            text-align: center;
            padding: 40px 0;
            margin-bottom: 30px;
            position: relative;
        }
        
        header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 5px;
            background: linear-gradient(90deg, #ff5722, #2196F3, #9C27B0);
            border-radius: 5px;
        }
        
        .logo {
            font-family: 'Orbitron', sans-serif;
            font-size: 3.5rem;
            margin-bottom: 15px;
            text-shadow: 0 0 20px rgba(0, 247, 255, 0.7);
            background: linear-gradient(90deg, #4FC3F7, #E91E63, #FFEB3B, #9C27B0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: hue-rotate 5s infinite alternate;
            letter-spacing: 2px;
        }
        
        @keyframes hue-rotate {
            0% { filter: hue-rotate(0deg); }
            100% { filter: hue-rotate(360deg); }
        }
        
        .description {
            font-size: 1.3rem;
            opacity: 0.9;
            max-width: 800px;
            margin: 0 auto;
            font-weight: 300;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 50px;
        }
        
        .feature-card {
            background: rgba(13, 19, 33, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
            cursor: pointer;
            text-align: center;
            box-shadow: 0 0 40px rgba(0, 0, 0, 0.7);
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            border-color: rgba(255, 255, 255, 0.2);
            background: rgba(13, 19, 33, 0.9);
            box-shadow: 0 0 50px rgba(33, 150, 243, 0.3);
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
        }
        
        .feature-title {
            font-size: 1.5rem;
            margin-bottom: 15px;
            background: linear-gradient(90deg, #ff0000, #ff8000, #ffff00, #80ff00, #00ff00, #00ff80, #00ffff, #0080ff, #0000ff, #8000ff, #ff00ff, #ff0080, #ff0000);
            background-size: 1200% 100%;
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            animation: rgbFlow 12s linear infinite;
        }
        
        @keyframes rgbFlow {
            0% { background-position: 0% 50%; }
            100% { background-position: 100% 50%; }
        }
        
        .feature-description {
            color: #aaa;
            line-height: 1.6;
        }
        
        .section {
            background: rgba(13, 19, 33, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 40px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            display: none;
            box-shadow: 0 0 40px rgba(0, 0, 0, 0.7);
        }
        
        .section.active {
            display: block;
            animation: fadeIn 0.5s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        h2 {
            margin-bottom: 20px;
            color: #4FC3F7;
            text-shadow: 0 0 10px rgba(79, 195, 247, 0.7);
            font-size: 2rem;
            font-family: 'Orbitron', sans-serif;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 12px;
            font-size: 1.1rem;
            color: #4FC3F7;
        }
        
        input, textarea {
            width: 100%;
            padding: 18px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            background: rgba(0, 0, 0, 0.4);
            color: #fff;
            font-size: 1rem;
            resize: vertical;
            transition: all 0.3s ease;
            font-family: 'Courier New', monospace;
        }
        
        input:focus, textarea:focus {
            outline: none;
            border-color: #2196F3;
            box-shadow: 0 0 20px rgba(33, 150, 243, 0.5);
        }
        
        button {
            padding: 16px 35px;
            background: linear-gradient(45deg, #2196F3, #9C27B0);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            display: inline-block;
            position: relative;
            overflow: hidden;
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 1px;
            margin-right: 15px;
        }
        
        button:hover {
            transform: translateY(-3px);
            box-shadow: 0 7px 20px rgba(33, 150, 243, 0.7);
        }
        
        .result {
            margin-top: 35px;
            padding: 25px;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
            position: relative;
        }
        
        .result:hover {
            box-shadow: 0 0 20px rgba(33, 150, 243, 0.3);
        }
        
        .success {
            color: #00d26a;
            text-align: center;
            font-weight: bold;
            margin-bottom: 15px;
        }
        
        .error {
            color: #ff0055;
            text-align: center;
            font-weight: bold;
            margin-bottom: 15px;
        }
        
        .items-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .item-input {
            margin-bottom: 10px;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        
        .loading-spinner {
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top: 3px solid #4361ee;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .copy-btn {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: #fff;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            margin-left: 15px;
            transition: all 0.3s ease;
            margin-top: 15px;
        }
        
        .copy-btn:hover {
            background: rgba(33, 150, 243, 0.5);
        }
        
        /* الإشعارات */
        .notifications {
            position: fixed;
            bottom: 20px;
            left: 20px;
            z-index: 1000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .notification {
            background: rgba(10, 10, 26, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text);
            padding: 15px 20px;
            border-radius: 10px;
            animation: slideIn 0.3s ease, fadeOut 0.5s ease 2.5s forwards;
            max-width: 300px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .notification.success {
            border-left: 4px solid #00d26a;
        }
        
        .notification.error {
            border-left: 4px solid #ff0055;
        }
        
        .notification.info {
            border-left: 4px solid #4361ee;
        }
        
        @keyframes slideIn {
            from { transform: translateX(-100px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; visibility: hidden; }
        }
        
        .back-btn {
            background: rgba(255, 255, 255, 0.1);
            border: none;
            color: #fff;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .back-btn:hover {
            background: rgba(255, 255, 255, 0.15);
        }
        
        .footer {
            text-align: center;
            margin-top: 60px;
            padding: 30px;
            opacity: 0.7;
            font-size: 0.95rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .copyright {
            font-family: 'Orbitron', sans-serif;
            color: #ff5722;
            margin-top: 10px;
            text-shadow: 0 0 10px rgba(255, 87, 34, 0.5);
        }
        
        @media (max-width: 768px) {
            .logo {
                font-size: 2.2rem;
            }
            
            .section {
                padding: 25px;
            }
            
            button {
                padding: 14px 25px;
                margin-bottom: 10px;
            }
        }
    </style>
</head>
<body>
    <!-- Matrix Rain Effect -->
    <canvas class="matrix-rain" id="matrixRain"></canvas>
    
    <!-- Floating Particles -->
    <div class="particles" id="particles-container"></div>
    
    <!-- منطقة الإشعارات -->
    <div class="notifications" id="notifications"></div>
    
    <div class="container">
        <header>
            <div class="logo">L7AJ</div>
            <p class="description">Advanced game tools with elegant RGB effects interface</p>
        </header>
        
        <!-- الصفحة الرئيسية -->
        <section id="home-section" class="section active">
            <div class="features">
                <div class="feature-card" data-target="token-section">
                    <div class="feature-icon">🔑</div>
                    <h3 class="feature-title">Get Token</h3>
                    <p class="feature-description">
                        Get API access token easily using your ACSSToken.
                    </p>
                </div>
                
                <div class="feature-card" data-target="jwt-section">
                    <div class="feature-icon">🔓</div>
                    <h3 class="feature-title">Decode JWT</h3>
                    <p class="feature-description">
                        Decode JWT tokens to view hidden contents and verify data.
                    </p>
                </div>
                
                <div class="feature-card" data-target="items-section">
                    <div class="feature-icon">🎮</div>
                    <h3 class="feature-title">Add Items</h3>
                    <p class="feature-description">
                        Add items to your game profile easily.
                    </p>
                </div>
                
                <div class="feature-card" data-target="bio-section">
                    <div class="feature-icon">📝</div>
                    <h3 class="feature-title">Edit Bio</h3>
                    <p class="feature-description">
                        Change your in-game bio easily.
                    </p>
                </div>
            </div>
        </section>
        
        <!-- قسم الحصول على Token -->
        <section id="token-section" class="section">
            <button class="back-btn" onclick="showSection('home-section')">← Back to Home</button>
            <h2>Get Access Token</h2>
            <div class="form-group">
                <label>Enter ACSSToken:</label>
                <input type="text" id="acsstoken" placeholder="Enter ACSSToken here">
            </div>
            <button id="get-token-btn">Get Token</button>
            
            <div class="loading" id="token-loading">
                <div class="loading-spinner"></div>
                <p>Loading...</p>
            </div>
            
            <div class="result" id="token-result"></div>
        </section>
        
        <!-- قسم فك تشفير JWT -->
        <section id="jwt-section" class="section">
            <button class="back-btn" onclick="showSection('home-section')">← Back to Home</button>
            <h2>Decode JWT Token</h2>
            <div class="form-group">
                <label>Enter JWT Token:</label>
                <textarea id="jwt-token" rows="4" placeholder="Enter JWT Token here"></textarea>
            </div>
            <button id="decode-btn">Decode</button>
            <div class="result" id="jwt-result"></div>
        </section>
        
        <!-- قسم إضافة العناصر -->
        <section id="items-section" class="section">
            <button class="back-btn" onclick="showSection('home-section')">← Back to Home</button>
            <h2>Add Items to Profile</h2>
            <div class="form-group">
                <label>Enter JWT Token (required for sending):</label>
                <input type="text" id="items-jwt-token" placeholder="Enter JWT Token here">
            </div>
            <p>Enter item IDs (leave empty for default value 203000000)</p>
            
            <div class="items-grid">
                {% for i in range(15) %}
                <div class="item-input">
                    <label>Item {{ i+1 }}:</label>
                    <input type="text" class="item-id" placeholder="203000000">
                </div>
                {% endfor %}
            </div>
            
            <div class="form-group">
                <label>Clan ID 1:</label>
                <input type="text" id="clan-id1" value="3048205855">
            </div>
            
            <div class="form-group">
                <label>Clan ID 2:</label>
                <input type="text" id="clan-id2" value="3048205855">
            </div>
            
            <button id="send-items-btn">Send Items</button>
            
            <div class="loading" id="items-loading">
                <div class="loading-spinner"></div>
                <p>Sending data...</p>
            </div>
            
            <div class="result" id="items-result"></div>
        </section>
        
        <!-- قسم تعديل البايو -->
        <section id="bio-section" class="section">
            <button class="back-btn" onclick="showSection('home-section')">← Back to Home</button>
            <h2>Edit Bio</h2>
            <div class="form-group">
                <label>Enter JWT Token (required for sending):</label>
                <input type="text" id="bio-jwt-token" placeholder="Enter JWT Token here">
            </div>
            <div class="form-group">
                <label>Enter new bio:</label>
                <textarea id="new-bio" rows="4" placeholder="Enter new bio text here"></textarea>
            </div>
            <button id="update-bio-btn">Update Bio</button>
            
            <div class="loading" id="bio-loading">
                <div class="loading-spinner"></div>
                <p>Updating bio...</p>
            </div>
            
            <div class="result" id="bio-result"></div>
        </section>
        
        <!-- التذييل -->
        <div class="footer">
            <p>Advanced Game Tools</p>
            <div class="copyright">© 2023 L7AJ - ALL RIGHTS RESERVED</div>
        </div>
    </div>

    <script>
        // إنشاء تأثير Matrix Rain
        function createMatrixRain() {
            const canvas = document.getElementById('matrixRain');
            const ctx = canvas.getContext('2d');
            
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            
            const letters = '01010101010101010101010101010101010101010101010101010101010101010101010101010101';
            const fontSize = 14;
            const columns = canvas.width / fontSize;
            
            const drops = [];
            for(let i = 0; i < columns; i++) {
                drops[i] = 1;
            }
            
            function draw() {
                ctx.fillStyle = 'rgba(0, 0, 20, 0.05)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                ctx.fillStyle = '#0F0';
                ctx.font = `${fontSize}px monospace`;
                
                for(let i = 0; i < drops.length; i++) {
                    const text = letters[Math.floor(Math.random() * letters.length)];
                    ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                    
                    if(drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                        drops[i] = 0;
                    }
                    
                    drops[i]++;
                }
            }
            
            setInterval(draw, 33);
        }
        
        // إنشاء جسيمات عائمة
        function createParticles() {
            const particlesContainer = document.getElementById('particles-container');
            const particleCount = 60;
            
            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.classList.add('particle');
                
                const size = Math.random() * 25 + 5;
                particle.style.width = `${size}px`;
                particle.style.height = `${size}px`;
                
                particle.style.left = `${Math.random() * 100}%`;
                particle.style.top = `${Math.random() * 100}%`;
                
                particle.style.animationDuration = `${Math.random() * 15 + 10}s`;
                particle.style.animationDelay = `${Math.random() * 5}s`;
                
                // ألوان عشوائية للجسيمات
                const colors = ['rgba(255, 87, 34, 0.5)', 'rgba(33, 150, 243, 0.5)', 'rgba(156, 39, 176, 0.5)', 'rgba(76, 175, 80, 0.5)'];
                particle.style.background = colors[Math.floor(Math.random() * colors.length)];
                
                particlesContainer.appendChild(particle);
            }
        }
        
        createMatrixRain();
        createParticles();
        
        // وظيفة لعرض القسم المحدد
        function showSection(sectionId) {
            // إخفاء جميع الأقسام
            document.querySelectorAll('.section').forEach(section => {
                section.classList.remove('active');
            });
            
            // إظهار القسم المحدد
            const targetSection = document.getElementById(sectionId);
            if (targetSection) {
                targetSection.classList.add('active');
            }
            
            // التمرير إلى الأعلى
            window.scrollTo(0, 0);
        }
        
        // التنقل بين الأقسام من الصفحة الرئيسية
        document.querySelectorAll('.feature-card').forEach(card => {
            card.addEventListener('click', () => {
                const targetSection = card.getAttribute('data-target');
                if (targetSection) {
                    showSection(targetSection);
                }
            });
        });
        
        // وظيفة لعرض الإشعارات
        function showNotification(message, type = 'info') {
            const notifications = document.getElementById('notifications');
            const notification = document.createElement('div');
            notification.classList.add('notification', type);
            notification.innerHTML = message;
            
            notifications.appendChild(notification);
            
            // إزالة الإشعار تلقائياً بعد 3 ثوان
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }
        
        // الحصول على Token
        document.getElementById('get-token-btn').addEventListener('click', async () => {
            const acsstoken = document.getElementById('acsstoken').value;
            if (!acsstoken) {
                showNotification('Please enter ACSSToken', 'error');
                return;
            }
            
            const loading = document.getElementById('token-loading');
            const resultDiv = document.getElementById('token-result');
            
            loading.style.display = 'block';
            resultDiv.innerHTML = '';
            
            try {
                // انتظار 4 ثواني كما هو مطلوب
                await new Promise(resolve => setTimeout(resolve, 4000));
                
                const response = await fetch(`/api/get_token/${acsstoken}`);
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `
                        <p class="success">Token obtained successfully!</p>
                        <p><strong>JWT Token:</strong></p>
                        <p style="overflow:auto; word-break: break-all;">${data.token}</p>
                        <button class="copy-btn" data-text="${data.token}">Copy Token</button>
                    `;
                    
                    // إضافة حدث النسخ للزر الجديد
                    const copyButton = document.querySelector('[data-text]');
                    if (copyButton) {
                        copyButton.addEventListener('click', (e) => {
                            const text = e.target.getAttribute('data-text');
                            navigator.clipboard.writeText(text);
                            showNotification('Token copied to clipboard', 'success');
                        });
                    }
                    
                    showNotification('Token obtained successfully', 'success');
                } else {
                    resultDiv.innerHTML = `<p class="error">${data.error}</p>`;
                    showNotification(data.error, 'error');
                }
            } catch (error) {
                resultDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
                showNotification('Error occurred while getting token', 'error');
            } finally {
                loading.style.display = 'none';
            }
        });
        
// Decode JWT
document.getElementById('decode-btn').addEventListener('click', () => {
    const jwtToken = document.getElementById('jwt-token').value;
    if (!jwtToken) {
        showNotification('Please enter a JWT Token', 'error');
        return;
    }
    
    const resultDiv = document.getElementById('jwt-result');
    
    try {
        // Split JWT parts (header, payload, signature)
        const parts = jwtToken.split('.');
        if (parts.length !== 3) {
            throw new Error('Invalid JWT Token format');
        }
        
        // Decode payload part
        const payload = parts[1];
        // Add padding if necessary
        const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
        const decodedPayload = atob(paddedPayload.replace(/-/g, '+').replace(/_/g, '/'));
        
        const decoded = JSON.parse(decodedPayload);
        
        if (decoded) {
            resultDiv.innerHTML = `
                <p class="success">JWT decoded successfully!</p>
                <p><strong>Decoded JWT data:</strong></p>
                <div style="max-height: 300px; overflow: auto;">
                    <pre style="white-space: pre-wrap; word-break: break-all;">${JSON.stringify(decoded, null, 2)}</pre>
                </div>
            `;
            showNotification('JWT decoded successfully', 'success');
        } else {
            resultDiv.innerHTML = `<p class="error">Unable to decode JWT Token</p>`;
            showNotification('Unable to decode JWT Token', 'error');
        }
    } catch (error) {
        resultDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
        showNotification('Error while decoding: ' + error.message, 'error');
    }
});
        
        // إرسال العناصر
        document.getElementById('send-items-btn').addEventListener('click', async () => {
            const jwtToken = document.getElementById('items-jwt-token').value;
            if (!jwtToken) {
                showNotification('Please enter JWT Token', 'error');
                return;
            }
            
            const itemInputs = document.querySelectorAll('.item-id');
            const clanId1 = document.getElementById('clan-id1').value || '3048205855';
            const clanId2 = document.getElementById('clan-id2').value || '3048205855';
            
            const items = [];
            itemInputs.forEach(input => {
                items.push(input.value || '203000000');
            });
            
            const loading = document.getElementById('items-loading');
            const resultDiv = document.getElementById('items-result');
            
            loading.style.display = 'block';
            resultDiv.innerHTML = '';
            
            try {
                const response = await fetch('/api/send_items', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        items: items,
                        clan_ids: [clanId1, clanId2],
                        jwt_token: jwtToken
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `
                        <p class="success">Items sent successfully!</p>
                        <p>Response code: ${data.status_code}</p>
                    `;
                    showNotification('Items sent successfully', 'success');
                } else {
                    let errorMsg = data.error;
                    if (data.status_code === 400 || data.status_code === 401) {
                        errorMsg = "Error! Items not sent. Please check your token and try again.";
                    }
                    resultDiv.innerHTML = `<p class="error">${errorMsg}</p>`;
                    showNotification(errorMsg, 'error');
                }
            } catch (error) {
                resultDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
                showNotification('Error occurred while sending items', 'error');
            } finally {
                loading.style.display = 'none';
            }
        });
        
        // تحديث البايو
        document.getElementById('update-bio-btn').addEventListener('click', async () => {
            const jwtToken = document.getElementById('bio-jwt-token').value;
            if (!jwtToken) {
                showNotification('Please enter JWT Token', 'error');
                return;
            }
            
            const newBio = document.getElementById('new-bio').value;
            if (!newBio) {
                showNotification('Please enter new bio', 'error');
                return;
            }
            
            const loading = document.getElementById('bio-loading');
            const resultDiv = document.getElementById('bio-result');
            
            loading.style.display = 'block';
            resultDiv.innerHTML = '';
            
            try {
                const response = await fetch('/api/update_bio', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        bio: newBio,
                        jwt_token: jwtToken
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.innerHTML = `
                        <p class="success">Bio updated successfully!</p>
                        <p>Response code: ${data.status_code}</p>
                    `;
                    showNotification('Bio updated successfully', 'success');
                } else {
                    let errorMsg = data.error;
                    if (data.status_code === 400 || data.status_code === 401) {
                        errorMsg = "Error! Bio not updated. Please check your token and try again.";
                    }
                    resultDiv.innerHTML = `<p class="error">${errorMsg}</p>`;
                    showNotification(errorMsg, 'error');
                }
            } catch (error) {
                resultDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
                showNotification('Error occurred while updating bio', 'error');
            } finally {
                loading.style.display = 'none';
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/get_token/<acsstoken>')
def get_token(acsstoken):
    try:
        # انتظار 4 ثواني كما هو مطلوب
        time.sleep(4)
        
        url = f"https://acsstoken.vercel.app/api/{acsstoken}"
        response = requests.get(url)
        data = response.json()
        
        if data.get("status") == "success":
            return jsonify({"success": True, "token": data.get("token", "")})
        else:
            return jsonify({"success": False, "error": "Failed to get token"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/send_items', methods=['POST'])
def send_items():
    try:
        data = request.json
        items = data.get('items', [])
        clan_ids = data.get('clan_ids', ['3048205855', '3048205855'])
        jwt_token = data.get('jwt_token', '')
        
        # إنشاء وتعبئة رسالة protobuf
        main_data = data_pb2.MainMessage()
        main_data.field_1 = 1

        # الحاوية الأولى
        container1 = main_data.field_2.add()
        container1.field_1 = 1

        # العناصر في الحاوية الأولى
        items_data = [
            {"field_1": 2, "field_4": 1, "field_6": {"field_6": int(items[0])}},
            {"field_1": 2, "field_4": 1, "field_5": 4, "field_6": {"field_6": int(items[1])}},
            {"field_1": 2, "field_4": 1, "field_5": 2, "field_6": {"field_6": int(items[2])}},
            {"field_1": 13, "field_3": 1, "field_6": {"field_6": int(items[3])}},
            {"field_1": 13, "field_3": 1, "field_4": 2, "field_6": {"field_6": int(items[4])}},
            {"field_1": 13, "field_3": 1, "field_5": 2, "field_6": {"field_6": int(items[5])}},
            {"field_1": 13, "field_3": 1, "field_5": 4, "field_6": {"field_6": int(items[6])}},
            {"field_1": 13, "field_3": 1, "field_4": 2, "field_5": 2, "field_6": {"field_6": int(items[7])}},
            {"field_1": 13, "field_3": 1, "field_4": 2, "field_5": 4, "field_6": {"field_6": int(items[8])}},
            {"field_1": 13, "field_3": 1, "field_4": 4, "field_6": {"field_6": int(items[9])}},
            {"field_1": 13, "field_3": 1, "field_4": 4, "field_5": 2, "field_6": {"field_6": int(items[10])}},
            {"field_1": 13, "field_3": 1, "field_4": 4, "field_5": 4, "field_6": {"field_6": int(items[11])}},
            {"field_1": 13, "field_3": 1, "field_4": 6, "field_6": {"field_6": int(items[12])}},
            {"field_1": 13, "field_3": 1, "field_4": 6, "field_5": 2, "field_6": {"field_6": int(items[13])}},
            {"field_1": 13, "field_3": 1, "field_4": 6, "field_5": 4, "field_6": {"field_6": int(items[14])}}
        ]

        for item_data in items_data:
            item = container1.field_2.add()
            item.field_1 = item_data["field_1"]
            if "field_3" in item_data:
                item.field_3 = item_data["field_3"]
            if "field_4" in item_data:
                item.field_4 = item_data["field_4"]
            if "field_5" in item_data:
                item.field_5 = item_data["field_5"]
            item.field_6.field_6 = item_data["field_6"]["field_6"]

        # الحاوية الثانية
        container2 = main_data.field_2.add()
        container2.field_1 = 9

        # العناصر في الحاوية الثانية
        item7 = container2.field_2.add()
        item7.field_4 = 3
        item7.field_6.field_14 = int(clan_ids[0])

        item8 = container2.field_2.add()
        item8.field_4 = 3
        item8.field_5 = 3
        item8.field_6.field_14 = int(clan_ids[1])

        # تشفير البيانات
        data_bytes = main_data.SerializeToString()
        padded_data = pad(data_bytes, AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(padded_data)

        # إرسال الطلب
        url = "https://clientbp.ggblueshark.com/SetPlayerGalleryShowInfo"
        headers = {
            "Expect": "100-continue",
            "Authorization": f"Bearer {jwt_token}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB50",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)",
            "Host": "clientbp.ggblueshark.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }

        response = requests.post(url, headers=headers, data=encrypted_data)
        
        return jsonify({
            "success": response.status_code == 200, 
            "status_code": response.status_code,
            "response_text": response.text
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "status_code": 500})

@app.route('/api/update_bio', methods=['POST'])
def update_bio():
    try:
        data = request.json
        bio_text = data.get('bio', '')
        jwt_token = data.get('jwt_token', '')
        
        # إنشاء وتعبئة رسالة protobuf للبايو
        bio_data = by_pb2.Data()
        bio_data.field_2 = 17
        bio_data.field_5.CopyFrom(by_pb2.EmptyMessage())
        bio_data.field_6.CopyFrom(by_pb2.EmptyMessage())
        bio_data.field_8 = bio_text
        bio_data.field_9 = 1
        bio_data.field_11.CopyFrom(by_pb2.EmptyMessage())
        bio_data.field_12.CopyFrom(by_pb2.EmptyMessage())

        # تشفير البيانات
        data_bytes = bio_data.SerializeToString()
        padded_data = pad(data_bytes, AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(padded_data)

        # إرسال الطلب
        url = "https://clientbp.ggblueshark.com/UpdateSocialBasicInfo"
        headers = {
            "Expect": "100-continue",
            "Authorization": f"Bearer {jwt_token}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB50",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Aferent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)",
            "Host": "clientbp.ggblueshark.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }

        response = requests.post(url, headers=headers, data=encrypted_data)
        
        return jsonify({
            "success": response.status_code == 200, 
            "status_code": response.status_code,
            "response_text": response.text
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "status_code": 500})

if __name__ == '__main__':
    app.run()
