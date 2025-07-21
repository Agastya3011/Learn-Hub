from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app) # Allow CORS for development

# Define the path to your JSON data file
RESOURCES_FILE_PATH = 'data.json'
LEARNING_RESOURCES = [] # Initialize as empty list

# Function to load resources from the JSON file
def load_learning_resources():
    global LEARNING_RESOURCES
    if os.path.exists(RESOURCES_FILE_PATH):
        with open(RESOURCES_FILE_PATH, 'r', encoding='utf-8') as f:
            LEARNING_RESOURCES = json.load(f)
        print(f"Loaded {len(LEARNING_RESOURCES)} topics from {RESOURCES_FILE_PATH}")
    else:
        print(f"Warning: {RESOURCES_FILE_PATH} not found. LEARNING_RESOURCES will be empty.")
        LEARNING_RESOURCES = [] # Ensure it's an empty list if file not found

# Load resources when the app starts
load_learning_resources()

# The HTML content for the single-page application
# This remains the same as it correctly fetches data from Flask endpoints
INDEX_HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Learning Resources Hub</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f4;
            color: #333;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background-color: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            color: #0056b3;
            margin-bottom: 25px;
        }
        .controls {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 30px;
            gap: 15px;
        }
        select {
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            min-width: 250px;
            background-color: #f9f9f9;
            cursor: pointer;
        }
        select:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
        }
        .dashboard {
            border: 1px solid #e0e0e0;
            padding: 20px;
            border-radius: 8px;
            background-color: #fcfcfc;
            min-height: 300px;
        }
        .initial-message {
            text-align: center;
            font-size: 24px;
            color: #666;
            padding: 50px 20px;
        }
        .topic-section {
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 1px dashed #eee;
        }
        .topic-section:last-child {
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }
        .topic-title {
            font-size: 22px;
            color: #0056b3;
            margin-top: 0;
            margin-bottom: 15px;
            border-bottom: 2px solid #007bff;
            padding-bottom: 5px;
            display: inline-block;
        }
        .resource-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .resource-item {
            background-color: #e9f5ff;
            border: 1px solid #cce5ff;
            margin-bottom: 10px;
            padding: 15px;
            border-radius: 6px;
            display: flex;
            flex-direction: column;
        }
        .resource-item:last-child {
            margin-bottom: 0;
        }
        .resource-title {
            font-size: 18px;
            margin: 0 0 5px 0;
            color: #004085;
        }
        .resource-title a {
            text-decoration: none;
            color: #004085;
        }
        .resource-title a:hover {
            text-decoration: underline;
        }
        .resource-description {
            font-size: 14px;
            color: #555;
            margin-bottom: 8px;
        }
        .resource-meta {
            font-size: 12px;
            color: #777;
            display: flex;
            gap: 10px;
        }
        .resource-meta span {
            background-color: #d1ecf1;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: bold;
            color: #0c5460;
        }
        .error-message {
            color: red;
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Learning Resources Hub</h1>

        <div class="controls">
            <label for="topic-select">Select a Topic:</label>
            <select id="topic-select">
                <option value="">-- Select --</option>
            </select>
        </div>

        <div id="dashboard" class="dashboard">
            <p class="initial-message">Search, Learn, Grow</p>
        </div>
    </div>

    <script>
        const topicSelect = document.getElementById('topic-select');
        const dashboard = document.getElementById('dashboard');

        // Function to fetch and populate topics dropdown
        async function populateTopics() {
            try {
                const response = await fetch('http://127.0.0.1:5000/topics'); // Assuming Flask runs on 5000
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const topics = await response.json();

                // Clear existing options, keeping the default "Select --"
                topicSelect.innerHTML = '<option value="">-- Select --</option>'; 

                topics.forEach(topic => {
                    const option = document.createElement('option');
                    option.value = topic;
                    option.textContent = topic;
                    topicSelect.appendChild(option);
                });
            } catch (error) {
                console.error('Error fetching topics:', error);
                dashboard.innerHTML = `<p class="error-message">Failed to load topics. Please try again later.</p>`;
            }
        }

        // Function to fetch and display resources for a selected topic
        async function fetchResourcesByTopic(topic) {
            dashboard.innerHTML = '<p class="initial-message">Loading resources...</p>'; // Loading message
            try {
                const url = topic ? `http://127.0.0.1:5000/search?topic=${encodeURIComponent(topic)}` : 'http://127.0.0.1:5000/search';
                const response = await fetch(url);

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                displayResources(data, topic); // Pass topic to display function to handle "all" vs "filtered" display
            } catch (error) {
                console.error('Error fetching resources:', error);
                dashboard.innerHTML = `<p class="error-message">Failed to load resources for "${topic}".</p>`;
            }
        }

        // Function to display resources in the dashboard
        function displayResources(data, selectedTopic) {
            dashboard.innerHTML = ''; // Clear previous content

            if (data.length === 0) {
                dashboard.innerHTML = '<p class="initial-message">No resources found for this topic.</p>';
                return;
            }

            if (!selectedTopic) { // Display all topics if no specific topic selected
                data.forEach(category => {
                    if (category.resources && category.resources.length > 0) {
                        const topicSection = document.createElement('div');
                        topicSection.classList.add('topic-section');

                        const topicTitle = document.createElement('h2');
                        topicTitle.classList.add('topic-title');
                        topicTitle.textContent = category.topic;
                        topicSection.appendChild(topicTitle);

                        const resourceList = document.createElement('ul');
                        resourceList.classList.add('resource-list');

                        category.resources.forEach(resource => {
                            resourceList.appendChild(createResourceItem(resource));
                        });
                        topicSection.appendChild(resourceList);
                        dashboard.appendChild(topicSection);
                    }
                });
            } else { // Display resources for a specific selected topic
                const resourceList = document.createElement('ul');
                resourceList.classList.add('resource-list');
                data.forEach(resource => {
                    resourceList.appendChild(createResourceItem(resource));
                });
                dashboard.appendChild(resourceList);
            }
        }

        // Helper function to create a resource item HTML element
        function createResourceItem(resource) {
            const listItem = document.createElement('li');
            listItem.classList.add('resource-item');

            const titleElement = document.createElement('h3');
            titleElement.classList.add('resource-title');
            const link = document.createElement('a');
            link.href = resource.url;
            link.target = "_blank"; // Open in new tab
            link.rel = "noopener noreferrer"; // Security best practice
            link.textContent = resource.title;
            titleElement.appendChild(link);
            listItem.appendChild(titleElement);

            if (resource.description) {
                const descriptionElement = document.createElement('p');
                descriptionElement.classList.add('resource-description');
                descriptionElement.textContent = resource.description;
                listItem.appendChild(descriptionElement);
            }

            const metaDiv = document.createElement('div');
            metaDiv.classList.add('resource-meta');
            if (resource.type) {
                const typeSpan = document.createElement('span');
                typeSpan.textContent = `Type: ${resource.type}`;
                metaDiv.appendChild(typeSpan);
            }
            if (resource.category) {
                const categorySpan = document.createElement('span');
                categorySpan.textContent = `Category: ${resource.category}`;
                metaDiv.appendChild(categorySpan);
            }
            listItem.appendChild(metaDiv);

            return listItem;
        }


        // Event Listener for dropdown change
        topicSelect.addEventListener('change', (event) => {
            const selectedTopic = event.target.value;
            if (selectedTopic) {
                fetchResourcesByTopic(selectedTopic);
            } else {
                dashboard.innerHTML = '<p class="initial-message">Search, Learn, Grow</p>';
            }
        });

        // Initial load: Populate dropdown and set initial dashboard message
        document.addEventListener('DOMContentLoaded', () => {
            populateTopics();
            // The initial message "Search, Learn, Grow" is already in the HTML
            // No need to call fetchResourcesByTopic('') here as it would load all resources
            // unless you want all resources to be displayed initially.
            // If you want all resources to be displayed initially, uncomment the line below:
            # fetchResourcesByTopic(''); 
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML_CONTENT)

@app.route('/topics', methods=['GET'])
def get_topics():
    topics = sorted(list(set(resource["topic"] for resource in LEARNING_RESOURCES)))
    return jsonify(topics)

@app.route('/search', methods=['GET'])
def search_resources():
    topic = request.args.get('topic')

    if not topic:
        # If no topic is specified, return all resources grouped by topic
        all_resources_grouped = []
        unique_topics = sorted(list(set(resource["topic"] for resource in LEARNING_RESOURCES)))
        for t in unique_topics:
            resources_for_topic = []
            for entry in LEARNING_RESOURCES:
                if entry["topic"] == t:
                    resources_for_topic.extend(entry["resources"])
            all_resources_grouped.append({"topic": t, "resources": resources_for_topic})
        return jsonify(all_resources_grouped)

    filtered_resources = []
    for entry in LEARNING_RESOURCES:
        if entry["topic"].lower() == topic.lower():
            filtered_resources.extend(entry["resources"])

    return jsonify(filtered_resources)

if __name__ == '__main__':
    app.run(debug=True)