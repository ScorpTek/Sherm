import os
import sqlite3
import json
import webbrowser
import threading
import time
import base64
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, g, send_from_directory

# HTML, CSS, and JavaScript as strings
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SHRM Matching FlashCard App</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

        :root {
            --primary-color: #4361ee;
            --primary-light: #edf2fb;
            --secondary-color: #3a0ca3;
            --text-color: #2b2d42;
            --light-text: #8d99ae;
            --background: #f8f9fa;
            --white: #ffffff;
            --success: #4cc9f0;
            --error: #f72585;
            --border-radius: 8px;
            --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            --transition: all 0.3s ease;
        }

        [data-theme="dark"] {
            --primary-color: #4cc9f0;
            --primary-light: #1e2a3a;
            --secondary-color: #f72585;
            --text-color: #e9ecef;
            --light-text: #adb5bd;
            --background: #121212;
            --white: #1e1e1e;
            --success: #06d6a0;
            --error: #ef476f;
            --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Poppins', sans-serif;
        }

        body {
            background-color: var(--background);
            color: var(--text-color);
            line-height: 1.6;
        }

        .container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 30px 20px;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
            position: relative;
        }

        .theme-toggle {
            position: absolute;
            top: 0;
            right: 0;
        }

        #theme-toggle-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 5px;
            box-shadow: none;
        }

        #theme-toggle-btn:hover {
            transform: scale(1.1);
            background: none;
        }

        .light-icon, .dark-icon {
            transition: var(--transition);
        }

        [data-theme="dark"] .light-icon {
            display: inline-block;
        }

        [data-theme="dark"] .dark-icon {
            display: none;
        }

        [data-theme="light"] .light-icon {
            display: none;
        }

        [data-theme="light"] .dark-icon {
            display: inline-block;
        }

        .love-note {
            color: var(--secondary-color);
            font-style: italic;
            margin-top: 5px;
            font-size: 0.9rem;
            opacity: 0.8;
        }

        h1 {
            color: var(--primary-color);
            margin-bottom: 10px;
            font-weight: 700;
            font-size: 2.5rem;
        }

        h2 {
            color: var(--secondary-color);
            margin-bottom: 25px;
            font-weight: 600;
            font-size: 1.8rem;
        }

        h3 {
            color: var(--text-color);
            margin: 20px 0;
            font-weight: 500;
            font-size: 1.3rem;
        }

        /* Tabs */
        .tabs {
            display: flex;
            margin-bottom: 30px;
            border-bottom: 2px solid #e9ecef;
            gap: 5px;
        }

        .tab-btn {
            padding: 12px 24px;
            background: none;
            border: none;
            border-radius: var(--border-radius) var(--border-radius) 0 0;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            color: var(--light-text);
            transition: var(--transition);
        }

        .tab-btn:hover {
            color: var(--primary-color);
            background-color: rgba(67, 97, 238, 0.05);
        }

        .tab-btn.active {
            color: var(--primary-color);
            border-bottom: 3px solid var(--primary-color);
            background-color: var(--primary-light);
        }

        .tab-content {
            display: none;
            padding: 25px 0;
            animation: fadeIn 0.3s ease-in-out;
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Forms */
        .form-group {
            margin-bottom: 25px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }

        .project-selector {
            margin-bottom: 25px;
        }

        input, select {
            padding: 12px 15px;
            border: 1px solid #e9ecef;
            border-radius: var(--border-radius);
            flex: 1;
            min-width: 200px;
            font-size: 15px;
            transition: var(--transition);
            box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
        }

        input:focus, select:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.15);
        }

        button {
            padding: 12px 20px;
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: var(--border-radius);
            cursor: pointer;
            transition: var(--transition);
            font-weight: 500;
            box-shadow: var(--box-shadow);
        }

        button:hover {
            background-color: var(--secondary-color);
            transform: translateY(-2px);
            box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
        }

        button:active {
            transform: translateY(0);
        }

        /* Lists */
        ul {
            list-style: none;
        }

        li {
            padding: 15px;
            margin-bottom: 10px;
            background-color: var(--white);
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            cursor: pointer;
            transition: var(--transition);
            border-left: 3px solid transparent;
        }

        li:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
        }

        li.selected {
            background-color: var(--primary-light);
            border-left: 3px solid var(--primary-color);
        }

        /* Tables */
        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin-top: 15px;
            box-shadow: var(--box-shadow);
            border-radius: var(--border-radius);
            overflow: hidden;
        }

        th, td {
            padding: 15px;
            text-align: left;
        }

        tr:not(:last-child) td {
            border-bottom: 1px solid #e9ecef;
        }

        th {
            background-color: var(--primary-light);
            color: var(--primary-color);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
        }

        tr:hover td {
            background-color: rgba(237, 242, 251, 0.5);
        }

        .actions-cell {
            width: 80px;
            text-align: center;
        }

        .delete-btn {
            background: none;
            border: none;
            font-size: 1.2rem;
            cursor: pointer;
            padding: 5px;
            box-shadow: none;
            transition: var(--transition);
        }

        .delete-btn:hover {
            transform: scale(1.2);
            color: var(--error);
            background: none;
        }

        /* Game Area */
        .hidden {
            display: none;
        }

        .drop-container, .drag-container {
            margin: 25px 0;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }

        /* Two-column game layout */
        .game-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
            background-color: var(--white);
            padding: 25px;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            max-height: 70vh;
            overflow: hidden;
        }

        .topics-column, .descriptions-column {
            overflow-y: auto;
            max-height: 65vh;
            padding: 0 10px;
        }

        .topics-column h3, .descriptions-column h3 {
            color: var(--primary-color);
            margin-bottom: 20px;
            text-align: center;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--primary-light);
        }

        .topic-box {
            background-color: var(--primary-light);
            border: 2px solid var(--primary-color);
            border-radius: var(--border-radius);
            padding: 15px;
            min-height: 100px;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
            box-shadow: var(--box-shadow);
            transition: var(--transition);
            position: relative;
        }

        .topic-box:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        }

        .topic-title {
            font-weight: 600;
            margin-bottom: 15px;
            text-align: center;
            color: var(--secondary-color);
            font-size: 1.1rem;
        }

        .description-card {
            background-color: var(--white);
            border-left: 4px solid var(--secondary-color);
            border-radius: var(--border-radius);
            padding: 15px;
            margin-bottom: 15px;
            cursor: grab;
            box-shadow: var(--box-shadow);
            transition: var(--transition);
            font-size: 0.95rem;
            width: 100%;
            position: relative;
        }

        .description-card::before {
            content: "⋮⋮";
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--light-text);
            font-size: 1.2rem;
        }

        .description-card:hover {
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
            transform: translateY(-3px);
        }

        .description-card.dragging {
            opacity: 0.6;
            transform: scale(1.05);
        }

        .drop-zone {
            min-height: 80px;
            border: 2px dashed #c7d2fe;
            border-radius: var(--border-radius);
            margin-top: 10px;
            padding: 10px;
            width: 100%;
            background-color: rgba(237, 242, 251, 0.5);
            transition: var(--transition);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .drop-zone.highlight {
            border-color: var(--primary-color);
            background-color: var(--primary-light);
        }

        .drop-zone:empty::before {
            content: "Drop description here";
            color: var(--light-text);
            font-style: italic;
        }

        /* Game Results */
        #game-results {
            background-color: var(--white);
            padding: 25px;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            animation: fadeIn 0.5s ease-in-out;
        }

        .correct {
            background-color: rgba(76, 201, 240, 0.1);
            border-left: 4px solid var(--success);
        }

        .incorrect {
            background-color: rgba(247, 37, 133, 0.05);
            border-left: 4px solid var(--error);
        }

        #score-display {
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--primary-color);
        }

        #results-details {
            margin: 25px 0;
            display: grid;
            gap: 15px;
        }

        .result-item {
            padding: 20px;
            margin-bottom: 15px;
            border-radius: var(--border-radius);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            transition: var(--transition);
        }

        .result-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
        }

        .result-item strong {
            color: var(--secondary-color);
        }

        .encouragement {
            margin-top: 25px;
            text-align: center;
            font-style: italic;
            color: var(--secondary-color);
            padding: 15px;
            border-top: 1px solid var(--primary-light);
        }

        .signature {
            text-align: center;
            margin-top: 20px;
            font-style: italic;
            font-weight: 500;
            color: var(--error);
            font-size: 0.9rem;
        }

        /* Import/Export styles */
        .import-export-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }

        .export-section, .import-section {
            background-color: var(--white);
            padding: 20px;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
        }

        #export-data, #import-data {
            width: 100%;
            height: 200px;
            margin: 15px 0;
            padding: 10px;
            border: 1px solid #e9ecef;
            border-radius: var(--border-radius);
            font-family: monospace;
            resize: vertical;
        }

        #export-result, #import-result {
            margin-top: 15px;
            padding: 10px;
            border-radius: var(--border-radius);
            background-color: var(--primary-light);
        }

        #copy-export-btn {
            background-color: var(--secondary-color);
        }

        /* Responsive */
        @media (max-width: 768px) {
            .tabs {
                flex-wrap: wrap;
            }
            
            .tab-btn {
                flex: 1;
                min-width: 100px;
                font-size: 14px;
                padding: 10px 15px;
            }
            
            .import-export-container {
                grid-template-columns: 1fr;
            }
            
            .form-group {
                flex-direction: column;
            }
            
            input, select, button {
                width: 100%;
            }
            
            .game-grid {
                grid-template-columns: 1fr;
                max-height: none;
            }
            
            .topics-column, .descriptions-column {
                max-height: 50vh;
            }
        }

        /* Game instructions */
        .scroll-instructions {
            text-align: center;
            margin-bottom: 15px;
            color: var(--light-text);
            font-style: italic;
            font-size: 0.9rem;
        }

        /* Love notes styling */
        .love-note {
            text-align: center;
            margin: 10px 0;
            color: var(--error);
            font-style: italic;
            font-size: 0.95rem;
            padding: 8px 15px;
            background-color: rgba(247, 37, 133, 0.05);
            border-radius: var(--border-radius);
            opacity: 1;
            transition: opacity 1s ease;
            animation: fadeIn 0.5s ease-in-out;
        }

        /* Confetti animation */
        .confetti-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9999;
            overflow: hidden;
        }

        .confetti {
            position: absolute;
            top: -10px;
            width: 10px;
            height: 20px;
            animation: confetti-fall linear forwards;
        }

        @keyframes confetti-fall {
            0% {
                transform: translateY(0) rotate(0deg);
                opacity: 1;
            }
            100% {
                transform: translateY(100vh) rotate(720deg);
                opacity: 0;
            }
        }

        /* Additional animations and effects */
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        .pulse {
            animation: pulse 1.5s infinite;
        }

        .button-container {
            display: flex;
            gap: 15px;
            margin: 20px 0;
            justify-content: center;
        }

        #submit-game, #play-again, #reset-matches {
            margin-top: 20px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        #submit-game, #play-again {
            background-color: var(--secondary-color);
        }

        #reset-matches {
            background-color: var(--light-text);
        }

        #submit-game:hover, #play-again:hover {
            background-color: var(--primary-color);
        }

        #reset-matches:hover {
            background-color: var(--text-color);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="theme-toggle">
                <button id="theme-toggle-btn">
                    <span class="light-icon">☀️</span>
                    <span class="dark-icon">🌙</span>
                </button>
            </div>
            <h1>SHRM Matching FlashCard App</h1>
            <p class="love-note">Made with ❤️ for Melissa, my brilliant star</p>
        </header>

        <div class="tabs">
            <button class="tab-btn active" data-tab="projects">Projects</button>
            <button class="tab-btn" data-tab="topics">Topics</button>
            <button class="tab-btn" data-tab="game">Game</button>
            <button class="tab-btn" data-tab="results">Results</button>
            <button class="tab-btn" data-tab="import-export">Import/Export</button>
        </div>

        <div id="projects" class="tab-content active">
            <h2>Projects</h2>
            <div class="form-group">
                <input type="text" id="project-name" placeholder="New Project Name">
                <button id="add-project">Add Project</button>
            </div>
            <div class="project-list">
                <h3>Your Projects</h3>
                <ul id="project-items"></ul>
            </div>
        </div>

        <div id="topics" class="tab-content">
            <h2>Topics</h2>
            <div class="project-selector">
                <label for="topic-project-select">Select Project:</label>
                <select id="topic-project-select"></select>
            </div>
            <div class="form-group">
                <input type="text" id="topic-input" placeholder="Topic">
                <input type="text" id="description-input" placeholder="Description">
                <button id="add-topic">Add Topic</button>
            </div>
            <div class="topic-list">
                <h3>Topics for this Project</h3>
                <table id="topic-table">
                    <thead>
                        <tr>
                            <th>Topic</th>
                            <th>Description</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="topic-items"></tbody>
                </table>
            </div>
        </div>

        <div id="game" class="tab-content">
            <h2>Match Game</h2>
            <div class="project-selector">
                <label for="game-project-select">Select Project:</label>
                <select id="game-project-select"></select>
                <button id="start-game">Start Game</button>
            </div>
            <div id="game-area" class="hidden">
                <!-- Game grid will be inserted here by JavaScript -->
                <div id="descriptions-container" class="drag-container"></div>
                <button id="submit-game">Submit Answers</button>
            </div>
            <div id="game-results" class="hidden">
                <h3>Game Results</h3>
                <p>Score: <span id="score-display"></span></p>
                <div id="results-details"></div>
                <button id="play-again">Play Again</button>
            </div>
        </div>

        <div id="results" class="tab-content">
            <h2>Game History</h2>
            <div class="project-selector">
                <label for="results-project-select">Select Project:</label>
                <select id="results-project-select"></select>
            </div>
            <div class="results-list">
                <h3>Previous Results</h3>
                <table id="results-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Score</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody id="results-items"></tbody>
                </table>
            </div>
        </div>

        <div id="import-export" class="tab-content">
            <h2>Import/Export</h2>
            <div class="import-export-container">
                <div class="export-section">
                    <h3>Export Project</h3>
                    <div class="project-selector">
                        <label for="export-project-select">Select Project to Export:</label>
                        <select id="export-project-select"></select>
                    </div>
                    <button id="export-project-btn">Export Project</button>
                    <div id="export-result" class="hidden">
                        <p>Copy the text below and save it:</p>
                        <textarea id="export-data" readonly></textarea>
                        <button id="copy-export-btn">Copy to Clipboard</button>
                    </div>
                </div>
                
                <div class="import-section">
                    <h3>Import Project</h3>
                    <p>Paste exported project data below:</p>
                    <textarea id="import-data" placeholder="Paste project data here..."></textarea>
                    <button id="import-project-btn">Import Project</button>
                    <div id="import-result" class="hidden">
                        <p>Project imported successfully!</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Wait for the DOM to be fully loaded
        window.onload = function() {
            console.log("Window loaded");
            
            // Initialize theme
            initTheme();
            
            // Initialize tabs
            initTabs();
            
            // Global state
            let currentProjectId = null;
            let gameTopics = [];
            
            // Helper function to get the base URL for API calls
            function getBaseUrl() {
                return window.location.pathname.includes('/sherm-flashcard-app') 
                    ? '/sherm-flashcard-app' 
                    : '';
            }
            
            // Load projects on page load
            loadProjects();
            
            // Add event listeners
            addEventListeners();
            
            // Theme functions
            function initTheme() {
                const savedTheme = localStorage.getItem('theme') || 'light';
                document.documentElement.setAttribute('data-theme', savedTheme);
                
                document.getElementById('theme-toggle-btn').onclick = function() {
                    const currentTheme = document.documentElement.getAttribute('data-theme');
                    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                    document.documentElement.setAttribute('data-theme', newTheme);
                    localStorage.setItem('theme', newTheme);
                };
            }
            
            // Tab functions
            function initTabs() {
                const tabButtons = document.querySelectorAll('.tab-btn');
                const tabContents = document.querySelectorAll('.tab-content');
                
                tabButtons.forEach(button => {
                    button.onclick = function() {
                        const tabName = this.getAttribute('data-tab');
                        
                        // Update active tab button
                        tabButtons.forEach(btn => btn.classList.remove('active'));
                        this.classList.add('active');
                        
                        // Show selected tab content
                        tabContents.forEach(content => {
                            content.classList.remove('active');
                            if (content.id === tabName) {
                                content.classList.add('active');
                            }
                        });
                    };
                });
            }
            
            // Add all event listeners
            function addEventListeners() {
                // Project Management
                document.getElementById('add-project').onclick = createProject;
                
                // Topic Management
                document.getElementById('topic-project-select').onchange = function() {
                    currentProjectId = this.value;
                    if (currentProjectId) {
                        loadTopics(currentProjectId);
                    }
                };
                
                document.getElementById('add-topic').onclick = createTopic;
                
                // Game Management
                document.getElementById('game-project-select').onchange = function() {
                    currentProjectId = this.value;
                };
                
                document.getElementById('start-game').onclick = startGame;
                document.getElementById('submit-game').onclick = submitGame;
                document.getElementById('play-again').onclick = resetGame;
                
                // Results Management
                document.getElementById('results-project-select').onchange = function() {
                    loadResults(this.value);
                };
                
                // Import/Export Management
                document.getElementById('export-project-btn').onclick = exportProject;
                document.getElementById('copy-export-btn').onclick = copyExportData;
                document.getElementById('import-project-btn').onclick = importProject;
            }
            
            // API Functions
            function loadProjects() {
                // Get the base URL for API calls
                const baseUrl = window.location.pathname.includes('/sherm-flashcard-app') 
                    ? '/sherm-flashcard-app' 
                    : '';
                    
                fetch(`${baseUrl}/api/debug`)
                    .then(response => response.json())
                    .then(data => {
                        console.log("API Debug:", data);
                        return fetch(`${baseUrl}/api/projects`);
                    })
                    .then(response => response.json())
                    .then(projects => {
                        console.log("Projects loaded:", projects);
                        updateProjectLists(projects);
                        
                        // Also update export dropdown
                        const exportSelect = document.getElementById('export-project-select');
                        exportSelect.innerHTML = '<option value="">Select a project</option>';
                        
                        projects.forEach(project => {
                            const option = document.createElement('option');
                            option.value = project.id;
                            option.textContent = project.name;
                            exportSelect.appendChild(option);
                        });
                    })
                    .catch(error => {
                        console.error('Error loading projects:', error);
                        alert('Error loading projects. Please check the console for details.');
                    });
            }
            
            function updateProjectLists(projects) {
                // Update project list in Projects tab
                const projectList = document.getElementById('project-items');
                projectList.innerHTML = '';
                
                // Update project dropdowns in other tabs
                const topicSelect = document.getElementById('topic-project-select');
                const gameSelect = document.getElementById('game-project-select');
                const resultsSelect = document.getElementById('results-project-select');
                
                topicSelect.innerHTML = '<option value="">Select a project</option>';
                gameSelect.innerHTML = '<option value="">Select a project</option>';
                resultsSelect.innerHTML = '<option value="">Select a project</option>';
                
                projects.forEach(project => {
                    // Add to project list
                    const li = document.createElement('li');
                    li.textContent = project.name;
                    li.dataset.id = project.id;
                    li.onclick = function() {
                        document.querySelectorAll('#project-items li').forEach(item => {
                            item.classList.remove('selected');
                        });
                        this.classList.add('selected');
                        
                        // Switch to Topics tab and load topics for this project
                        document.querySelector('[data-tab="topics"]').click();
                        document.getElementById('topic-project-select').value = project.id;
                        currentProjectId = project.id;
                        loadTopics(project.id);
                    };
                    projectList.appendChild(li);
                    
                    // Add to dropdowns
                    const option = document.createElement('option');
                    option.value = project.id;
                    option.textContent = project.name;
                    
                    topicSelect.appendChild(option.cloneNode(true));
                    gameSelect.appendChild(option.cloneNode(true));
                    resultsSelect.appendChild(option.cloneNode(true));
                });
            }
            
            function createProject() {
                const projectName = document.getElementById('project-name').value.trim();
                if (!projectName) {
                    alert('Please enter a project name');
                    return;
                }
                
                // Get the base URL for API calls
                const baseUrl = window.location.pathname.includes('/sherm-flashcard-app') 
                    ? '/sherm-flashcard-app' 
                    : '';
                    
                fetch(`${baseUrl}/api/projects`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name: projectName })
                })
                .then(response => response.json())
                .then(newProject => {
                    console.log("Project created:", newProject);
                    document.getElementById('project-name').value = '';
                    loadProjects();
                })
                .catch(error => {
                    console.error('Error creating project:', error);
                    alert('Error creating project. Please try again.');
                });
            }
            
            function loadTopics(projectId) {
                const baseUrl = getBaseUrl();
                fetch(`${baseUrl}/api/projects/${projectId}/topics`)
                    .then(response => response.json())
                    .then(topics => {
                        console.log("Topics loaded:", topics);
                        const topicTable = document.getElementById('topic-items');
                        topicTable.innerHTML = '';
                        
                        topics.forEach(topic => {
                            const row = document.createElement('tr');
                            
                            const topicCell = document.createElement('td');
                            topicCell.textContent = topic.topic;
                            
                            const descriptionCell = document.createElement('td');
                            descriptionCell.textContent = topic.description;
                            
                            const actionsCell = document.createElement('td');
                            actionsCell.className = 'actions-cell';
                            
                            const deleteBtn = document.createElement('button');
                            deleteBtn.className = 'delete-btn';
                            deleteBtn.innerHTML = '🗑️';
                            deleteBtn.title = 'Delete this topic';
                            deleteBtn.onclick = function() {
                                if (confirm('Are you sure you want to delete this topic?')) {
                                    deleteTopic(topic.id, projectId);
                                }
                            };
                            
                            actionsCell.appendChild(deleteBtn);
                            
                            row.appendChild(topicCell);
                            row.appendChild(descriptionCell);
                            row.appendChild(actionsCell);
                            
                            topicTable.appendChild(row);
                        });
                    })
                    .catch(error => {
                        console.error('Error loading topics:', error);
                        alert('Error loading topics. Please try again.');
                    });
            }
            
            function deleteTopic(topicId, projectId) {
                const baseUrl = getBaseUrl();
                fetch(`${baseUrl}/api/topics/${topicId}`, {
                    method: 'DELETE'
                })
                .then(response => {
                    if (response.ok) {
                        loadTopics(projectId);
                    } else {
                        throw new Error('Failed to delete topic');
                    }
                })
                .catch(error => {
                    console.error('Error deleting topic:', error);
                    alert('Error deleting topic. Please try again.');
                });
            }
            
            function createTopic() {
                const projectId = document.getElementById('topic-project-select').value;
                const topic = document.getElementById('topic-input').value.trim();
                const description = document.getElementById('description-input').value.trim();
                
                if (!projectId) {
                    alert('Please select a project');
                    return;
                }
                
                if (!topic || !description) {
                    alert('Please enter both topic and description');
                    return;
                }
                
                const baseUrl = getBaseUrl();
                fetch(`${baseUrl}/api/projects/${projectId}/topics`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ topic, description })
                })
                .then(response => response.json())
                .then(newTopic => {
                    console.log("Topic created:", newTopic);
                    document.getElementById('topic-input').value = '';
                    document.getElementById('description-input').value = '';
                    loadTopics(projectId);
                })
                .catch(error => {
                    console.error('Error creating topic:', error);
                    alert('Error creating topic. Please try again.');
                });
            }
            
            function startGame() {
                console.log("Starting game...");
                const projectId = document.getElementById('game-project-select').value;
                
                if (!projectId) {
                    alert('Please select a project');
                    return;
                }
                
                console.log(`Loading topics for project ${projectId}`);
                
                const baseUrl = getBaseUrl();
                fetch(`${baseUrl}/api/projects/${projectId}/topics`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(topics => {
                        console.log(`Loaded ${topics.length} topics`);
                        
                        if (topics.length < 2) {
                            alert('You need at least 2 topics to play the game');
                            return;
                        }
                        
                        gameTopics = topics;
                        renderGame(topics);
                        
                        document.getElementById('game-area').classList.remove('hidden');
                        document.getElementById('game-results').classList.add('hidden');
                    })
                    .catch(error => {
                        console.error('Error loading topics for game:', error);
                        alert('Error loading topics. Please try again.');
                    });
            }
            
            function renderGame(topics) {
                console.log("Rendering game with topics:", topics);
                
                // Clear any existing game grid
                const existingGrid = document.querySelector('.game-grid');
                if (existingGrid) {
                    existingGrid.remove();
                }
                
                const gameArea = document.getElementById('game-area');
                const descriptionsContainer = document.getElementById('descriptions-container');
                descriptionsContainer.innerHTML = '';
                
                // Create game grid container
                const gameGrid = document.createElement('div');
                gameGrid.className = 'game-grid';
                gameArea.insertBefore(gameGrid, descriptionsContainer);
                
                // Create topics column
                const topicsColumn = document.createElement('div');
                topicsColumn.className = 'topics-column';
                topicsColumn.innerHTML = '<h3>Topics</h3>';
                gameGrid.appendChild(topicsColumn);
                
                // Create descriptions column
                const descriptionsColumn = document.createElement('div');
                descriptionsColumn.className = 'descriptions-column';
                descriptionsColumn.innerHTML = '<h3>Descriptions</h3>';
                gameGrid.appendChild(descriptionsColumn);
                
                // Add scroll instructions
                const scrollInstructions = document.createElement('div');
                scrollInstructions.className = 'scroll-instructions';
                scrollInstructions.innerHTML = '<p>Scroll within each column to see all items</p>';
                gameArea.insertBefore(scrollInstructions, gameGrid);
                
                // Always show a love note (not random anymore)
                const loveNote = document.createElement('div');
                loveNote.className = 'love-note';
                
                // Select a random love message
                const loveMessages = [
                    "Melissa, you make every day brighter. - Jr",
                    "For my amazing wife, who inspires me every day. - Jr",
                    "Learning is better together. Love you, Melissa! - Jr",
                    "You're the smartest person I know. - Your Jr",
                    "Every match you make reminds me of how we match perfectly. - Jr"
                ];
                
                loveNote.textContent = loveMessages[Math.floor(Math.random() * loveMessages.length)];
                gameArea.insertBefore(loveNote, gameGrid);
                
                // Keep the message visible permanently
                
                // Create shuffled array of descriptions
                const descriptions = [...topics].map(t => t.description);
                shuffleArray(descriptions);
                
                // Create topic boxes with drop zones
                topics.forEach((topic, index) => {
                    const topicBox = document.createElement('div');
                    topicBox.className = 'topic-box';
                    topicBox.dataset.id = topic.id;
                    
                    const topicTitle = document.createElement('div');
                    topicTitle.className = 'topic-title';
                    topicTitle.textContent = topic.topic;
                    
                    const dropZone = document.createElement('div');
                    dropZone.className = 'drop-zone';
                    dropZone.dataset.topicId = topic.id;
                    dropZone.dataset.index = index;
                    
                    // Add drag and drop event listeners
                    dropZone.ondragover = function(e) {
                        e.preventDefault();
                        this.classList.add('highlight');
                    };
                    
                    dropZone.ondragleave = function() {
                        this.classList.remove('highlight');
                    };
                    
                    dropZone.ondrop = function(e) {
                        e.preventDefault();
                        this.classList.remove('highlight');
                        
                        const draggedId = e.dataTransfer.getData('text/plain');
                        const draggedElement = document.getElementById(draggedId);
                        
                        // If there's already a card in this drop zone, swap them
                        if (this.children.length > 0) {
                            const existingCard = this.children[0];
                            descriptionsColumn.appendChild(existingCard);
                        }
                        
                        this.appendChild(draggedElement);
                    };
                    
                    topicBox.appendChild(topicTitle);
                    topicBox.appendChild(dropZone);
                    topicsColumn.appendChild(topicBox);
                });
                
                // Add reset button
                const resetButton = document.createElement('button');
                resetButton.id = 'reset-matches';
                resetButton.textContent = 'Reset Matches';
                resetButton.onclick = function() {
                    // Move all cards back to descriptions column
                    document.querySelectorAll('.drop-zone .description-card').forEach(card => {
                        descriptionsColumn.appendChild(card);
                    });
                };
                
                const buttonContainer = document.createElement('div');
                buttonContainer.className = 'button-container';
                buttonContainer.appendChild(resetButton);
                gameGrid.after(buttonContainer);
                
                // Create draggable description cards
                descriptions.forEach((description, index) => {
                    const card = document.createElement('div');
                    card.className = 'description-card';
                    card.id = `desc-${index}`;
                    card.textContent = description;
                    card.draggable = true;
                    
                    card.ondragstart = function(e) {
                        e.dataTransfer.setData('text/plain', this.id);
                        this.classList.add('dragging');
                    };
                    
                    card.ondragend = function() {
                        this.classList.remove('dragging');
                    };
                    
                    descriptionsColumn.appendChild(card);
                });
            }
            
            function submitGame() {
                const dropZones = document.querySelectorAll('.drop-zone');
                let score = 0;
                const total = gameTopics.length;
                const results = [];
                
                dropZones.forEach(zone => {
                    const topicId = zone.dataset.topicId;
                    const topic = gameTopics.find(t => t.id == topicId);
                    
                    if (zone.children.length > 0) {
                        const userAnswer = zone.children[0].textContent;
                        const isCorrect = userAnswer === topic.description;
                        
                        if (isCorrect) {
                            score++;
                        }
                        
                        results.push({
                            topic: topic.topic,
                            correctAnswer: topic.description,
                            userAnswer: userAnswer,
                            isCorrect: isCorrect
                        });
                    } else {
                        results.push({
                            topic: topic.topic,
                            correctAnswer: topic.description,
                            userAnswer: 'No answer',
                            isCorrect: false
                        });
                    }
                });
                
                // Save result to database
                const projectId = document.getElementById('game-project-select').value;
                
                const baseUrl = getBaseUrl();
                fetch(`${baseUrl}/api/projects/${projectId}/results`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ score, total })
                })
                .then(response => response.json())
                .then(() => {
                    displayGameResults(score, total, results);
                })
                .catch(error => {
                    console.error('Error saving game results:', error);
                    alert('Error saving game results. Please try again.');
                });
            }
            
            function displayGameResults(score, total, results) {
                document.getElementById('game-area').classList.add('hidden');
                document.getElementById('game-results').classList.remove('hidden');
                
                const percentage = Math.round(score/total*100);
                document.getElementById('score-display').textContent = `${score} out of ${total} (${percentage}%)`;
                
                // Show confetti for perfect scores
                if (percentage === 100) {
                    showConfetti();
                }
                
                const resultsDetails = document.getElementById('results-details');
                resultsDetails.innerHTML = '';
                
                results.forEach(result => {
                    const resultItem = document.createElement('div');
                    resultItem.className = `result-item ${result.isCorrect ? 'correct' : 'incorrect'}`;
                    
                    resultItem.innerHTML = `
                        <strong>Topic:</strong> ${result.topic}<br>
                        <strong>Correct Answer:</strong> ${result.correctAnswer}<br>
                        <strong>Your Answer:</strong> ${result.userAnswer}<br>
                        <strong>Result:</strong> ${result.isCorrect ? 'Correct' : 'Incorrect'}
                    `;
                    
                    resultsDetails.appendChild(resultItem);
                });
                
                // Add encouraging message based on score
                const encouragement = document.createElement('div');
                encouragement.className = 'encouragement';
                
                let message = '';
                
                if (percentage === 100) {
                    message = "Perfect score! You're amazing, Melissa! Just like you are in everything you do. ❤️";
                } else if (percentage >= 80) {
                    message = "Great job, Melissa! Your brilliance shines through as always!";
                } else if (percentage >= 60) {
                    message = "Well done! I believe in you, just like I always have. - Jr";
                } else {
                    message = "Keep going! You've got this. I'm always here cheering for you. - Jr";
                }
                
                encouragement.textContent = message;
                document.getElementById('game-results').appendChild(encouragement);
                
                // Add a special signature
                const signature = document.createElement('div');
                signature.className = 'signature';
                signature.innerHTML = "Made with love by Jr ❤️";
                document.getElementById('game-results').appendChild(signature);
            }
            
            function resetGame() {
                // Remove the game grid if it exists
                const gameGrid = document.querySelector('.game-grid');
                if (gameGrid) {
                    gameGrid.remove();
                }
                
                document.getElementById('game-area').classList.remove('hidden');
                document.getElementById('game-results').classList.add('hidden');
                startGame();
            }
            
            function loadResults(projectId) {
                if (!projectId) return;
                
                const baseUrl = getBaseUrl();
                fetch(`${baseUrl}/api/projects/${projectId}/results`)
                    .then(response => response.json())
                    .then(results => {
                        console.log("Results loaded:", results);
                        const resultsTable = document.getElementById('results-items');
                        resultsTable.innerHTML = '';
                        
                        results.forEach(result => {
                            const row = document.createElement('tr');
                            
                            const dateCell = document.createElement('td');
                            dateCell.textContent = result.timestamp;
                            
                            const scoreCell = document.createElement('td');
                            scoreCell.textContent = `${result.score} / ${result.total}`;
                            
                            const percentageCell = document.createElement('td');
                            const percentage = Math.round((result.score / result.total) * 100);
                            percentageCell.textContent = `${percentage}%`;
                            
                            row.appendChild(dateCell);
                            row.appendChild(scoreCell);
                            row.appendChild(percentageCell);
                            
                            resultsTable.appendChild(row);
                        });
                    })
                    .catch(error => {
                        console.error('Error loading results:', error);
                        alert('Error loading results. Please try again.');
                    });
            }
            
            // Import/Export functions
            function exportProject() {
                const projectId = document.getElementById('export-project-select').value;
                
                if (!projectId) {
                    alert('Please select a project to export');
                    return;
                }
                
                // Get project details
                const baseUrl = getBaseUrl();
                fetch(`${baseUrl}/api/projects/${projectId}/topics`)
                    .then(response => response.json())
                    .then(topics => {
                        // Get project name
                        const projectName = document.getElementById('export-project-select').options[
                            document.getElementById('export-project-select').selectedIndex
                        ].text;
                        
                        // Create export data
                        const exportData = {
                            project: {
                                name: projectName
                            },
                            topics: topics.map(topic => ({
                                topic: topic.topic,
                                description: topic.description
                            }))
                        };
                        
                        // Display export data
                        document.getElementById('export-data').value = JSON.stringify(exportData, null, 2);
                        document.getElementById('export-result').classList.remove('hidden');
                    })
                    .catch(error => {
                        console.error('Error exporting project:', error);
                        alert('Error exporting project. Please try again.');
                    });
            }
            
            function copyExportData() {
                const exportData = document.getElementById('export-data');
                exportData.select();
                document.execCommand('copy');
                
                // Show feedback
                const copyBtn = document.getElementById('copy-export-btn');
                const originalText = copyBtn.textContent;
                copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 2000);
            }
            
            function importProject() {
                const importData = document.getElementById('import-data').value.trim();
                
                if (!importData) {
                    alert('Please paste project data to import');
                    return;
                }
                
                try {
                    const data = JSON.parse(importData);
                    
                    if (!data.project || !data.project.name || !data.topics || !Array.isArray(data.topics)) {
                        throw new Error('Invalid project data format');
                    }
                    
                    // First create the project
                    const baseUrl = getBaseUrl();
                    fetch(`${baseUrl}/api/projects`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ name: data.project.name })
                    })
                    .then(response => response.json())
                    .then(newProject => {
                        // Then add all topics
                        const addTopicPromises = data.topics.map(topic => {
                            return fetch(`${baseUrl}/api/projects/${newProject.id}/topics`, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    topic: topic.topic,
                                    description: topic.description
                                })
                            });
                        });
                        
                        return Promise.all(addTopicPromises).then(() => newProject);
                    })
                    .then(project => {
                        // Show success message
                        document.getElementById('import-result').classList.remove('hidden');
                        document.getElementById('import-data').value = '';
                        
                        // Reload projects
                        loadProjects();
                        
                        // Hide success message after a while
                        setTimeout(() => {
                            document.getElementById('import-result').classList.add('hidden');
                        }, 3000);
                    })
                    .catch(error => {
                        console.error('Error importing project:', error);
                        alert('Error importing project: ' + error.message);
                    });
                } catch (error) {
                    console.error('Error parsing import data:', error);
                    alert('Invalid project data format. Please check your input.');
                }
            }
            
            // Confetti animation for perfect scores
            function showConfetti() {
                const confettiCount = 200;
                const colors = ['#f72585', '#4361ee', '#4cc9f0', '#3a0ca3', '#7209b7'];
                
                const confettiContainer = document.createElement('div');
                confettiContainer.className = 'confetti-container';
                document.body.appendChild(confettiContainer);
                
                for (let i = 0; i < confettiCount; i++) {
                    const confetti = document.createElement('div');
                    confetti.className = 'confetti';
                    confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                    confetti.style.left = Math.random() * 100 + 'vw';
                    confetti.style.animationDuration = (Math.random() * 3 + 2) + 's';
                    confetti.style.animationDelay = Math.random() * 5 + 's';
                    confettiContainer.appendChild(confetti);
                }
                
                setTimeout(() => {
                    confettiContainer.remove();
                }, 8000);
            }
            
            // Utility function to shuffle array
            function shuffleArray(array) {
                for (let i = array.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [array[i], array[j]] = [array[j], array[i]];
                }
                return array;
            }
        };
    </script>
</body>
</html>
'''

# Initialize Flask app
app = Flask(__name__)

# Database setup
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.cursor().executescript('''
            DROP TABLE IF EXISTS projects;
            DROP TABLE IF EXISTS topics;
            DROP TABLE IF EXISTS results;

            CREATE TABLE projects (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );

            CREATE TABLE topics (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL,
                topic TEXT NOT NULL,
                description TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            );

            CREATE TABLE results (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            );
        ''')
        db.commit()

# Create tables if they don't exist
def setup_database():
    if not os.path.exists(DATABASE):
        init_db()

# Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# API Endpoints
@app.route('/api/projects', methods=['GET', 'POST'])
def handle_projects():
    db = get_db()
    if request.method == 'POST':
        data = request.get_json()
        project_name = data.get('name')
        
        cursor = db.cursor()
        cursor.execute('INSERT INTO projects (name) VALUES (?)', (project_name,))
        db.commit()
        
        return jsonify({'id': cursor.lastrowid, 'name': project_name}), 201
    else:
        cursor = db.execute('SELECT * FROM projects')
        projects = [dict(id=row['id'], name=row['name']) for row in cursor.fetchall()]
        return jsonify(projects)

@app.route('/api/projects/<int:project_id>/topics', methods=['GET', 'POST'])
def handle_topics(project_id):
    db = get_db()
    if request.method == 'POST':
        data = request.get_json()
        topic = data.get('topic')
        description = data.get('description')
        
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO topics (project_id, topic, description) VALUES (?, ?, ?)',
            (project_id, topic, description)
        )
        db.commit()
        
        return jsonify({
            'id': cursor.lastrowid,
            'project_id': project_id,
            'topic': topic,
            'description': description
        }), 201
    else:
        cursor = db.execute(
            'SELECT * FROM topics WHERE project_id = ?',
            (project_id,)
        )
        topics = [dict(
            id=row['id'],
            project_id=row['project_id'],
            topic=row['topic'],
            description=row['description']
        ) for row in cursor.fetchall()]
        return jsonify(topics)

@app.route('/api/projects/<int:project_id>/results', methods=['GET', 'POST'])
def handle_results(project_id):
    db = get_db()
    if request.method == 'POST':
        data = request.get_json()
        score = data.get('score')
        total = data.get('total')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO results (project_id, score, total, timestamp) VALUES (?, ?, ?, ?)',
            (project_id, score, total, timestamp)
        )
        db.commit()
        
        return jsonify({
            'id': cursor.lastrowid,
            'project_id': project_id,
            'score': score,
            'total': total,
            'timestamp': timestamp
        }), 201
    else:
        cursor = db.execute(
            'SELECT * FROM results WHERE project_id = ? ORDER BY timestamp DESC',
            (project_id,)
        )
        results = [dict(
            id=row['id'],
            project_id=row['project_id'],
            score=row['score'],
            total=row['total'],
            timestamp=row['timestamp']
        ) for row in cursor.fetchall()]
        return jsonify(results)

@app.route('/api/topics/<int:topic_id>', methods=['DELETE'])
def delete_topic(topic_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM topics WHERE id = ?', (topic_id,))
    db.commit()
    return '', 204

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to check if API is working"""
    return jsonify({
        'status': 'ok',
        'message': 'API is working',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    # Print welcome message
    print("=" * 60)
    print("SHERM Matching FlashCard App")
    print("Created with love by Jr for Melissa")
    print("=" * 60)
    print("Starting up...")
    
    # Setup database
    setup_database()
    
    # Open browser automatically
    threading.Thread(target=open_browser).start()
    
    # Run the app
    print("App is running! Open your browser to http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000)
